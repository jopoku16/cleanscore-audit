"""How the sensitivity interval moves under three readings of the control bank.

A reviewer pointed out an inconsistency the paper had not confronted. The audit
switches to a distribution-free interval whenever fewer than 200 parents are
audited, on the ground that Wald under-covers there. The control banks hold 40
and 60 parents and are summarised with a Wald interval anyway. They are also
composed rather than sampled, so it is not obvious what population a sampling
interval on them is meant to describe.

There are three defensible readings and the paper should not pick one silently:

  wald       the registered construction, a sampling interval on b_C
  hoeffding  the paper's own guardrail applied to the control bank as well
  fixed      the bank as a fully measured finite object, so b_C is a constant
             and the transport radius carries all the uncertainty about
             generalising it

The first is what was registered. The second is the most conservative and the
most internally consistent. The third is the narrowest and asks the most of the
radius. This reports all three for every pair, and answers the only question
that matters for the paper's claims: does any conclusion change?
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "results" / "analysis_primary_5models_20260821"
RAW = ROOT / "results" / "primary_5models_20260821"
FRAMES = {"gsm8k": 1319, "arc": 1165}
RHO_STAR = 0.02
Z25 = 2.2414027276049473    # z at 1 - 0.0125, the registered alpha split
ALPHA_C = 0.025


def parent_gaps(df: pd.DataFrame, original: str) -> pd.Series:
    orig = df[df.form_type == original].set_index("parent_id")["correct"].astype(float)
    fresh = df[df.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
    return (orig - fresh).dropna()


def control_halfwidths(cgaps: pd.Series) -> dict[str, float]:
    n = len(cgaps)
    wald = Z25 * math.sqrt(max(0.0, cgaps.var(ddof=1) / n))
    # Hoeffding on a range-two variable at the control bank's own alpha.
    hoeffding = math.sqrt(2.0 * math.log(2.0 / ALPHA_C) / n)
    return {"wald": wald, "hoeffding": hoeffding, "fixed": 0.0}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=PRIMARY)
    args = ap.parse_args()

    summary = pd.read_csv(PRIMARY / "audit_summary.csv")
    rows, flips = [], []
    for _, rec in summary.iterrows():
        model_dir = rec.model.replace("/", "--")
        domain = rec.domain
        audit = pd.read_csv(RAW / model_dir / f"{domain}_results.csv")
        control = pd.read_csv(RAW / model_dir / f"{domain}_control_results.csv")
        gaps = parent_gaps(audit, "original_public")
        cgaps = parent_gaps(control, "public_like")
        n = len(gaps)
        d_half = Z25 * math.sqrt(max(0.0, (1 - n / FRAMES[domain]) * gaps.var(ddof=1) / n))
        halves = control_halfwidths(cgaps)

        entry = {"model": rec.model, "domain": domain, "n_control": len(cgaps),
                 "b_c": round(float(cgaps.mean()), 4)}
        for name, c_half in halves.items():
            lo = (rec.delta_hat - d_half) - (cgaps.mean() + c_half) - RHO_STAR
            hi = (rec.delta_hat + d_half) - (cgaps.mean() - c_half) + RHO_STAR
            entry[f"{name}_half"] = round(c_half, 4)
            entry[f"{name}_lo"] = round(lo, 4)
            entry[f"{name}_hi"] = round(hi, 4)
            entry[f"{name}_excludes_zero"] = bool(lo > 0 or hi < 0)
        rows.append(entry)
        verdicts = {k: entry[f"{k}_excludes_zero"] for k in halves}
        if len(set(verdicts.values())) > 1:
            flips.append({"model": rec.model, "domain": domain, **verdicts})

    table = pd.DataFrame(rows)
    table.to_csv(args.out / "control_interval_sensitivity.csv", index=False)

    widths = {k: round(float((table[f"{k}_hi"] - table[f"{k}_lo"]).mean()), 4)
              for k in ("wald", "hoeffding", "fixed")}
    verdict = {
        "mean_tau_width": widths,
        "control_half_range": {k: [round(float(table[f"{k}_half"].min()), 4),
                                   round(float(table[f"{k}_half"].max()), 4)]
                               for k in ("wald", "hoeffding", "fixed")},
        "pairs_excluding_zero": {k: int(table[f"{k}_excludes_zero"].sum())
                                 for k in ("wald", "hoeffding", "fixed")},
        "conclusion_flips": flips,
        "any_conclusion_changes": bool(flips),
    }
    (args.out / "control_interval_sensitivity.json").write_text(
        json.dumps(verdict, indent=2), encoding="utf-8")

    print(f"{'model':38s} {'dom':5s} {'wald':>16s} {'hoeffding':>16s} {'fixed':>16s}")
    for r in rows:
        short = r["model"].split("/")[-1][:36]
        cells = [f"[{r[f'{k}_lo']:+.2f},{r[f'{k}_hi']:+.2f}]"
                 for k in ("wald", "hoeffding", "fixed")]
        print(f"{short:38s} {r['domain']:5s} {cells[0]:>16s} {cells[1]:>16s} {cells[2]:>16s}")
    print()
    print("mean interval width:", widths)
    print("control half-widths:", verdict["control_half_range"])
    print("pairs excluding zero:", verdict["pairs_excluding_zero"])
    print("conclusion flips:", flips or "none: every pair keeps the same verdict")


if __name__ == "__main__":
    main()
