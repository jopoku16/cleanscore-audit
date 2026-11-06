"""Study 9 analysis: the four GSM8K positive controls under four training seeds each.

Implements POSITIVE_CONTROL_STUDY9_REGISTRATION.md. Reads, for each of the four models,
the registered run (seed 20260822, Studies 1 to 3), the clean audit, and the three Study 9
runs, and reports:

  1. a table of every run: DiD public, DiD fresh, visible gap;
  2. per-model means over the four runs, and the spread;
  3. pooled DiD public and fresh (mean over models of per-model means) and the invisible share
     (pooled DiD fresh over pooled DiD public);
  4. the registered two-level interval: parents are resampled once per draw and applied to every
     model and seed (they are shared across all runs), plus a t-based seed component built from
     each model's four runs (sampling error of the mean of four runs is t(3) * s / 2);
  5. two comparison intervals so the contribution of each source can be seen: the Study 3
     estimator (independent parent resampling per model, registered runs only) and shared-parent
     resampling on the registered runs only.

Usage: python paper10_pool_study9.py [--study9-dir results/study9_gsm8k] [--selftest]
--selftest builds three synthetic extra runs per model by adding noise to the registered run, to
check the code on shapes it will meet. Its output is never a result.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DRAWS = 20000
SEEDS = (20261024, 20261025, 20261026)
PRIMARY = ROOT / "results" / "primary_5models_20260821"
MODELS = {
    "Qwen2.5-1.5B": (ROOT / "results/positive_control_registered_20260822/exposed_qwen15b",
                     PRIMARY / "Qwen--Qwen2.5-1.5B-Instruct", "qwen"),
    "SmolLM2-1.7B": (ROOT / "results/positive_control_study2_20260822/exposed_smollm2",
                     PRIMARY / "HuggingFaceTB--SmolLM2-1.7B-Instruct", "smollm2"),
    "OLMo-2-1B": (ROOT / "results/positive_control_study3_olmo1b/exposed",
                  ROOT / "results/positive_control_study3_olmo1b/base", "olmo1b"),
    "StableLM-2-1.6B": (ROOT / "results/positive_control_study3_stablelm/exposed",
                        ROOT / "results/positive_control_study3_stablelm/base", "stablelm"),
}


def forms(path: Path) -> tuple[pd.Series, pd.Series]:
    df = pd.read_csv(path)
    public = df[df.form_type == "original_public"].set_index("parent_id")["correct"].astype(float)
    fresh = df[df.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
    return public, fresh


def run_changes(exposed_csv: Path, base_csv: Path, parents: list[str]) -> tuple[np.ndarray, np.ndarray]:
    pe, fe = forms(exposed_csv)
    pb, fb = forms(base_csv)
    return (pe.reindex(parents) - pb.reindex(parents)).to_numpy(), (fe.reindex(parents) - fb.reindex(parents)).to_numpy()


def did(change: np.ndarray, e_idx: np.ndarray, c_idx: np.ndarray) -> float:
    return float(change[e_idx].mean() - change[c_idx].mean())


def summarize(draws: np.ndarray) -> list[float]:
    return [round(float(np.percentile(draws, q)), 4) for q in (2.5, 50, 97.5)]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--study9-dir", type=Path, default=ROOT / "results" / "study9_gsm8k")
    p.add_argument("--out-dir", type=Path, default=ROOT / "results" / "study9_gsm8k" / "analysis")
    p.add_argument("--seed", type=int, default=20261030)
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--save-draws", action="store_true",
                   help="also save the primary two-level draws (pooled and per model) to draws.npz in --out-dir; "
                        "consumes no extra random numbers, so every reported number is unchanged")
    args = p.parse_args()
    rng = np.random.default_rng(args.seed)

    assignment = pd.read_csv(ROOT / "data" / "positive_control_exposure_seed20260822.csv").set_index("parent_id")["exposed"]
    parents = list(assignment.index)
    e_pos = np.flatnonzero(assignment.to_numpy() == 1)
    c_pos = np.flatnonzero(assignment.to_numpy() == 0)

    runs: dict[str, list[tuple[str, np.ndarray, np.ndarray]]] = {}
    for name, (reg_dir, base_dir, slug) in MODELS.items():
        base_csv = base_dir / "gsm8k_results.csv"
        runs[name] = []
        pub, fre = run_changes(reg_dir / "gsm8k_results.csv", base_csv, parents)
        runs[name].append(("20260822", pub, fre))
        for seed in SEEDS:
            f = args.study9_dir / f"{slug}_{seed}" / "gsm8k_results.csv"
            if args.selftest:
                noise = np.random.default_rng(seed + len(slug))
                runs[name].append((str(seed), pub + noise.normal(0, 0.15, len(pub)), fre + noise.normal(0, 0.15, len(fre))))
            elif f.is_file():
                a, b = run_changes(f, base_csv, parents)
                runs[name].append((str(seed), a, b))
            else:
                raise SystemExit(f"missing Study 9 result: {f}")

    rows = []
    for name, rs in runs.items():
        for seed, pub, fre in rs:
            dp, df_ = did(pub, e_pos, c_pos), did(fre, e_pos, c_pos)
            rows.append({"model": name, "seed": seed, "did_public": round(dp, 4), "did_fresh": round(df_, 4),
                         "visible_gap": round(dp - df_, 4)})
    table = pd.DataFrame(rows)
    per_model = table.groupby("model").agg(did_public=("did_public", "mean"), did_fresh=("did_fresh", "mean"),
                                           spread_public=("did_public", lambda x: x.max() - x.min()),
                                           spread_fresh=("did_fresh", lambda x: x.max() - x.min())).round(4)
    pooled_p = float(per_model.did_public.mean())
    pooled_f = float(per_model.did_fresh.mean())

    seed_sd = {name: (np.std([did(r[1], e_pos, c_pos) for r in rs], ddof=1),
                      np.std([did(r[2], e_pos, c_pos) for r in rs], ddof=1)) for name, rs in runs.items()}

    captured: dict = {}

    def draw_two_level(correlated: bool = False) -> tuple[np.ndarray, np.ndarray]:
        """Parents resampled once per draw and shared by every run; plus a t-based seed component.

        With only four runs per model, resampling the runs would be crude. The between-run standard
        deviation s of a model's DiD is estimated from its four runs, and the sampling error of the
        mean of four runs is t(3) * s / 2, the usual t interval. Public and fresh draw independent t
        variables by default, which is the conservative choice for the ratio.
        """
        P, F = np.empty(DRAWS), np.empty(DRAWS)
        per = {name: (np.empty(DRAWS), np.empty(DRAWS)) for name in runs}
        for b in range(DRAWS):
            e = e_pos[rng.integers(0, len(e_pos), len(e_pos))]
            c = c_pos[rng.integers(0, len(c_pos), len(c_pos))]
            mp, mf = [], []
            for name, rs in runs.items():
                t1 = rng.standard_t(3)
                t2 = t1 if correlated else rng.standard_t(3)
                k = len(rs)
                mp.append(np.mean([did(r[1], e, c) for r in rs]) + t1 * seed_sd[name][0] / np.sqrt(k))
                mf.append(np.mean([did(r[2], e, c) for r in rs]) + t2 * seed_sd[name][1] / np.sqrt(k))
                per[name][0][b], per[name][1][b] = mp[-1], mf[-1]
            P[b], F[b] = np.mean(mp), np.mean(mf)
        if not correlated:
            captured.update(per)
        return P, F

    def draw_shared_parents_registered_only() -> tuple[np.ndarray, np.ndarray]:
        P, F = np.empty(DRAWS), np.empty(DRAWS)
        for b in range(DRAWS):
            e = e_pos[rng.integers(0, len(e_pos), len(e_pos))]
            c = c_pos[rng.integers(0, len(c_pos), len(c_pos))]
            P[b] = np.mean([did(rs[0][1], e, c) for rs in runs.values()])
            F[b] = np.mean([did(rs[0][2], e, c) for rs in runs.values()])
        return P, F

    def draw_study3_estimator() -> tuple[np.ndarray, np.ndarray]:
        P, F = np.empty(DRAWS), np.empty(DRAWS)
        for b in range(DRAWS):
            mp, mf = [], []
            for rs in runs.values():
                e = e_pos[rng.integers(0, len(e_pos), len(e_pos))]
                c = c_pos[rng.integers(0, len(c_pos), len(c_pos))]
                mp.append(did(rs[0][1], e, c))
                mf.append(did(rs[0][2], e, c))
            P[b], F[b] = np.mean(mp), np.mean(mf)
        return P, F

    out = {"pooled_did_public": round(pooled_p, 4), "pooled_did_fresh": round(pooled_f, 4),
           "invisible_share_point": round(pooled_f / pooled_p, 4), "n_runs": int(len(table)),
           "selftest": bool(args.selftest)}
    for label, fn in (("two_level_primary", draw_two_level),
                      ("two_level_seed_noise_correlated", lambda: draw_two_level(True)),
                      ("shared_parents_registered_runs_only", draw_shared_parents_registered_only),
                      ("study3_estimator_registered_runs_only", draw_study3_estimator)):
        P, F = fn()
        if label == "two_level_primary":
            primary_draws = (P.copy(), F.copy())
        ok = P > 0.05
        out[label] = {"did_public_95": summarize(P), "did_fresh_95": summarize(F),
                      "share_95": summarize(F[ok] / P[ok]) if ok.any() else None,
                      "share_above_half": round(float(np.mean(F[ok] / P[ok] > 0.5)), 4) if ok.any() else None,
                      "share_above_quarter": round(float(np.mean(F[ok] / P[ok] > 0.25)), 4) if ok.any() else None,
                      "fresh_effect_positive_share": round(float(np.mean(F > 0)), 4),
                      "draws_with_public_effect_at_most_0.05": int((~ok).sum())}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    tag = "SELFTEST_" if args.selftest else ""
    table.to_csv(args.out_dir / f"{tag}per_run.csv", index=False)
    per_model.to_csv(args.out_dir / f"{tag}per_model.csv")
    (args.out_dir / f"{tag}pooled.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    if args.save_draws:
        arrays = {"pooled_public": primary_draws[0], "pooled_fresh": primary_draws[1]}
        ok = primary_draws[0] > 0.05
        arrays["transfer_ratio"] = primary_draws[1][ok] / primary_draws[0][ok]
        for name, (dp_, df_) in captured.items():
            arrays[f"{name}_public"], arrays[f"{name}_fresh"] = dp_, df_
        np.savez(args.out_dir / f"{tag}draws.npz", **arrays)
    print(table.to_string(index=False))
    print(per_model.to_string())
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
