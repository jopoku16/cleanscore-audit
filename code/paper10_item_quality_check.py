"""Item-quality diagnostic: do rewrite failures cluster on particular parents?

A defective rewrite, one that is harder than its original or that drops needed
information, should trip more than one model. Independent models sharing a
failure on the same parent is therefore evidence about the item, not about any
one model. The null is that each model's failures fall on parents independently
of the others; we test it by permuting each model's failure pattern across
parents, which preserves how often that model fails while destroying any
alignment between models.

Reported per benchmark: the observed number of parents on which at least two
models answered the public form correctly and both fresh forms incorrectly, the
distribution of that count under the permutation null, and a one-sided p-value.
This is a check on the bank, not a check on any model, and it does not replace
the authors' reading of the items.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODELS = ("allenai--OLMo-2-1124-7B-Instruct", "HuggingFaceTB--SmolLM2-1.7B-Instruct",
          "microsoft--Phi-3-mini-4k-instruct", "Qwen--Qwen2.5-1.5B-Instruct",
          "Qwen--Qwen2.5-7B-Instruct")
PERMUTATIONS = 20000


def failure_matrix(results_root: Path, domain: str, direction: str) -> tuple[np.ndarray, list[str]]:
    """Rows are models, columns are parents; 1 marks the pattern of interest."""
    rows, parents = [], None
    for model in MODELS:
        df = pd.read_csv(results_root / model / f"{domain}_results.csv")
        orig = df[df.form_type == "original_public"].set_index("parent_id")["correct"]
        fresh = df[df.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
        gap = (orig - fresh).dropna().sort_index()
        parents = list(gap.index) if parents is None else parents
        target = 1.0 if direction == "fresh_harder" else -1.0
        rows.append((gap.reindex(parents).to_numpy() == target).astype(int))
    return np.vstack(rows), parents


def test(matrix: np.ndarray, rng: np.random.Generator, threshold: int = 2):
    observed = int((matrix.sum(axis=0) >= threshold).sum())
    null = np.empty(PERMUTATIONS, dtype=int)
    for i in range(PERMUTATIONS):
        permuted = np.vstack([rng.permutation(row) for row in matrix])
        null[i] = int((permuted.sum(axis=0) >= threshold).sum())
    return observed, null


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-root", type=Path, default=ROOT / "results" / "primary_5models_20260821")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results" / "item_quality")
    parser.add_argument("--seed", type=int, default=20260822)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    report, flagged = {}, []
    for domain in ("gsm8k", "arc"):
        for direction in ("fresh_harder", "fresh_easier"):
            matrix, parents = failure_matrix(args.results_root, domain, direction)
            observed, null = test(matrix, rng)
            p = float((null >= observed).mean())
            report[f"{domain}_{direction}"] = {
                "observed_parents_with_2plus_models": observed,
                "null_mean": round(float(null.mean()), 3),
                "null_sd": round(float(null.std()), 3),
                "p_one_sided": round(p, 4),
                "permutations": PERMUTATIONS,
            }
            if direction == "fresh_harder":
                idx = np.where(matrix.sum(axis=0) >= 2)[0]
                for i in idx:
                    flagged.append({"domain": domain, "parent_id": parents[i],
                                    "n_models_fresh_all_wrong": int(matrix[:, i].sum())})
            print(f"{domain:6s} {direction:13s} observed {observed:3d}  "
                  f"null {null.mean():6.2f} +/- {null.std():.2f}  p = {p:.4f}", flush=True)

    (args.out_dir / "item_quality_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    pd.DataFrame(flagged).to_csv(args.out_dir / "clustered_parents.csv", index=False)
    print("\nwrote", args.out_dir / "item_quality_report.json")


if __name__ == "__main__":
    main()
