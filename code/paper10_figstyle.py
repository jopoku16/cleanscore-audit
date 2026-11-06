"""One visual language for every figure in the CleanScore paper.

Figures were previously drawn at 8 to 11 inches wide with 7 to 9 point text.
Placed in a 6.5 inch text column that renders as roughly 5 point type, and
because each script chose its own width the apparent font size changed from
figure to figure. Everything here is drawn at the true column width so that a
point specified is a point printed, and so that type is the same size in every
panel of the paper.

Colour is never the only channel. Every series that is distinguished by colour
is also distinguished by marker or dash pattern, so the figures survive
greyscale printing and dichromatic vision. The two-series pairs use navy and
terracotta, the safest pairing under both common forms of colour blindness.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Column geometry, in inches. FULL is the JMLR/TMLR text width.
FULL = 6.5
HALF = 3.2

# Semantic palette. The same quantity is the same colour everywhere in the paper.
INK = "#1C2B36"        # axes, text: a warm dark slate, not black
PUBLIC = "#1B4965"     # public form / trained wording / GSM8K
FRESH = "#D1603D"      # fresh forms / unseen paraphrases / ARC-Challenge
MUTED = "#8D99AE"      # guardrail intervals, "before exposure"
CRIMSON = "#A4133C"    # zero reference, negative values, nominal level
GRID = "#E2E8EC"
HALO = "#F4F7F9"       # panel wash behind plotted data
FILL = "#EAF0F4"

DOMAIN_COLOR = {"gsm8k": PUBLIC, "arc": FRESH}
DOMAIN_NAME = {"gsm8k": "GSM8K", "arc": "ARC-Challenge"}
DOMAIN_MARKER = {"gsm8k": "o", "arc": "s"}

# Segoe UI is the nicest face available on the authoring machine; DejaVu Sans
# ships with matplotlib and is the guaranteed fallback, so this file reproduces
# anywhere even though it will not be glyph-identical off Windows.
FONT_STACK = ["Source Sans 3", "Fira Sans", "Segoe UI", "DejaVu Sans"]

RC = {
    "font.family": "sans-serif",
    "font.sans-serif": FONT_STACK,
    "font.size": 8.5,
    "axes.titlesize": 9.0,
    "axes.labelsize": 8.5,
    "xtick.labelsize": 8.0,
    "ytick.labelsize": 8.0,
    "legend.fontsize": 7.5,
    "figure.titlesize": 10.0,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "axes.linewidth": 0.8,
    "axes.titlepad": 6.0,
    "axes.titlelocation": "left",
    "axes.titleweight": "semibold",
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.major.size": 0.0,   # gridlines do this job; ticks are clutter
    "ytick.major.size": 0.0,
    "lines.linewidth": 1.6,
    "lines.markersize": 5.0,
    "legend.frameon": False,
    "legend.handlelength": 1.8,
    "legend.columnspacing": 1.2,
    "legend.labelspacing": 0.35,
    "figure.dpi": 120,
    "savefig.dpi": 400,
    "savefig.bbox": None,
    "pdf.fonttype": 42,      # embed TrueType so the PDF is not bitmapped
    "ps.fonttype": 42,
}


def use() -> None:
    """Install the house style. Call once at the top of a plotting script."""
    plt.rcParams.update(RC)


def axis(ax, grid: str = "both", spines: str = "left,bottom") -> None:
    """Reduce the frame to what carries information.

    Tick marks are removed: the gridlines already say where the values are, and
    a tick beside a gridline is the same fact drawn twice.
    """
    keep = {s.strip() for s in spines.split(",") if s.strip()}
    for side in ("top", "right", "bottom", "left"):
        ax.spines[side].set_visible(side in keep)
    for side in keep:
        ax.spines[side].set_color(GRID if side in ("top", "right") else INK)
    if grid in ("x", "both"):
        ax.grid(axis="x", color=GRID, linewidth=0.7, zorder=0)
    if grid in ("y", "both"):
        ax.grid(axis="y", color=GRID, linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, pad=3.5)


def label_end(ax, x, y, text, color, dx=6, size=7.8, weight="semibold", va="center"):
    """Name a series beside its own data instead of in a legend box.

    A legend makes the reader hold a colour in working memory and carry it to
    the line; a label on the line does not.
    """
    return ax.annotate(text, (x, y), xytext=(dx, 0), textcoords="offset points",
                       color=color, fontsize=size, fontweight=weight,
                       va=va, ha="left" if dx >= 0 else "right", zorder=6)


def density(ax, draws, y, color, height=0.34, interval=None, point=None, alpha=0.85):
    """Draw a bootstrap distribution as a shape, with its interval marked.

    Shows the sampling distribution the interval was cut from rather than only
    the two percentiles, so the reader can see the shape and the skew.
    """
    import numpy as np
    from scipy.stats import gaussian_kde

    lo_c, hi_c = np.percentile(draws, [0.2, 99.8])
    grid = np.linspace(lo_c, hi_c, 400)
    # A bootstrap of a mean over ~100 near-binary differences lands on a coarse
    # lattice, so the raw histogram is spiky in a way that says nothing about
    # the distribution. Widen the kernel past Scott's rule to show the shape
    # rather than the lattice.
    kde = gaussian_kde(draws, bw_method="scott")
    kde.set_bandwidth(kde.factor * 2.2)
    smooth = kde(grid)
    smooth = smooth / smooth.max() * height

    ax.fill_between(grid, y, y + smooth, color=color, alpha=0.16, linewidth=0, zorder=2)
    ax.plot(grid, y + smooth, color=color, linewidth=0.9, alpha=alpha, zorder=3)
    if interval is not None:
        inside = (grid >= interval[0]) & (grid <= interval[1])
        ax.fill_between(grid[inside], y, (y + smooth)[inside], color=color,
                        alpha=0.42, linewidth=0, zorder=3)
        ax.plot(interval, [y, y], color=color, linewidth=1.4, solid_capstyle="butt", zorder=4)
    if point is not None:
        ax.plot([point], [y], "o", color=color, markersize=4.2, markeredgecolor="white",
                markeredgewidth=0.7, zorder=5)


def zero_line(ax, vertical: bool = True) -> None:
    """The no-effect reference. Thin, dashed, and behind the estimates."""
    draw = ax.axvline if vertical else ax.axhline
    draw(0.0, color=CRIMSON, linewidth=0.9, linestyle=(0, (4, 3)), zorder=1)


def panel_letter(ax, letter: str, dx: float = -0.02, dy: float = 1.0) -> None:
    """Place (a), (b), ... above the axes so reviewers can cite a panel."""
    ax.text(dx, dy, f"({letter})", transform=ax.transAxes, fontsize=9.5,
            fontweight="bold", va="bottom", ha="right", color=INK)


def letter_panels(axes, dx: float = -0.02, dy: float = 1.0) -> None:
    for letter, ax in zip("abcdefgh", axes):
        panel_letter(ax, letter, dx=dx, dy=dy)


def save(fig, out_dir: Path, stem: str) -> None:
    """Write the raster copy the manuscript embeds and the vector copy for print."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(out_dir / f"{stem}.{ext}")
    plt.close(fig)
