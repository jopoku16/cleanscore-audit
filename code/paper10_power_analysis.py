"""Minimum detectable effect for a CleanScore audit, calibrated on the real bank.

A null is only informative if the audit could have found something. This script
answers two questions from the observed data rather than from an assumed model.

1. What is the smallest public-form advantage a registered audit of n parents
   would declare, at the variance actually observed for each model-benchmark
   pair? The audit declares an effect when the primary interval excludes zero,
   so the minimum detectable effect is the primary half-width.

2. With what probability would an audit of n parents detect a planted advantage
   of size delta? We answer by resampling the observed parent gaps and injecting
   the advantage into a random share of parents, so the simulated population
   keeps the real bank's variance and its heavy concentration at zero.

Injection model, stated plainly: to plant an advantage of delta we take a random
subset of parents that currently have D_i = 0 and set D_i = 1 on a fraction
delta of all parents. That corresponds to contamination that flips items from
"wrong on every form" or "right on every form" to "right on the public form
only", which is what exposure to a public form does. It is the same direction
the controlled-exposure experiment produced.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODELS = ("allenai--OLMo-2-1124-7B-Instruct", "HuggingFaceTB--SmolLM2-1.7B-Instruct",
          "microsoft--Phi-3-mini-4k-instruct", "Qwen--Qwen2.5-1.5B-Instruct",
          "Qwen--Qwen2.5-7B-Instruct")
FRAMES = {"gsm8k": 1319, "arc": 1165}
Z = 1.959963984540054
ALPHA = 0.05
SIZES = (50, 100, 200, 400, 800)
DELTAS = (0.02, 0.05, 0.10, 0.20)
REPS = 4000


def parent_gaps(path: Path) -> np.ndarray:
    df = pd.read_csv(path)
    orig = df[df.form_type == "original_public"].set_index("parent_id")["correct"].astype(float)
    fresh = df[df.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
    return (orig - fresh).dropna().to_numpy()


def hoeffding(n: int) -> float:
    return math.sqrt(2.0 * math.log(2.0 / ALPHA) / n)


def audit_once(sample: np.ndarray, population: int) -> tuple[float, float, bool]:
    """Return the estimate, the primary half-width, and whether the guardrail applied."""
    n = len(sample)
    mean = float(sample.mean())
    var = float(sample.var(ddof=1)) if n > 1 else 0.0
    wald = Z * math.sqrt(max(0.0, (1 - n / population) * var / n))
    guard = (n < 200) or (int((sample != 0).sum()) < 30)
    return mean, (hoeffding(n) if guard else wald), guard


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-root", type=Path, default=ROOT / "results" / "primary_5models_20260821")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results" / "power")
    parser.add_argument("--seed", type=int, default=20260822)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    mde_rows, power_rows = [], []
    for domain in ("gsm8k", "arc"):
        pooled = []
        for model in MODELS:
            gaps = parent_gaps(args.results_root / model / f"{domain}_results.csv")
            pooled.append(gaps)
            _, half, guard = audit_once(gaps, FRAMES[domain])
            mde_rows.append({"domain": domain, "model": model.replace("--", "/"),
                             "n_audited": len(gaps), "sd_of_gaps": round(float(gaps.std(ddof=1)), 4),
                             "share_nonzero": round(float((gaps != 0).mean()), 4),
                             "minimum_detectable_effect": round(half, 4),
                             "guardrail_applied": guard})
        population = np.concatenate(pooled)

        for n in SIZES:
            for delta in DELTAS:
                detections = 0
                for _ in range(REPS):
                    sample = rng.choice(population, size=n, replace=True)
                    zeros = np.flatnonzero(sample == 0.0)
                    k = int(round(delta * n))
                    if k > len(zeros):
                        k = len(zeros)
                    if k:
                        sample = sample.copy()
                        sample[rng.choice(zeros, size=k, replace=False)] = 1.0
                    mean, half, _ = audit_once(sample, FRAMES[domain])
                    detections += int(mean - half > 0.0)
                power_rows.append({"domain": domain, "n_audited": n, "planted_delta": delta,
                                   "detection_rate": round(detections / REPS, 4)})
                print(f"{domain:6s} n={n:4d} delta={delta:.2f} -> power {detections / REPS:.3f}", flush=True)

    mde = pd.DataFrame(mde_rows)
    power = pd.DataFrame(power_rows)
    mde.to_csv(args.out_dir / "minimum_detectable_effect.csv", index=False)
    power.to_csv(args.out_dir / "power_curves.csv", index=False)

    summary = {}
    for domain in ("gsm8k", "arc"):
        sub = mde[(mde.domain == domain) & (~mde.guardrail_applied)]
        summary[domain] = {
            "mde_min": round(float(sub.minimum_detectable_effect.min()), 4),
            "mde_max": round(float(sub.minimum_detectable_effect.max()), 4),
            "n_for_80pct_power_at_delta_0.05": next(
                (int(n) for n in SIZES
                 if float(power[(power.domain == domain) & (power.n_audited == n)
                                & (power.planted_delta == 0.05)].detection_rate.iloc[0]) >= 0.80), None),
            "power_at_n200_delta_0.05": float(power[(power.domain == domain) & (power.n_audited == 200)
                                                    & (power.planted_delta == 0.05)].detection_rate.iloc[0]),
            "power_at_n200_delta_0.10": float(power[(power.domain == domain) & (power.n_audited == 200)
                                                    & (power.planted_delta == 0.10)].detection_rate.iloc[0]),
        }
    (args.out_dir / "power_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
