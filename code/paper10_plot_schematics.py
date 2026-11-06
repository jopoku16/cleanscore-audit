"""The paper's two explanatory figures.

design_schematic       what a matched-form audit does, and what each estimand
                       in Sections 3 and 4 refers to. No data; this is the
                       protocol drawn out.
effect_decomposition   the central empirical finding, drawn from the pooled
                       positive-control numbers: how much of a contamination
                       effect a paraphrase audit can see.

The decomposition figure reads its numbers from the archived pooled summary
rather than carrying its own copies, so it cannot drift away from Table 12.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper10_figstyle as fs
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

fs.use()


def box(ax, x, y, w, h, text, face="white", edge=None, bold=False, size=7.4, pad=0.012):
    edge = edge or fs.INK
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad={pad},rounding_size=0.02",
                                linewidth=0.9, edgecolor=edge, facecolor=face, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size,
            color=fs.INK, zorder=3, linespacing=1.35,
            fontweight="semibold" if bold else "normal")


def arrow(ax, xy_from, xy_to, label=None, color=None, size=6.8, dy=0.022):
    color = color or fs.MUTED
    ax.add_patch(FancyArrowPatch(xy_from, xy_to, arrowstyle="-|>", mutation_scale=8,
                                 linewidth=0.9, color=color, zorder=1,
                                 shrinkA=1.5, shrinkB=1.5))
    if label:
        ax.text((xy_from[0] + xy_to[0]) / 2, (xy_from[1] + xy_to[1]) / 2 + dy, label,
                ha="center", va="bottom", fontsize=size, color=fs.INK, zorder=3)


def fig_design(out: Path) -> None:
    """Figure: the matched-form audit, from benchmark to claim rule."""
    fig, ax = plt.subplots(figsize=(fs.FULL, 2.95), constrained_layout=True)
    ax.set_xlim(-0.02, 1.05)
    ax.set_ylim(0.15, 1.0)
    ax.axis("off")

    # Five columns, laid out once so nothing has to be nudged by hand. The gaps
    # are wide enough that the connecting arrows read as arrows and not as nubs.
    c1, w1 = 0.000, 0.138
    c2, w2 = 0.213, 0.198
    c3, w3 = 0.486, 0.100
    c4, w4 = 0.640, 0.186
    c5, w5 = 0.881, 0.149

    # Column 1: the two banks the forms are drawn from.
    box(ax, c1, 0.605, w1, 0.150, "Public benchmark\n$\\mathcal{B}$, $N$ items",
        face=fs.FILL, bold=True)
    ax.text(c1 + w1 / 2, 0.582, "seeded sample\nof $n$ parents", ha="center", va="top",
            fontsize=6.9, color=fs.INK, linespacing=1.4)
    box(ax, c1, 0.285, w1, 0.135, "Control bank\n$\\mathcal{C}$, never public",
        face="white", edge=fs.MUTED, bold=True)

    # Column 2: one parent's three matched forms, and the control forms below.
    ax.text(c2 + w2 / 2, 0.945, "one parent item, three matched forms", ha="center", va="bottom",
            fontsize=7.0, fontweight="semibold", color=fs.INK)
    box(ax, c2, 0.800, w2, 0.125, "public form  $x_i^{\\mathrm{pub}}$\nthe wording on the web",
        face="#E4EDF2", edge=fs.PUBLIC)
    box(ax, c2, 0.650, w2, 0.125, "fresh form  $x_i^{(1)}$\nwritten for this audit",
        face="#FBEBE4", edge=fs.FRESH)
    box(ax, c2, 0.500, w2, 0.125, "fresh form  $x_i^{(2)}$\nnever published",
        face="#FBEBE4", edge=fs.FRESH)
    box(ax, c2, 0.285, w2, 0.135, "control forms\nsame rewrite rules",
        face="white", edge=fs.MUTED)
    for y in (0.862, 0.712, 0.562):
        arrow(ax, (c1 + w1 + 0.014, 0.680), (c2 - 0.014, y))
    arrow(ax, (c1 + w1 + 0.014, 0.352), (c2 - 0.014, 0.352))

    # Column 3: one model, queried once per form, everything else held fixed.
    box(ax, c3, 0.330, w3, 0.520,
        "model under\naudit  $f$\n\none query\nper form\n\nsame decoding\nthroughout",
        face=fs.FILL, bold=True)
    for y in (0.862, 0.712, 0.562, 0.352):
        arrow(ax, (c2 + w2 + 0.014, y), (c3 - 0.014, 0.590 if y > 0.5 else 0.400))

    # Column 4: the two estimands the audit produces.
    box(ax, c4, 0.620, w4, 0.190,
        "public-form advantage $\\hat{\\Delta}$\n\nmean correct on the\npublic form, minus\n"
        "mean on the fresh forms", face="#E4EDF2", edge=fs.PUBLIC, size=7.0)
    box(ax, c4, 0.290, w4, 0.165,
        "control-bank gap $\\hat{b}_C$\n\nthe same contrast on\nitems no model\n"
        "can have memorised", face="white", edge=fs.MUTED, size=7.0)
    arrow(ax, (c3 + w3 + 0.014, 0.660), (c4 - 0.014, 0.715))
    arrow(ax, (c3 + w3 + 0.014, 0.450), (c4 - 0.014, 0.372))

    # Column 5: the rule that turns the two estimands into a claim.
    box(ax, c5, 0.400, w5, 0.290,
        "registered claim rule\n\nclaim contamination\nonly if the primary\ninterval and the\n"
        "sensitivity interval\nat $\\rho^*$ both\nexclude zero",
        face="#F7E9EC", edge=fs.CRIMSON, bold=True, size=7.0)
    arrow(ax, (c4 + w4 + 0.014, 0.700), (c5 - 0.014, 0.610), color=fs.CRIMSON)
    arrow(ax, (c4 + w4 + 0.014, 0.372), (c5 - 0.014, 0.480), color=fs.CRIMSON)

    ax.text(-0.02, 0.175,
            "Fresh forms preserve the parent's numbers and its answer, so a model that has learned the "
            "item rather than its wording\nscores the same on all three. Only the wording was ever public, "
            "so $\\hat{\\Delta}$ isolates advantage that comes from the surface form.",
            fontsize=7.0, color=fs.INK, va="bottom", ha="left", linespacing=1.5)
    fs.save(fig, out, "design_schematic")


def fig_decomposition(out: Path, pooled_json: Path) -> None:
    """Figure: how much of a measured contamination effect an audit can see."""
    pooled = json.loads(Path(pooled_json).read_text())
    total = pooled["pooled_did_public"]
    hidden = pooled["pooled_did_fresh"]
    visible = pooled["pooled_visible_gap"]
    lo, hi = pooled["transfer_ci"]
    share = hidden / total

    fig, ax = plt.subplots(figsize=(fs.FULL, 2.55), constrained_layout=True)
    y, h = 0.0, 0.36

    ax.add_patch(Rectangle((0, y - h / 2), hidden, h, facecolor=fs.PUBLIC, edgecolor="none", zorder=2))
    ax.add_patch(Rectangle((hidden, y - h / 2), visible, h, facecolor=fs.FRESH,
                           edgecolor="none", zorder=2))
    ax.add_patch(Rectangle((0, y - h / 2), total, h, facecolor="none", edgecolor=fs.INK,
                           linewidth=0.9, zorder=4))

    ax.text(hidden / 2, y, f"invisible to a paraphrase audit    {hidden:+.3f}", ha="center",
            va="center", color="white", fontsize=8.2, fontweight="semibold", zorder=6)
    ax.annotate(f"visible  {visible:+.3f}", xy=(hidden + visible / 2, y + h / 2 + 0.01),
                xytext=(hidden + visible / 2, 0.52), ha="center", va="bottom", fontsize=8.2,
                fontweight="semibold", color=fs.FRESH,
                arrowprops=dict(arrowstyle="-", color=fs.FRESH, lw=0.8, shrinkA=1, shrinkB=1))

    ax.annotate("", xy=(0, -0.34), xytext=(total, -0.34),
                arrowprops=dict(arrowstyle="<->", color=fs.INK, lw=0.8, shrinkA=0, shrinkB=0))
    ax.text(total / 2, -0.40,
            f"effect of leaking an item's wording, {total:+.3f}",
            ha="center", va="top", fontsize=8.0, fontweight="semibold", color=fs.INK)

    # Where the split falls is itself estimated. Drawn as its own distribution
    # below the bar rather than shaded over it, so it is not mistaken for a
    # third segment. The draws are the archived bootstrap the interval came
    # from, rescaled from a share of the effect into accuracy points.
    draws_path = Path(pooled_json).with_name("bootstrap_draws.npz")
    if draws_path.is_file():
        ratio = np.load(draws_path)["transfer_ratio"] * total
        fs.density(ax, ratio[(ratio > -0.02) & (ratio < 0.315)], -1.00, fs.CRIMSON,
                   height=0.42, interval=(lo * total, hi * total), point=hidden)
    else:
        ax.plot([lo * total, hi * total], [-1.00, -1.00], color=fs.CRIMSON, lw=2.0,
                solid_capstyle="butt", zorder=3)
        ax.plot([hidden], [-1.00], "o", color=fs.CRIMSON, ms=5, markeredgecolor="white",
                markeredgewidth=0.6, zorder=4)
    ax.text(0, -1.38, f"the split is itself estimated: {share:.0%} of the effect transfers, "
            f"interval [{lo:.0%}, {hi:.0%}]", ha="left", va="top", fontsize=7.4,
            color=fs.CRIMSON)
    wrong = pooled.get("wrong_way_case")
    if wrong:
        # Study 9 pooled summary: the model with the most negative visible gap, read from the data
        case = (f"{wrong['model']} is that case: {wrong['did_public'] * 100:.0f} points of real "
                f"contamination,\nand the gap a paraphrase audit measures is ${wrong['visible_gap']:+.3f}$, "
                "pointing the wrong way.")
    else:
        case = ("StableLM-2-1.6B is that case: twenty points of real contamination,\nand the gap "
                "a paraphrase audit measures is $-0.030$, pointing the wrong way.")
    ax.text(0, -1.62, "At the top of that interval nothing is visible at all. " + case,
            ha="left", va="top", fontsize=7.4, color=fs.INK, linespacing=1.5)

    ax.set_xlim(-0.004, 0.325)
    ax.set_ylim(-2.15, 0.80)
    ax.set_yticks([])
    ax.set_xlabel("Change in accuracy on the leaked items, against uncontaminated controls")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color=fs.GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(length=3.0, pad=2.5)
    fs.save(fig, out, "effect_decomposition")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--pooled-json", type=Path, required=True)
    args = parser.parse_args()
    fig_design(args.out_dir)
    fig_decomposition(args.out_dir, args.pooled_json)
    print("wrote: design_schematic, effect_decomposition")


if __name__ == "__main__":
    main()
