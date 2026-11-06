"""Pool Study 6 and the three Study 8 seeds, and apply the registered rules.

Study 8's registration fixed four commitments in place of the stopping rule it
overrides: every seed reported, no seed excluded for any reason, the headline
becoming the spread rather than a chosen run, and no further attempts. This
script is where the first three are enforced rather than remembered. It refuses
to run if a seed's results are missing, so a silently dropped seed is a crash.

Study 6's run is seed 20260824 and is included on equal terms. It keeps its
separate reporting elsewhere as the registered single-seed result; here it is
one of four.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260824
NEW_SEEDS = (20260828, 20260829, 20260830)
SPREAD_TOLERANCE = 0.10   # registration section 4, first bullet
FLOOR = 0.05              # manipulation check


def per_parent(df: pd.DataFrame) -> pd.DataFrame:
    p = df[df.form_type == "original_public"].set_index("parent_id")["correct"].astype(float)
    f = df[df.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
    g = df[df.form_type == "deep_paraphrase"].set_index("parent_id")["correct"].astype(float)
    return pd.DataFrame({"P": p, "F": f, "G": g})


def dids(base: pd.DataFrame, exposed: pd.DataFrame, assign: pd.Series,
         exempt: set[str]) -> dict[str, float]:
    change = exposed - base
    ex = [i for i in change.index if assign.get(i, 0) == 1]
    ct = [i for i in change.index if assign.get(i, 0) == 0]
    gex = [i for i in ex if i not in exempt and not np.isnan(change.loc[i, "G"])]
    gct = [i for i in ct if i not in exempt and not np.isnan(change.loc[i, "G"])]
    return {
        "did_P": float(change.loc[ex, "P"].mean() - change.loc[ct, "P"].mean()),
        "did_F": float(change.loc[ex, "F"].mean() - change.loc[ct, "F"].mean()),
        "did_G": float(change.loc[gex, "G"].mean() - change.loc[gct, "G"].mean()),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "study8_arc")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    base = per_parent(pd.read_csv(
        ROOT / "study6_out" / "results" / "base" / "arc_study6_results.csv"))
    assign = pd.read_csv(
        ROOT / "data" / f"positive_control_arc_exposure_seed{SEED}.csv"
    ).set_index("parent_id")["exposed"]
    exempt = {w.strip() for w in
              (ROOT / "data" / "arc_g_exempt.txt").read_text().split() if w.strip()}

    runs = {SEED: ROOT / "study6_out" / "results" / "exposed" / "arc_study6_results.csv"}
    for s in NEW_SEEDS:
        runs[s] = ROOT / "study8_out" / "results" / f"seed{s}" / "arc_study8_results.csv"

    rows = []
    for seed, path in sorted(runs.items()):
        if not path.is_file():
            raise SystemExit(
                f"seed {seed} has no results at {path}. Study 8's registration "
                f"commits to reporting every seed, so this script will not pool a "
                f"subset. Fetch the missing run or record why it does not exist.")
        d = dids(base, per_parent(pd.read_csv(path)), assign, exempt)
        d["seed"] = seed
        d["manipulation_passed"] = bool(d["did_P"] >= FLOOR)
        d["registered_run"] = seed == SEED
        rows.append(d)

    table = pd.DataFrame(rows)[
        ["seed", "registered_run", "did_P", "did_F", "did_G", "manipulation_passed"]]
    table.to_csv(args.out / "seed_replication.csv", index=False)

    summary = {"n_seeds": len(rows), "floor": FLOOR, "spread_tolerance": SPREAD_TOLERANCE}
    for key in ("did_P", "did_F", "did_G"):
        vals = table[key].values
        summary[key] = {"mean": round(float(vals.mean()), 4),
                        "min": round(float(vals.min()), 4),
                        "max": round(float(vals.max()), 4),
                        "spread": round(float(vals.max() - vals.min()), 4),
                        "sd": round(float(vals.std(ddof=1)), 4)}
    summary["all_manipulations_passed"] = bool(table.manipulation_passed.all())
    summary["deep_arm_positive_on_every_seed"] = bool((table.did_G > 0).all())

    # Registration section 4, evaluated rather than eyeballed.
    if not summary["all_manipulations_passed"]:
        verdict = ("at least one seed failed its manipulation check, so the effect is not "
                   "reliably implantable at this dose and every ARC conclusion in the "
                   "paper is qualified by it")
    elif not summary["deep_arm_positive_on_every_seed"]:
        verdict = ("the deep-paraphrase arm does not hold on every seed, so Section 7.14's "
                   "claim is reported as holding on some seeds and not others and the "
                   "abstract is narrowed accordingly")
    elif summary["did_P"]["spread"] <= SPREAD_TOLERANCE:
        verdict = ("optimisation variability is small relative to the planted effect: the "
                   "four public-form estimates span "
                   f"{summary['did_P']['spread']:.3f}, inside the registered "
                   f"{SPREAD_TOLERANCE}, so the parent bootstrap was not badly understating "
                   "uncertainty and Sections 7.13 and 7.14 stand with the spread reported")
    else:
        verdict = ("the across-seed spread is comparable to the effect, so the single-seed "
                   "intervals understate uncertainty and the across-seed range becomes the "
                   "honest interval")
    summary["registered_verdict"] = verdict
    (args.out / "seed_replication.json").write_text(json.dumps(summary, indent=2),
                                                    encoding="utf-8")

    print(table.to_string(index=False))
    print()
    for key in ("did_P", "did_F", "did_G"):
        s = summary[key]
        print(f"  {key}: mean {s['mean']:+.4f}  range [{s['min']:+.4f}, {s['max']:+.4f}]  "
              f"spread {s['spread']:.4f}  sd {s['sd']:.4f}")
    print(f"\nregistered verdict: {verdict}")


if __name__ == "__main__":
    main()
