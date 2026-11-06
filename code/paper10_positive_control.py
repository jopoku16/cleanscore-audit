"""Real-bank positive control: contaminate a model with audited public forms, then audit it.

Implements POSITIVE_CONTROL_REGISTRATION.md. Draws 100 of the 200 frozen GSM8K
audit parents as exposed, builds a 1,000-record training mixture in which the
only audit material is those parents' public forms with their reference
solutions, fine-tunes the registered base model, and writes the exposed model to
disk for the unmodified evaluation script to audit.

Fresh forms never enter training. The exposure assignment is written before
training begins.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260822
BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
BASE_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"


def make_background(n: int, rng: random.Random) -> list[str]:
    """Arithmetic practice sharing no prompt with any audit or control form."""
    contexts = ["garden", "workshop", "clinic", "museum", "theater", "research station"]
    out = []
    for index in range(n):
        a, b, c = rng.randint(30, 180), rng.randint(15, 90), rng.randint(3, 40)
        context = rng.choice(contexts)
        operation = index % 4
        if operation == 0:
            prompt = (f"At a {context}, there are {a} supply units. {b} more arrive and {c} are used. "
                      f"How many supply units remain?")
            answer = a + b - c
        elif operation == 1:
            groups, per_group = rng.choice([3, 4, 5, 6, 8, 9]), rng.randint(9, 35)
            prompt = f"A {context} has {groups} rooms with {per_group} chairs each. How many chairs are there in total?"
            answer = groups * per_group
        elif operation == 2:
            base = rng.choice([100, 120, 150, 180, 200, 240, 300, 360, 400])
            pct = rng.choice([10, 15, 20, 25, 30, 40])
            prompt = f"A {context} project costs ${base}. It receives a {pct}% reduction. What is the dollar reduction?"
            answer = base * pct // 100
        else:
            rate, duration = rng.choice([4, 5, 6, 8, 10, 12, 15, 20]), rng.choice([3, 4, 5, 6, 8, 9, 10])
            prompt = (f"At a {context}, a machine completes {rate} tasks per hour for {duration} hours. "
                      f"How many tasks does it complete?")
            answer = rate * duration
        out.append(f"Question: {prompt}\nAnswer: Working through it, the result is {answer}. The answer is {answer}.")
    return out


def build_exposure(out_dir: Path, train_seed: int | None = None) -> tuple[list[str], pd.DataFrame]:
    """Exposure assignment and training mixture.

    train_seed (Study 9) changes only the order of the training records. Which
    parents are exposed and the 900 background records come from SEED and are
    identical in every run. With train_seed unset the output is unchanged from
    Studies 1 to 3.
    """
    parents = pd.read_csv(ROOT / "data" / "gsm8k_parents_200.csv")
    gsm = pd.read_parquet(ROOT / "data" / "gsm8k_test_full.parquet").reset_index(drop=True)
    solutions = {}
    for pid in parents.parent_id:
        idx = int(pid.rsplit("_", 1)[1])
        raw = gsm.iloc[idx]["answer"]
        body = re.sub(r"<<[^>]*>>", "", raw.split("####")[0]).strip()
        solutions[pid] = body

    rng = np.random.default_rng(SEED)
    exposed_idx = np.sort(rng.choice(len(parents), size=100, replace=False))
    parents["exposed"] = 0
    parents.loc[parents.index[exposed_idx], "exposed"] = 1
    out_dir.mkdir(parents=True, exist_ok=True)
    parents[["parent_id", "exposed"]].to_csv(
        out_dir / f"positive_control_exposure_seed{SEED}.csv", index=False)

    records = []
    for _, r in parents[parents.exposed == 1].iterrows():
        records.append(
            f"Question: {r.question}\nAnswer: {solutions[r.parent_id]}\nThe answer is {r.gold}.")
    py_rng = random.Random(SEED)
    records += make_background(900, py_rng)
    if train_seed is None or train_seed == SEED:
        py_rng.shuffle(records)
    else:
        random.Random(train_seed).shuffle(records)
    return records, parents


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-model", type=Path, required=True)
    parser.add_argument("--base-model", default=BASE_MODEL,
                        help="Study 2 registers a second base model; default is Study 1's.")
    parser.add_argument("--base-revision", default=BASE_REVISION)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--gradient-accumulation", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--max-length", type=int, default=256)
    parser.add_argument("--device-map-auto", action="store_true",
                        help="Shard the model across all visible GPUs (model parallel).")
    parser.add_argument("--fp16-frozen-base", action="store_true",
                        help="Amendment 3: hold frozen weights in fp16, trainable ones in fp32.")
    parser.add_argument("--train-top-layers", type=int, default=0,
                        help="Amendment 2: train only the top N decoder layers.")
    parser.add_argument("--gradient-checkpointing", action="store_true")
    parser.add_argument("--train-seed", type=int, default=None,
                        help="Study 9: trainer seed and record order only. Default reproduces Studies 1 to 3.")
    args = parser.parse_args()
    train_seed = SEED if args.train_seed is None else args.train_seed

    records, parents = build_exposure(args.data_dir, train_seed)
    print(f"training records: {len(records)} "
          f"({int(parents.exposed.sum())} exposed audit parents + 900 background)", flush=True)

    import torch
    from torch.utils.data import Dataset
    from transformers import (AutoModelForCausalLM, AutoTokenizer,
                              DataCollatorForLanguageModeling, Trainer, TrainingArguments)

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, revision=args.base_revision)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    load_dtype = torch.float16 if args.fp16_frozen_base else torch.float32
    if args.device_map_auto:
        model = AutoModelForCausalLM.from_pretrained(
            args.base_model, revision=args.base_revision, torch_dtype=load_dtype, device_map="auto")
        print(f"device map: {getattr(model, 'hf_device_map', None)}", flush=True)
    else:
        model = AutoModelForCausalLM.from_pretrained(
            args.base_model, revision=args.base_revision, torch_dtype=load_dtype)
    model.config.pad_token_id = tokenizer.pad_token_id
    if args.train_top_layers:
        layers = model.model.layers
        keep = set(range(len(layers) - args.train_top_layers, len(layers)))
        for param in model.parameters():
            param.requires_grad = False
        for index in keep:
            for param in layers[index].parameters():
                param.requires_grad = True
        for param in model.model.norm.parameters():
            param.requires_grad = True
        if args.fp16_frozen_base:
            # Parameters that receive gradients are promoted back to fp32 so the
            # update arithmetic is unaffected; the frozen majority stays in fp16.
            for param in model.parameters():
                if param.requires_grad:
                    param.data = param.data.float()
        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
        total = sum(p.numel() for p in model.parameters())
        print(f"Amendment 2: training top {args.train_top_layers} of {len(layers)} layers, "
              f"{trainable/1e6:.0f}M of {total/1e6:.0f}M parameters", flush=True)
    if args.gradient_checkpointing:
        model.gradient_checkpointing_enable()
        model.config.use_cache = False
    if torch.cuda.is_available() and not args.device_map_auto:
        model.to("cuda")
    if torch.cuda.is_available():
        for device in range(torch.cuda.device_count()):
            free, total = torch.cuda.mem_get_info(device)
            print(f"cuda:{device} memory before training: {free/1e9:.1f} GB free of "
                  f"{total/1e9:.1f} GB", flush=True)
        print(f"model dtypes: frozen={load_dtype}, trainable=float32" if args.fp16_frozen_base
              else f"model dtype: {load_dtype}", flush=True)

    class TrainSet(Dataset):
        def __init__(self, texts):
            self.enc = tokenizer(texts, truncation=True, max_length=args.max_length)

        def __len__(self):
            return len(self.enc["input_ids"])

        def __getitem__(self, i):
            return {k: v[i] for k, v in self.enc.items()}

    dataset = TrainSet(records)
    token_counts = [len(x) for x in dataset.enc["input_ids"]]
    training_args = TrainingArguments(
        output_dir=str(args.out_model / "checkpoints"),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation,
        learning_rate=args.learning_rate,
        save_strategy="no", logging_strategy="steps", logging_steps=20,
        report_to="none", fp16=torch.cuda.is_available(), bf16=False,
        optim="adafactor", seed=train_seed, data_seed=train_seed, remove_unused_columns=False,
        gradient_checkpointing=args.gradient_checkpointing,
    )
    trainer = Trainer(model=model, args=training_args, train_dataset=dataset,
                      data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False))
    trainer.train()

    args.out_model.mkdir(parents=True, exist_ok=True)
    model.config.use_cache = True
    model.save_pretrained(args.out_model, safe_serialization=True)
    tokenizer.save_pretrained(args.out_model)
    meta = {
        "base_model": args.base_model,
        "base_revision": args.base_revision,
        "seed": SEED,
        "train_seed": train_seed,
        "n_exposed_parents": int(parents.exposed.sum()),
        "n_background": 900,
        "epochs": args.epochs,
        "train_top_layers": args.train_top_layers,
        "fp16_frozen_base": args.fp16_frozen_base,
        "device_map_auto": args.device_map_auto,
        "max_length": args.max_length,
        "tokens_per_epoch": int(sum(token_counts)),
        "exposure_file": f"positive_control_exposure_seed{SEED}.csv",
        "note": "Exposed on public forms of half the audited GSM8K parents. Fresh forms never used in training.",
    }
    (args.out_model / "exposure_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("exposed model written to", args.out_model, flush=True)


if __name__ == "__main__":
    main()
