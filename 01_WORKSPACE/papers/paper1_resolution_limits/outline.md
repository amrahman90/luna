# LLTB-1 Paper 1 — figure and table outline

| Tag | Type | Source | Purpose |
|-----|------|--------|---------|
| F1  | Figure | `data/outputs/wp1/detectability_curve.png` (auto) | P(detect) vs GSD; headline result |
| F2  | Figure | `data/outputs/wp1/vci_overview.png` (auto) | VCI histogram + raster, best site |
| F3  | Figure | `data/outputs/wp1/sag_panels_<rung>m.png` (auto, per rung) | depth, Frangi, score, hillshade per rung |
| F4  | Figure | (built) | F1 vs feature-size quartiles (I11) |
| T1  | Table  | `data/outputs/wp1/per_rung_metrics.csv` (auto) | GSD, threshold, F1, P, R, FP-cell density (CSV col `fp_per_1e4km2_test`; predict-all tile extrapolation, not a survey rate — lunar FP per 10⁴ km² NOT MEASURED) |
| T2  | Table  | (built) | VCI detection stats by site |
| T3  | Table  | (built) | failure modes (I14) - per-site classification |

## Build order
- All F1, F2, F3, T1 are produced by `code/wp1_lla/run_lltb1.py`.
- F4, T2, T3 added in v0.2.

## v0.5 additions (Task 16.3, 2026-08-22)

- Committed-artifact figure set (10 copies) indexed in
  `figs/README.md`: ladder (hapke grid, sensor preview), wp0
  (kriging ×2, noise floor, pit recovery, depth check), scope map
  v1.1 ×2, analog registration. No new computation.
- §4.5 of main.md: illumination × sensor degradation narration
  (Table 2 composed arms). New tags: F5 = hapke grid, F6 = sensor
  preview, T4 = composed degradation table.
