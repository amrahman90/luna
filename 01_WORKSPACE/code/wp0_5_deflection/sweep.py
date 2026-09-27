"""WP0.5 — Parameter sweep driver.

Iterates the full (L, h, E, rho) sweep defined in the WP0.5 dispatch,
computes all three regime deflections (slab, arch, damaged at six
damage factors), and writes a long-format CSV with one row per regime
combination.

Sweep definition (per dispatch):
    L  in {60, 100, 150, 200, 300, 500} m               (6 values)
    h  in {5, 10, 20, 26, 50} m                        (5 values)
    E  in {5, 10, 20, 50} GPa                          (4 values)
    rho in {2700, 2900, 3100} kg/m^3                   (3 values)
    g = 1.62 m/s^2  (constant)
    R/L = 0.2  (arch geometry, constant)
    damage_factor in {0.0, 0.2, 0.4, 0.5, 0.6, 0.7}   (6 values)

Combos per (L, h, E, rho): 1 slab + 1 arch + 6 damaged = 8 regimes
Total combos:    6 * 5 * 4 * 3 = 360
Total CSV rows:  360 * 8 = 2880

Output columns:
    regime, L_m, h_m, E_GPa, rho_kgm3, R_over_L, damage_factor, delta_m

Usage:
    ~/lunarvoid/venv/bin/python sweep.py \
        --out /home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube/01_WORKSPACE/data/outputs/wp0_5_deflection/sweep_results.csv

Determinism
-----------
This sweep is pure arithmetic; no randomness. Re-running produces a
byte-identical CSV. All sums and outputs are computed in float64 (IEEE
754 double) and serialized via numpy float64 -> Python float -> str
round-trip so CSV bytes are reproducible across numpy versions.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

# Make sibling module importable regardless of cwd.
sys.path.insert(0, str(Path(__file__).parent))
from deflection_model import (  # noqa: E402
    G_LUNAR,
    DEFAULT_R_OVER_L,
    clamped_slab,
    clamped_arch,
    cumulative_damage,
)

# Per-dispatch parameter grids.
L_GRID_M    = (60, 100, 150, 200, 300, 500)              # 6
H_GRID_M    = (5, 10, 20, 26, 50)                        # 5
E_GRID_GPA  = (5, 10, 20, 50)                            # 4
RHO_GRID    = (2700, 2900, 3100)                         # 3
DMG_FACTORS = (0.0, 0.2, 0.4, 0.5, 0.6, 0.7)             # 6

G_LUNAR_CONST: float = G_LUNAR
R_OVER_L_CONST: float = DEFAULT_R_OVER_L

# Regime label for each row of the CSV (8 per (L,h,E,rho) combo).
REGIME_LABELS: tuple[str, ...] = (
    "slab",
    "arch",
    "damaged_d0.0",
    "damaged_d0.2",
    "damaged_d0.4",
    "damaged_d0.5",
    "damaged_d0.6",
    "damaged_d0.7",
)


def expected_row_count() -> int:
    """Compute and return the expected total CSV row count."""
    return (
        len(L_GRID_M) * len(H_GRID_M) * len(E_GRID_GPA) * len(RHO_GRID)
        * len(REGIME_LABELS)
    )


def iter_rows() -> "list[dict]":
    """Materialise the full sweep as a list of dicts (in memory)."""
    rows: list[dict] = []
    for L in L_GRID_M:
        for h in H_GRID_M:
            for E_GPa in E_GRID_GPA:
                E_Pa = float(E_GPa) * 1.0e9
                for rho in RHO_GRID:
                    # Slab
                    d_slab = clamped_slab(rho, G_LUNAR_CONST, L, E_Pa, h)
                    rows.append({
                        "regime": "slab",
                        "L_m": L, "h_m": h, "E_GPa": E_GPa, "rho_kgm3": rho,
                        "R_over_L": R_OVER_L_CONST, "damage_factor": 0.0,
                        "delta_m": d_slab,
                    })
                    # Arch (same R/L for all rows in this sweep)
                    d_arch = clamped_arch(rho, G_LUNAR_CONST, L, E_Pa, h,
                                          R_over_L=R_OVER_L_CONST)
                    rows.append({
                        "regime": "arch",
                        "L_m": L, "h_m": h, "E_GPa": E_GPa, "rho_kgm3": rho,
                        "R_over_L": R_OVER_L_CONST, "damage_factor": 0.0,
                        "delta_m": d_arch,
                    })
                    # Damage sweep
                    for df in DMG_FACTORS:
                        d_dam, _, _ = cumulative_damage(
                            rho, G_LUNAR_CONST, L, E_Pa, h, df,
                        )
                        rows.append({
                            "regime": f"damaged_d{df:.1f}",
                            "L_m": L, "h_m": h, "E_GPa": E_GPa, "rho_kgm3": rho,
                            "R_over_L": R_OVER_L_CONST, "damage_factor": df,
                            "delta_m": d_dam,
                        })
    return rows


def write_csv(rows: list[dict], out_path: Path) -> int:
    """Write the sweep to CSV; return the number of data rows written."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "regime", "L_m", "h_m", "E_GPa", "rho_kgm3",
        "R_over_L", "damage_factor", "delta_m",
    ]
    n = 0
    # Use float format with high precision (15 sig digits is the IEEE-754
    # double round-trip guarantee).
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({
                "regime": r["regime"],
                "L_m": int(r["L_m"]),
                "h_m": int(r["h_m"]),
                "E_GPa": int(r["E_GPa"]),
                "rho_kgm3": int(r["rho_kgm3"]),
                "R_over_L": f"{r['R_over_L']:.4f}",
                "damage_factor": f"{r['damage_factor']:.4f}",
                "delta_m": f"{r['delta_m']:.15e}",
            })
            n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(
            "/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube/"
            "01_WORKSPACE/data/outputs/wp0_5_deflection/sweep_results.csv"
        ),
        help="Output CSV path (default: dispatch-mandated location).",
    )
    a = ap.parse_args()

    expected = expected_row_count()
    print(f"Sweep: {len(L_GRID_M)}L x {len(H_GRID_M)}h x {len(E_GRID_GPA)}E x "
          f"{len(RHO_GRID)}rho = {len(L_GRID_M)*len(H_GRID_M)*len(E_GRID_GPA)*len(RHO_GRID)} "
          f"parameter combos x {len(REGIME_LABELS)} regimes "
          f"= {expected} CSV rows")

    rows = iter_rows()
    n = len(rows)
    assert n == expected, f"row count mismatch: got {n}, expected {expected}"

    n_written = write_csv(rows, a.out)

    # Print a few sanity rows (head, tail, extremes).
    print(f"Wrote {n_written} rows to {a.out}")
    print("First 3 rows:")
    for r in rows[:3]:
        print(f"  {r}")
    print("Last 3 rows:")
    for r in rows[-3:]:
        print(f"  {r}")
    # Find max-delta row (the most detectable)
    max_row = max(rows, key=lambda r: r["delta_m"])
    print(f"Max delta in sweep: {max_row['delta_m']:.4f} m at "
          f"L={max_row['L_m']}m h={max_row['h_m']}m "
          f"E={max_row['E_GPa']}GPa rho={max_row['rho_kgm3']} "
          f"regime={max_row['regime']}")
    # Find min-delta row in the slab regime (the 'pristine' floor)
    slab_rows = [r for r in rows if r["regime"] == "slab"]
    min_slab = min(slab_rows, key=lambda r: r["delta_m"])
    print(f"Min delta (slab, intact): {min_slab['delta_m']:.6f} m at "
          f"L={min_slab['L_m']}m h={min_slab['h_m']}m "
          f"E={min_slab['E_GPa']}GPa rho={min_slab['rho_kgm3']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
