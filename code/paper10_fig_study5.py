"""Figure for Study 5: the two leaks side by side.

Left panel is the whole methodological point in one comparison: same model, same
items, same seed, and the manipulation check moves from far below the registered
floor to far above it purely because the leaked line changed shape.

Right panel is where the effect went under the corrected leak, and the distance
between the first two bars is what a paraphrase audit would report.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import paper10_figstyle as st

ROOT = Path(__file__).resolve().parents[1]


def per_parent(df: pd.DataFrame) -> pd.DataFrame:
    p = df[df.form_type == "original_public"].set_index("parent_id")["correct"].astype(float)
    f = df[df.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
    g = df[df.form_type == "deep_paraphrase"].set_index("parent_id")["correct"].astype(float)
    return pd.DataFrame({"P": p, "F": f, "G": g})


def load(study: str, tag: str) -> pd.DataFrame:
    return pd.read_csv(ROOT / f"{study}_out" / "results" / tag / f"arc_{study}_results.csv")


def main() -> None:
    st.use()
    assign = pd.read_csv(
        ROOT / "data" / "positive_control_arc_exposure_seed20260824.csv"
    ).set_index("parent_id")["exposed"]
    exempt = {w.strip() for w in (ROOT / "data" / "arc_g_exempt.txt").read_text().split()
              if w.strip()}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(st.FULL, 2.9))

    # Left: manipulation check under the two exposure formats.
    dids = {}
    for study in ("study4", "study5"):
        ch = per_parent(load(study, "exposed")) - per_parent(load(study, "base"))
        ex = [i for i in ch.index if assign.get(i, 0) == 1]
        ct = [i for i in ch.index if assign.get(i, 0) == 0]
        dids[study] = float(ch.loc[ex, "P"].mean() - ch.loc[ct, "P"].mean())

    labels = ["Study 4\nleak ends in a letter", "Study 5\nleak ends in the answer"]
    colours = [st.CRIMSON, st.PUBLIC]
    for i, (study, colour) in enumerate(zip(("study4", "study5"), colours)):
        ax1.bar(i, dids[study], 0.5, color=colour, zorder=3)
        va = "top" if dids[study] < 0 else "bottom"
        off = -0.02 if dids[study] < 0 else 0.02
        ax1.text(i, dids[study] + off, f"{dids[study]:+.2f}", ha="center", va=va,
                 fontsize=9, weight="semibold", color=colour)
    ax1.axhline(0.05, color=st.MUTED, lw=1.1, ls=(0, (4, 3)), zorder=4)
    ax1.text(1.42, 0.075, "registered floor", color=st.MUTED, fontsize=7.2, ha="right")
    st.zero_line(ax1, vertical=False)
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(labels, fontsize=7.4)
    ax1.set_xlim(-0.55, 1.55)
    ax1.set_ylim(-0.36, 0.66)
    ax1.set_ylabel("effect on the trained wording")
    st.axis(ax1, grid="y")
    ax1.set_title("One change: the shape of the leaked line", loc="left", fontsize=8.6)

    # Right: where the corrected leak's effect landed.
    base, exposed = per_parent(load("study5", "base")), per_parent(load("study5", "exposed"))
    ex = [i for i in base.index if assign.get(i, 0) == 1]
    gex = [i for i in ex if i not in exempt and not np.isnan(base.loc[i, "G"])]
    bars = [("public\n(trained on)", base.loc[ex, "P"].mean(), exposed.loc[ex, "P"].mean()),
            ("fresh\n(options kept)", base.loc[ex, "F"].mean(), exposed.loc[ex, "F"].mean()),
            ("deep paraphrase\n(options reworded)", base.loc[gex, "G"].mean(),
             exposed.loc[gex, "G"].mean())]
    x = np.arange(len(bars))
    width = 0.36
    ax2.bar(x - width / 2, [b for _, b, _ in bars], width, color=st.MUTED,
            label="before", zorder=3)
    ax2.bar(x + width / 2, [a for _, _, a in bars], width, color=st.PUBLIC,
            label="after", zorder=3)
    # The gap an auditor would actually compute.
    ax2.annotate("", xy=(0 + width / 2, bars[0][2]), xytext=(1 + width / 2, bars[1][2]),
                 arrowprops=dict(arrowstyle="<->", color=st.CRIMSON, lw=1.2))
    ax2.text(0.5 + width / 2, 1.045, "what the audit sees: -0.02",
             ha="center", fontsize=7.4, color=st.CRIMSON, weight="semibold")
    ax2.set_xticks(x)
    ax2.set_xticklabels([lab for lab, _, _ in bars], fontsize=7.0)
    ax2.set_ylim(0, 1.20)
    ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax2.set_ylabel("accuracy on the leaked items")
    st.axis(ax2, grid="y")
    ax2.legend(frameon=False, fontsize=7.4, loc="upper right", handlelength=1.1)
    ax2.set_title("Where the corrected leak went", loc="left", fontsize=8.6)

    st.save(fig, ROOT / "results" / "figures", "study5_arc")
    print("wrote study5_arc")


if __name__ == "__main__":
    main()
