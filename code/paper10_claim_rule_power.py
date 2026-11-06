"""Detection rate of the full registered claim rule, not just the primary interval.

Section 7.9 reports how often the primary interval for the public-form advantage
excludes zero. The registered claim rule is stricter. A pair is reported as
showing an exposure-consistent advantage only if the primary interval excludes
zero AND the sensitivity interval at the headline radius excludes zero. The
sensitivity interval is the audit interval widened by the control-bank interval
and the radius, so it needs a larger advantage than the primary interval does.
This script measures how much larger, using the same resampling design as
paper10_power_analysis.py.

Design, stated plainly:
  * Audit gaps are resampled from the five models' observed parent gaps and an
    advantage delta is planted in a random share of the parents whose gap is
    zero (identical to paper10_power_analysis.py).
  * Control-bank gaps are resampled from the five models' observed control gaps.
    No exposure is planted in the control bank, so its mean stays at the pooled
    observed form gap.
  * The claim rule is evaluated exactly as paper10_analyze_real_audit.py does:
    Wald components at alpha = 0.025 each, radius 0.02, and the primary interval
    is Wald when n >= 200 with at least 30 nonzero gaps, Hoeffding otherwise.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
MODELS = ("allenai--OLMo-2-1124-7B-Instruct", "HuggingFaceTB--SmolLM2-1.7B-Instruct",
          "microsoft--Phi-3-mini-4k-instruct", "Qwen--Qwen2.5-1.5B-Instruct",
          "Qwen--Qwen2.5-7B-Instruct")
FRAMES = {"gsm8k": 1319, "arc": 1165}
REGISTERED_CONTROL = {"gsm8k": 60, "arc": 40}
ALPHA_TEST = 0.05  # per-test level; set by --alpha-family and --k-tests
Z = 1.959963984540054
Z25 = 2.2414027276049473
RHO_STAR = 0.02
ALPHA = 0.05
AUDIT_SIZES = (200, 400, 800)
DELTAS = (0.05, 0.10, 0.15, 0.20, 0.30)
REPS = 4000


def gaps_from(path: Path, original_label: str) -> np.ndarray:
    df = pd.read_csv(path)
    orig = df[df.form_type == original_label].set_index("parent_id")["correct"].astype(float)
    fresh = df[df.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
    return (orig - fresh).dropna().to_numpy()


def hoeffding(n: int) -> float:
    return math.sqrt(2.0 * math.log(2.0 / ALPHA_TEST) / n)


def hoeffding_at(n: int, alpha: float) -> float:
    return math.sqrt(2.0 * math.log(2.0 / alpha) / n)


def bernstein_at(var: float, n: int, alpha: float) -> float:
    lt = math.log(4.0 / alpha)
    return math.sqrt(2.0 * var * lt / n) + 14.0 * lt / (3.0 * (n - 1))


MODE = "union"            # "union": Proposition 3 as registered; "independent": one interval on Delta - b_C
CONTROL_GUARDRAIL = False  # apply the nonzero-gap guardrail to the control component as well
CONTROL_BRANCH = "hoeffding"  # control component when its guardrail binds: "hoeffding" (as first registered) or "bernstein" (Amendment 1)


def claim_fires(audit: np.ndarray, control: np.ndarray, population: int, ctrl_shift: float = 0.0) -> tuple[bool, bool]:
    """Return (primary interval excludes zero, full registered claim rule fires).

    Components of the sensitivity interval are Wald unless the guardrail applies to that
    component, in which case they are the distribution-free (Hoeffding) interval at alpha/2.
    """
    n, m = len(audit), len(control)
    delta_hat = float(audit.mean())
    var = float(audit.var(ddof=1))
    fpc = 1.0 - n / population
    wald = Z * math.sqrt(max(0.0, fpc * var / n))
    guard = (n < 200) or (int((audit != 0).sum()) < 30)
    primary_half = hoeffding(n) if guard else wald
    primary = abs(delta_hat) > primary_half
    # ctrl_shift moves the control mean (the transport scenario) without touching the count of nonzero
    # gaps or the variance, which are what the guardrail and the intervals actually use
    b_c = float(control.mean()) + ctrl_shift
    var_c = float(control.var(ddof=1))
    guard_c = CONTROL_GUARDRAIL and ((m < 200) or (int((control != 0).sum()) < 30))
    if MODE == "independent" and not guard and not guard_c:
        half = Z * math.sqrt(max(0.0, fpc * var / n + var_c / m))
        lo = (delta_hat - b_c) - half - RHO_STAR
        hi = (delta_hat - b_c) + half + RHO_STAR
    else:
        d_half = hoeffding_at(n, ALPHA_TEST / 2) if guard else Z25 * math.sqrt(max(0.0, fpc * var / n))
        if guard_c:
            c_half = bernstein_at(var_c, m, ALPHA_TEST / 2) if CONTROL_BRANCH == "bernstein" else hoeffding_at(m, ALPHA_TEST / 2)
        else:
            c_half = Z25 * math.sqrt(max(0.0, var_c / m))
        lo = (delta_hat - d_half) - (b_c + c_half) - RHO_STAR
        hi = (delta_hat + d_half) - (b_c - c_half) + RHO_STAR
    tau_excludes = (lo > 0) or (hi < 0)
    return primary, bool(primary and tau_excludes and delta_hat > 0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-root", type=Path, default=ROOT / "results" / "primary_5models_20260821")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results" / "power")
    parser.add_argument("--seed", type=int, default=20261023)
    parser.add_argument("--reps", type=int, default=REPS)
    parser.add_argument("--alpha-family", type=float, default=0.05)
    parser.add_argument("--k-tests", type=int, default=1, help="Bonferroni: per-test alpha = alpha-family / k-tests")
    parser.add_argument("--sizes", type=int, nargs="+", default=list(AUDIT_SIZES))
    parser.add_argument("--control-sizes", type=int, nargs="+", default=None)
    parser.add_argument("--tag", default="claim_rule_power")
    parser.add_argument("--mode", choices=["union", "independent"], default="union")
    parser.add_argument("--boundary-rho", type=float, default=None,
                        help="evaluate the null at the edge of the transport assumption: shift the control pool so that E[Delta-hat - b_C-hat] equals this value with nothing planted")
    parser.add_argument("--control-guardrail", action="store_true")
    parser.add_argument("--finite-frame", action="store_true",
                        help="draw the audited parents WITHOUT replacement from a fixed frame of the benchmark's size, as the real audit does, so the finite-population correction in the intervals is the right one")
    parser.add_argument("--qwen-768", action="store_true",
                        help="read the two Qwen models' gaps from the first audit's 768-token reruns (Amendment 1 of the first audit), the budget the extension uses")
    parser.add_argument("--control-branch", choices=["hoeffding", "bernstein"], default="hoeffding")
    parser.add_argument("--models", nargs="+", default=None, help="restrict both pools to models whose name contains one of these strings")
    parser.add_argument("--domains", nargs="+", default=["gsm8k", "arc"])
    args = parser.parse_args()
    global ALPHA_TEST, Z, Z25, MODE, CONTROL_GUARDRAIL, CONTROL_BRANCH
    MODE, CONTROL_GUARDRAIL, CONTROL_BRANCH = args.mode, args.control_guardrail, args.control_branch
    models = tuple(m for m in MODELS if args.models is None or any(t in m for t in args.models))
    ALPHA_TEST = args.alpha_family / args.k_tests
    Z, Z25 = float(norm.ppf(1 - ALPHA_TEST / 2)), float(norm.ppf(1 - ALPHA_TEST / 4))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    rows = []
    for domain in args.domains:
        def root_for(m):
            return ROOT / "results" / "amendment1_qwen_20260821" if (args.qwen_768 and m.startswith("Qwen")) else args.results_root
        audit_pool = np.concatenate([gaps_from(root_for(m) / m / f"{domain}_results.csv", "original_public")
                                     for m in models])
        control_pool = np.concatenate([gaps_from(root_for(m) / m / f"{domain}_control_results.csv", "public_like")
                                       for m in models])
        ctrl_add = 0.0 if args.boundary_rho is None else float(audit_pool.mean() - args.boundary_rho - control_pool.mean())
        control_sizes = tuple(args.control_sizes) if args.control_sizes else (REGISTERED_CONTROL[domain], 100, 200, 400)
        for n in args.sizes:
            for m in control_sizes:
                for delta in (0.0,) + DELTAS:
                    prim = full = 0
                    for _ in range(args.reps):
                        if args.finite_frame:
                            # a fresh frame of the benchmark's size each time; the control mean is placed relative to THIS frame's mean
                            frame = rng.choice(audit_pool, size=FRAMES[domain], replace=True)
                            sample = rng.choice(frame, size=n, replace=False)
                            ctrl_add = 0.0 if args.boundary_rho is None else float(frame.mean() - args.boundary_rho - control_pool.mean())
                        else:
                            sample = rng.choice(audit_pool, size=n, replace=True)
                        zeros = np.flatnonzero(sample == 0.0)
                        k = min(int(round(delta * n)), len(zeros))
                        if k:
                            sample = sample.copy()
                            sample[rng.choice(zeros, size=k, replace=False)] = 1.0
                        control = rng.choice(control_pool, size=m, replace=True)
                        p, f = claim_fires(sample, control, FRAMES[domain], ctrl_add)
                        prim += p
                        full += f
                    rows.append({"domain": domain, "n_audited": n, "n_control": m, "planted_delta": delta,
                                 "primary_rate": round(prim / args.reps, 4),
                                 "claim_rule_rate": round(full / args.reps, 4)})
                    print(f"{domain:5s} n={n:3d} m={m:3d} delta={delta:.2f} "
                          f"primary={prim / args.reps:.3f} claim_rule={full / args.reps:.3f}", flush=True)

    out = pd.DataFrame(rows)
    out.to_csv(args.out_dir / f"{args.tag}.csv", index=False)
    summary = {
        "reps": args.reps, "seed": args.seed, "rho_star": RHO_STAR, "alpha_test": ALPHA_TEST, "mode": MODE, "control_guardrail": CONTROL_GUARDRAIL, "finite_frame": args.finite_frame,
        "control_pool_mean": {d: float(np.concatenate([gaps_from(args.results_root / m / f"{d}_control_results.csv",
                                                                  "public_like") for m in MODELS]).mean())
                              for d in ("gsm8k", "arc")},
    }
    (args.out_dir / f"{args.tag}_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
