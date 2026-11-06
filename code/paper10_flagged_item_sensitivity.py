"""Does the deep-paraphrase result depend on the items the screening flagged?

A second screening pass over all 200 deep-paraphrase items flagged three from the
original 125 as needing a human decision. The bank was not edited: it had already
been used for Studies 6 and 8, and removing items after seeing results is the
move that makes a bank untrustworthy. The same choice was made for the 21
near-copy GSM8K forms in Section 7.7.

What can be done instead is to measure what those items are worth. This drops all
three from the deep-paraphrase arm and recomputes the estimate on every seed. If
the answer barely moves, the flagged items are not carrying the result, and a
reader who disagrees with our judgement on any of them can see that it does not
matter. If it moves a lot, that is the more important finding and it is reported
as such.

Nothing here changes a published number. It adds a sensitivity beside them.
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
# Flagged by the screening in STUDY4_READING_FINDINGS.md.
FLAGGED = {
    "arcc_test_0407": "key and a distractor both read as a conclusion",
    "arcc_test_0699": "the key restates the stem",
    "arcc_test_0677": "a distractor may have widened into a second correct answer",
}


def per_parent(df: pd.DataFrame) -> pd.DataFrame:
    p = df[df.form_type == "original_public"].set_index("parent_id")["correct"].astype(float)
    f = df[df.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
    g = df[df.form_type == "deep_paraphrase"].set_index("parent_id")["correct"].astype(float)
    return pd.DataFrame({"P": p, "F": f, "G": g})


def did_g(change: pd.DataFrame, assign: pd.Series, excluded: set[str]) -> tuple[float, int, int]:
    ex = [i for i in change.index if assign.get(i, 0) == 1
          and i not in excluded and not np.isnan(change.loc[i, "G"])]
    ct = [i for i in change.index if assign.get(i, 0) == 0
          and i not in excluded and not np.isnan(change.loc[i, "G"])]
    return float(change.loc[ex, "G"].mean() - change.loc[ct, "G"].mean()), len(ex), len(ct)


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
        change = per_parent(pd.read_csv(path)) - base
        kept, ne, nc = did_g(change, assign, exempt)
        dropped, ne2, nc2 = did_g(change, assign, exempt | set(FLAGGED))
        rows.append({"seed": seed, "as_published": round(kept, 4),
                     "flagged_removed": round(dropped, 4),
                     "shift": round(dropped - kept, 4),
                     "n_exposed": ne, "n_exposed_after": ne2,
                     "n_control": nc, "n_control_after": nc2})

    table = pd.DataFrame(rows)
    table.to_csv(args.out / "flagged_item_sensitivity.csv", index=False)
    worst = float(table["shift"].abs().max())
    summary = {"flagged": FLAGGED, "n_flagged": len(FLAGGED),
               "largest_absolute_shift": round(worst, 4),
               "all_shifts_positive": bool((table["shift"] > 0).all()),
               "still_positive_on_every_seed": bool((table["flagged_removed"] > 0).all()),
               "bank_edited": False,
               "note": "the bank was not modified; the three items remain in it and the "
                       "published estimates are unchanged"}
    (args.out / "flagged_item_sensitivity.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")

    print(table.to_string(index=False))
    print(f"\nlargest absolute shift across seeds: {worst:.4f}")
    print(f"deep-paraphrase effect still positive on every seed without them: "
          f"{summary['still_positive_on_every_seed']}")


if __name__ == "__main__":
    main()
