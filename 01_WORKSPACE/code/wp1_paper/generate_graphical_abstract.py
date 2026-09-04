"""generate_graphical_abstract.py - LLTB-1 graphical abstract (RSE).

Single-shot PNG builder for the Paper 1 graphical abstract (LLTB-1
calibrated benchmark + lunar extension). Produces
`01_WORKSPACE/papers/paper1_resolution_limits/figs/fig_graphical_abstract.png`
at >= 1280x720 px, < 1 MB, Tufte-inspired minimal aesthetic.

CLAIM DISCIPLINE: every number in this figure traces to Paper 1
`main.md` §4.1/§4.2 (Table 1) and `data/outputs/wp2_sag/transfer/
transfer_summary.json` block `aggregate`. No number is invented; no
"detection" framing is used. The aggregate FP rate is reported as
calibration-context, NOT survey (Paper 1 §4.1 lines 232-239 + §5.2
line 555-556).

Style (from `01_WORKSPACE/learning/assets/lesson.css`):
  - background #fdfdfb (off-white)
  - serif body (Palatino/ETBembo fallback DejaVu Serif)
  - sans-serif headers (Helvetica/Arial fallback DejaVu Sans)
  - dark text #1a1a1a, muted #666, accent #1565c0, warning #c2410c
  - NO gradients, shadows, glow, or 3D bevels

Re-run:
    ~/lunarvoid/venv/bin/python 01_WORKSPACE/code/wp1_paper/generate_graphical_abstract.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO = Path("/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube")
OUT_PNG = (
    REPO
    / "01_WORKSPACE"
    / "papers"
    / "paper1_resolution_limits"
    / "figs"
    / "fig_graphical_abstract.png"
)

# ---------------------------------------------------------------------------
# Palette (from lesson.css)
# ---------------------------------------------------------------------------

BG = "#fdfdfb"
FG = "#1a1a1a"
MUTED = "#666666"
RULE = "#d4d0c8"
ACCENT = "#1565c0"
WARN = "#c2410c"
PANEL_BG = "#ffffff"
PANEL_RULE = "#cfcabc"
BOX_GREY = "#ececec"
BOX_GREY_EDGE = "#b5b2a8"
BOX_DARK = "#3a3a3a"

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

SERIF_CANDIDATES = ["Palatino Linotype", "Palatino", "ETBembo",
                    "URW Palladio L", "DejaVu Serif"]
SANS_CANDIDATES = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]
MONO_CANDIDATES = ["JetBrains Mono", "Menlo", "Consolas", "DejaVu Sans Mono"]


def _first_available(candidates: list[str]) -> str:
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            return name
    return candidates[-1]


SERIF = _first_available(SERIF_CANDIDATES)
SANS = _first_available(SANS_CANDIDATES)
MONO = _first_available(MONO_CANDIDATES)

# ---------------------------------------------------------------------------
# Load-bearing numbers (every value traces to Paper 1 main.md)
# ---------------------------------------------------------------------------

# Per-rung F1 (Table 1, §4.2). Three representative rungs (0.5, 1, 5 m)
# from the v0.4-freeze table; numbers are the frozen pre-v0.4 values,
# with the v0.4 tuning lifts noted in main.md lines 315-318.
LADDER_RUNGS = [
    {"rung_m": 0.5, "f1_best": 0.097,
     "site": "IndianTunnel_Collapse3",
     "note": "real lava tube; thr=0 predict-all"},
    {"rung_m": 1.0, "f1_best": 0.277,
     "site": "IndianTunnel_NorthSurface",
     "note": "BEST HONEST F1; cliff/overhang"},
    {"rung_m": 5.0, "f1_best": 0.071,
     "site": "IndianTunnel_Collapse3",
     "note": "predict-all; precision-bound"},
]

# 21 on-disk NAC DTMs (G2 close set, Paper 1 §3.3.1 line 174-201 + §4.1
# line 243-250). Six shown with text labels; the rest are unlabelled grey
# boxes (per the task brief: "just coloured boxes labelled with a few
# DTM names like TRANQPIT1, MARIUSPIT01, INGENIIPIT, etc.").
LUNAR_DTMS = [
    "TRANQPIT1", "MARIUSPIT01", "INGENIIPIT", "IRIDIUMPIT1",
    "FECUNPIT", "FECNDITATS2", "PRCLRMPIT01", "SWFECUNPIT1",
    "TYCHOPK", "GRUITHUIS17", "GRUITHMARE2", "MARIUSCONE",
    "KINGCRATER", "FRESHMELT", "MARIUSHILS", "HEPK2",
    "TYCHOPK02", "TYCHOPK04", "TYCHOPK07", "TYCHOPK_FLR", "FRESHMELT2",
]
assert len(LUNAR_DTMS) == 21, f"expected 21 NAC DTMs, got {len(LUNAR_DTMS)}"
LABELLED_DTMS = {"TRANQPIT1", "MARIUSPIT01", "INGENIIPIT",
                 "TYCHOPK", "FECUNPIT", "MARIUSCONE"}

# Short labels for cells (so they always fit cleanly inside the box).
# Keys must match LUNAR_DTMS entries; values are the cell text.
SHORT_LABELS = {
    "TRANQPIT1":   "TRANQ",
    "MARIUSPIT01": "MARIUS",
    "INGENIIPIT":  "INGENII",
    "TYCHOPK":     "TYCHO",
    "FECUNPIT":    "FECUN",
    "MARIUSCONE":  "MCONE",
}

# Headline numbers (Paper 1 §4.1 lines 232-239 + §5.2 lines 555-556).
F1_BEST = 0.277          # IndianTunnel_NorthSurface @ 1 m (frozen pre-v0.4)
FP_AGG = 3.74            # aggregate FP per 1e4 km^2, N=21
FP_CI_LOW = 1.71
FP_CI_HIGH = 7.10
N_ABOVE_FLOOR = 14       # above-floor inferred void candidates (tier-C)
TIER_C_ROWS = 278        # tier-C morphometry rows
FP_N = 9                 # n_fp
TP_N = 14                # n_tp
ABOVE_FLOOR_N = 45       # n_above_local_floor
AREA_KM2 = 24062.96      # denominator (N=21)
DEFERRED_RANDOM_MARE = 30  # random-mare sites deferred (no LROC NAC)

LIMITATIONS = [
    "Catalogued-pits-only sampling (no random-mare control; "
    f"{DEFERRED_RANDOM_MARE} deferred)",
    "Tranquillitatis = only verified subsurface void (Carrer 2024)",
    "Morphometry only (no multi-evidence stacking)",
    "Tier-A promotions = 0 by design (P5.2 deferred)",
]

# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def t(ax, x: float, y: float, s: str, *, family: str = SERIF,
      size: float = 10, color: str = FG, weight: str = "normal",
      ha: str = "left", va: str = "baseline",
      style: str = "normal") -> None:
    ax.text(x, y, s, transform=ax.transAxes, family=family,
            fontsize=size, color=color, fontweight=weight,
            fontstyle=style, ha=ha, va=va, zorder=3)


# ---------------------------------------------------------------------------
# Panel builders (each draws inside an explicit Bbox in figure coords)
# ---------------------------------------------------------------------------


def build_panel_a(ax, bbox) -> None:
    """Panel A - the detector chain (LLTB-1 v0.5 ladder).

    Source: Paper 1 §4.2 Table 1. Three rungs (0.5/1/5 m) shown as
    horizontal bars (NOT nested boxes - simpler, fits the panel).
    """
    x0, y0, x1, y1 = bbox.x0, bbox.y0, bbox.x1, bbox.y1
    w = x1 - x0
    h = y1 - y0

    # Caption above the ladder
    t(ax, x0, y1 - 0.010,
      "Depth x Frangi-vesselness (30-300 m) per rung; frozen pre-v0.4.",
      size=8.5, color=MUTED, style="italic")

    # Ladder: 3 horizontal bars, each rung posting on the left
    band_y1 = y1 - 0.040
    band_y0 = y0 + 0.050
    n = len(LADDER_RUNGS)
    rung_h = (band_y1 - band_y0) / n - 0.012
    rung_gap = 0.012

    for i, rung in enumerate(LADDER_RUNGS):
        ry = band_y1 - (i + 1) * rung_h - i * rung_gap
        rx0 = x0 + 0.010
        rx1 = x1 - 0.010

        # Bar
        rect = Rectangle((rx0, ry), rx1 - rx0, rung_h,
                         transform=ax.transAxes,
                         facecolor=BG, edgecolor=FG, linewidth=0.9,
                         zorder=2)
        ax.add_patch(rect)

        # Left rung posting (sans-serif, big)
        t(ax, rx0 + 0.012, ry + rung_h * 0.66,
          f"{rung['rung_m']:g} m",
          family=SANS, size=12, weight="bold")
        t(ax, rx0 + 0.012, ry + rung_h * 0.28,
          "rung", family=SANS, size=7.5, color=MUTED)

        # Centre: site + note
        t(ax, rx0 + 0.075, ry + rung_h * 0.66,
          rung["site"], size=8.5, weight="bold")
        t(ax, rx0 + 0.075, ry + rung_h * 0.28,
          rung["note"], size=7, color=MUTED, style="italic")

        # Right F1 callout
        is_best = rung["f1_best"] == F1_BEST
        t(ax, rx1 - 0.010, ry + rung_h * 0.66,
          f"F1 = {rung['f1_best']:.3f}",
          family=SANS, size=12, weight="bold",
          color=ACCENT if is_best else FG, ha="right")

    # Footnote
    t(ax, x0, y0 + 0.012,
      "6 NASA analog sites x 5 GSD rungs = 30 (site x GSD) cells",
      size=8, color=MUTED, style="italic")


def build_panel_b(ax, bbox) -> None:
    """Panel B - the lunar application (N=21 NAC DTMs).

    Source: Paper 1 §3.3.1 lines 174-201 + §4.1 lines 232-239.
    Layout: 7-col x 3-row DTM grid on the LEFT half of the panel,
    an arrow + two callouts on the RIGHT half (computed as fractions
    of the panel bbox so the callout never bleeds past the right edge).
    """
    x0, y0, x1, y1 = bbox.x0, bbox.y0, bbox.x1, bbox.y1
    w = x1 - x0
    h = y1 - y0

    # Sub-caption
    t(ax, x0, y1 - 0.010,
      "NAC DTM -> Planchon-Darboux fill -> Frangi -> threshold -> "
      "local-max -> registry",
      size=8.5, color=MUTED, style="italic")

    # Grid occupies left 55% of the panel
    grid_frac_w = 0.55
    grid_x0 = x0 + 0.010
    grid_x1 = x0 + w * grid_frac_w - 0.010
    grid_y0 = y0 + 0.080
    grid_y1 = y1 - 0.040

    n_cols, n_rows = 7, 3
    cell_w = (grid_x1 - grid_x0) / n_cols
    cell_h = (grid_y1 - grid_y0) / n_rows

    for i, dtm in enumerate(LUNAR_DTMS):
        col = i % n_cols
        row = i // n_cols
        cx0 = grid_x0 + col * cell_w + 0.003
        cy0 = grid_y0 + (n_rows - 1 - row) * cell_h + 0.003
        cw = cell_w - 0.006
        ch = cell_h - 0.006

        if dtm in LABELLED_DTMS:
            rect = Rectangle((cx0, cy0), cw, ch, transform=ax.transAxes,
                             facecolor=BOX_DARK, edgecolor="none",
                             zorder=3)
            ax.add_patch(rect)
            label = SHORT_LABELS.get(dtm, dtm)
            t(ax, cx0 + cw / 2, cy0 + ch / 2 - 0.002, label,
              family=SANS, size=5.5, color="#fdfdfb", weight="bold",
              ha="center", va="center")
        else:
            rect = Rectangle((cx0, cy0), cw, ch, transform=ax.transAxes,
                             facecolor=BOX_GREY, edgecolor=BOX_GREY_EDGE,
                             linewidth=0.5, zorder=2)
            ax.add_patch(rect)

    # Grid caption below the grid
    t(ax, grid_x0, y0 + 0.025,
      "N = 21 processed NAC DTMs",
      family=SANS, size=9, weight="bold")
    t(ax, grid_x0 + 0.145, y0 + 0.025,
      "(Cycles 1-2 close, 2026-08-23)",
      size=8, color=MUTED, style="italic")

    # Arrow + callout live in the RIGHT half of the panel.
    callout_x0 = x0 + w * (grid_frac_w + 0.02)  # starts 2% past the grid edge
    callout_x1 = x1 - 0.010
    arrow_y = (grid_y0 + grid_y1) / 2

    arrow = FancyArrowPatch(
        (grid_x1 + 0.004, arrow_y),
        (callout_x0 - 0.003, arrow_y),
        arrowstyle="-|>", mutation_scale=10,
        transform=ax.transAxes, color=FG, lw=0.9,
        shrinkA=0, shrinkB=0, zorder=3,
    )
    ax.add_patch(arrow)

    # Right-side callout (two stacked callouts, both inside the right half)
    t(ax, callout_x0, arrow_y + 0.045,
      f"{TIER_C_ROWS} tier-C rows",
      family=SANS, size=10.5, weight="bold")
    t(ax, callout_x0, arrow_y + 0.020,
      f"{ABOVE_FLOOR_N} above-floor; {TP_N} inferred voids",
      size=8, color=MUTED, style="italic")
    t(ax, callout_x0, arrow_y - 0.045,
      "9/9 FPs at 2 pit sites",
      family=SANS, size=10, weight="bold", color=WARN)
    t(ax, callout_x0, arrow_y - 0.070,
      "(FECUNPIT 6 + TRANQPIT1 3)",
      size=8, color=MUTED, style="italic")


def build_panel_c(ax, bbox) -> None:
    """Panel C - the headline number (F1 and FP rate).

    Source: Paper 1 §4.1 lines 232-239 and §4.2 Table 1a line 262.
    Numbers stacked vertically so the panel width (45% of page) is
    never overflowed. The two big numbers are still the largest type
    on the page.
    """
    x0, y0, x1, y1 = bbox.x0, bbox.y0, bbox.x1, bbox.y1
    w = x1 - x0
    h = y1 - y0

    # Block 1: best honest F1 (top half of panel)
    y_f1_label = y1 - 0.028
    y_f1_num = y_f1_label - 0.072
    t(ax, x0, y_f1_label, "Best honest F1",
      family=SANS, size=9, weight="bold", color=MUTED)
    t(ax, x0, y_f1_num, f"{F1_BEST:.3f}",
      family=SANS, size=30, weight="bold", color=ACCENT)
    t(ax, x0 + 0.105, y_f1_num + 0.005,
      "IndianTunnel_NorthSurface @ 1 m",
      family=SANS, size=9, weight="bold")
    t(ax, x0 + 0.105, y_f1_num - 0.018,
      "(v0.4-tuned: 0.362 @ 45 deg)",
      size=8, color=MUTED, style="italic")

    # Thin horizontal rule between the two blocks
    rule_y = y_f1_num - 0.045
    ax.plot([x0, x1 - 0.010], [rule_y, rule_y],
            transform=ax.transAxes, color=RULE, lw=0.7, zorder=3)

    # Block 2: aggregate FP (bottom half of panel) - the true headline.
    y_fp_label = rule_y - 0.022
    y_fp_num = y_fp_label - 0.075
    t(ax, x0, y_fp_label, "Aggregate lunar FP",
      family=SANS, size=9, weight="bold", color=MUTED)
    t(ax, x0, y_fp_num, f"{FP_AGG:.2f}",
      family=SANS, size=34, weight="bold", color=ACCENT)
    t(ax, x0 + 0.115, y_fp_num + 0.020,
      f"[{FP_CI_LOW:.2f}, {FP_CI_HIGH:.2f}]",
      family=SANS, size=13, weight="bold")
    t(ax, x0 + 0.115, y_fp_num + 0.000,
      "per 10\u2074 km\u00b2", size=9.5)
    t(ax, x0 + 0.230, y_fp_num + 0.000,
      "(95% CI)", size=8.5, color=MUTED, style="italic")
    t(ax, x0, y_fp_num - 0.040,
      "Poisson-exact (Garwood); calibration-context, NOT survey",
      size=8, color=WARN, style="italic")

    # Footer micro-stats (single line, fits inside the panel)
    t(ax, x0, y0 + 0.018,
      f"n_fp = {FP_N}  |  n_tp = {TP_N}  |  "
      f"n_above_floor = {ABOVE_FLOOR_N}  |  "
      f"denom = {AREA_KM2:,.0f} km\u00b2",
      size=7.5, color=MUTED, style="italic")


def build_panel_d(ax, bbox) -> None:
    """Panel D - honest limitations (4 bullets, claim-discipline framing).

    Source: Paper 1 §5.2 lines 529-591 (Honest limitations).
    """
    x0, y0, x1, y1 = bbox.x0, bbox.y0, bbox.x1, bbox.y1
    h = y1 - y0

    t(ax, x0, y1 - 0.010,
      "What this paper is not, by design.",
      size=8.5, color=MUTED, style="italic")

    # 4 bullets stacked vertically, evenly spaced
    bullet_y_top = y1 - 0.050
    bullet_y_bot = y0 + 0.060
    n = len(LIMITATIONS)
    bullet_step = (bullet_y_top - bullet_y_bot) / n

    for i, line in enumerate(LIMITATIONS):
        by = bullet_y_top - i * bullet_step

        # Number marker
        t(ax, x0 + 0.005, by - 0.005, f"{i + 1}",
          family=SANS, size=9, weight="bold", color=WARN)

        # Body text
        ax.text(x0 + 0.030, by - 0.005, line,
                transform=ax.transAxes, family=SERIF, fontsize=9.5,
                color=FG, ha="left", va="top",
                wrap=True, zorder=3)

    # Footer line
    t(ax, x0, y0 + 0.015,
      "Source: Paper 1 main.md \u00a74.1/4.2/5.2; "
      "transfer_summary.json `aggregate` block",
      size=7.5, color=MUTED, style="italic")


# ---------------------------------------------------------------------------
# Compose the page
# ---------------------------------------------------------------------------


def _panel_box(ax, x0: float, y0: float, w: float, h: float,
               kicker: str, title: str, subtitle: str):
    """Draw the panel frame and header; return content Bbox."""
    rect = Rectangle((x0, y0), w, h, transform=ax.transAxes,
                     facecolor=PANEL_BG, edgecolor=PANEL_RULE,
                     linewidth=0.8, zorder=1)
    ax.add_patch(rect)

    t(ax, x0 + 0.012, y0 + h - 0.022, kicker,
      family=SANS, size=8, weight="bold", color=ACCENT)
    t(ax, x0 + 0.012, y0 + h - 0.045, title,
      family=SANS, size=12, weight="bold")
    if subtitle:
        t(ax, x0 + 0.012, y0 + h - 0.072, subtitle,
          size=9.5, color=MUTED, style="italic")

    # Title block height: 0.082 (kicker + title + subtitle) or 0.058
    title_block_h = 0.082 if subtitle else 0.058
    return (x0 + 0.018, y0 + 0.018, x0 + w - 0.018, y0 + h - title_block_h)


def compose() -> plt.Figure:
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor=BG)
    fig.patch.set_facecolor(BG)

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()

    # Page margins
    margin_l = 0.030
    margin_r = 0.030
    margin_t = 0.020
    margin_b = 0.020

    # Header band
    header_h = 0.115
    header_y0 = 1 - margin_t - header_h
    header_x0 = margin_l
    header_x1 = 1 - margin_r

    t(ax, header_x0, header_y0 + header_h - 0.022,
      "LLTB-1 \u00b7 Paper 1 \u00b7 Graphical Abstract",
      family=SANS, size=9, weight="bold", color=ACCENT)
    t(ax, header_x0, header_y0 + header_h - 0.048,
      "Detectability limits for lava-tube roof signatures in "
      "orbital topography",
      size=17, weight="bold")
    t(ax, header_x0, header_y0 + 0.018,
      "LLTB-1 calibrated analog benchmark + lunar extension "
      "(Cycles 1-2 close, 2026-08-23)",
      size=10, color=MUTED, style="italic", va="bottom")

    ax.plot([margin_l, 1 - margin_r],
            [header_y0 - 0.005, header_y0 - 0.005],
            transform=ax.transAxes, color=FG, lw=1.0, zorder=3)

    # Footer band
    footer_h = 0.040
    footer_y0 = margin_b
    footer_x0 = margin_l
    footer_x1 = 1 - margin_r

    t(ax, footer_x0, footer_y0 + footer_h / 2,
      "LUNARVOID team",
      family=SANS, size=8.5, weight="bold", va="center")
    t(ax, footer_x0 + 0.090, footer_y0 + footer_h / 2,
      "single-author manuscript \u00b7 code & registry open at LUNARVOID repo",
      size=8.5, color=MUTED, style="italic", va="center")
    t(ax, footer_x1, footer_y0 + footer_h / 2,
      "Remote Sensing of Environment \u00b7 Paper 1",
      family=SANS, size=8.5, color=MUTED, va="center", ha="right")

    ax.plot([margin_l, 1 - margin_r],
            [footer_y0 + footer_h, footer_y0 + footer_h],
            transform=ax.transAxes, color=RULE, lw=0.7, zorder=3)

    # Panel grid (2x2)
    grid_y1 = header_y0 - 0.012
    grid_y0 = footer_y0 + footer_h + 0.012
    grid_x0 = margin_l
    grid_x1 = 1 - margin_r

    col_gap = 0.010
    row_gap = 0.010

    panel_w_total = grid_x1 - grid_x0
    panel_a_w = panel_w_total * 0.45 - col_gap / 2
    panel_b_w = panel_w_total * 0.55 - col_gap / 2

    panel_h_total = grid_y1 - grid_y0
    panel_top_y = grid_y0 + panel_h_total / 2 + row_gap / 2
    panel_top_h = panel_h_total / 2 - row_gap / 2
    panel_bot_y = grid_y0
    panel_bot_h = panel_top_h

    # Panel A
    ax0, ay0, ax1, ay1 = _panel_box(ax, grid_x0, panel_top_y,
                                     panel_a_w, panel_top_h,
                                     "PANEL A", "The detector chain",
                                     "LLTB-1 v0.5 ladder across 6 NASA "
                                     "analog sites")
    from matplotlib.transforms import Bbox
    build_panel_a(ax, Bbox.from_extents(ax0, ay0, ax1, ay1))

    # Panel B
    bx0, by0, bx1, by1 = _panel_box(ax, grid_x0 + panel_a_w + col_gap,
                                     panel_top_y, panel_b_w, panel_top_h,
                                     "PANEL B", "The lunar application",
                                     "Apply to lunar mare catalogued-pit DTMs")
    build_panel_b(ax, Bbox.from_extents(bx0, by0, bx1, by1))

    # Panel C
    cx0, cy0, cx1, cy1 = _panel_box(ax, grid_x0, panel_bot_y,
                                     panel_a_w, panel_bot_h,
                                     "PANEL C", "The headline number",
                                     "Calibrated inference, NOT detection")
    build_panel_c(ax, Bbox.from_extents(cx0, cy0, cx1, cy1))

    # Panel D
    dx0, dy0, dx1, dy1 = _panel_box(ax, grid_x0 + panel_a_w + col_gap,
                                     panel_bot_y, panel_b_w, panel_bot_h,
                                     "PANEL D", "Honest limitations",
                                     "Claim-discipline caveats (Paper 1 \u00a75.2)")
    build_panel_d(ax, Bbox.from_extents(dx0, dy0, dx1, dy1))

    return fig


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig = compose()
    fig.savefig(OUT_PNG, dpi=100, facecolor=BG)
    plt.close(fig)

    size_kb = OUT_PNG.stat().st_size / 1024
    print(f"OK: wrote {OUT_PNG}")
    print(f"    {size_kb:.1f} KB")
    try:
        from PIL import Image
        with Image.open(OUT_PNG) as im:
            w, h = im.size
            print(f"    dimensions: {w}x{h} px")
            assert w >= 1280, f"width {w} < 1280"
            assert h >= 720, f"height {h} < 720"
        assert size_kb < 1024, f"size {size_kb:.1f} KB >= 1 MB"
        print("    PASS: >= 1280x720 px and < 1 MB")
    except ImportError:
        print("    (Pillow not installed; skipping dimension check)")


if __name__ == "__main__":
    main()