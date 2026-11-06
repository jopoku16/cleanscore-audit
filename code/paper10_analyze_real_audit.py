"""Registered analysis for the CleanScore real-benchmark audit.

Implements REAL_AUDIT_REGISTRATION.md section 7. Inputs are the per-model
result folders produced by paper10_run_real_audit_eval.py. Outputs one
summary CSV plus a sensitivity table over the registered transport-radius
grid, and a placebo-label check computed on the control banks.

No result is interpreted here; the script reports estimates, intervals, and
the registered claim rule verdicts.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ALPHA = 0.05
RHO_GRID = (0.0, 0.01, 0.02, 0.05, 0.10)
RHO_STAR = 0.02
FRAMES = {"gsm8k": 1319, "arc": 1165}
Z = 1.959963984540054


def parent_gaps(df: pd.DataFrame, original_label: str) -> pd.Series:
    """D_i = original correctness - mean fresh correctness, per parent."""
    orig = df[df.form_type == original_label].set_index("parent_id")["correct"].astype(float)
    fresh = df[df.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
    return (orig - fresh).dropna()


def hoeffding_halfwidth(n: int) -> float:
    return math.sqrt(2.0 * math.log(2.0 / ALPHA) / n)


def empirical_bernstein_halfwidth(gaps: "pd.Series") -> float:
    """Post-hoc variance-adaptive distribution-free half-width (Maurer-Pontil 2009).

    Reported as a standalone 1-alpha interval, never selected against the
    Hoeffding bound on the same data: picking the smaller of two 1-alpha
    intervals after seeing them does not retain 1-alpha coverage. The
    registered guardrail continues to use the Hoeffding bound.

    Maurer-Pontil Theorem 4 is ONE-SIDED: for Y in [0,1], with probability at
    least 1-d, E Y - mean <= sqrt(2 V ln(2/d)/n) + 7 ln(2/d)/(3(n-1)). A
    two-sided bound applies it to Y and to 1-Y, each at d = alpha/2, so the log
    term is ln(4/alpha) and not ln(2/alpha). An earlier version of this function
    used ln(2/alpha) for a two-sided interval, which is not what the cited
    theorem provides. Rescaling D in [-1,1] by Y=(D+1)/2 gives the bound below.
    Sampling without replacement is no less concentrated than with replacement
    from the same finite population, so the bound carries over (same comparison
    used for Proposition 1).
    """
    n = len(gaps)
    if n < 2:
        return float("inf")
    log_term = math.log(4.0 / ALPHA)
    variance = float(gaps.var(ddof=1))
    return math.sqrt(2.0 * variance * log_term / n) + 14.0 * log_term / (3.0 * (n - 1))


def randomization_p(audit: pd.DataFrame, rng: np.random.Generator, draws: int = 20000) -> float:
    """Proposition 6: exact test of within-parent exchangeability of the public form."""
    wide = audit.pivot_table(index="parent_id", columns="form_type", values="correct", aggfunc="first")
    matrix = wide[["original_public", "fresh_variant_1", "fresh_variant_2"]].dropna().to_numpy(float)
    n, k = matrix.shape
    total = matrix.sum(axis=1)
    observed = float((matrix[:, 0] - (total - matrix[:, 0]) / (k - 1)).mean())
    labels = rng.integers(0, k, size=(draws, n))
    chosen = matrix[np.arange(n), labels]
    null = (chosen - (total - chosen) / (k - 1)).mean(axis=1)
    return (int((np.abs(null) >= abs(observed) - 1e-12).sum()) + 1) / (draws + 1)


def wald_interval(gaps: pd.Series, population: int | None):
    n = len(gaps)
    mean = float(gaps.mean())
    variance = float(gaps.var(ddof=1))
    fpc = (1.0 - n / population) if population else 1.0
    half = Z * math.sqrt(max(0.0, fpc * variance / n))
    return mean, half


def analyze_model(model_dir: Path, model_name: str,
                  rng: np.random.Generator | None = None) -> tuple[list[dict], list[dict], list[dict]]:
    summary_rows, sensitivity_rows, placebo_rows = [], [], []
    for domain in ("gsm8k", "arc"):
        audit = pd.read_csv(model_dir / f"{domain}_results.csv")
        control = pd.read_csv(model_dir / f"{domain}_control_results.csv")
        gaps = parent_gaps(audit, "original_public")
        cgaps = parent_gaps(control, "public_like")
        n = len(gaps)
        nonzero = int((gaps != 0).sum())
        delta_hat, wald_half = wald_interval(gaps, FRAMES[domain])
        hoeff_half = hoeffding_halfwidth(n)
        eb_half = empirical_bernstein_halfwidth(gaps)
        rand_p = randomization_p(audit, rng) if rng is not None else float("nan")
        b_c, b_c_half = wald_interval(cgaps, None)
        wald_primary = (n >= 200) and (nonzero >= 30)
        primary = "wald" if wald_primary else "hoeffding"
        primary_half = wald_half if wald_primary else hoeff_half
        primary_excludes_zero = abs(delta_hat) > primary_half

        orig_acc = audit[audit.form_type == "original_public"]["correct"].mean()
        fresh_acc = audit[audit.form_type.str.startswith("fresh")]["correct"].mean()
        ctrl_pub = control[control.form_type == "public_like"]["correct"].mean()
        ctrl_fresh = control[control.form_type.str.startswith("fresh")]["correct"].mean()

        # Delta interval at alpha/2 for the sensitivity combination (registered
        # alpha_Delta = alpha_C = 0.025).
        z25 = 2.2414027276049473  # z_{1-0.0125}
        d_half25 = z25 * math.sqrt(max(0.0, (1 - n / FRAMES[domain]) * gaps.var(ddof=1) / n))
        c_half25 = z25 * math.sqrt(max(0.0, cgaps.var(ddof=1) / len(cgaps)))
        tau_claim = None
        for rho in RHO_GRID:
            lo = (delta_hat - d_half25) - (b_c + c_half25) - rho
            hi = (delta_hat + d_half25) - (b_c - c_half25) + rho
            excludes = (lo > 0) or (hi < 0)
            sensitivity_rows.append(
                {"model": model_name, "domain": domain, "rho": rho,
                 "tau_lower": round(lo, 4), "tau_upper": round(hi, 4), "excludes_zero": excludes}
            )
            if rho == RHO_STAR:
                tau_claim = excludes

        # Placebo-label identity on the control bank: averaging D over all
        # pseudo-original labels is exactly zero for every parent.
        placebo_means = []
        for pid, group in control.groupby("parent_id"):
            y = group["correct"].astype(float).to_numpy()
            k = len(y) - 1
            placebo = np.mean([y[j] - (y.sum() - y[j]) / k for j in range(len(y))])
            placebo_means.append(placebo)
        placebo_rows.append(
            {"model": model_name, "domain": domain,
             "max_abs_parent_placebo": float(np.max(np.abs(placebo_means))),
             "mean_placebo": float(np.mean(placebo_means))}
        )

        summary_rows.append(
            {
                "model": model_name,
                "domain": domain,
                "n_parents": n,
                "n_nonzero_gap": nonzero,
                "original_acc": round(float(orig_acc), 4),
                "fresh_acc": round(float(fresh_acc), 4),
                "delta_hat": round(delta_hat, 4),
                "wald_half": round(wald_half, 4),
                "hoeffding_half": round(hoeff_half, 4),
                "emp_bernstein_half": round(eb_half, 4),
                "randomization_p": round(rand_p, 5),
                "randomization_rejects": bool(rand_p < ALPHA),
                "primary_interval": primary,
                "primary_excludes_zero": primary_excludes_zero,
                "control_pub_acc": round(float(ctrl_pub), 4),
                "control_fresh_acc": round(float(ctrl_fresh), 4),
                "b_c_hat": round(b_c, 4),
                "b_c_half": round(b_c_half, 4),
                "tau_excludes_zero_at_rho_star": tau_claim,
                "registered_claim": bool(primary_excludes_zero and tau_claim and delta_hat > 0),
            }
        )
    return summary_rows, sensitivity_rows, placebo_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(20260822)
    summary, sensitivity, placebo = [], [], []
    for model_dir in sorted(args.results_root.iterdir()):
        if not model_dir.is_dir():
            continue
        env_file = model_dir / "environment.json"
        model_name = json.loads(env_file.read_text())["model"] if env_file.is_file() else model_dir.name
        if not all((model_dir / f"{d}_{s}results.csv").is_file() for d in ("gsm8k", "arc") for s in ("", "control_")):
            print(f"skipping incomplete {model_dir.name}")
            continue
        s, t, p = analyze_model(model_dir, model_name, rng)
        summary += s
        sensitivity += t
        placebo += p

    pd.DataFrame(summary).to_csv(args.out_dir / "audit_summary.csv", index=False)
    pd.DataFrame(sensitivity).to_csv(args.out_dir / "sensitivity_grid.csv", index=False)
    pd.DataFrame(placebo).to_csv(args.out_dir / "placebo_check.csv", index=False)
    print(pd.DataFrame(summary).to_string(index=False))
    print("\nPlacebo check:")
    print(pd.DataFrame(placebo).to_string(index=False))


if __name__ == "__main__":
    main()
