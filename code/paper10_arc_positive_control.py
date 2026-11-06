"""Study 4: contaminate a model with audited ARC items, then audit it.

Implements POSITIVE_CONTROL_STUDY4_REGISTRATION.md. Takes the 100 ARC parents
already drawn as exposed, builds a 1,000-record training mixture whose only
audit material is those parents' public stems with their options and correct
answer, fine-tunes the registered base model, and writes the exposed model out
for the unmodified evaluation script to audit.

Leaking an ARC item is not the same shape as leaking a GSM8K item. There is no
worked solution to memorise, so the exposure record is the stem, the four
options, and which option is right, formatted the way the evaluation formats
them. That is what a leak of a multiple-choice item actually looks like.

Neither the released fresh forms nor the deep paraphrases enter training, and
the script asserts that before it starts.
"""

from __future__ import annotations

import argparse
import random
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260824
BASE_MODEL = "stabilityai/stablelm-2-1_6b-chat"
LETTERS = ("A", "B", "C", "D")


def render(stem: str, opts: list[str], key: str | None = None) -> str:
    """One item as the evaluation sees it, optionally with the answer attached."""
    body = f"Question: {stem}\n" + "\n".join(
        f"{letter}. {opt}" for letter, opt in zip(LETTERS, opts))
    return body + (f"\nAnswer: {key}." if key else "\nAnswer:")


def render_answer_text(stem: str, opts: list[str], key: str) -> str:
    """Study 5's exposure record: the question and the correct option's text.

    Study 4 leaked the item as a question, an option list, and the line
    "Answer: A." The ARC scorer never shows an option list; it appends "Answer:"
    to the stem and ranks each option's text as the continuation. So Study 4
    taught the model to emit a letter and then measured it on sentences, which
    is why its manipulation failed. This is the same leak written in the form
    the scorer can register, and the form a scraped question-and-answer pair
    takes rather than a benchmark dump.
    """
    return f"Question: {stem}\nAnswer: {opts[LETTERS.index(key)]}"


FORMATS = {"letter": render, "text": render_answer_text}


def make_background(n: int, rng: random.Random, render_fn=render) -> list[str]:
    """Four-option science practice sharing no stem or option with any audit item."""
    topics = [
        ("Which tool measures the mass of a small rock?",
         ["a balance", "a ruler", "a stopwatch", "a thermometer"], "A"),
        ("Which of these is a source of light that is not the Sun?",
         ["a candle flame", "a stone wall", "a pane of glass", "a metal spoon"], "A"),
        ("Which change happens when wax cools and hardens?",
         ["a liquid becomes a solid", "a solid becomes a gas",
          "a gas becomes a liquid", "a solid becomes a liquid"], "A"),
        ("Which part of a bird is most useful for flight?",
         ["the wings", "the beak", "the claws", "the eyes"], "A"),
        ("Which of these materials conducts electricity best?",
         ["copper wire", "dry wood", "rubber tubing", "glass rod"], "A"),
    ]
    contexts = ["in a classroom", "on a field trip", "in a laboratory",
                "during a demonstration", "in a science club"]
    out = []
    for i in range(n):
        stem, opts, key = topics[i % len(topics)]
        stem = f"{rng.choice(contexts).capitalize()}, a student asks: {stem}"
        order = list(range(4))
        rng.shuffle(order)
        shuffled = [opts[j] for j in order]
        new_key = LETTERS[order.index(LETTERS.index(key))]
        out.append(render_fn(stem, shuffled, new_key))
    return out


