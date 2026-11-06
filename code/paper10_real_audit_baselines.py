"""Baseline comparisons and budgeted-audit curves on the CleanScore real-audit data.

Baselines (REAL_AUDIT_REGISTRATION.md section 7):
- raw public-form score, Clean-Eval-style fresh-form score, unadjusted gap;
- PaCoST-style paired confidence comparison: per parent, the model's mean
  per-token log probability on the original form versus the mean over its
  fresh forms (GSM8K: greedy continuation; ARC: the chosen option), tested
  with a paired t-test and a Wilcoxon signed-rank test. A model-benchmark pair
  is "flagged" by the baseline when the paired test rejects at 0.05 with
  higher confidence on the original form.

Budgeted audit (charter contribution 4): for audit sizes n in the grid, draw
repeated subsamples without replacement from the 200 audited parents and
record the Wald half-width, the coverage of the full-sample estimate, and the
stability of the cross-model ranking by fresh-form accuracy (the
audit-adjusted score).
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

Z = 1.959963984540054
FRAMES = {"gsm8k": 1319, "arc": 1165}
BUDGETS = (25, 50, 100, 150, 200)
REPS = 2000


def paired_conf(df: pd.DataFrame, conf_col: str):
    orig = df[df.form_type == "original_public"].set_index("parent_id")[conf_col]
    fresh = df[df.form_type.str.startswith("fresh")].groupby("parent_id")[conf_col].mean()
    joined = pd.concat([orig.rename("orig"), fresh.rename("fresh")], axis=1).dropna()
    return joined


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260821)

    baseline_rows, budget_rows = [], []
    gaps_by_model: dict[str, dict[str, pd.Series]] = {}
    fresh_by_model: dict[str, dict[str, pd.Series]] = {}
    for model_dir in sorted(args.results_root.iterdir()):
        if not model_dir.is_dir() or not (model_dir / "arc_control_results.csv").is_file():
            continue
        name = model_dir.name.replace("--", "/")
        for domain, conf_col in (("gsm8k", "mean_logprob"), ("arc", "chosen_mean_logprob")):
            df = pd.read_csv(model_dir / f"{domain}_results.csv")
            orig_acc = df[df.form_type == "original_public"]["correct"].mean()
            fresh_acc = df[df.form_type.str.startswith("fresh")]["correct"].mean()
            conf = paired_conf(df, conf_col)
            diff = conf["orig"] - conf["fresh"]
            t, p_t = stats.ttest_1samp(diff, 0.0)
            try:
                w, p_w = stats.wilcoxon(diff)
            except ValueError:
                w, p_w = float("nan"), float("nan")
            baseline_rows.append(
                {
                    "model": name, "domain": domain,
                    "raw_public_score": round(orig_acc, 4),
                    "cleaneval_fresh_score": round(fresh_acc, 4),
                    "unadjusted_gap": round(orig_acc - fresh_acc, 4),
                    "pacost_conf_orig": round(conf["orig"].mean(), 4),
                    "pacost_conf_fresh": round(conf["fresh"].mean(), 4),
                    "pacost_t": round(t, 3), "pacost_p_t": round(p_t, 4),
                    "pacost_p_wilcoxon": round(p_w, 4),
                    "pacost_flags_contamination": bool(p_t < 0.05 and diff.mean() > 0),
                }
            )
            # parent-level gaps for the budget curves
            orig = df[df.form_type == "original_public"].set_index("parent_id")["correct"].astype(float)
            fresh = df[df.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
            gaps = (orig - fresh).dropna()
            gaps_by_model.setdefault(domain, {})[name] = gaps
            fresh_by_model.setdefault(domain, {})[name] = fresh

    for domain, by_model in gaps_by_model.items():
        names = sorted(by_model)
        full = {m: by_model[m].mean() for m in names}
        fresh_full = {m: fresh_by_model[domain][m].mean() for m in names}
        full_rank = tuple(sorted(names, key=lambda m: fresh_full[m]))
        parents = by_model[names[0]].index.to_numpy()
        N = FRAMES[domain]
        for n in BUDGETS:
            covered = {m: 0 for m in names}
            widths = {m: [] for m in names}
            rank_same = 0
            pair_hits = 0
            pair_total = 0
            for _ in range(REPS):
                idx = rng.choice(len(parents), size=n, replace=False)
                sub_ids = parents[idx]
                est = {}
                for m in names:
                    g = by_model[m].loc[sub_ids]
                    mean = g.mean()
                    var = g.var(ddof=1) if n > 1 else 0.0
                    half = Z * math.sqrt(max(0.0, (1 - n / N) * var / n))
                    widths[m].append(half)
                    covered[m] += int(abs(mean - full[m]) <= half)
                    est[m] = fresh_by_model[domain][m].loc[sub_ids].mean()
                rank_same += int(tuple(sorted(names, key=lambda m: est[m])) == full_rank)
                for a_i in range(len(names)):
                    for b_i in range(a_i + 1, len(names)):
                        a, b = names[a_i], names[b_i]
                        if fresh_full[a] == fresh_full[b]:
                            continue
                        pair_total += 1
                        pair_hits += int((est[a] < est[b]) == (fresh_full[a] < fresh_full[b]))
            for m in names:
                budget_rows.append(
                    {"domain": domain, "model": m, "n_audited": n,
                     "mean_wald_half": round(float(np.mean(widths[m])), 4),
                     "coverage_of_full_estimate": round(covered[m] / REPS, 4),
                     "rank_order_stability": round(rank_same / REPS, 4),
                     "pairwise_concordance": round(pair_hits / max(1, pair_total), 4)}
                )

    pd.DataFrame(baseline_rows).to_csv(args.out_dir / "baselines.csv", index=False)
    pd.DataFrame(budget_rows).to_csv(args.out_dir / "budget_curves.csv", index=False)
    print(pd.DataFrame(baseline_rows).to_string(index=False))
    print()
    print(pd.DataFrame(budget_rows).pivot_table(index=["domain", "n_audited"], values=["mean_wald_half", "rank_order_stability"], aggfunc="mean").round(4).to_string())


if __name__ == "__main__":
    main()
