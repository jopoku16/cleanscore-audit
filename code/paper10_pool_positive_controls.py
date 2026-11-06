"""Pool the positive-control studies into one transfer estimate.

Implements the analysis registered across POSITIVE_CONTROL_REGISTRATION.md and
its Study 2 and Study 3 companions. For each study, the effect of leaking an
item's public wording is a difference in differences against the unexposed
parents of the same model, which absorbs whatever the fine-tuning did to the
model in general. Studies whose manipulation check fails are reported and
excluded from the pool, as registered.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MANIPULATION_THRESHOLD = 0.05
DRAWS = 20000


def forms(path: Path) -> tuple[pd.Series, pd.Series]:
    df = pd.read_csv(path)
    public = df[df.form_type == "original_public"].set_index("parent_id")["correct"].astype(float)
    fresh = df[df.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
    return public, fresh


def study_arrays(exposed_dir: Path, base_dir: Path, assignment: pd.Series):
    pe, fe = forms(exposed_dir / "gsm8k_results.csv")
    pb, fb = forms(base_dir / "gsm8k_results.csv")
    shared = [i for i in assignment.index if i in pe.index and i in pb.index]
    exposed = [i for i in shared if assignment[i] == 1]
    control = [i for i in shared if assignment[i] == 0]
    return {
        "public_exposed": (pe.reindex(exposed) - pb.reindex(exposed)).to_numpy(),
        "fresh_exposed": (fe.reindex(exposed) - fb.reindex(exposed)).to_numpy(),
        "public_control": (pe.reindex(control) - pb.reindex(control)).to_numpy(),
        "fresh_control": (fe.reindex(control) - fb.reindex(control)).to_numpy(),
    }


def did(arrays: dict) -> tuple[float, float]:
    return (float(arrays["public_exposed"].mean() - arrays["public_control"].mean()),
            float(arrays["fresh_exposed"].mean() - arrays["fresh_control"].mean()))


def bootstrap_one(a: dict, rng: np.random.Generator):
    """Bootstrap a single study's two difference-in-differences."""
    dps, dfs = [], []
    for _ in range(DRAWS):
        ie = rng.integers(0, len(a["public_exposed"]), len(a["public_exposed"]))
        ic = rng.integers(0, len(a["public_control"]), len(a["public_control"]))
        dps.append(a["public_exposed"][ie].mean() - a["public_control"][ic].mean())
        dfs.append(a["fresh_exposed"][ie].mean() - a["fresh_control"][ic].mean())
    return np.array(dps), np.array(dfs)