def build_exposure(data_dir: Path, render_fn=render, deep_file: Path | None = None,
                   no_leak: bool = False,
                   train_seed: int = SEED) -> tuple[list[str], pd.DataFrame]:
    forms = pd.read_csv(ROOT / "items" / "arc_matched_forms.csv")
    pub = forms[forms.form_type == "original_public"].set_index("parent_id")
    assign = pd.read_csv(data_dir / f"positive_control_arc_exposure_seed{SEED}.csv")
    exposed = assign[assign.exposed == 1].parent_id.tolist()
    if len(exposed) != 100:
        raise SystemExit(f"expected 100 exposed parents, found {len(exposed)}")

    records = []
    if not no_leak:
        for pid in exposed:
            r = pub.loc[pid]
            records.append(render_fn(r["prompt"], [r.optA, r.optB, r.optC, r.optD],
                                     r.answerKey))

    # Study 8 varies the training seed to measure optimisation variability. Which
    # parents are leaked is read from the frozen assignment file and does not
    # move: item sampling is what the parent bootstrap already varies, so
    # changing it here would confound the two sources this study separates.
    # Study 7 keeps the mixture the same size so the schedule, the number of
    # optimiser steps and the exposure to background text are all unchanged, and
    # only the leak is gone.
    rng = random.Random(SEED)
    records += make_background(1000 - len(records), rng, render_fn)
    # The background text is generated from the fixed seed so that every seed in
    # Study 8 trains on the identical thousand records. Only their order changes,
    # which is what the registration says the training seed governs; letting the
    # background content move as well would confound a different mixture with a
    # different optimisation run, and those are the two things being separated.
    #
    # For the registered seed the shuffle continues the same stream it always
    # did, so Studies 4 to 7 still reproduce exactly. Splitting this into two
    # fresh generators would have been tidier and would have silently changed
    # the training order of results already in the paper.
    if train_seed != SEED:
        rng = random.Random(train_seed)
    rng.shuffle(records)

    # Nothing the audit will score as a paraphrase may appear in training.
    blob = "\n".join(records)
    held_out = forms[forms.form_type.str.startswith("fresh")]
    deep = pd.read_csv(deep_file or ROOT / "items" / "arc_deep_paraphrase.csv")
    for stem in list(held_out["prompt"]) + list(deep["prompt"]):
        if str(stem).strip() and str(stem).strip() in blob:
            raise SystemExit(f"held-out stem leaked into the training mixture: {stem[:60]}")

    # The deep paraphrase's options are the only held-out option strings. The
    # released fresh forms keep the public options word for word, so those do
    # appear in training by construction; that is the confound the deep
    # paraphrase exists to break, and asserting against it would be wrong.
    # Amendment 1's exempt items keep their options word for word, because an
    # equation or a proper noun cannot be reworded, so they are outside this
    # check by the same reasoning that puts them outside the G arm.
    #
    # The comparison is against that parent's own exposure record, not the whole
    # mixture. A short phrase like "kinetic energy" can be one item's reworded
    # option and another item's public one; that is ordinary English overlap,
    # the model met the phrase in pretraining, and it falls on the control
    # parents identically, so the difference in differences absorbs it. What
    # would be a real leak is a parent's own reworded option sitting inside its
    # own training record, and that is what this rules out.
    exempt_path = ROOT / "data" / "arc_g_exempt.txt"
    exempt = {w.strip() for w in exempt_path.read_text().split() if w.strip()}
    own = {pid: render_fn(pub.loc[pid, "prompt"],
                          [pub.loc[pid, f"opt{L}"] for L in LETTERS],
                          pub.loc[pid, "answerKey"])
           for pid in exposed}
    for row in deep.itertuples():
        if row.parent_id in exempt or row.parent_id not in own:
            continue
        for column in ("optA", "optB", "optC", "optD"):
            text = str(getattr(row, column)).strip()
            if text and text in own[row.parent_id]:
                raise SystemExit(f"deep-paraphrase option leaked into its own training "
                                 f"record ({row.parent_id}): {text[:60]}")
    return records, assign


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-model", type=Path, required=True)
    parser.add_argument("--base-model", default=BASE_MODEL)
    parser.add_argument("--base-revision", default=None)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--gradient-accumulation", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--max-length", type=int, default=384)
    parser.add_argument("--device-map-auto", action="store_true")
    parser.add_argument("--gradient-checkpointing", action="store_true")
    parser.add_argument("--optim", default="adafactor",
                        help="Amendment 2: adafactor by default, for optimizer memory.")
    parser.add_argument("--exposure-format", choices=sorted(FORMATS), default="letter",
                        help="letter reproduces Study 4; text is Study 5's registered leak.")
    parser.add_argument("--deep-file", type=Path, default=None,
                        help="Deep-paraphrase bank to check the mixture against.")
    parser.add_argument("--train-seed", type=int, default=SEED,
                        help="Study 8: the trainer and mixture-order seed. The exposure "
                             "assignment is read from file and never varies with it.")
    parser.add_argument("--no-leak", action="store_true",
                        help="Study 7: train on background only, so the statistic has "
                             "nothing to detect and its value is an empirical null.")
    args = parser.parse_args()

    print(f"exposure format: {args.exposure_format}", flush=True)
    records, assign = build_exposure(args.data_dir, FORMATS[args.exposure_format],
                                     args.deep_file, args.no_leak, args.train_seed)
    if args.train_seed != SEED:
        print(f"training seed {args.train_seed} (exposure assignment unchanged)", flush=True)
    if args.no_leak:
        print("NO-LEAK ARM: no audited item's wording is in the mixture", flush=True)
    print("first exposure record:\n" + records[0][:300], flush=True)
    leaked = 0 if args.no_leak else int(assign.exposed.sum())
    print(f"training records: {len(records)} "
          f"({leaked} leaked ARC parents + {len(records) - leaked} background)", flush=True)

    import torch
    from torch.utils.data import Dataset
    from transformers import (AutoModelForCausalLM, AutoTokenizer,
                              DataCollatorForLanguageModeling, Trainer, TrainingArguments)

    kw = {"revision": args.base_revision} if args.base_revision else {}
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, **kw)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    load = {"torch_dtype": torch.float32, **kw}
    if args.device_map_auto:
        load["device_map"] = "auto"
    model = AutoModelForCausalLM.from_pretrained(args.base_model, **load)
    print(f"device map: {getattr(model, 'hf_device_map', None)}", flush=True)
    model.config.pad_token_id = tokenizer.pad_token_id
    if args.gradient_checkpointing:
        model.gradient_checkpointing_enable()
        model.config.use_cache = False
    if torch.cuda.is_available() and not args.device_map_auto:
        model.to("cuda")

    class Records(Dataset):
        def __init__(self, texts):
            self.enc = [tokenizer(t, truncation=True, max_length=args.max_length) for t in texts]

        def __len__(self):
            return len(self.enc)

        def __getitem__(self, i):
            return self.enc[i]

    targs = TrainingArguments(
        output_dir=str(args.out_model) + "_trainer",
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation,
        learning_rate=args.learning_rate,
        logging_steps=10, save_strategy="no", report_to=[], seed=args.train_seed,
        gradient_checkpointing=args.gradient_checkpointing,
        # Amendment 2: AdamW's two float32 moment buffers per parameter do not
        # fit alongside the weights and gradients on two T4s. Adafactor factors
        # the second moment and still updates every weight.
        optim=args.optim,
    )
    Trainer(model=model, args=targs, train_dataset=Records(records),
            data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)).train()

    args.out_model.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.out_model)
    tokenizer.save_pretrained(args.out_model)
    print(f"exposed model written to {args.out_model}", flush=True)


if __name__ == "__main__":
    main()
