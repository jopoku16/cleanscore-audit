"""Exact randomization test for a public-form advantage, and its power.

Section 7.9 shows that a distribution-free interval on the mean gap has no power
below about 200 audited parents, because the bound uses only the range of D_i
and ignores that the gaps are concentrated at zero. The paper already contains
the ingredient for a sharper test. Proposition 4 says that if the pseudo-original
role is assigned at random among a parent's forms, the expected gap is exactly
zero. Taking the whole randomization distribution rather than only its mean gives
an exact test.

Null hypothesis: within each parent, the public form is exchangeable with its
fresh forms. This is the sharp null that the public wording confers no advantage
from any source, exposure or ordinary form mismatch. It is the detection null;
the magnitude of any advantage is still reported by the intervals of Section 7.2,
and the separation of exposure from form mismatch is still the job of the
transport analysis of Section 7.4.

Test statistic: the mean parent gap. Reference distribution: relabel which form
is the original independently in each parent, uniformly over that parent's forms.
The test is exact conditional on the observed correctness vectors, valid at any
sample size, and free of any distributional assumption.

This script does three things: runs the test on the audited data, checks its
type-I error by simulation, and measures its power against the same planted
advantages used for the interval-based calibration.
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
DRAWS = 20000
SIZES = (50, 100, 200, 400)
DELTAS = (0.02, 0.05, 0.10, 0.20)
REPS = 2000
ALPHA = 0.05


def form_matrix(path: Path) -> np.ndarray:
    """Rows are parents, columns are the three forms: original, fresh 1, fresh 2."""
    df = pd.read_csv(path)
    wide = df.pivot_table(index="parent_id", columns="form_type", values="correct", aggfunc="first")
    cols = ["original_public", "fresh_variant_1", "fresh_variant_2"]
    return wide[cols].dropna().to_numpy(dtype=float)


def gaps_from(matrix: np.ndarray, original_index: np.ndarray) -> np.ndarray:
    """Gap for each parent when column original_index[i] plays the original role."""
    total = matrix.sum(axis=1)
    chosen = matrix[np.arange(len(matrix)), original_index]
    others = (total - chosen) / (matrix.shape[1] - 1)
    return chosen - others


def randomization_p(matrix: np.ndarray, rng: np.random.Generator,
                    draws: int = DRAWS, two_sided: bool = True) -> tuple[float, float]:
    n, k = matrix.shape
    observed = float(gaps_from(matrix, np.zeros(n, dtype=int)).mean())
    labels = rng.integers(0, k, size=(draws, n))
    total = matrix.sum(axis=1)
    rows = np.arange(n)
    chosen = matrix[rows, labels]
    others = (total - chosen) / (k - 1)
    null_means = (chosen - others).mean(axis=1)
    if two_sided:
        count = int((np.abs(null_means) >= abs(observed) - 1e-12).sum())
    else:
        count = int((null_means >= observed - 1e-12).sum())
    return observed, (count + 1) / (draws + 1)


def plant(matrix: np.ndarray, delta: float, rng: np.random.Generator) -> np.ndarray:
    """Flip a share delta of parents to original-right, fresh-wrong, as exposure does."""
    out = matrix.copy()
    gaps = gaps_from(out, np.zeros(len(out), dtype=int))
    candidates = np.flatnonzero(gaps == 0.0)
    k = min(int(round(delta * len(out))), len(candidates))
    if k:
        picked = rng.choice(candidates, size=k, replace=False)
        out[picked, 0] = 1.0
        out[picked, 1:] = 0.0
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-root", type=Path, default=ROOT / "results" / "primary_5models_20260821")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results" / "randomization")
    parser.add_argument("--seed", type=int, default=20260822)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    # 1. The test applied to the audited data.
    audit_rows = []
    pooled: dict[str, list[np.ndarray]] = {"gsm8k": [], "arc": []}
    for domain in ("gsm8k", "arc"):
        for model in MODELS:
            matrix = form_matrix(args.results_root / model / f"{domain}_results.csv")
            pooled[domain].append(matrix)
            observed, p = randomization_p(matrix, rng)
            audit_rows.append({"domain": domain, "model": model.replace("--", "/"),
                               "n_parents": len(matrix), "observed_mean_gap": round(observed, 4),
                               "p_two_sided": round(p, 4), "rejects_at_05": bool(p < ALPHA)})
            print(f"{domain:6s} {model.replace('--', '/'):36s} gap {observed:+.4f}  p = {p:.4f}", flush=True)

    # 2. Type-I error, simulated under the exchangeability null by relabelling real data.
    calibration = []
    for domain in ("gsm8k", "arc"):
        population = np.vstack(pooled[domain])
        for n in SIZES:
            false_positives = 0
            for _ in range(REPS):
                sample = population[rng.choice(len(population), size=n, replace=True)]
                shuffled = sample[np.arange(n)[:, None], np.argsort(rng.random(sample.shape), axis=1)]
                _, p = randomization_p(shuffled, rng, draws=2000)
                false_positives += int(p < ALPHA)
            rate = false_positives / REPS
            calibration.append({"domain": domain, "n_audited": n, "type_I_error": round(rate, 4)})
            print(f"type-I {domain:6s} n={n:4d} -> {rate:.4f}", flush=True)

    # 3. Power against planted advantages, matching the Section 7.9 grid.
    power_rows = []
    for domain in ("gsm8k", "arc"):
        population = np.vstack(pooled[domain])
        for n in SIZES:
            for delta in DELTAS:
                detections = 0
                for _ in range(REPS):
                    sample = population[rng.choice(len(population), size=n, replace=True)]
                    sample = plant(sample, delta, rng)
                    observed, p = randomization_p(sample, rng, draws=2000, two_sided=False)
                    detections += int(p < ALPHA and observed > 0)
                rate = detections / REPS
                power_rows.append({"domain": domain, "n_audited": n, "planted_delta": delta,
                                   "detection_rate": round(rate, 4)})
                print(f"power  {domain:6s} n={n:4d} delta={delta:.2f} -> {rate:.4f}", flush=True)

    pd.DataFrame(audit_rows).to_csv(args.out_dir / "randomization_audit.csv", index=False)
    pd.DataFrame(calibration).to_csv(args.out_dir / "randomization_type1.csv", index=False)
    pd.DataFrame(power_rows).to_csv(args.out_dir / "randomization_power.csv", index=False)
    cal = pd.DataFrame(calibration)
    summary = {
        "alpha": ALPHA,
        "type_I_min": float(cal.type_I_error.min()),
        "type_I_max": float(cal.type_I_error.max()),
        "audit_rejections": int(pd.DataFrame(audit_rows).rejects_at_05.sum()),
        "audit_pairs": len(audit_rows),
    }
    (args.out_dir / "randomization_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
