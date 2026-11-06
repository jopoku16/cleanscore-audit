"""Figure for Study 4: what the leak actually installed.

Two panels. Left: accuracy on the leaked parents against the untouched ones,
which is where the failed manipulation shows up as a drop rather than a gain.
Right: the share of items on which the scorer's preferred option is the one
listed first, by form type, which is the artefact that caused the drop and which
fades as the memorised option strings are reworded away.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import paper10_figstyle as st

ROOT = Path(__file__).resolve().parents[1]
FORMS = [("original_public", "public\n(trained on)"), ("fresh_variant_1", "fresh 1"),
         ("fresh_variant_2", "fresh 2"), ("deep_paraphrase", "deep\nparaphrase")]


def main() -> None:
    st.use()
    base = pd.read_csv(ROOT / "study4_out" / "results" / "base" / "arc_study4_results.csv")
    exposed = pd.read_csv(ROOT / "study4_out" / "results" / "exposed" / "arc_study4_results.csv")
    assign = pd.read_csv(
        ROOT / "data" / "positive_control_arc_exposure_seed20260824.csv"
    ).set_index("parent_id")["exposed"]
    for df in (base, exposed):
        df["grp"] = df.parent_id.map(assign).map({1: "exposed", 0: "control"})

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(st.FULL, 2.9))

    # Left: accuracy on the public form, leaked parents versus untouched ones.
    def acc(df, grp):
        s = df[(df.form_type == "original_public") & (df.grp == grp)]
        return float(s["correct"].mean())

    groups = [("leaked parents", "exposed", st.PUBLIC), ("untouched parents", "control", st.MUTED)]
    for i, (name, grp, colour) in enumerate(groups):
        before, after = acc(base, grp), acc(exposed, grp)
        ax1.plot([0, 1], [before, after], "-o", color=colour, lw=2.0, ms=5, zorder=3)
        st.label_end(ax1, 1, after, f"{name}\n{after - before:+.2f}", colour, dx=7, va="center")
    ax1.set_xlim(-0.12, 1.9)
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(["before", "after exposure"])
    ax1.set_ylabel("accuracy on the leaked wording")
    ax1.set_ylim(0.2, 0.55)
    st.axis(ax1, grid="y")
    ax1.set_title("Training on the items made them worse", loc="left", fontsize=8.6)

    # Right: preference for the first-listed option, by form type.
    width = 0.36
    x = np.arange(len(FORMS))
    for offset, df, name, colour in ((-width / 2, base, "before", st.MUTED),
                                     (width / 2, exposed, "after", st.PUBLIC)):
        vals = [float((df[(df.form_type == ft) & (df.grp == "exposed")].pred_norm == "A").mean())
                for ft, _ in FORMS]
        ax2.bar(x + offset, vals, width, color=colour, label=name, zorder=3)
    ax2.axhline(0.25, color=st.CRIMSON, lw=1.1, ls=(0, (4, 3)), zorder=4)
    ax2.set_xlim(-0.55, len(FORMS) - 0.25)
    ax2.text(len(FORMS) - 0.42, 0.25, "chance", color=st.CRIMSON, fontsize=7.4,
             ha="left", va="center")
    ax2.set_xticks(x)
    ax2.set_xticklabels([lab for _, lab in FORMS], fontsize=7.0)
    ax2.set_ylabel("picks the first-listed option")
    ax2.set_ylim(0, 0.78)
    st.axis(ax2, grid="y")
    ax2.legend(frameon=False, fontsize=7.4, loc="upper right", handlelength=1.1)
    ax2.set_title("What the leak installed instead", loc="left", fontsize=8.6)

    st.save(fig, ROOT / "results" / "figures", "study4_arc")
    print("wrote study4_arc")


if __name__ == "__main__":
    main()
