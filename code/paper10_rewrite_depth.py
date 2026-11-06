"""Does the audit's answer depend on how deeply the fresh forms were rewritten?

The registered item verifier holds ARC fresh stems to a token-dissimilarity
threshold against their original: a Jaccard overlap of 0.80 or more is a
failure. GSM8K fresh forms were checked for exact identity to the original but
never for near-identity, so the same threshold was never applied to them. This
script measures the consequence.

The worry is specific and directional. A fresh form that is nearly a copy of the
public form should be answered nearly like the public form, whether or not the
model has seen either. The parent's gap would then be pulled toward zero, and
enough such parents would manufacture a null. Two tests:

1. Recompute Delta-hat with every parent whose closest fresh form exceeds the
   ARC threshold removed. If the nulls are an artefact of shallow rewrites, the
   estimate should move once they are gone.
2. Correlate the parent-level gap with the parent's rewrite similarity across
   all parents, which uses the whole range rather than a cut.

The bank was frozen before any model was queried and is not modified here. This
is a diagnostic of the frozen bank, reported as one.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ARC_THRESHOLD = 0.80  # the registered verifier's ARC rule
FRESH = ("fresh_variant_1", "fresh_variant_2")


def tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9']+", str(text).lower()))


def jaccard(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    return len(ta & tb) / max(1, len(ta | tb))


def parent_similarity(items_csv: Path) -> pd.Series:
    """Per parent, the Jaccard overlap of its *closest* fresh form to the original.

    The maximum rather than the mean: one near-copy is enough to make a parent's
    gap uninformative, and averaging it against a deeper rewrite hides that.
    """
    d = pd.read_csv(items_csv)
    out = {}
    for pid, grp in d.groupby("parent_id"):
        original = grp[grp.form_type == "original_public"]["prompt"].iloc[0]
        sims = [jaccard(grp[grp.form_type == k]["prompt"].iloc[0], original)
                for k in FRESH if len(grp[grp.form_type == k])]
        if sims:
            out[pid] = float(max(sims))
    return pd.Series(out, name="similarity")


def parent_gaps(results_csv: Path) -> pd.Series:
    d = pd.read_csv(results_csv)
    public = d[d.form_type == "original_public"].set_index("parent_id")["correct"].astype(float)
    fresh = d[d.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
    return (public - fresh).dropna()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--items-dir", type=Path, required=True)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    similarity = {b: parent_similarity(args.items_dir / f"{b}_matched_forms.csv")
                  for b in ("gsm8k", "arc")}

    rows, pooled = [], {b: {"sim": [], "gap": []} for b in similarity}
    for model_dir in sorted(p for p in args.results_root.iterdir() if p.is_dir()):
        for bench in ("gsm8k", "arc"):
            path = model_dir / f"{bench}_results.csv"
            if not path.is_file():
                continue
            gaps = parent_gaps(path)
            sims = similarity[bench].reindex(gaps.index)
            keep = sims < ARC_THRESHOLD
            r, p = stats.pearsonr(sims.to_numpy(), gaps.to_numpy())
            pooled[bench]["sim"].append(sims.to_numpy())
            pooled[bench]["gap"].append(gaps.to_numpy())
            rows.append({
                "model": model_dir.name.replace("--", "/"),
                "domain": bench,
                "n_parents": int(len(gaps)),
                "n_above_threshold": int((~keep).sum()),
                "delta_hat_all": round(float(gaps.mean()), 4),
                "delta_hat_deep_rewrites_only": round(float(gaps[keep].mean()), 4),
                "shift": round(float(gaps[keep].mean() - gaps.mean()), 4),
                "pearson_r_similarity_gap": round(float(r), 4),
                "p_value": round(float(p), 4),
            })

    table = pd.DataFrame(rows)
    table.to_csv(args.out_dir / "rewrite_depth_sensitivity.csv", index=False)
    print(table.to_string(index=False))

    summary = {"arc_threshold": ARC_THRESHOLD}
    for bench, acc in pooled.items():
        s = similarity[bench]
        S, G = np.concatenate(acc["sim"]), np.concatenate(acc["gap"])
        r, p = stats.pearsonr(S, G)
        summary[bench] = {
            "parents": int(len(s)),
            "parents_at_or_above_threshold": int((s >= ARC_THRESHOLD).sum()),
            "similarity_median": round(float(s.median()), 4),
            "similarity_max": round(float(s.max()), 4),
            "pooled_pearson_r": round(float(r), 4),
            "pooled_p_value": round(float(p), 4),
            # bracket access: "shift" is also a DataFrame method
            "max_abs_shift": round(float(table[table.domain == bench]["shift"].abs().max()), 4),
        }
        if (S >= ARC_THRESHOLD).any():
            hi, lo = G[S >= ARC_THRESHOLD], G[S < ARC_THRESHOLD]
            t, tp = stats.ttest_ind(hi, lo, equal_var=False)
            summary[bench].update({
                "mean_gap_near_copy_parents": round(float(hi.mean()), 4),
                "mean_gap_other_parents": round(float(lo.mean()), 4),
                "welch_p": round(float(tp), 4),
            })
    (args.out_dir / "rewrite_depth_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    print()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
