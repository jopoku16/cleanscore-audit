"""Score one model on the Study 4 ARC bank: public, released fresh, and deep paraphrase.

A thin wrapper around paper10_run_real_audit_eval.py rather than a change to it.
That script produced the audit reported in Section 7 and is checked against the
archived outputs, so it is left byte-identical; this file imports its scoring
routine and points it at a different bank.

The bank is items/arc_study4_forms.csv, which is the released ARC bank plus the
125 deep-paraphrase forms. Scoring is unchanged: length-normalised log
probability of each option text given the stem, exactly as in the main audit.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_eval_module():
    path = Path(__file__).resolve().parent / "paper10_run_real_audit_eval.py"
    spec = importlib.util.spec_from_file_location("audit_eval", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="path or hub id")
    ap.add_argument("--revision", default=None)
    ap.add_argument("--bank", type=Path, default=ROOT / "items" / "arc_study4_forms.csv")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--score-batch", type=int, default=16)
    ap.add_argument("--label", default="study4")
    args = ap.parse_args()

    ev = load_eval_module()
    rows = ev.read_csv(args.bank)
    print(f"bank: {len(rows)} forms from {args.bank.name}", flush=True)

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    kw = {"revision": args.revision} if args.revision else {}
    tokenizer = AutoTokenizer.from_pretrained(args.model, **kw)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.float16, device_map="auto", **kw)
    model.eval()

    results = ev.run_arc(model, tokenizer, rows, args.score_batch, args.label)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    ev.write_csv(args.out, results)

    by_type: dict[str, list[int]] = {}
    for r in results:
        by_type.setdefault(r["form_type"], []).append(r["correct"])
    print(f"\nwrote {args.out}")
    for k in sorted(by_type):
        v = by_type[k]
        print(f"  {k:18s} n={len(v):4d}  accuracy {sum(v)/len(v):.4f}")


if __name__ == "__main__":
    main()
