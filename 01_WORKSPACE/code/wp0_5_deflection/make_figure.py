"""WP0.5 — 4-panel deflection figure.

Panels
------
(a) δ_slab vs L (h=26 m, E swept, ρ=2900); L=300 m vertical line,
    4 m detector-floor horizontal band.
(b) δ_slab vs h (L=300 m, E swept, ρ=2900); 4 m detector-floor band.
(c) Regime comparison at the F1 canonical points: slab vs arch vs
    damaged (d=0.3 and d=0.6) for each of the 7 anchors.
(d) All-regime heatmap: x=L, y=h, color=log10(δ_slab with E=10 GPa,
    ρ=2700 + damage factor 0.5); overlaid 4-5 m detector-floor
    contours.

Saves to `figures/deflection_4panel.png` at 150 dpi (Agg backend,
no display). The script is intentionally standalone so it can be
re-run independently of the sweep driver.

Determinism
-----------
No randomness; matplotlib defaults + a fixed colour cycle.
Re-running produces a byte-identical PNG modulo the EXIF/creation
timestamp inside the PNG metadata.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # no display
import matplotlib.pyplot as plt
import numpy as np

# Make sibling module importable.
sys.path.insert(0, str(Path(__file__).parent))
from deflection_model import (  # noqa: E402
    G_LUNAR,
    DEFAULT_R_OVER_L,
    clamped_slab,
    clamped_arch,
    cumulative_damage,
    CANONICAL_ANCHORS,
)

E_SWEEP = (5, 10, 20, 50)  # GPa
RHO_FIXED = 2900           # kg/m^3
H_PANEL_A = 26             # m (panel a)
L_PANEL_B = 300            # m (panel b)
L_GRID = np.array([60, 100, 150, 200, 300, 500], dtype=float)
H_GRID = np.array([5, 10, 20, 26, 50], dtype=float)

DETECTOR_FLOOR_M = 4.0
DETECTOR_FLOOR_M_MARIUS = 5.0  # MARIUSPIT01 is higher-noise per WP2


def _nice_axes(ax):
    ax.grid(True, which="both", alpha=0.3)
    ax.set_axisbelow(True)


def panel_a(ax):
    """δ_slab vs L (h=26, E swept, ρ=2900) with detector-floor band."""
    L = np.linspace(50, 520, 400)
    for E_GPa in E_SWEEP:
        d = clamped_slab(RHO_FIXED, G_LUNAR, L, E_GPa * 1e9, H_PANEL_A)
        ax.loglog(L, d, label=f"E={E_GPa} GPa")
    ax.axvline(300, color="black", linestyle=":", linewidth=1.2,
               label="L=300 m (max-span intact)")
    ax.axhline(DETECTOR_FLOOR_M, color="red", linestyle="--",
               linewidth=1.5, alpha=0.7,
               label=f"detector floor ({DETECTOR_FLOOR_M:.0f} m)")
    ax.axhline(DETECTOR_FLOOR_M_MARIUS, color="darkorange", linestyle="--",
               linewidth=1.2, alpha=0.6,
               label=f"Marius floor ({DETECTOR_FLOOR_M_MARIUS:.0f} m)")
    ax.set_xlabel("Span L (m)")
    ax.set_ylabel("δ_slab (m)")
    ax.set_title(f"(a) Intact slab, h={H_PANEL_A} m, ρ={RHO_FIXED} kg/m³\n"
                 "(elastic flexure only; detector floor unattainable "
                 "for E=50 GPa competent basalt)")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_ylim(1e-5, 1e3)
    _nice_axes(ax)


def panel_b(ax):
    """δ_slab vs h (L=300, E swept, ρ=2900) with detector-floor band."""
    h = np.linspace(3, 60, 400)
    for E_GPa in E_SWEEP:
        d = clamped_slab(RHO_FIXED, G_LUNAR, L_PANEL_B, E_GPa * 1e9, h)
        ax.loglog(h, d, label=f"E={E_GPa} GPa")
    ax.axhline(DETECTOR_FLOOR_M, color="red", linestyle="--",
               linewidth=1.5, alpha=0.7,
               label=f"detector floor ({DETECTOR_FLOOR_M:.0f} m)")
    ax.axhline(DETECTOR_FLOOR_M_MARIUS, color="darkorange", linestyle="--",
               linewidth=1.2, alpha=0.6,
               label=f"Marius floor ({DETECTOR_FLOOR_M_MARIUS:.0f} m)")
    ax.set_xlabel("Roof thickness h (m)")
    ax.set_ylabel("δ_slab (m)")
    ax.set_title(f"(b) Intact slab, L={L_PANEL_B} m, ρ={RHO_FIXED} kg/m³\n"
                 "(thinning the roof helps but only with weak rock)")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_ylim(1e-5, 1e3)
    _nice_axes(ax)


def panel_c(ax):
    """Regime comparison at the 7 F1 canonical anchors."""
    labels = [a["label"] for a in CANONICAL_ANCHORS]
    short_labels = [
        f"L={a['L']}\nh={a['h']}\nE={a['E']}" for a in CANONICAL_ANCHORS
    ]
    x = np.arange(len(CANONICAL_ANCHORS))
    width = 0.18

    delta_slab = []
    delta_arch = []
    delta_d03 = []
    delta_d05 = []
    delta_d07 = []
    for a in CANONICAL_ANCHORS:
        L, h, E_GPa = a["L"], a["h"], a["E"]
        E_Pa = E_GPa * 1e9
        # Use rho=3000 (F1-stated, exact match)
        rho = 3000.0
        delta_slab.append(clamped_slab(rho, G_LUNAR, L, E_Pa, h))
        delta_arch.append(clamped_arch(rho, G_LUNAR, L, E_Pa, h,
                                       R_over_L=DEFAULT_R_OVER_L))
        delta_d03.append(cumulative_damage(rho, G_LUNAR, L, E_Pa, h, 0.3)[0])
        delta_d05.append(cumulative_damage(rho, G_LUNAR, L, E_Pa, h, 0.5)[0])
        delta_d07.append(cumulative_damage(rho, G_LUNAR, L, E_Pa, h, 0.7)[0])

    ax.bar(x - 2*width, delta_slab, width, label="slab (intact)", color="C0")
    ax.bar(x - width,   delta_arch, width, label=f"arch (R/L={DEFAULT_R_OVER_L})", color="C1")
    ax.bar(x,           delta_d03, width, label="damaged d=0.3", color="C2")
    ax.bar(x + width,   delta_d05, width, label="damaged d=0.5", color="C3")
    ax.bar(x + 2*width, delta_d07, width, label="damaged d=0.7", color="C4")

    ax.axhline(DETECTOR_FLOOR_M, color="red", linestyle="--",
               linewidth=1.5, alpha=0.7,
               label=f"detector floor ({DETECTOR_FLOOR_M:.0f} m)")

    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, fontsize=7)
    ax.set_ylabel("δ (m, log scale)")
    ax.set_title("(c) F1 canonical anchors: regime comparison\n"
                 "(only d≥0.5 + wide span crosses the 4 m floor)")
    ax.legend(loc="upper left", fontsize=7)
    ax.set_ylim(1e-5, 1e3)
    _nice_axes(ax)


def panel_d(ax):
    """All-regime heatmap: log10(δ) over (L, h) for one representative
    damaged regime, with 4 m and 5 m detector-floor contours overlaid."""
    # Use the near-collapse regime: E=10 GPa, ρ=2700, damage=0.5
    # (mid-range, plausible vesicular protolith with significant damage).
    E_GPa = 10
    rho = 2700
    dmg = 0.5
    L_plot = np.linspace(50, 520, 60)
    h_plot = np.linspace(3, 55, 50)
    LL, HH = np.meshgrid(L_plot, h_plot)
    DD = np.zeros_like(LL)
    for i in range(LL.shape[0]):
        for j in range(LL.shape[1]):
            DD[i, j] = cumulative_damage(
                rho, G_LUNAR, LL[i, j], E_GPa * 1e9, HH[i, j], dmg,
            )[0]

    pcm = ax.pcolormesh(
        LL, HH, np.log10(np.maximum(DD, 1e-6)),
        cmap="viridis", shading="auto",
    )
    cb = plt.colorbar(pcm, ax=ax, label="log₁₀(δ_damaged) (m)")
    # Detector-floor contours (4 m and 5 m)
    cs4 = ax.contour(LL, HH, DD, levels=[DETECTOR_FLOOR_M],
                     colors="red", linewidths=2.0)
    cs5 = ax.contour(LL, HH, DD, levels=[DETECTOR_FLOOR_M_MARIUS],
                     colors="orange", linewidths=2.0, linestyles="--")
    ax.clabel(cs4, fmt="4 m floor", inline=True, fontsize=8)
    ax.clabel(cs5, fmt="5 m floor (Marius)", inline=True, fontsize=8)

    ax.set_xlabel("Span L (m)")
    ax.set_ylabel("Roof thickness h (m)")
    ax.set_title(f"(d) Near-collapse regime: E={E_GPa} GPa, ρ={rho}, d={dmg}\n"
                 "(red contour = 4 m detector floor; orange dashed = 5 m Marius)")
    _nice_axes(ax)


def make_figure(out_path: Path, dpi: int = 150) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    panel_a(axes[0, 0])
    panel_b(axes[0, 1])
    panel_c(axes[1, 0])
    panel_d(axes[1, 1])
    fig.suptitle(
        "WP0.5 Roof Deformation Forward Model — three regimes "
        "(reconciles elastic flexure with the 4-5 m NAC DTM detection floor)",
        fontsize=12, y=0.995,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(
            "/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube/"
            "01_WORKSPACE/data/outputs/wp0_5_deflection/figures/"
            "deflection_4panel.png"
        ),
        help="Output PNG path (default: dispatch-mandated location).",
    )
    ap.add_argument(
        "--dpi", type=int, default=150,
        help="Output DPI (default 150; dispatch minimum).",
    )
    a = ap.parse_args()
    make_figure(a.out, dpi=a.dpi)
    return 0


if __name__ == "__main__":
    sys.exit(main())
