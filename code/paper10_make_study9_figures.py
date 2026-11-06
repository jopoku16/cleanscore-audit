"""Redraw the decomposition and four-model transfer figures from the Study 9 pooled analysis.

Reads results/study9_gsm8k/analysis_draws/{pooled.json, per_model.csv, draws.npz}, which come from
`paper10_pool_study9.py --save-draws` and reproduce the registered pooled.json exactly. Writes the inputs the two
existing figure functions expect to results/positive_control_pooled_study9/ and the figures to --out-dir.

Per-model points are the means over the model's four runs; per-model intervals are the 2.5th and 97.5th
percentiles of the same two-level draws that give the pooled interval (parents shared across models and seeds,
plus the t-based seed component). The pooled share interval is the registered one.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper10_plot_real_audit as pra  # noqa: E402
import paper10_plot_schematics as pls  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "results" / "study9_gsm8k" / "analysis_draws"
OUT_IN = ROOT / "results" / "positive_control_pooled_study9"
ORDER = ["Qwen2.5-1.5B", "SmolLM2-1.7B", "OLMo-2-1B", "StableLM-2-1.6B"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=ROOT / "results" / "figures_study9")
    args = p.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    OUT_IN.mkdir(parents=True, exist_ok=True)

    pooled = json.loads((ANALYSIS / "pooled.json").read_text())
    per_model = pd.read_csv(ANALYSIS / "per_model.csv").set_index("model")
    z = np.load(ANALYSIS / "draws.npz")
    prim = pooled["two_level_primary"]

    rows = []
    for m in ORDER:
        dp_ci = [round(float(np.percentile(z[f"{m}_public"], q)), 4) for q in (2.5, 97.5)]
        df_ci = [round(float(np.percentile(z[f"{m}_fresh"], q)), 4) for q in (2.5, 97.5)]
        rows.append({"model": m, "did_public": float(per_model.loc[m, "did_public"]), "dp_ci": dp_ci,
                     "did_fresh": float(per_model.loc[m, "did_fresh"]), "df_ci": df_ci,
                     "visible_gap": round(float(per_model.loc[m, "did_public"] - per_model.loc[m, "did_fresh"]), 4),
                     "df_p_gt_0": round(float(np.mean(z[f"{m}_fresh"] > 0)), 4)})
    (OUT_IN / "per_study_ci.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    np.savez(OUT_IN / "per_study_draws.npz", **{f"{m}_{k}": z[f"{m}_{k}"] for m in ORDER for k in ("public", "fresh")})
    np.savez(OUT_IN / "bootstrap_draws.npz", pooled_public=z["pooled_public"], pooled_fresh=z["pooled_fresh"],
             transfer_ratio=z["transfer_ratio"])
    worst = min(rows, key=lambda r: r["visible_gap"])
    summary = {
        "studies_pooled": ORDER, "pooled_did_public": pooled["pooled_did_public"],
        "pooled_did_public_ci": [prim["did_public_95"][0], prim["did_public_95"][2]],
        "pooled_did_fresh": pooled["pooled_did_fresh"],
        "pooled_did_fresh_ci": [prim["did_fresh_95"][0], prim["did_fresh_95"][2]],
        "pooled_visible_gap": round(pooled["pooled_did_public"] - pooled["pooled_did_fresh"], 4),
        "transfer_ci": [prim["share_95"][0], prim["share_95"][2]],
        "share_transfer_above_half": prim["share_above_half"], "share_transfer_above_25pct": prim["share_above_quarter"],
        "fresh_effect_positive_share": prim["fresh_effect_positive_share"], "n_runs": pooled["n_runs"],
        "models_with_positive_did_fresh": int(sum(r["did_fresh"] > 0 for r in rows)), "models_total": len(rows),
        "wrong_way_case": {"model": worst["model"], "did_public": worst["did_public"], "visible_gap": worst["visible_gap"]},
    }
    (OUT_IN / "pooled_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")

    pra.fig_four_models(args.out_dir, OUT_IN / "per_study_ci.json", OUT_IN / "pooled_summary.json",
                        OUT_IN / "per_study_draws.npz", OUT_IN / "bootstrap_draws.npz")
    pls.fig_decomposition(args.out_dir, OUT_IN / "pooled_summary.json")
    print(json.dumps({k: summary[k] for k in ("pooled_did_public", "pooled_did_public_ci", "pooled_did_fresh",
                                              "pooled_did_fresh_ci", "pooled_visible_gap", "transfer_ci",
                                              "share_transfer_above_half", "wrong_way_case")}, indent=1))
    for r in rows:
        print(r["model"], r["did_public"], r["dp_ci"], r["did_fresh"], r["df_ci"], r["visible_gap"], r["df_p_gt_0"])


if __name__ == "__main__":
    main()
