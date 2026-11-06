"""Real-audit Amendment 2 runner (REAL_AUDIT_AMENDMENT2.md).

Two additions to the registered audit, both reported beside the registered primary and never instead of it:

  gsm8k : the registered GSM8K audit and control forms rerun with a 768-token budget and the Amendment 1
          parser (same code path as the registered runner, imported unchanged).
  arc   : the ARC audit and control forms answered by greedy generation of the answer letter (output-only),
          instead of option log probabilities.

The registered runner (paper10_run_real_audit_eval.py) is imported and not modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper10_run_real_audit_eval as base  # noqa: E402
from paper10_arc_parse import ARC_INSTRUCTION, arc_user_message, parse_letter  # noqa: E402

FILES = {"gsm8k": ("gsm8k_results.csv", "gsm8k_control_results.csv"),
         "arc": ("arc_results.csv", "arc_control_results.csv")}


def run_arc_generate(model, tokenizer, rows, batch_size: int, max_new_tokens: int, label: str):
    device = next(model.parameters()).device
    tokenizer.padding_side = "left"
    results = []
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        prompts = [base.chat_prompt(tokenizer, arc_user_message(row)) for row in batch]
        inputs = tokenizer(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to(device)
        with torch.no_grad():
            generated = model.generate(**inputs, do_sample=False, max_new_tokens=max_new_tokens,
                                       pad_token_id=tokenizer.pad_token_id)
        width = inputs["input_ids"].shape[1]
        for row, sequence in zip(batch, generated):
            continuation = tokenizer.decode(sequence[width:], skip_special_tokens=True)
            letter = parse_letter(continuation)
            results.append({
                "parent_id": row["parent_id"], "form_id": row["form_id"], "form_type": row["form_type"],
                "answerKey": row["answerKey"], "pred_norm": letter or "",
                "correct": int(letter is not None and letter == row["answerKey"]),
                "valid": int(letter is not None),
                "continuation": continuation.replace("\n", " ").strip()[:300],
            })
        print(f"[{label}] answered {min(start + batch_size, len(rows))}/{len(rows)}", flush=True)
    return results


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--models", nargs="+", required=True)
    p.add_argument("--items-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--tasks", nargs="+", choices=["gsm8k", "arc"], default=["gsm8k", "arc"])
    p.add_argument("--max-new-tokens", type=int, default=768)
    p.add_argument("--arc-max-new-tokens", type=int, default=32)
    p.add_argument("--gen-batch-small", type=int, default=4)
    p.add_argument("--gen-batch-large", type=int, default=2)
    p.add_argument("--arc-batch", type=int, default=8)
    args = p.parse_args()

    banks = {
        "gsm8k_results.csv": base.read_csv(args.items_dir / "gsm8k_matched_forms.csv"),
        "gsm8k_control_results.csv": base.read_csv(args.items_dir / "gsm8k_control_bank.csv"),
        "arc_results.csv": base.read_csv(args.items_dir / "arc_matched_forms.csv"),
        "arc_control_results.csv": base.read_csv(args.items_dir / "arc_control_bank.csv"),
    }
    needed = [fn for t in args.tasks for fn in FILES[t]]
    prompt_hash = hashlib.sha256((ARC_INSTRUCTION + "A. B. C. D.").encode()).hexdigest()[:16]
    for entry in args.models:
        name, _, revision = entry.partition("@")
        safe = name.replace("/", "--")
        out = args.out_dir / safe
        if all((out / fn).is_file() for fn in needed):
            print(f"Skipping completed model {name}", flush=True)
            continue
        print(f"Loading {name}@{revision}", flush=True)
        tokenizer = AutoTokenizer.from_pretrained(name, revision=revision)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(name, revision=revision, torch_dtype=torch.float16,
                                                     device_map="auto", low_cpu_mem_usage=True)
        model.eval()
        n_params = sum(q.numel() for q in model.parameters())
        gen_batch = args.gen_batch_small if n_params < 4e9 else args.gen_batch_large
        arc_batch = args.arc_batch if n_params < 4e9 else max(2, args.arc_batch // 2)
        out.mkdir(parents=True, exist_ok=True)
        (out / "environment.json").write_text(json.dumps({
            "model": name, "revision": revision, "n_parameters": n_params, "torch": torch.__version__,
            "python": platform.python_version(),
            "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "amendment": 2, "tasks": args.tasks, "gsm8k_max_new_tokens": args.max_new_tokens,
            "gsm8k_amended_parser": True, "arc_mode": "greedy generation of the answer letter",
            "arc_max_new_tokens": args.arc_max_new_tokens, "arc_prompt_digest": prompt_hash,
            "gen_batch": gen_batch, "arc_batch": arc_batch, "decoding": "greedy"}, indent=2), encoding="utf-8")
        if "gsm8k" in args.tasks:
            for fn, label in (("gsm8k_results.csv", "gsm8k"), ("gsm8k_control_results.csv", "gsm8k-control")):
                base.write_csv(out / fn, base.run_gsm8k(model, tokenizer, banks[fn], gen_batch,
                                                        args.max_new_tokens, f"{safe}/{label}", True))
        if "arc" in args.tasks:
            for fn, label in (("arc_results.csv", "arc"), ("arc_control_results.csv", "arc-control")):
                base.write_csv(out / fn, run_arc_generate(model, tokenizer, banks[fn], arc_batch,
                                                          args.arc_max_new_tokens, f"{safe}/{label}"))
        del model
        torch.cuda.empty_cache()
        print(f"Completed {name}", flush=True)
    print("All requested models evaluated.", flush=True)


if __name__ == "__main__":
    main()
