# Task 3 (Z0.2) — TRANQPIT1 depression-depth primitive: fill-engine comparison log

Date: 2026-08-19. DTM: `NAC_DTM_TRANQPIT1.TIF` (2372 x 14388 px, 2 m/px,
local equirectangular, sphere R=1737400 m, lat_ts=8, lon_0=180).
Acceptance: max sink-fill depth > 50 m within 200 m of MTP
(8.3355 N, 33.2220 E; pit pixel row 8005, col 1612).

## Root cause of the initial Wang & Liu failure

The pit interior is largely **NoData** in the DTM: photogrammetry fails on
the shadowed floor (rim ~ -780 m; the few valid floor pixels reach
-912 m, surrounded by a NoData blob of ~2500 px inside the 120x120 m
center). WhiteboxTools' Wang & Liu fill and the least-cost breach treat
NoData cells as free drains, so the pit never ponds: water "escapes"
through the shadow gap instead of spilling over the rim.

## Variant results (max depth within 200 m of pit)

| Engine (WhiteboxTools call) | Pit max depth | Verdict |
|---|---|---|
| `fill_depressions` (Wang & Liu, fix_flats=True) — roadmap default | 3.18 m | FAIL (drains via NoData) |
| `breach_depressions_least_cost` (dist=50, fill=True) | 0.34 m | FAIL (breaches the rim outright) |
| `fill_missing_data` (void fill) -> Wang & Liu fill | 5.19 m | FAIL (interpolation bridges the pit shallowly) |
| **`fill_depressions_planchon_and_darboux` (epsilon fill, fix_flats=True)** | **129.67 m** | **PASS** |

Chosen engine: **Planchon-Darboux epsilon fill**, now the default in
`01_WORKSPACE/code/wp0_primitive/depression_depth.py`.

The recovered 129.67 m exceeds the catalogued ~105 m because the few valid
floor pixels (-912.3 m) fill up to the local spill point (-782.6 m);
sink-fill depth is a lower-bound-of-depth / upper-bound-of-fill measure,
not a pit-depth measurement — consistent with the v5 "inference, with
error bars" framing.

## False-positive spot check (criterion 2)

Flattest 1x1 km panel (median slope 1.862 deg from DTM gradient), center
8.0555 N / 33.1646 E, 8.7 km from the pit: max depth **8.13 m** < 30 m.
PASS. (Small sub-30 m sinks on nominal mare are expected noise/thermal
contraction craters, not pit-scale FPs.)

## Implications for Task 4 (8-pit sweep)

- Use the PD engine for all tiles; if a pit still fails, check for the
  NoData-drain pattern (confidence map) before concluding funnel geometry
  (pre-registered failure mode I14).
- Pit-interior NoData means recovered depth samples the *valid-pixel*
  floor, not the true floor — record per-pit NoData fraction alongside
  recovered depth in `pit_recovery_table.csv`.
