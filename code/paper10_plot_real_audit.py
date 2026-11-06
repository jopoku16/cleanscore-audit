"""Figures for the CleanScore empirical sections.

Every figure is drawn at the manuscript's text width through paper10_figstyle,
so type is the same physical size in all of them and nothing is rescaled on the
way into the document.

  validation_forest    the two registered contrasts in both model families
  audit_forest         Delta-hat with its primary interval, all ten pairs
  budget_curves        precision and ranking recovery against audit size
  power_curves         minimum detectable effect and detection rate
  randomization_test   the exact test against the interval, and its level
  positive_control     where the planted contamination effect went
  four_model_transfer  the same decomposition across four model families
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper10_figstyle as fs
import matplotlib.pyplot as plt

fs.use()

SHORT = {
    "allenai/OLMo-2-1124-7B-Instruct": "OLMo-2-7B",
    "HuggingFaceTB/SmolLM2-1.7B-Instruct": "SmolLM2-1.7B",
    "microsoft/Phi-3-mini-4k-instruct": "Phi-3-mini",
    "Qwen/Qwen2.5-1.5B-Instruct": "Qwen2.5-1.5B",
    "Qwen/Qwen2.5-7B-Instruct": "Qwen2.5-7B",
}

# Registered validation contrasts (results/*/analysis/registered_condition_contrasts.csv).
VALIDATION = [
    ("SmolLM2-360M", "Exact exposure", 0.0200, 0.0062, 0.0338),
    ("SmolLM2-360M", "Paraphrase exposure", -0.0017, -0.0087, 0.0054),
    ("Qwen2.5-0.5B", "Exact exposure", 0.0429, -0.0178, 0.1037),
    ("Qwen2.5-0.5B", "Paraphrase exposure", -0.0146, -0.0451, 0.0159),
]


def interval(ax, y, lo, hi, mid, color, marker="o", dashed=False, ms=5.0):
    """One estimate with its interval: a rule, end caps, and a point."""
    ax.plot([lo, hi], [y, y], color=color, linewidth=1.8, solid_capstyle="butt",
            linestyle=(0, (2.2, 1.8)) if dashed else "-", zorder=2)
    for end in (lo, hi):
        ax.plot([end, end], [y - 0.10, y + 0.10], color=color, linewidth=1.3, zorder=2)
    ax.plot([mid], [y], marker, color=color, markersize=ms, zorder=3,
            markeredgecolor="white", markeredgewidth=0.6)


def fig_validation(out: Path) -> None:
    """One panel per model family, so the family name is a title and not a floating label."""
    families = ["SmolLM2-360M", "Qwen2.5-0.5B"]
    fig, axes = plt.subplots(2, 1, figsize=(fs.FULL, 2.6), sharex=True, constrained_layout=True)
    for ax, family in zip(axes, families):
        rows = [r for r in VALIDATION if r[0] == family]
        for i, (_, contrast, mean, lo, hi) in enumerate(rows):
            exact = contrast.startswith("Exact")
            interval(ax, 1 - i, lo, hi, mean, fs.PUBLIC if exact else fs.MUTED,
                     marker="o" if exact else "s", dashed=not exact)
        fs.zero_line(ax)
        ax.set_yticks([1, 0])
        ax.set_yticklabels(["exact\nexposure", "paraphrase\nexposure"], fontsize=7.5)
        ax.set_ylim(-0.55, 1.55)
        ax.set_title(family)
        fs.axis(ax, grid="x")
    axes[1].set_xlabel("Seed-paired difference in public-form advantage vs related-task control")
    fig.suptitle("Exposure to the exact public form shifts the advantage; a paraphrase does not",
                 fontsize=9.0, fontweight="semibold", x=0.0, ha="left")
    fs.letter_panels(axes)
    fs.save(fig, out, "validation_forest")


def fig_audit(summary: pd.DataFrame, out: Path) -> None:
    df = summary.copy()
    df["short"] = df.model.map(SHORT)
    df["half"] = df.apply(
        lambda r: r.hoeffding_half if r.primary_interval == "hoeffding" else r.wald_half, axis=1)
    order = df.sort_values(["domain", "short"], ascending=[True, False])

    fig, axes = plt.subplots(1, 2, figsize=(fs.FULL, 2.7), sharex=True, sharey=True,
                             constrained_layout=True)
    for ax, domain in zip(axes, ("gsm8k", "arc")):
        sub = order[order.domain == domain].reset_index(drop=True)
        for y, r in enumerate(sub.itertuples()):
            guard = r.primary_interval == "hoeffding"
            interval(ax, y, r.delta_hat - r.half, r.delta_hat + r.half, r.delta_hat,
                     fs.MUTED if guard else fs.PUBLIC, dashed=guard)
            ax.plot([r.b_c_hat], [y], "x", color=fs.CRIMSON, markersize=5,
                    markeredgewidth=1.4, zorder=4)
        ax.set_yticks(range(len(sub)))
        ax.set_yticklabels(sub.short)
        ax.set_ylim(-0.6, len(sub) - 0.4)
        ax.set_title(fs.DOMAIN_NAME[domain])
        ax.set_xlabel(r"Public-form advantage $\hat{\Delta}$")
        fs.zero_line(ax)
        fs.axis(ax, grid="x")
    axes[0].set_xlim(-0.22, 0.22)

    # Annotate the three marks where they actually occur, once each, instead of
    # asking the reader to carry a key across from a legend box.
    guard_row = order[(order.domain == "arc")].reset_index(drop=True)
    guard_y = int(guard_row.index[guard_row.primary_interval == "hoeffding"][0])
    axes[1].annotate("guardrail: the conservative\nbound is primary here",
                     xy=(0.16, guard_y), xytext=(0.055, guard_y + 0.62), fontsize=6.8,
                     color=fs.MUTED, linespacing=1.4, ha="left", va="center",
                     arrowprops=dict(arrowstyle="-", color=fs.MUTED, lw=0.7,
                                     shrinkA=3, shrinkB=3))
    wald_row = order[order.domain == "gsm8k"].reset_index(drop=True)
    wy = int(wald_row.index[wald_row.primary_interval != "hoeffding"][0])
    axes[0].annotate(r"$\hat{\Delta}$ with its primary interval",
                     xy=(float(wald_row.delta_hat[wy]) + 0.055, wy),
                     xytext=(0.085, wy + 0.70), fontsize=6.8, color=fs.PUBLIC,
                     ha="left", va="center",
                     arrowprops=dict(arrowstyle="-", color=fs.PUBLIC, lw=0.7,
                                     shrinkA=3, shrinkB=3))
    axes[0].annotate(r"control-bank gap $\hat{b}_C$",
                     xy=(float(wald_row.b_c_hat[3]), 3), xytext=(-0.215, 3.58),
                     fontsize=6.8, color=fs.CRIMSON, ha="left", va="center",
                     arrowprops=dict(arrowstyle="-", color=fs.CRIMSON, lw=0.7,
                                     shrinkA=3, shrinkB=3))
    fs.letter_panels(axes)
    fs.save(fig, out, "audit_forest")


def fig_budget(budget: pd.DataFrame, out: Path) -> None:
    agg = budget.groupby(["domain", "n_audited"]).agg(
        half=("mean_wald_half", "mean"),
        exact=("rank_order_stability", "mean"),
        pair=("pairwise_concordance", "mean")).reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(fs.FULL, 2.6), constrained_layout=True)
    for domain, sub in agg.groupby("domain"):
        c, m, name = fs.DOMAIN_COLOR[domain], fs.DOMAIN_MARKER[domain], fs.DOMAIN_NAME[domain]
        axes[0].plot(sub.n_audited, sub.half, marker=m, color=c, label=name)
        axes[1].plot(sub.n_audited, sub.pair, marker=m, color=c, label=f"{name}, pairwise")
        axes[1].plot(sub.n_audited, sub.exact, marker=m, color=c, linestyle=(0, (2.2, 1.8)),
                     alpha=0.6, label=f"{name}, exact order")
    axes[0].set_ylabel("Mean Wald half-width")
    axes[0].set_title("Precision improves smoothly")
    axes[1].set_ylabel("Share of orderings reproduced")
    axes[1].set_ylim(0, 1.08)
    axes[1].set_title("Pairwise order is cheap, exact order is not")
    for ax in axes:
        ax.set_xlabel("Audited parent items")
        fs.axis(ax)
    axes[0].set_xlim(0, 272)
    axes[1].set_xlim(0, 215)
    # Panel (a) names the two benchmarks on their own curves, so panel (b) can
    # reuse that colour association and spend its labels on what is new there:
    # solid against dashed. The four curves converge at the right, so panel (b)
    # labels at the left, where they are furthest apart.
    for domain in ("gsm8k", "arc"):
        sub = agg[agg.domain == domain].sort_values("n_audited")
        fs.label_end(axes[0], 200, sub.half.iloc[-1], fs.DOMAIN_NAME[domain],
                     fs.DOMAIN_COLOR[domain])
    gsm = agg[agg.domain == "gsm8k"].sort_values("n_audited")
    fs.label_end(axes[1], 25, gsm.pair.iloc[0] + 0.055, "pairwise", fs.PUBLIC, dx=8, size=7.4)
    fs.label_end(axes[1], 25, gsm.exact.iloc[0] + 0.055, "exact order", fs.PUBLIC, dx=8, size=7.4)
    fs.letter_panels(axes)
    fs.save(fig, out, "budget_curves")


def fig_power(mde: pd.DataFrame, power: pd.DataFrame, out: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(fs.FULL, 2.9), constrained_layout=True,
                             gridspec_kw={"width_ratios": [1.15, 1.0]})
    rows = list(mde.sort_values(["domain", "model"]).itertuples())
    ys, labels = [], []
    for i, r in enumerate(rows):
        y = len(rows) - 1 - i
        c = fs.DOMAIN_COLOR[r.domain]
        axes[0].plot([0, r.minimum_detectable_effect], [y, y], color=c, alpha=0.45, lw=1.2, zorder=2)
        axes[0].plot([r.minimum_detectable_effect], [y], fs.DOMAIN_MARKER[r.domain],
                     mfc="white" if r.guardrail_applied else c, mec=c, mew=1.4, ms=6, zorder=3)
        ys.append(y)
        labels.append(SHORT.get(r.model, r.model))
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels(labels)
    axes[0].set_xlabel("Minimum detectable advantage at n = 200")
    axes[0].set_title("Smallest effect the audit would declare")
    axes[0].set_xlim(0, 0.215)
    axes[0].axhline(4.5, color=fs.GRID, lw=0.8, zorder=0)
    for y, key in ((8.4, "arc"), (3.4, "gsm8k")):
        axes[0].text(0.212, y, fs.DOMAIN_NAME[key], fontsize=8, fontweight="semibold",
                     ha="right", va="center", color=fs.DOMAIN_COLOR[key])
    axes[0].plot([], [], "o", mfc="white", mec=fs.INK, mew=1.4, ms=6, linestyle="none",
                 label="guardrail applies: no finite MDE")
    axes[0].legend(loc="lower right")
    fs.axis(axes[0], grid="x")

    markers = {0.02: "o", 0.05: "s", 0.10: "^", 0.20: "D"}
    for domain, sub in power.groupby("domain"):
        for delta, g in sub.groupby("planted_delta"):
            g = g.sort_values("n_audited")
            axes[1].plot(g.n_audited, g.detection_rate, marker=markers[delta], ms=3.6,
                         color=fs.DOMAIN_COLOR[domain], alpha=0.4 + 2.8 * delta, lw=1.3)
    axes[1].axvspan(40, 200, color=fs.CRIMSON, alpha=0.055, zorder=0)
    axes[1].text(103, 0.80, "guardrail:\nzero power", ha="center", va="center",
                 fontsize=7.5, color=fs.CRIMSON, linespacing=1.3)
    axes[1].set_xlabel("Audited parent items")
    axes[1].set_ylabel("Detection rate")
    axes[1].set_ylim(-0.04, 1.06)
    axes[1].set_title("Power against a planted advantage")
    # Panel (a) already names the two benchmarks by colour, so the key here
    # carries only the planted effect sizes.
    handles = [plt.Line2D([], [], color=fs.INK, marker=markers[d], ms=3.6, lw=1.3,
                          label=f"{int(d * 100)} pts") for d in (0.02, 0.05, 0.10, 0.20)]
    axes[1].legend(handles=handles, loc="lower right", ncol=2, fontsize=7,
                   title="planted advantage", title_fontsize=7)
    fs.axis(axes[1])
    fs.letter_panels(axes)
    fs.save(fig, out, "power_curves")


def fig_randomization(interval_df: pd.DataFrame, exact: pd.DataFrame,
                      type1: pd.DataFrame, out: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(fs.FULL, 2.4), constrained_layout=True)
    for ax, delta in zip(axes[:2], (0.05, 0.10)):
        for domain in ("gsm8k", "arc"):
            c, m = fs.DOMAIN_COLOR[domain], fs.DOMAIN_MARKER[domain]
            iv = interval_df[(interval_df.domain == domain)
                             & (interval_df.planted_delta == delta)].sort_values("n_audited")
            ex = exact[(exact.domain == domain)
                       & (exact.planted_delta == delta)].sort_values("n_audited")
            ax.plot(iv.n_audited, iv.detection_rate, marker=m, ms=3.6, color=c,
                    linestyle=(0, (2.2, 1.8)), alpha=0.6, lw=1.3)
            ax.plot(ex.n_audited, ex.detection_rate, marker=m, ms=3.6, color=c, lw=1.6)
        ax.set_xlabel("Audited parent items")
        ax.set_ylim(-0.04, 1.06)
        ax.set_title(f"Planted advantage {int(delta * 100)} points")
        fs.axis(ax)
    axes[0].set_ylabel("Detection rate")

    for domain in ("gsm8k", "arc"):
        sub = type1[type1.domain == domain].sort_values("n_audited")
        axes[2].plot(sub.n_audited, sub.type_I_error, marker=fs.DOMAIN_MARKER[domain], ms=3.6,
                     color=fs.DOMAIN_COLOR[domain], lw=1.6)
    axes[2].axhline(0.05, color=fs.CRIMSON, lw=0.9, ls=(0, (4, 3)))
    axes[2].set_xlabel("Audited parent items")
    axes[2].set_ylabel("Type-I error")
    axes[2].set_ylim(0, 0.105)
    axes[2].set_title("The exact test holds its level")
    axes[2].annotate("nominal 0.05", xy=(0.97, 0.054), xycoords=("axes fraction", "data"),
                     fontsize=7, color=fs.CRIMSON, ha="right", va="bottom")
    fs.axis(axes[2])

    handles = [plt.Line2D([], [], color=fs.DOMAIN_COLOR[d], marker=fs.DOMAIN_MARKER[d], ms=3.6,
                          label=fs.DOMAIN_NAME[d]) for d in ("gsm8k", "arc")]
    handles += [plt.Line2D([], [], color=fs.INK, lw=1.6, label="exact test"),
                plt.Line2D([], [], color=fs.INK, lw=1.3, linestyle=(0, (2.2, 1.8)), alpha=0.6,
                           label="interval")]
    fig.legend(handles=handles, loc="outside lower center", ncol=4)
    fs.letter_panels(axes)
    fs.save(fig, out, "randomization_test")


def fig_positive_control(out: Path, exposed_csv: Path, base_csv: Path, assignment_csv: Path) -> None:
    e = pd.read_csv(exposed_csv)
    b = pd.read_csv(base_csv)
    a = pd.read_csv(assignment_csv).set_index("parent_id")["exposed"]

    def acc(df, form, ids):
        if form == "public":
            s = df[df.form_type == "original_public"].set_index("parent_id")["correct"]
        else:
            s = df[df.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
        return float(s.reindex(ids).mean())

    fig, axes = plt.subplots(1, 2, figsize=(fs.FULL, 3.0), sharey=True, constrained_layout=True)
    panels = [("Exposed parents: the 100 leaked items", a[a == 1].index, axes[0]),
              ("Untouched parents: the 100 controls", a[a == 0].index, axes[1])]
    for title, ids, ax in panels:
        before = [acc(b, "public", ids), acc(b, "fresh", ids)]
        after = [acc(e, "public", ids), acc(e, "fresh", ids)]
        x = [0, 1]
        ax.fill_between(x, before, after, color=fs.PUBLIC, alpha=0.09, zorder=1)
        ax.plot(x, before, marker="s", color=fs.MUTED, ms=6, linestyle=(0, (2.2, 1.8)), zorder=3)
        ax.plot(x, after, marker="o", color=fs.PUBLIC, ms=6, zorder=3)
        for xi, (b0, a0) in enumerate(zip(before, after)):
            ax.annotate(f"{a0 - b0:+.3f}", (xi, max(a0, b0) + 0.012),
                        ha="center", va="bottom", fontsize=7.5, fontweight="semibold",
                        color=fs.PUBLIC if a0 > b0 else fs.CRIMSON)
        ax.set_xticks(x)
        ax.set_xticklabels(["public form\n(trained on)", "fresh forms\n(never seen)"])
        ax.set_xlim(-0.28, 1.28)
        ax.set_title(f"{title}\nvisible gap {before[0] - before[1]:+.3f} "
                     f"$\\rightarrow$ {after[0] - after[1]:+.3f}", fontsize=8.5)
        fs.axis(ax, grid="y")
    axes[0].set_ylabel("Accuracy")
    axes[0].set_ylim(0.36, 0.715)
    handles = [plt.Line2D([], [], color=fs.MUTED, marker="s", ms=6, linestyle=(0, (2.2, 1.8)),
                          label="before exposure"),
               plt.Line2D([], [], color=fs.PUBLIC, marker="o", ms=6, label="after exposure")]
    axes[0].legend(handles=handles, loc="lower left")
    fs.letter_panels(axes, dy=1.04)
    fs.save(fig, out, "positive_control")


def fig_four_models(out: Path, per_study_json: Path, pooled_json: Path,
                    per_draws: Path, pooled_draws: Path) -> None:
    """The headline result, drawn from the archived bootstrap draws themselves.

    The intervals in the paper are percentiles of these arrays, so showing the
    distributions is showing the published inference rather than a summary of
    it; the reader can see that the pooled fresh-form effect has no mass at or
    below zero, which is a stronger statement than an interval that misses it.
    """
    per = json.loads(Path(per_study_json).read_text())
    pooled = json.loads(Path(pooled_json).read_text())
    pd_draws = np.load(per_draws)
    pool_draws = np.load(pooled_draws)

    rows = [dict(r, key=r["model"]) for r in per]
    rows.append({"model": "Pooled, four models", "key": "pooled",
                 "did_public": pooled["pooled_did_public"],
                 "dp_ci": pooled["pooled_did_public_ci"],
                 "did_fresh": pooled["pooled_did_fresh"],
                 "df_ci": pooled["pooled_did_fresh_ci"],
                 "visible_gap": pooled["pooled_visible_gap"]})

    def draws(row, kind):
        if row["key"] == "pooled":
            return pool_draws["pooled_public" if kind == "public" else "pooled_fresh"]
        return pd_draws[f"{row['key']}_{kind}"]

    y = np.arange(len(rows))[::-1].astype(float)
    fig, axes = plt.subplots(1, 2, figsize=(fs.FULL, 3.5), constrained_layout=True,
                             gridspec_kw={"width_ratios": [1.45, 1.0]})

    for i, r in zip(y, rows):
        fs.density(axes[0], draws(r, "public"), i + 0.04, fs.PUBLIC,
                   height=0.40, interval=r["dp_ci"], point=r["did_public"])
        fs.density(axes[0], draws(r, "fresh"), i - 0.40, fs.FRESH,
                   height=0.32, interval=r["df_ci"], point=r["did_fresh"])
    fs.zero_line(axes[0])
    axes[0].axhline(0.62, color=fs.GRID, lw=0.8, zorder=0)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels([r["model"] for r in rows])
    axes[0].set_ylim(-0.75, len(rows) - 0.15)
    axes[0].set_xlim(-0.16, 0.92)
    axes[0].set_xlabel("Difference-in-differences vs uncontaminated control items")
    axes[0].set_title("Effect of leaking an item's wording")
    # Named on the data, once, on the row with the clearest separation.
    fs.label_end(axes[0], 0.70, y[2] + 0.20, "on the leaked wording", fs.PUBLIC, dx=8)
    fs.label_end(axes[0], 0.52, y[2] - 0.24, "on unseen paraphrases", fs.FRESH, dx=8)
    fs.axis(axes[0], grid="x")

    gaps = [r["visible_gap"] for r in rows]
    for i, g in zip(y, gaps):
        colour = fs.PUBLIC if g > 0 else fs.CRIMSON
        axes[1].barh(i - 0.18, g, color=colour, height=0.46, zorder=2,
                     alpha=1.0 if g < 0 else 0.9)
        axes[1].annotate(f"{g:+.3f}", (g, i - 0.18), xytext=(5 if g > 0 else -5, 0),
                         textcoords="offset points", va="center", fontsize=7.6,
                         fontweight="semibold" if g < 0 else "normal",
                         ha="left" if g > 0 else "right", color=colour)
    axes[1].axhline(0.62, color=fs.GRID, lw=0.8, zorder=0)
    axes[1].axvline(0, color=fs.INK, lw=0.9, zorder=3)
    axes[1].set_yticks([])
    axes[1].set_ylim(-0.75, len(rows) - 0.15)
    axes[1].set_xlim(-0.135, 0.225)
    axes[1].set_xlabel("Visible gap")
    axes[1].set_title("All a paraphrase audit can see")
    axes[1].annotate("negative: the audit\npoints the wrong way",
                     xy=(-0.032, 0.82), xytext=(-0.130, 2.45), fontsize=7.0,
                     color=fs.CRIMSON, linespacing=1.45, ha="left", va="center",
                     arrowprops=dict(arrowstyle="-", color=fs.CRIMSON, lw=0.7,
                                     shrinkA=4, shrinkB=3))
    fs.axis(axes[1], grid="x", spines="bottom")
    fs.letter_panels(axes)
    fs.save(fig, out, "four_model_transfer")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--power-dir", type=Path, default=None)
    parser.add_argument("--randomization-dir", type=Path, default=None)
    parser.add_argument("--positive-control-dir", type=Path, default=None)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary = pd.read_csv(args.analysis_dir / "audit_summary.csv")
    budget = pd.read_csv(args.analysis_dir / "budget_curves.csv")
    fig_validation(args.out_dir)
    fig_audit(summary, args.out_dir)
    fig_budget(budget, args.out_dir)
    if args.power_dir and (args.power_dir / "power_curves.csv").is_file():
        fig_power(pd.read_csv(args.power_dir / "minimum_detectable_effect.csv"),
                  pd.read_csv(args.power_dir / "power_curves.csv"), args.out_dir)
    if (args.randomization_dir and args.power_dir
            and (args.randomization_dir / "randomization_power.csv").is_file()):
        fig_randomization(pd.read_csv(args.power_dir / "power_curves.csv"),
                          pd.read_csv(args.randomization_dir / "randomization_power.csv"),
                          pd.read_csv(args.randomization_dir / "randomization_type1.csv"),
                          args.out_dir)
    pooled_dir = args.analysis_dir.parent / "positive_control_pooled"
    if (pooled_dir / "per_study_ci.json").is_file():
        fig_four_models(args.out_dir, pooled_dir / "per_study_ci.json",
                        pooled_dir / "pooled_summary.json",
                        pooled_dir / "per_study_draws.npz",
                        pooled_dir / "bootstrap_draws.npz")
    if args.positive_control_dir:
        fig_positive_control(
            args.out_dir,
            args.positive_control_dir / "exposed_qwen15b" / "gsm8k_results.csv",
            args.analysis_dir.parent / "primary_5models_20260821"
            / "Qwen--Qwen2.5-1.5B-Instruct" / "gsm8k_results.csv",
            args.positive_control_dir.parent.parent / "data"
            / "positive_control_exposure_seed20260822.csv")
    print("wrote:", sorted(p.name for p in args.out_dir.iterdir()))


if __name__ == "__main__":
    main()
