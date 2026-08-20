# LLTB-1 Paper 1 — figure and table outline

| Tag | Type | Source | Purpose |
|-----|------|--------|---------|
| F1  | Figure | `data/outputs/wp1/detectability_curve.png` (auto) | P(detect) vs GSD; headline result |
| F2  | Figure | `data/outputs/wp1/vci_overview.png` (auto) | VCI histogram + raster, best site |
| F3  | Figure | `data/outputs/wp1/sag_panels_<rung>m.png` (auto, per rung) | depth, Frangi, score, hillshade per rung |
| F4  | Figure | (built) | F1 vs feature-size quartiles (I11) |
| T1  | Table  | `data/outputs/wp1/per_rung_metrics.csv` (auto) | GSD, threshold, F1, P, R, FP/10^4 km^2 |
| T2  | Table  | (built) | VCI detection stats by site |
| T3  | Table  | (built) | failure modes (I14) - per-site classification |

## Build order
- All F1, F2, F3, T1 are produced by `code/wp1_lla/run_lltb1.py`.
- F4, T2, T3 added in v0.2.
