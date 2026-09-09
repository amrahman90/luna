"""generate_graphical_abstract.py - Paper 1 v2.0 graphical abstract (RSE).

Single-shot PNG builder for the Paper 1 graphical abstract, rebuilt to
match the canonical panel spec VERBATIM:
``papers/paper1_resolution_limits/graphical_abstract_plan.md`` (v2.0),
whose §3 string table is the SINGLE SOURCE for panel content.

Layout (plan §1): 1280x720, header band + 2x2 panel grid + footer strip.
  Panel A (top-left, 48%): method chain, 4 arrow-connected boxes
  Panel B (top-right, 52%): FP calibration result (headline number)
  Panel C (bottom-left, 48%): outcome + resolution limit
  Panel D (bottom-right, 52%): claim framing + LLTB-1 v0.5
Every rendered string is asserted against the plan §3 table (or the
small set of structural/derived strings documented in ALLOWED_DERIVED
below) before the figure is saved.

Number provenance (plan §3, verification pull — nothing hard-coded
without one): row-based rate + area from
``data/outputs/wp2_sag/transfer/transfer_summary.json`` (`aggregate`);
unique-feature companion from
``data/outputs/wp2_sag/unique_accounting_2026-09-07.json``
(``unique_b1_key``); resolution-limit strings from main.md §4.6.
Claim discipline: calibrated inference, never verified detection.

Deterministic: no clock, no randomness, fixed fonts and dpi. Re-run:
    ~/lunarvoid/venv/bin/python 01_WORKSPACE/code/wp1_paper/generate_graphical_abstract.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO = Path("/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube")
OUT_PNG = (
    REPO / "01_WORKSPACE" / "papers" / "paper1_resolution_limits"
    / "figs" / "fig_graphical_abstract.png"
)
TRANSFER_JSON = (
    REPO / "01_WORKSPACE" / "data" / "outputs" / "wp2_sag" / "transfer"
    / "transfer_summary.json"
)
UNIQUE_JSON = (
    REPO / "01_WORKSPACE" / "data" / "outputs" / "wp2_sag"
    / "unique_accounting_2026-09-07.json"
)

# ---------------------------------------------------------------------------
# Palette + fonts (plan §4; unchanged guidance from v1 plan)
# ---------------------------------------------------------------------------

BG = "#F7F7F7"        # white/very-light-grey background
SLATE = "#2E4053"     # pipeline arrows / dark slate
OCHRE = "#B7791F"     # headline callout (muted ochre)
BRICK = "#9B2C2C"     # limitation/caveat text (muted brick)
GRIDL = "#D1D5DB"     # grid lines (light grey)
MUTED = "#6B7280"     # small/caption text
PANEL_BG = "#FFFFFF"
STRIP_BG = "#E9ECF1"

SERIF = "DejaVu Serif"
SANS = "DejaVu Sans"

# ---------------------------------------------------------------------------
# Plan §3 exact panel text strings (verbatim; renderer copies these)
# ---------------------------------------------------------------------------

PLAN = {
    "header title": "Detectability limits for lava tube roof "
                    "signatures in orbital topography",
    "header sub": "LLTB-1 calibrated benchmark · 21 NAC DTM instances "
                  "· 24,062.96 km²",
    "A box 1": "NAC DTM",
    "A box 2": "Planchon–Darboux fill",
    "A box 3": "multi-rung sag detection",
    "A box 4": "calibration",
    "A micro": "detector: depth × vesselness, rungs 0.5–10 m",
    "B headline": "3.74 [1.71, 7.10] per 10⁴ km²",
    "B label": "row-based",
    "B companion": "unique-feature: 2.08 [0.67, 4.85]",
    "B population": "21 DTM instances · 24,062.96 km² · "
                    "calibration-context, not survey",
    "B CI tag": "Garwood exact 95% CI",
    "C line 1": "14 catalogued pits re-detected",
    "C line 2": "zero novel above-floor candidates",
    "C limit 1": "single-DTM limit: sag A ≥ 5 m (≥ 4 m at quieter site)",
    "C limit 2": "1–2 m sags → multi-evidence stacking",
    "D banner": "Calibrated inference, not detection",
    "D tool": "detector: LLTB-1 v0.5",
    "D anchor": "only instrument-evidenced conduit: "
                "Tranquillitatis (Carrer 2024)",
    "footer": "calibrated inference, never verified detection",
}

# Strings outside the §3 table, each traceable (no numeric claims):
ALLOWED_DERIVED = {
    # Panel names from the plan §1 layout diagram.
    "Method chain", "FP calibration result", "Outcome", "Claim framing",
    # Panel letters from the plan §1 diagram / §3 slot names.
    "A", "B", "C", "D",
    # Fixed version label (plan title line: "Paper 1 v2.0").
    "Paper 1 · v2.0",
    # Analog-calibration scope, from main.md §2.1 ("four field sites,
    # represented as six map instances"); replaces the refuted
    # 30-cell grid caption per plan §5 item 4.
    "four field sites · six map instances",
    # Verbatim line-wrap fragments of §3 strings (box labels wrap to
    # two lines inside the chain boxes; the §3 headline "3.74
    # [1.71, 7.10] per 10⁴ km²" is drawn number-first at two sizes on
    # one baseline). These are substrings of table strings, not claims.
    "Planchon–Darboux", "fill", "multi-rung sag", "detection",
    "3.74", "[1.71, 7.10] per 10⁴ km²",
}
ALLOWED = set(PLAN.values()) | ALLOWED_DERIVED

# ---------------------------------------------------------------------------
# Verification pull (plan §6 item 3): build the numeric strings from the
# two JSONs and assert equality with the §3 table before rendering.
# ---------------------------------------------------------------------------

_transfer = json.loads(TRANSFER_JSON.read_text())
AGG = _transfer["aggregate"]
UNIQ = json.loads(UNIQUE_JSON.read_text())["unique_b1_key"]


def _check(built: str, slot: str) -> str:
    assert built == PLAN[slot], (
        f"verification pull mismatch for {slot!r}: "
        f"JSON-built {built!r} != plan {PLAN[slot]!r}"
    )
    return built


_check(
    f"{AGG['fp_per_1e4km2']:.2f} "
    f"[{AGG['fp_per_1e4km2_ci95_lo']:.2f}, "
    f"{AGG['fp_per_1e4km2_ci95_hi']:.2f}] per 10\u2074 km\u00b2",
    "B headline",
)
_check(
    f"unique-feature: {UNIQ['fp_per_1e4km2']:.2f} "
    f"[{UNIQ['ci95_lo']:.2f}, {UNIQ['ci95_hi']:.2f}]",
    "B companion",
)
_check(
    f"{AGG['n_dtms_with_score_raster']} DTM instances "
    f"· {AGG['total_area_km2']:,.2f} km² · "
    f"calibration-context, not survey",
    "B population",
)
_check(
    f"LLTB-1 calibrated benchmark · {AGG['n_dtms_with_score_raster']} "
    f"NAC DTM instances · {AGG['total_area_km2']:,.2f} km²",
    "header sub",
)
assert UNIQ["ci_method"].startswith("Poisson-exact (Garwood)"), (
    "unique-feature CI method is not Garwood exact"
)

# ---------------------------------------------------------------------------
# Text helper — records every rendered string for the traceability assert
# ---------------------------------------------------------------------------

RENDERED: list[str] = []


def t(ax, x: float, y: float, s: str, *, family: str = SANS,
      size: float = 10, color: str = SLATE, weight: str = "normal",
      ha: str = "left", va: str = "baseline",
      style: str = "normal") -> None:
    RENDERED.append(s)
    ax.text(x, y, s, transform=ax.transAxes, family=family,
            fontsize=size, color=color, fontweight=weight,
            fontstyle=style, ha=ha, va=va, zorder=3)


def register(s: str) -> None:
    """Record a composite string drawn as multiple text calls."""
    RENDERED.append(s)


# ---------------------------------------------------------------------------
# Panel builders (each draws inside an explicit bbox in axes fractions)
# ---------------------------------------------------------------------------


def _panel_card(ax, x0, y0, w, h, letter: str, name: str) -> None:
    """White panel card with light-grey edge, letter badge, §1 name."""
    ax.add_patch(Rectangle((x0, y0), w, h, transform=ax.transAxes,
                           facecolor=PANEL_BG, edgecolor=GRIDL,
                           linewidth=0.9, zorder=1))
    t(ax, x0 + 0.011, y0 + h - 0.026, letter,
      size=10, weight="bold", color=OCHRE)
    t(ax, x0 + 0.030, y0 + h - 0.026, name,
      size=8.5, weight="bold", color=MUTED)


def build_panel_a(ax, bbox) -> None:
    """Panel A — method chain: 4 arrow-connected boxes + micro-caption."""
    x0, y0, x1, y1 = bbox.x0, bbox.y0, bbox.x1, bbox.y1
    register(PLAN["A box 1"])
    register(PLAN["A box 2"])
    register(PLAN["A box 3"])
    register(PLAN["A box 4"])

    boxes = [
        (PLAN["A box 1"], ["NAC DTM"]),
        (PLAN["A box 2"], ["Planchon–Darboux", "fill"]),
        (PLAN["A box 3"], ["multi-rung sag", "detection"]),
        (PLAN["A box 4"], ["calibration"]),
    ]
    n = len(boxes)
    pad = 0.022
    gap = 0.026
    inner_w = (x1 - x0) - 2 * pad
    box_w = (inner_w - (n - 1) * gap) / n
    box_h = 0.105
    cy = y0 + 0.62 * (y1 - y0)

    for i, (full, lines) in enumerate(boxes):
        bx = x0 + pad + i * (box_w + gap)
        ax.add_patch(Rectangle((bx, cy - box_h / 2), box_w, box_h,
                               transform=ax.transAxes,
                               facecolor=PANEL_BG, edgecolor=SLATE,
                               linewidth=1.0, zorder=2))
        n_lines = len(lines)
        for j, line in enumerate(lines):
            yy = cy + (n_lines / 2 - 0.5 - j) * 0.026
            t(ax, bx + box_w / 2, yy, line, size=8, weight="bold",
              ha="center", va="center")
        if i < n - 1:
            ax.add_patch(FancyArrowPatch(
                (bx + box_w + 0.004, cy), (bx + box_w + gap - 0.004, cy),
                arrowstyle="-|>", mutation_scale=11,
                transform=ax.transAxes, color=SLATE, lw=1.1,
                shrinkA=0, shrinkB=0, zorder=3))

    t(ax, x0 + pad, cy - box_h / 2 - 0.038, PLAN["A micro"],
      size=10, color=MUTED)
    t(ax, x0 + pad, cy - box_h / 2 - 0.066,
      "four field sites · six map instances",
      size=9, color=MUTED, style="italic")

    # Scale-bar-style ruler + viridis strip (plan §2 Panel A visual
    # guidance: manuscript colormap/scale-bar language, not a verbatim
    # figure). No text.
    strip_y1 = y0 + 0.09
    strip_y0 = strip_y1 - 0.020
    import numpy as np
    grad = np.linspace(0.0, 1.0, 256).reshape(1, -1)
    ax.imshow(grad, cmap="viridis", aspect="auto", interpolation="nearest",
              extent=(x0 + pad, x1 - pad, strip_y0, strip_y1),
              transform=ax.transAxes, zorder=2)
    for k in range(5):
        xt = x0 + pad + (x1 - x0 - 2 * pad) * k / 4
        ax.plot([xt, xt], [strip_y1 + 0.004, strip_y1 + 0.012],
                transform=ax.transAxes, color=SLATE, lw=0.8, zorder=3)


def build_panel_b(ax, bbox) -> None:
    """Panel B — FP calibration result (headline + labels + strip)."""
    x0, y0, x1, y1 = bbox.x0, bbox.y0, bbox.x1, bbox.y1
    pad = 0.022

    # Headline: "3.74" huge + the rest of the §3 string at large weight
    # on the same baseline (composite registered for the assert).
    y_num = y1 - 0.105
    t(ax, x0 + pad, y_num, "3.74", size=48, weight="bold", color=OCHRE)
    t(ax, x0 + pad + 0.148, y_num, "[1.71, 7.10] per 10⁴ km²",
      size=20, weight="bold")
    register("3.74" + " " + "[1.71, 7.10] per 10⁴ km²")

    # Definition label directly under the number, prominent.
    t(ax, x0 + pad, y_num - 0.070, PLAN["B label"],
      size=18, weight="bold", color=BRICK)

    # Companion line (small).
    t(ax, x0 + pad, y_num - 0.108, PLAN["B companion"], size=13)

    # Population strip.
    sy1 = y_num - 0.152
    sy0 = sy1 - 0.050
    ax.add_patch(Rectangle((x0 + 0.010, sy0), (x1 - x0) - 0.020,
                           sy1 - sy0, transform=ax.transAxes,
                           facecolor=STRIP_BG, edgecolor=GRIDL,
                           linewidth=0.8, zorder=2))
    t(ax, (x0 + x1) / 2, (sy0 + sy1) / 2, PLAN["B population"],
      size=11.5, weight="bold", ha="center", va="center")

    # CI tag (small).
    t(ax, x0 + pad, sy0 - 0.028, PLAN["B CI tag"], size=10,
      color=MUTED, style="italic")


def build_panel_c(ax, bbox) -> None:
    """Panel C — outcome: re-detections + resolution limit."""
    x0, y0, x1, y1 = bbox.x0, bbox.y0, bbox.x1, bbox.y1
    pad = 0.022

    t(ax, x0 + pad, y1 - 0.075, PLAN["C line 1"], size=16,
      weight="bold")
    t(ax, x0 + pad, y1 - 0.118, PLAN["C line 2"], size=16,
      weight="bold")

    # Resolution-limit callout: brick text with a brick left bar.
    callout_y1 = y1 - 0.168
    callout_y0 = y0 + 0.055
    ax.add_patch(Rectangle((x0 + pad, callout_y0), 0.005,
                           callout_y1 - callout_y0,
                           transform=ax.transAxes, facecolor=BRICK,
                           edgecolor="none", zorder=2))
    t(ax, x0 + pad + 0.016, callout_y1 - 0.028, PLAN["C limit 1"],
      size=11, color=BRICK)
    t(ax, x0 + pad + 0.016, callout_y1 - 0.062, PLAN["C limit 2"],
      size=11, color=BRICK)


def build_panel_d(ax, bbox) -> None:
    """Panel D — claim framing: banner + tool + anchor."""
    x0, y0, x1, y1 = bbox.x0, bbox.y0, bbox.x1, bbox.y1
    pad = 0.022

    by1 = y1 - 0.085
    by0 = by1 - 0.068
    ax.add_patch(Rectangle((x0 + 0.010, by0), (x1 - x0) - 0.020,
                           by1 - by0, transform=ax.transAxes,
                           facecolor=STRIP_BG, edgecolor=GRIDL,
                           linewidth=0.8, zorder=2))
    ax.add_patch(Rectangle((x0 + 0.010, by0), 0.005, by1 - by0,
                           transform=ax.transAxes, facecolor=OCHRE,
                           edgecolor="none", zorder=3))
    t(ax, (x0 + x1) / 2 + 0.008, (by0 + by1) / 2, PLAN["D banner"],
      family=SERIF, size=19, weight="bold", ha="center", va="center")

    t(ax, x0 + pad, by0 - 0.070, PLAN["D tool"], size=13, weight="bold")
    t(ax, x0 + pad, by0 - 0.108, PLAN["D anchor"], size=10.5,
      color=MUTED, style="italic")


# ---------------------------------------------------------------------------
# Compose the page (plan §1 geometry)
# ---------------------------------------------------------------------------


def compose() -> plt.Figure:
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor=BG)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()

    from matplotlib.transforms import Bbox

    margin_l = margin_r = 0.028
    header_h = 0.125   # ~90 px
    footer_h = 0.056   # ~40 px

    # Header band
    header_y0 = 1 - 0.022 - header_h
    hx0, hx1 = margin_l, 1 - margin_r
    t(ax, hx0, header_y0 + header_h - 0.038, PLAN["header title"],
      family=SERIF, size=19, weight="bold")
    t(ax, hx0, header_y0 + 0.024, PLAN["header sub"],
      size=11, color=MUTED)
    t(ax, hx1, header_y0 + 0.024, "Paper 1 · v2.0",
      size=9, color=MUTED, ha="right")
    ax.plot([hx0, hx1], [header_y0 - 0.006, header_y0 - 0.006],
            transform=ax.transAxes, color=GRIDL, lw=1.0, zorder=3)

    # Footer strip
    footer_y1 = 0.022 + footer_h
    ax.plot([hx0, hx1], [footer_y1 + 0.008, footer_y1 + 0.008],
            transform=ax.transAxes, color=GRIDL, lw=0.8, zorder=3)
    t(ax, 0.5, 0.022 + footer_h / 2, PLAN["footer"], family=SERIF,
      size=11.5, color=SLATE, style="italic", ha="center", va="center")

    # 2x2 panel grid: A/C ~48% wide, B/D ~52% wide (plan §1)
    grid_x0, grid_x1 = margin_l, 1 - margin_r
    grid_y1 = header_y0 - 0.018
    grid_y0 = footer_y1 + 0.018
    col_gap, row_gap = 0.014, 0.014

    panel_w_total = grid_x1 - grid_x0 - col_gap
    w_ac = panel_w_total * 0.48
    w_bd = panel_w_total * 0.52
    panel_h_total = grid_y1 - grid_y0 - row_gap
    row_h = panel_h_total / 2

    top_y = grid_y0 + row_h + row_gap
    bot_y = grid_y0
    x_ac = grid_x0
    x_bd = grid_x0 + w_ac + col_gap

    for (x, y, w, letter, name, builder) in [
        (x_ac, top_y, w_ac, "A", "Method chain", build_panel_a),
        (x_bd, top_y, w_bd, "B", "FP calibration result", build_panel_b),
        (x_ac, bot_y, w_ac, "C", "Outcome", build_panel_c),
        (x_bd, bot_y, w_bd, "D", "Claim framing", build_panel_d),
    ]:
        _panel_card(ax, x, y, w, row_h, letter, name)
        builder(ax, Bbox.from_extents(x + 0.012, y + 0.012,
                                      x + w - 0.012, y + row_h - 0.048))

    return fig


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig = compose()

    # Traceability gate: every rendered string must be a plan §3 string
    # or one of the documented derived strings, and every §3 string must
    # be rendered. No other claims render.
    stray = [s for s in RENDERED if s not in ALLOWED]
    assert not stray, f"untraceable strings rendered: {stray!r}"
    missing = [s for s in PLAN.values() if s not in RENDERED]
    assert not missing, f"plan §3 strings missing from render: {missing!r}"

    fig.savefig(OUT_PNG, dpi=100, facecolor=BG)
    plt.close(fig)

    size_kb = OUT_PNG.stat().st_size / 1024
    print(f"OK: wrote {OUT_PNG}")
    print(f"    {size_kb:.1f} KB")
    print(f"    strings rendered: {len(RENDERED)} "
          f"(all traceable to plan §3 / documented derived set)")

    from PIL import Image
    with Image.open(OUT_PNG) as im:
        w, h = im.size
        print(f"    dimensions: {w}x{h} px")
        assert (w, h) == (1280, 720), f"expected 1280x720, got {w}x{h}"
    assert size_kb < 1024, f"size {size_kb:.1f} KB >= 1 MB"
    print("    PASS: 1280x720 px, < 1 MB, all strings traceable")


if __name__ == "__main__":
    main()
