"""Registered sampling for the CleanScore real-benchmark audit.

Run once on 2026-08-21. Seed and draw order are locked by
REAL_AUDIT_REGISTRATION.md: GSM8K first, then ARC-Challenge, from one
default_rng(20260821) stream.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260821


def gold(answer: str) -> str:
    match = re.search(r"####\s*([\-0-9,\.]+)", answer)
    return match.group(1).replace(",", "").rstrip(".")


def normalize_arc(row: pd.Series):
    mapping = {"1": "A", "2": "B", "3": "C", "4": "D"}
    labels = [mapping.get(l, l) for l in row["choices"]["label"]]
    key = mapping.get(row["answerKey"], row["answerKey"])
    if sorted(labels) != ["A", "B", "C", "D"]:
        return None
    options = dict(zip(labels, row["choices"]["text"]))
    return options["A"], options["B"], options["C"], options["D"], key


def main() -> None:
    rng = np.random.default_rng(SEED)

    gdf = pd.read_parquet(ROOT / "data" / "gsm8k_test_full.parquet").reset_index(drop=True)
    gdf["gold"] = gdf["answer"].map(gold)
    g_idx = np.sort(rng.choice(len(gdf), size=200, replace=False))
    gs = gdf.iloc[g_idx].copy()
    gs["parent_id"] = [f"gsm8k_test_{i:04d}" for i in g_idx]
    gs[["parent_id", "question", "gold"]].to_csv(ROOT / "data" / "gsm8k_parents_200.csv", index=False)

    adf = pd.read_parquet(ROOT / "data" / "arc_challenge_test_full.parquet").reset_index(drop=True)
    norm = adf.apply(normalize_arc, axis=1)
    eligible = adf[norm.notna()].index.to_numpy()
    a_idx = np.sort(rng.choice(len(eligible), size=200, replace=False))
    rows = []
    for i in eligible[a_idx]:
        a, b, c, d, key = norm[i]
        rows.append(
            {
                "parent_id": f"arcc_test_{i:04d}",
                "arc_id": adf.iloc[i]["id"],
                "question": adf.iloc[i]["question"],
                "optA": a,
                "optB": b,
                "optC": c,
                "optD": d,
                "answerKey": key,
            }
        )
    pd.DataFrame(rows).to_csv(ROOT / "data" / "arc_parents_200.csv", index=False)


if __name__ == "__main__":
    main()
