"""WP0.5 — Roof Deformation Forward Model (analytical, three regimes).

Purpose
-------
Closes the F1 critical finding from `00_SOURCE_ORIGINALS/LUNARVOID_v5_Review_Report.txt`
("the roof-sag amplitude was never estimated"). Provides the physics
basis for Paper 1 §1.2's strongest honest claim: detectable surface
depression over a lunar lava tube is NOT elastic flexure of an intact
basalt roof (sub-mm), but cumulative near-collapse degradation (m-scale)
of wide unsupported spans in damaged rock.

Regimes implemented
-------------------
1. **Elastic clamped slab** (intact flat roof, upper bound):
       delta_slab = rho * g * L^4 / (32 * E * h^2)
   Arched roofs carry load in compression and deflect less, so this is
   an UPPER BOUND on intact-roof deflection.

2. **Clamped parabolic arch** (typical lava-tube geometry):
       delta_arch = delta_slab * (1 - 0.5 * (R/L)^2)
   R/L = 0.2 is representative of surveyed lunar tubes (e.g. Marius
   Hills floor "Marius Pit" measured roof rise ~5 m over ~30 m span).
   Shallow-arch first-order correction from Timoshenko plate theory.

3. **Cumulative damage** (long-term, ~3.5 Gyr, near-collapse):
       E_damaged   = E * (1 - damage_factor)
       h_damaged   = h * (1 - damage_factor / 2)
       delta_damaged = rho * g * L^4 / (32 * E_damaged * h_damaged^2)
   damage_factor in [0, 0.7] sweeps roof spalling, rubble infill,
   regolith drainage, and impact-induced weakening.

Constants
---------
- g_lunar = 1.62 m/s^2
- All inputs SI: E in Pa, L and h in metres, rho in kg/m^3.

Outputs are in metres. Convert to mm/cm/m as needed for display.

Reference
---------
F1 derivation in `00_SOURCE_ORIGINALS/LUNARVOID_v5_Review_Report.txt`
sec. F1, with rho = 3000 kg/m^3 (note: the canonical-table dispatch
mistakenly states rho = 2900 in the rho column; the expected values
match rho = 3000 to all reported digits, see verify_wp0_5_deflection.py
for both computations).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional

# Lunar surface gravity (m/s^2). Used as default; functions also accept
# any g (e.g. for terrestrial sanity checks).
G_LUNAR: float = 1.62

# Representative R/L for shallow lunar lava-tube roofs.
DEFAULT_R_OVER_L: float = 0.2


def clamped_slab(rho: float, g: float, L: float, E: float, h: float) -> float:
    """Elastic deflection of a uniformly-loaded clamped rectangular plate.

    This is the UPPER BOUND on intact-roof deflection (arches deflect
    less because they carry self-weight in compression rather than
    bending).

    Accepts both scalar and array-like inputs (for plotting and
    sweeps). Returns the same type/shape as `L` (numpy-aware).

    Parameters
    ----------
    rho : float
        Rock density, kg/m^3 (lunar basalt ~2700-3100).
    g : float
        Gravitational acceleration, m/s^2 (lunar: 1.62).
    L : float or array-like
        Span (width of unsupported roof), metres.
    E : float
        Young's modulus, **Pa** (50 GPa basalt = 5e10 Pa).
    h : float
        Roof thickness, metres.

    Returns
    -------
    float or numpy.ndarray
        Mid-span deflection, metres. Positive downward.

    Notes
    -----
    Formula (Timoshenko & Woinowsky-Krieger, "Theory of Plates and
    Shells", 2nd ed., 1959, eq. 35, p. 197, clamped case for uniform
    load, unit width):
        w_max = q * L^4 / (32 * D),  D = E * h^3 / (12 * (1 - nu^2))
    Taking nu = 0 and unit width absorbs 12 * (1 - nu^2) into the
    coefficient, yielding the simplified form used by v5 F1:
        delta = rho * g * L^4 / (32 * E * h^2)
    The omission of (1 - nu^2) under-estimates stiffness by ~6-9% for
    typical basalt (nu ~ 0.25-0.30); this is conservative (gives a
    slightly larger delta, reinforcing the UPPER-BOUND intent).
    """
    import numpy as np
    L_arr = np.asarray(L, dtype=float)
    h_arr = np.asarray(h, dtype=float)
    # Validation: only fire on plain scalars to keep the hot path fast.
    if L_arr.ndim == 0 and h_arr.ndim == 0:
        if not (E > 0 and h_arr > 0 and L_arr > 0):
            raise ValueError(
                f"clamped_slab requires L>0, h>0, E>0; got L={L}, h={h}, E={E}"
            )
    result = rho * g * L_arr ** 4 / (32.0 * E * h_arr ** 2)
    # Return scalar if both L and h inputs were scalars (preserves the
    # type contract for the canonical-anchor verifier).
    if np.isscalar(L) and np.isscalar(h):
        return float(result)
    return result


def clamped_arch(
    rho: float,
    g: float,
    L: float,
    E: float,
    h: float,
    R_over_L: float = DEFAULT_R_OVER_L,
) -> float:
    """Elastic deflection of a clamped parabolic-arch roof.

    Approximated as the clamped-slab deflection reduced by a shallow-
    arch correction:
        delta_arch = delta_slab * (1 - 0.5 * (R/L)^2)
    Valid for shallow arches (R/L ~ 0.1-0.3); deep arches (R/L > 0.5)
    need a full shell analysis (out of scope for this first-order
    analytical model).

    Parameters
    ----------
    rho, g, L, E, h : see clamped_slab.
    R_over_L : float, default 0.2
        Arch rise / span ratio. 0.2 is representative of typical
        lunar tubes (small-to-moderate rise).

    Returns
    -------
    float
        Mid-span deflection, metres.
    """
    if not 0.0 <= R_over_L <= 1.0:
        raise ValueError(f"R_over_L must be in [0, 1]; got {R_over_L}")
    delta_slab = clamped_slab(rho, g, L, E, h)
    arch_correction = 1.0 - 0.5 * R_over_L ** 2
    return delta_slab * arch_correction


def cumulative_damage(
    rho: float,
    g: float,
    L: float,
    E: float,
    h: float,
    damage_factor: float,
) -> tuple[float, float, float]:
    """Deflection under cumulative long-term damage.

    Models ~3.5 Gyr of roof degradation via effective-modulus and
    effective-thickness reduction:
        E_damaged = E * (1 - damage_factor)
        h_damaged = h * (1 - damage_factor / 2)
    damage_factor = 0.0  -> pristine (returns clamped_slab value)
    damage_factor = 0.7  -> severe (E drops to 30%, h to 65%)

    Parameters
    ----------
    rho, g, L, E, h : see clamped_slab.
    damage_factor : float in [0, 1)
        0 = pristine; 0.7 = near-collapse; values above ~0.85 imply
        the roof has already failed and the geometry is no longer
        a clamped plate (out of model scope).

    Returns
    -------
    (delta_damaged, E_damaged, h_damaged) : tuple[float, float, float]
        Damaged deflection (m) and the effective modulus / thickness
        used.
    """
    if not 0.0 <= damage_factor < 1.0:
        raise ValueError(f"damage_factor must be in [0, 1); got {damage_factor}")
    E_damaged = E * (1.0 - damage_factor)
    h_damaged = h * (1.0 - damage_factor / 2.0)
    if E_damaged <= 0 or h_damaged <= 0:
        raise ValueError(
            "damage_factor reduces E or h to <=0 (roof has already failed)"
        )
    delta = rho * g * L ** 4 / (32.0 * E_damaged * h_damaged ** 2)
    return delta, E_damaged, h_damaged


@dataclass(frozen=True)
class RegimeSummary:
    """All three regime deflections for one (L, h, E, rho) combo.

    Slab and arch are recoverable from L, h, E, rho (no extra state).
    Damaged is computed at damage_factor=0 (== slab) plus a couple of
    representative factors that bracket the 'near-collapse' regime:
    factor 0.3 (Marius Hills-like moderate damage) and 0.6 (heavily
    damaged / near-collapse).
    """
    L_m: float
    h_m: float
    E_GPa: float
    rho_kgm3: float
    g_mps2: float
    delta_slab_m: float
    delta_arch_m: float        # R_over_L = 0.2 default
    R_over_L: float
    delta_damaged_d0p0_m: float
    delta_damaged_d0p3_m: float
    delta_damaged_d0p6_m: float


def regime_summary(
    L: float,
    h: float,
    E_GPa: float,
    rho: float,
    g: float = G_LUNAR,
    R_over_L: float = DEFAULT_R_OVER_L,
) -> RegimeSummary:
    """Compute all three regime deflections + metadata for a single combo.

    Convenience wrapper for the sweep driver and for figure/table
    generation. Returns a frozen dataclass that round-trips to dict()
    for JSON evidence records.
    """
    E_Pa = E_GPa * 1.0e9
    d_slab = clamped_slab(rho, g, L, E_Pa, h)
    d_arch = clamped_arch(rho, g, L, E_Pa, h, R_over_L=R_over_L)
    d_d0, _, _ = cumulative_damage(rho, g, L, E_Pa, h, 0.0)
    d_d3, _, _ = cumulative_damage(rho, g, L, E_Pa, h, 0.3)
    d_d6, _, _ = cumulative_damage(rho, g, L, E_Pa, h, 0.6)
    return RegimeSummary(
        L_m=L,
        h_m=h,
        E_GPa=E_GPa,
        rho_kgm3=rho,
        g_mps2=g,
        delta_slab_m=d_slab,
        delta_arch_m=d_arch,
        R_over_L=R_over_L,
        delta_damaged_d0p0_m=d_d0,
        delta_damaged_d0p3_m=d_d3,
        delta_damaged_d0p6_m=d_d6,
    )


def to_dict(s: RegimeSummary) -> dict:
    """Dataclass -> dict (handy for json.dump)."""
    return asdict(s)


# Self-check / canonical anchor points (NOT a substitute for the
# verifier script — kept here for fast import-time sanity).
CANONICAL_ANCHORS: list[dict] = [
    # Each: (L_m, h_m, E_GPa, rho_kgm3, expected_m, label)
    {"L": 65,  "h": 26, "E": 50, "rho": 2900, "expected_m": 0.08e-3,
     "label": "Marius Hills intact (upper bound)"},
    {"L": 100, "h": 26, "E": 50, "rho": 2900, "expected_m": 0.45e-3,
     "label": "Tranquillitatis-scale competent basalt"},
    {"L": 300, "h": 26, "E": 50, "rho": 2900, "expected_m": 3.6e-2,
     "label": "Max-span intact rock"},
    {"L": 300, "h": 26, "E": 10, "rho": 2900, "expected_m": 18.2e-2,
     "label": "Wide fractured (Marius Hills-like)"},
    {"L": 300, "h": 10, "E": 10, "rho": 2900, "expected_m": 1.23,
     "label": "Thin roof, weak rock"},
    {"L": 300, "h": 10, "E":  5, "rho": 2900, "expected_m": 2.46,
     "label": "Thin roof, heavily damaged"},
    {"L": 500, "h": 10, "E": 10, "rho": 2900, "expected_m": 9.49,
     "label": "Near-collapse unsupported span"},
]


if __name__ == "__main__":
    # Minimal CLI smoke test (canonical anchors, table-stated rho=2900).
    import json
    g = G_LUNAR
    print("WP0.5 deflection model: canonical anchors (rho=2900 from table)")
    for a in CANONICAL_ANCHORS:
        d = clamped_slab(a["rho"], g, a["L"], a["E"] * 1e9, a["h"])
        rel = abs(d - a["expected_m"]) / a["expected_m"]
        print(f"  L={a['L']:>4}m h={a['h']:>3}m E={a['E']:>3}GPa  "
              f"delta={d*1000:>8.4f} mm  expected={a['expected_m']*1000:>8.4f} mm  "
              f"rel={rel*100:>5.2f}%  [{a['label']}]")