def bootstrap(arrays_by_study: list[dict], rng: np.random.Generator):
    pub, fresh, ratio = [], [], []
    for _ in range(DRAWS):
        dps, dfs = [], []
        for a in arrays_by_study:
            ie = rng.integers(0, len(a["public_exposed"]), len(a["public_exposed"]))
            ic = rng.integers(0, len(a["public_control"]), len(a["public_control"]))
            dps.append(a["public_exposed"][ie].mean() - a["public_control"][ic].mean())
            dfs.append(a["fresh_exposed"][ie].mean() - a["fresh_control"][ic].mean())
        p, f = float(np.mean(dps)), float(np.mean(dfs))
        pub.append(p)
        fresh.append(f)
        if p > 0.05:
            ratio.append(f / p)
    return np.array(pub), np.array(fresh), np.array(ratio)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results" / "positive_control_pooled")
    parser.add_argument("--seed", type=int, default=20260823)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    assignment = pd.read_csv(ROOT / "data" / "positive_control_exposure_seed20260822.csv").set_index("parent_id")["exposed"]
    primary = ROOT / "results" / "primary_5models_20260821"

    registry = [
        ("Qwen2.5-1.5B", "Qwen",
         ROOT / "results/positive_control_registered_20260822/exposed_qwen15b",
         primary / "Qwen--Qwen2.5-1.5B-Instruct"),
        ("SmolLM2-1.7B", "SmolLM2",
         ROOT / "results/positive_control_study2_20260822/exposed_smollm2",
         primary / "HuggingFaceTB--SmolLM2-1.7B-Instruct"),
        ("OLMo-2-1B", "OLMo",
         ROOT / "results/positive_control_study3_olmo1b/exposed",
         ROOT / "results/positive_control_study3_olmo1b/base"),
        ("StableLM-2-1.6B", "StableLM",
         ROOT / "results/positive_control_study3_stablelm/exposed",
         ROOT / "results/positive_control_study3_stablelm/base"),
    ]

    rows, pooled_arrays, excluded, base_public = [], [], [], {}
    for name, family, exposed_dir, base_dir in registry:
        if not (exposed_dir / "gsm8k_results.csv").is_file() or not (base_dir / "gsm8k_results.csv").is_file():
            print(f"skipping {name}: results not present yet")
            continue
        a = study_arrays(exposed_dir, base_dir, assignment)
        pb, _ = forms(base_dir / "gsm8k_results.csv")
        base_public[name] = float(pb.reindex([i for i in assignment.index if i in pb.index]).mean())
        dp, df_ = did(a)
        passed = dp >= MANIPULATION_THRESHOLD
        rows.append({"study": name, "family": family, "n_exposed": len(a["public_exposed"]),
                     "did_public": round(dp, 4), "did_fresh": round(df_, 4),
                     "visible_gap": round(dp - df_, 4),
                     "transfer": round(df_ / dp, 4) if dp > 0.02 else None,
                     "manipulation_check_passed": bool(passed)})
        (pooled_arrays if passed else excluded).append((name, a))

    if not rows:
        raise SystemExit("no studies available")
    table = pd.DataFrame(rows)
    table.to_csv(args.out_dir / "per_study.csv", index=False)
    print(table.to_string(index=False))

    if excluded:
        print("\nexcluded from the pool for a failed manipulation check: "
              + ", ".join(n for n, _ in excluded))

    # Per-study intervals. These were originally produced by a separate script
    # that was never checked in, so the release shipped per_study_ci.json with
    # nothing that regenerated it. Folding it in here closes that gap: the
    # generator is seeded independently of the pooled one, exactly as the two
    # scripts were, and reproduces the archived file to the digit.
    per_study_rng = np.random.default_rng(args.seed)
    per_study_ci, per_study_draws = [], {}
    for name, a in [(n, x) for n, x in pooled_arrays] + excluded:
        dps, dfs = bootstrap_one(a, per_study_rng)
        dp, df_ = did(a)
        per_study_ci.append({
            "model": name,
            "base_acc": round(base_public[name], 4),
            "control_public_change": round(float(a["public_control"].mean()), 4),
            "did_public": round(dp, 4),
            "dp_ci": [round(float(x), 4) for x in np.percentile(dps, [2.5, 97.5])],
            "did_fresh": round(df_, 4),
            "df_ci": [round(float(x), 4) for x in np.percentile(dfs, [2.5, 97.5])],
            "df_p_gt_0": round(float((dfs > 0).mean()), 4),
            "visible_gap": round(dp - df_, 4),
        })
        per_study_draws[f"{name}_public"] = dps
        per_study_draws[f"{name}_fresh"] = dfs
    np.savez_compressed(args.out_dir / "per_study_draws.npz", **per_study_draws)
    (args.out_dir / "per_study_ci.json").write_text(
        json.dumps(per_study_ci, indent=2), encoding="utf-8")

    pub, fresh, ratio = bootstrap([a for _, a in pooled_arrays], rng)
    summary = {
        "studies_pooled": [n for n, _ in pooled_arrays],
        "studies_excluded": [n for n, _ in excluded],
        "pooled_did_public": round(float(pub.mean()), 4),
        "pooled_did_public_ci": [round(float(x), 4) for x in np.percentile(pub, [2.5, 97.5])],
        "pooled_did_fresh": round(float(fresh.mean()), 4),
        "pooled_did_fresh_ci": [round(float(x), 4) for x in np.percentile(fresh, [2.5, 97.5])],
        "pooled_did_fresh_p_gt_0": round(float((fresh > 0).mean()), 4),
        "pooled_visible_gap": round(float(pub.mean() - fresh.mean()), 4),
        "transfer_ci": [round(float(x), 4) for x in np.percentile(ratio, [2.5, 97.5])] if len(ratio) else None,
        "share_transfer_above_25pct": round(float((ratio > 0.25).mean()), 4) if len(ratio) else None,
        "models_with_positive_did_fresh": int(sum(r["did_fresh"] > 0 for r in rows)),
        "models_total": len(rows),
    }
    (args.out_dir / "pooled_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    # Archive the draws themselves. The intervals above are percentiles of these
    # arrays, so a figure that plots the densities is showing the published
    # inference rather than a redraw of it.
    np.savez_compressed(args.out_dir / "bootstrap_draws.npz",
                        pooled_public=pub, pooled_fresh=fresh, transfer_ratio=ratio)
    print()
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
