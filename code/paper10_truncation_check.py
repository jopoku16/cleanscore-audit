"""Post hoc truncation check for the registered 320-token GSM8K audit (written 2026-11-06).

Not registered. Run after the results were known, in response to a referee-style comment that
truncation may differ between the public and the fresh forms. It reads only the saved primary
outputs and reports, per model:

  1. the truncation rate on the public form and on the fresh forms (a form is truncated when it
     generated the full 320 tokens);
  2. the audit estimate Delta-hat on all 200 parents (it reproduces the registered point estimate);
  3. the same estimate on the parents in which none of the three forms was truncated;
  4. worst-case (Manski-type) bounds on Delta-hat when every truncated outcome may be right or
     wrong, public and fresh outcomes chosen against each other.

Usage: python paper10_truncation_check.py [--results-dir results/primary_5models_20260821]
                                          [--out-dir results/truncation_check] [--cap 320]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def one_model(path: Path, cap: int) -> dict:
    df = pd.read_csv(path, usecols=["parent_id", "form_type", "correct", "n_generated_tokens"])
    df["trunc"] = (df["n_generated_tokens"] >= cap).astype(int)
    pub_mask = df["form_type"] == "original_public"
    pub = df[pub_mask].set_index("parent_id")
    fresh = df[~pub_mask]
    fg = fresh.groupby("parent_id")

    c_pub = pub["correct"]
    c_fresh = fg["correct"].mean().reindex(c_pub.index)
    delta_all = float((c_pub - c_fresh).mean())

    any_trunc = df.groupby("parent_id")["trunc"].max().reindex(c_pub.index)
    complete = any_trunc[any_trunc == 0].index
    delta_cc = float((c_pub.loc[complete] - c_fresh.loc[complete]).mean())

    lo = np.where(df["trunc"] == 1, 0, df["correct"])
    hi = np.where(df["trunc"] == 1, 1, df["correct"])
    d = df.assign(lo=lo, hi=hi)
    pub_d = d[pub_mask].set_index("parent_id")
    fr_d = d[~pub_mask].groupby("parent_id")
    gap_lo = float((pub_d["lo"] - fr_d["hi"].mean().reindex(pub_d.index)).mean())
    gap_hi = float((pub_d["hi"] - fr_d["lo"].mean().reindex(pub_d.index)).mean())

    return {
        "n_parents": int(len(c_pub)),
        "trunc_rate_all_forms": round(float(df["trunc"].mean()), 4),
        "trunc_rate_public_form": round(float(pub["trunc"].mean()), 4),
        "trunc_rate_fresh_forms": round(float(fresh["trunc"].mean()), 4),
        "n_parents_no_truncated_form": int(len(complete)),
        "delta_hat_all_parents": round(delta_all, 4),
        "delta_hat_complete_parents": round(delta_cc, 4),
        "worst_case_lower": round(gap_lo, 4),
        "worst_case_upper": round(gap_hi, 4),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=Path, default=Path("results/primary_5models_20260821"))
    ap.add_argument("--out-dir", type=Path, default=Path("results/truncation_check"))
    ap.add_argument("--cap", type=int, default=320)
    args = ap.parse_args()

    rows = {}
    for d in sorted(p for p in args.results_dir.iterdir() if p.is_dir()):
        f = d / "gsm8k_results.csv"
        if f.exists():
            rows[d.name.split("--")[-1]] = one_model(f, args.cap)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "truncation_check.json").write_text(
        json.dumps({"status": "post hoc, run 2026-11-06, not registered", "cap_tokens": args.cap,
                    "models": rows}, indent=2), encoding="utf-8")
    pd.DataFrame(rows).T.to_csv(args.out_dir / "truncation_check.csv")
    print(pd.DataFrame(rows).T.to_string())


if __name__ == "__main__":
    main()
