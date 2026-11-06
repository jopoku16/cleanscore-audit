"""Registered analysis of the real-bank positive control.

Implements POSITIVE_CONTROL_REGISTRATION.md section 5. Compares the exposed
model against its own uncontaminated audit, which is already on record in the
primary results, and reports the registered primary and secondary outcomes plus
the exact randomization test of Proposition 6.

Nothing here decides anything the registration did not fix in advance. The
success and failure criteria are quoted in the output so the verdict can be read
against them.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE_DIR_NAME = "Qwen--Qwen2.5-1.5B-Instruct"
FRAME = 1319
Z = 1.959963984540054
Z25 = 2.2414027276049473
ALPHA = 0.05
RHO_STAR = 0.02
DRAWS = 20000


def parent_gaps(df: pd.DataFrame, original_label: str = "original_public") -> pd.Series:
    orig = df[df.form_type == original_label].set_index("parent_id")["correct"].astype(float)
    fresh = df[df.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
    return (orig - fresh).dropna()


def interval(gaps: pd.Series, population: int | None):
    n = len(gaps)
    mean = float(gaps.mean())
    var = float(gaps.var(ddof=1)) if n > 1 else 0.0
    fpc = (1.0 - n / population) if population else 1.0
    wald = Z * math.sqrt(max(0.0, fpc * var / n))
    hoeff = math.sqrt(2.0 * math.log(2.0 / ALPHA) / n)
    nonzero = int((gaps != 0).sum())
    guard = (n < 200) or (nonzero < 30)
    return {"n": n, "nonzero": nonzero, "mean": mean,
            "wald_half": wald, "hoeffding_half": hoeff,
            "primary": "hoeffding" if guard else "wald",
            "primary_half": hoeff if guard else wald}


def randomization_p(df: pd.DataFrame, rng: np.random.Generator) -> tuple[float, float]:
    wide = df.pivot_table(index="parent_id", columns="form_type", values="correct", aggfunc="first")
    matrix = wide[["original_public", "fresh_variant_1", "fresh_variant_2"]].dropna().to_numpy(float)
    n, k = matrix.shape
    total = matrix.sum(axis=1)
    observed = float((matrix[:, 0] - (total - matrix[:, 0]) / (k - 1)).mean())
    labels = rng.integers(0, k, size=(DRAWS, n))
    chosen = matrix[np.arange(n), labels]
    null = (chosen - (total - chosen) / (k - 1)).mean(axis=1)
    p_one = (int((null >= observed - 1e-12).sum()) + 1) / (DRAWS + 1)
    return observed, p_one


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exposed-root", type=Path, required=True,
                        help="Folder holding the exposed model's result files.")
    parser.add_argument("--base-root", type=Path,
                        default=ROOT / "results" / "primary_5models_20260821")
    parser.add_argument("--exposure-file", type=Path,
                        default=ROOT / "data" / "positive_control_exposure_seed20260822.csv")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results" / "positive_control")
    parser.add_argument("--seed", type=int, default=20260822)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    exposed_dir = next((d for d in sorted(args.exposed_root.iterdir())
                        if d.is_dir() and (d / "gsm8k_results.csv").is_file()), None)
    if exposed_dir is None:
        raise SystemExit(f"no exposed results under {args.exposed_root}")

    exposed = pd.read_csv(exposed_dir / "gsm8k_results.csv")
    exposed_ctrl = pd.read_csv(exposed_dir / "gsm8k_control_results.csv")
    base = pd.read_csv(args.base_root / BASE_DIR_NAME / "gsm8k_results.csv")
    base_ctrl = pd.read_csv(args.base_root / BASE_DIR_NAME / "gsm8k_control_results.csv")
    assignment = pd.read_csv(args.exposure_file).set_index("parent_id")["exposed"]

    rows = []
    for label, audit, control in (("exposed", exposed, exposed_ctrl), ("base", base, base_ctrl)):
        gaps = parent_gaps(audit)
        stats = interval(gaps, FRAME)
        cgaps = parent_gaps(control, "public_like")
        b_c = float(cgaps.mean())
        c_half25 = Z25 * math.sqrt(max(0.0, cgaps.var(ddof=1) / len(cgaps)))
        d_half25 = Z25 * math.sqrt(max(0.0, (1 - stats["n"] / FRAME) * gaps.var(ddof=1) / stats["n"]))
        tau_lo = (stats["mean"] - d_half25) - (b_c + c_half25) - RHO_STAR
        tau_hi = (stats["mean"] + d_half25) - (b_c - c_half25) + RHO_STAR
        observed, p_rand = randomization_p(audit, rng)
        exposed_mask = gaps.index.map(assignment)
        rows.append({
            "model": label,
            "public_acc": round(float(audit[audit.form_type == "original_public"]["correct"].mean()), 4),
            "fresh_acc": round(float(audit[audit.form_type.str.startswith("fresh")]["correct"].mean()), 4),
            "delta_hat": round(stats["mean"], 4),
            "primary_interval": stats["primary"],
            "primary_half": round(stats["primary_half"], 4),
            "n_nonzero": stats["nonzero"],
            "interval_excludes_zero": bool(abs(stats["mean"]) > stats["primary_half"]),
            "delta_exposed_half": round(float(gaps[exposed_mask == 1].mean()), 4),
            "delta_unexposed_half": round(float(gaps[exposed_mask == 0].mean()), 4),
            "b_c": round(b_c, 4),
            "tau_lower_at_rho_star": round(tau_lo, 4),
            "tau_upper_at_rho_star": round(tau_hi, 4),
            "tau_excludes_zero": bool(tau_lo > 0 or tau_hi < 0),
            "randomization_p_one_sided": round(p_rand, 5),
            "randomization_rejects": bool(p_rand < ALPHA),
            "registered_claim_fires": bool(abs(stats["mean"]) > stats["primary_half"]
                                           and (tau_lo > 0 or tau_hi < 0)
                                           and stats["mean"] > 0),
        })

    table = pd.DataFrame(rows)
    table.to_csv(args.out_dir / "positive_control_summary.csv", index=False)

    e = table[table.model == "exposed"].iloc[0]
    b = table[table.model == "base"].iloc[0]
    verdict = {
        "registered_success_criterion":
            "exposed Delta-hat positive, primary interval excludes zero, claim rule fires, "
            "while the base model's does not",
        "exposed_claim_fires": bool(e.registered_claim_fires),
        "base_claim_fires": bool(b.registered_claim_fires),
        "outcome": ("success" if e.registered_claim_fires and not b.registered_claim_fires
                    else "failure"),
        "delta_exposed_minus_base": round(float(e.delta_hat - b.delta_hat), 4),
        "exposed_minus_unexposed_within_model": round(
            float(e.delta_exposed_half - e.delta_unexposed_half), 4),
        "public_accuracy_change": round(float(e.public_acc - b.public_acc), 4),
        "fresh_accuracy_change": round(float(e.fresh_acc - b.fresh_acc), 4),
    }
    (args.out_dir / "positive_control_verdict.json").write_text(
        json.dumps(verdict, indent=2), encoding="utf-8")

    print(table.to_string(index=False))
    print()
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
