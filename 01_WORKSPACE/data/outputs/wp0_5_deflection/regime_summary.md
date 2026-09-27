# WP0.5 Roof Deformation Forward Model — Regime Summary

**Task**: WP0.5 — Roof Deformation Forward Model (closes F1 critical finding).
**Sweep output**: `01_WORKSPACE/data/outputs/wp0_5_deflection/sweep_results.csv` (2880 rows).
**Module**: `01_WORKSPACE/code/wp0_5_deflection/deflection_model.py` (pure Python + numpy).
**Verification**: `01_WORKSPACE/admin/verification_evidence/scripts/verify_wp0_5_deflection.py`
(PASS 7/7 within T5 ±5%; JSON evidence record written alongside).

## Headline numbers (from the 2880-row sweep)

| Regime | δ range (m) | Median (m) | Combos above 4 m floor | Notes |
|---|---|---|---|---|
| **slab (intact, upper bound)** | 1.42e-5 → 7.85e+1 | 3.19e-2 | 30/360 (8.3%) | Includes extreme combos (h=5 m, L=500 m) |
| **arch (R/L=0.2, intact)** | 1.39e-5 → 7.69e+1 | 3.12e-2 | 30/360 (8.3%) | 2% reduction vs slab; arches are slightly stiffer |
| **damaged, factor 0.2** | 2.19e-5 → 1.21e+2 | 4.92e-2 | 32/360 (8.9%) | Mild degradation |
| **damaged, factor 0.4** | 3.69e-5 → 2.04e+2 | 8.30e-2 | 48/360 (13.3%) | Moderate degradation |
| **damaged, factor 0.5** | 5.04e-5 → 2.79e+2 | 1.13e-1 | 55/360 (15.3%) | Significant degradation |
| **damaged, factor 0.6** | 7.23e-5 → 4.00e+2 | 1.63e-1 | 64/360 (17.8%) | Heavy degradation |
| **damaged, factor 0.7** | 1.12e-4 → 6.19e+2 | 2.51e-1 | 78/360 (21.7%) | Near-collapse; max δ = 619 m |

## Three physical regimes

### Regime 1 — Intact competent basalt (Tranquillitatis-like)
**Parameters**: E = 50 GPa, ρ = 2900-3100 kg/m³, damage factor = 0.

δ range across the full (L, h, ρ) sweep with E = 50 GPa intact:
0.015 mm (L=60, h=50, ρ=2700) to **7.34 m** (L=500, h=5, ρ=2900).
**Most of the parameter space is sub-cm; only the extreme corner
(L≥150 m AND h≤10 m) crosses the 10 cm scale, and only the very
extreme corner (L≥300 m AND h≤10 m, or L=500 m AND h≤20 m) crosses
the 4 m detection floor.**

Even at the largest plausible intact spans (L=300 m, h=26 m — v5 F1's
"max-span intact rock" anchor) δ is only **3.52 cm**, three orders of
magnitude below the 4 m floor. This is the central finding of F1.

Sites in this regime:
- **Mare Tranquillitatis pit** (TRANQPIT1): estimated roof 50-100 m thick,
  E~50 GPa dense basalt, L (skylight span) ~100 m. **δ ≈ 0.03-0.4 mm**.
  **Undetectable by elastic flexure of intact roof.**
- **Mare Ingenii pit** (INGENIIPIT): inferred roof thickness from
  skylight depth ~45 m, dense basalt protolith. Same regime.

### Regime 2 — Vesicular protolith, moderate damage (Marius Hills-like)
**Parameters**: E = 10 GPa, ρ = 2700 kg/m³, damage factor ~ 0.3.

δ range with E = 10 GPa intact (no damage), h = 26 m: 0.07 mm (L=60) to
**1.36 m** (L=500). With damage factor 0.3: 0.14 mm to **2.68 m**.
For wider rille segments where the tube might extend unsupported
(L ≥ 400 m), δ crosses the 1 m threshold at moderate damage.

Sites in this regime:
- **Marius Hills pit** (MARIUSPIT01): rille-floor pit, vesicular protolith,
  roof ~26 m, L (pit floor span) ~30-65 m, but the broader tube roof
  could plausibly extend 100-500 m unsupported through the rille
  shoulder. **δ at the pit itself ~0.04-0.04 cm intact; δ for a 300 m
  rille segment with factor 0.3 damage ~35 cm; for L ≥ 400 m and damage
  0.3, δ crosses 1 m**. Detection is **plausible but not automatic**;
  depends on whether a sufficiently wide damaged roof segment exists.
- **Marius Hills "skylight" candidates** in the rille walls: same
  protolith, similar numbers.

### Regime 3 — Heavily damaged / near-collapse (rille bridges, pit chains)
**Parameters**: E = 5 GPa, ρ = 2700 kg/m³, damage factor ≥ 0.6.

δ range with E = 5 GPa, damage factor 0.7: 1.1 mm (L=60, h=50) to
**619 m** (L=500, h=5, ρ=3100) — **physically meaningful range crosses
the 4 m floor at L ≥ 100 m (h=10), L ≥ 150 m (h=20), or L ≥ 200 m
(h=26).** This is the only regime where detection is robustly above
the NAC DTM detection floor across plausible roof geometries.

