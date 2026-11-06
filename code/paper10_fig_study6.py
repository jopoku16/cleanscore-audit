"""Figure for Study 6: what is there against what an audit sees.

One panel, three intervals. The two arms that hit the ceiling are drawn hollow
so the eye does not read a censored estimate as a measured one, and the bracket
marks the only quantity a paraphrase audit of this benchmark actually reports.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

import paper10_figstyle as st

ROOT = Path(__file__).resolve().parents[1]

ARMS = [
    ("public form\n(trained on)", "did_P", True),
    ("released fresh\n(options kept)", "did_F", True),
    ("deep paraphrase\n(options rewritten)", "did_G", False),
]


def main() -> None:
    st.use()
    s = json.loads((ROOT / "results" / "study6_arc" / "study6_summary.json").read_text())
    est = s["estimates"]

    fig, ax = plt.subplots(figsize=(st.FULL, 2.8))
    labels: list[str] = []
    for i, (label, key, censored) in enumerate(ARMS):
        y = len(ARMS) - 1 - i
        e = est[key]
        colour = st.MUTED if censored else st.PUBLIC
        ax.plot([e["ci_low"], e["ci_high"]], [y, y], color=colour, lw=2.2,
                solid_capstyle="butt", zorder=3)
        ax.plot([e["estimate"]], [y], "o", ms=8, zorder=4, color=colour,
                markerfacecolor="white" if censored else colour,
                markeredgewidth=1.8)
        ax.text(e["ci_high"] + 0.02, y, f"{e['estimate']:+.3f}", va="center",
                fontsize=8.4, weight="semibold", color=colour)
        labels.append(label)

    # The gap an auditor computes: public minus fresh, which is what the released
    # ARC bank can see at all.
    # The whole point is how narrow this is beside the bars, so draw it to scale
    # as a band rather than as a bracket that degenerates into a cross.
    vis = est["visible_F"]
    lo, hi = sorted((est["did_P"]["estimate"], est["did_F"]["estimate"]))
    ax.axvspan(lo, hi, color=st.CRIMSON, alpha=0.30, zorder=2)
    ax.annotate(f"what the audit sees: {vis['estimate']:+.3f}",
                xy=((lo + hi) / 2, 2.40), xytext=(0.30, 2.62),
                ha="center", fontsize=7.8, color=st.CRIMSON, weight="semibold",
                arrowprops=dict(arrowstyle="-", color=st.CRIMSON, lw=1.0,
                                shrinkA=2, shrinkB=2))

    st.zero_line(ax, vertical=True)
    ax.set_yticks(range(len(ARMS)))
    ax.set_yticklabels(list(reversed(labels)), fontsize=7.6)
    ax.set_ylim(-0.6, 2.9)
    ax.set_xlim(-0.06, 0.72)
    ax.set_xlabel("effect of leaking the item, against untouched parents")
    st.axis(ax, grid="x", spines="bottom")
    ax.text(0.72, -0.45, "hollow = censored by a ceiling at 1.000",
            ha="right", fontsize=7.0, color=st.MUTED)

    fig.subplots_adjust(left=0.20)
    st.save(fig, ROOT / "results" / "figures", "study6_arc")
    print("wrote study6_arc")


if __name__ == "__main__":
    main()