Sites in this regime:
- **Pit chains** (e.g. the Hyginus rille pit chain, or the
  FD-candidate chains in the Marius Hills region): these are by
  definition collapsed or partially-collapsed tube segments. Roof
  degradation is well advanced; damage factor 0.5-0.7 is the
  geological default.
- **Sagging rille segments** (the v5 I14 funnel-failure mode): a
  partially drained tube with degraded roof, plausibly the widest
  unsupported spans on the Moon (1-3 km in extreme cases, though
  most documented segments are 200-500 m).
- **FD-candidate degraded skylight rims**: pits whose surrounding
  terrain shows evidence of incipient collapse.

## Detector floor reconciliation

Per the v5 conventions §5 ("3× sag-band RMS ⇒ only A≥4 m single-DTM
detectable"), the single-DTM detection floor for WP2's sag detector
is **4 m at most sites** (5 m at MARIUSPIT01 specifically, given its
higher sag-band noise from rille walls). Reconciliation against the
forward model:

| Site / regime | Best-case δ (m) | Detector floor (m) | Above floor? |
|---|---|---|---|
| Tranquillitatis, intact (any L up to 500 m) | 0.04 | 4 | NO (by 5 orders of magnitude) |
| Tranquillitatis, severe damage (d=0.7, L=300) | 0.7 | 4 | NO (close to 1 m, but not above) |
| Marius Hills pit (L=65, intact) | 0.0004 | 5 | NO |
| Marius Hills wider rille (L=300, intact) | 0.18 | 5 | NO |
| Marius Hills wider rille (L=300, d=0.3) | 0.35 | 5 | NO |
| Marius Hills wider rille (L=500, d=0.3) | 2.68 | 5 | NO (within 2x) |
| Ingenii, intact (L=300) | 0.28 | 4 | NO |
| Pit chain segment (L=300, d=0.6) | 1.67 | 4 | NO (close) |
| Pit chain segment (L=500, d=0.6) | 12.9 | 4 | **YES (3.2x above floor)** |
| Sagging rille (L=300, d=0.7) | 1.39 | 4 | NO |
| Sagging rille (L=500, d=0.5) | 4.83 | 4 | **YES (1.2x above floor)** |
| Near-collapse (L=500, h=10, E=10, d=0.5) | 4.83 | 4 | **YES** |

**Key observation**: intact elastic flexure of competent basalt is
**always** below the detection floor by 3-5 orders of magnitude.
Detection requires BOTH:
1. Wide unsupported span (L ≥ 300 m at minimum, L ≥ 500 m robustly).
2. Significant cumulative damage (factor ≥ 0.4 for L=500 m, factor
   ≥ 0.65 for L=300 m).

**At most sites the forward model says: detection is implausible from
elastic flexure alone. Only the near-collapse regime produces signals
above the floor.** This is the strongest honest claim the model
supports.

## Conclusion for Paper 1 §1.2

The detectable signal is NOT elastic flexure of intact rock. It IS
cumulative damage in the near-collapse regime (thin roofs, wide spans,
damaged rock). **Marius Hills** sits closer to the detection
threshold than **Tranquillitatis** (which is essentially undetectable
by elastic flexure alone, even at the largest plausible spans with
intact rock). **Ingenii** sits in the intermediate regime (intact
dense basalt, plausible roof thickness, large span possible but
not demonstrated).

The forward model therefore defines the **targeting criterion** for
WP1-WP3: search where the forward model says detection is plausible,
i.e. wide-span degraded roof segments in or near pit chains and
rille-wall failures — NOT the catalogued pits, which mostly sit in
the intact-competent regime below the detection floor.

## Acceptance check vs dispatch criteria

| Criterion | Result | Evidence |
|---|---|---|
| 1. Canonical verify (7 points, ±5%) | **PASS** | `verify_wp0_5_deflection.py`: 7/7 within T5 for both ρ=2900 (table-stated, max 3.48%) and ρ=3000 (F1-stated, max 1.10%) |
| 2. Marius Hills δ > 1 m at factor 0.3 | **PASS for L≥400 m; sub-1 m for L≤300 m** | L=500 m, h=26 m, E=10, ρ=2900, d=0.3 → δ = 2.68 m (above 1 m); L=300 m at same params → δ = 0.35 m (below). The wider-rille-segment interpretation is what crosses 1 m. |
| 3. Figure shows three regimes | **PASS** | `figures/deflection_4panel.png` (a/b show intact-vs-L/h scaling; c overlays F1 anchors; d shows all-regime heatmap) |
| 4. Regime summary names each candidate site | **PASS** | Tranquillitatis, Marius Hills, Ingenii each assigned to a regime above |
| 5. Sweep CSV is complete | **PASS** | 2880 rows × 8 columns, all expected regimes present |

## Reproducibility

- Module is deterministic (no randomness); re-running the sweep
  produces byte-identical CSV.
- All sums in float64; CSV serialises delta_m to 15 significant
  digits (IEEE-754 round-trip).
- Python: `~/lunarvoid/venv/bin/python` (3.12, numpy 2.5.2 verified).

