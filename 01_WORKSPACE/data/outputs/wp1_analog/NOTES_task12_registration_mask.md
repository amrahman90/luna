# WP1-analog Task 12.1 + 12.2 — Indian Tunnel entrance-trench + skylight mask (2026-08-21; relabelled 2026-08-22 after skeptic review)

## What was produced

- **12.1 registration**: cave-interior cloud (NASA Pits & Caves analog
  dataset, Wong/Whittaker/Jones/Whittaker 2014; `IndianTunnel_full_1x.f32`,
  116.2 M pts) registered into the `Indian_NorthSurface_1x` scanner frame
  (61.0 M pts) — the frame/grid of the LLTB-1 ladder site
  `IndianTunnel_NorthSurface` (master_0.5m.tif, 131x250 @ 0.5 m).
- **12.2 entrance-trench + skylight mask** (NOT roofed-void ground truth;
  in-window roofed-void cells = 5 / 1.25 m²): ground-projected occupancy of
  the registered cloud on that exact grid ->
  `entrance_trench_skylight_mask.tif` + GeoJSON footprint + stats + PNG.

## Method (deterministic, seed 42)

1. **Coarse**: yaw sweep 0-358 deg step 2 deg, XY-translation seeded by FFT
   cross-correlation of 0.5 m occupancy bitmaps, scored by 3D NN inliers
   (<1 m) via cKDTree. Best: yaw 102 deg, d=(-2.0, 4.5, -0.20) m, 15.1 %
   inliers. (Collapse3 anchor found too: yaw 248 deg, 20.3 % — unused.)
2. **ICP**: scipy trimmed point-to-plane (Open3D NOT in venv — documented;
   CloudCompare absent). I1 parameters: overlap 90 %, rigid only
   (adjust-scale OFF), stop |dRMSE|<1e-7 (hit 100-iter cap), correspondence
   cap 2.0->0.25 m. 0.15 m voxel clouds (342 k src / 234 k dst).
3. **Mask**: occupancy of registered cloud (0.05 m voxel, 2.84 M pts) in the
   DTM grid; binary closing 3x3; drop components <5 cells. Open-vs-roofed
   split via interior ceiling (points strictly below the mapped surface
   band, z < DTM-0.5 m): open = no interior points or roof <1 m.
4. **Deg-sign convention**: positive yaw = clockwise when viewed from +z;
   the coarse seed 102° ≡ −102° in the ICP frame, ICP final net yaw
   −106.6° (registration_report.json `net_yaw_deg`).

## Headline numbers

- Registration: coarse RMS(<2 m) 0.884 -> ICP trimmed RMS **0.139 m** at
  0.25 m cap (8,955 correspondences). Dense eval (755 k pts @ 0.10 m voxel):
  <1 m inliers 70,118 (9.3 %), RMS 0.490 m; <0.5 m inliers 44,602 (5.9 %),
  RMS 0.284 m. **Registration gate statistic = the DENSE eval (9.3 %
  inliers <1 m, RMS 0.490 m), NOT the 0.139 m trimmed ICP RMSE (2.6 %
  correspondences, 100-iter cap).** **Sub-metre: PASS. Roadmap's <0.1 m:
  NOT reached** — shared geometry is entrance-area only (both scanners at
  the north entrance; 62 % of the cave cloud lies outside the DTM window),
  two different scanners/epochs, 0.15 m ICP voxel. Reported honestly.
- Mask: 2,055 cells = **513.75 m²** (raw occupancy 544 m²), 6.27 % of DTM
  extent = 16.6 % of valid DTM (2,055/12,402). The 9.28 % figure is the
  share of VALID DTM cells overlapping the cave cloud footprint
  (1,151/12,402), NOT "of the mask". Corridor in-window: 50.6 m long,
  width median 9.5 m / p90 13.5 m / max 14.5 m; 3 open-cell clusters;
  in-window corridor is an OPEN entrance trench (1,146/1,151 cells with DTM
  are open; floor <=1.8 m below surface) — the roofed tube continues
  outside the NorthSurface window.

## Sanity check vs known alignment (citation)

Dataset page (Wong et al. 2014, `~/lunarvoid/data/analog/index.html`;
research/academic use only): Indian Tunnel ">10 m in diameter and 250 m
long", "numerous collapses and skylights", "portions ... were mapped in
August 2014" from El Malpais (Blue Dragon Flow). Observed: width p90/max
13.5/14.5 m (>=10 m), elongate single corridor, 3 skylight/entrance
clusters in-window. NPS El Malpais (https://www.nps.gov/elma/index.htm,
public domain) confirms lava tubes at El Malpais incl. accessible Indian
Tunnel (open-entrance character). NOTE: the dataset carries NO absolute
georeferencing (scanner-local frames), so the check is morphological +
ICP residual based; no map overlay is possible.

## Bugs found & fixed this session

1. `wp1_ladder/degrade.py cloud_to_master_grid`: `np.add.at` into a
   NaN-initialised accumulator -> every master/rung raster silently
   all-NaN (summary "valid_frac" counted cnt>0, masking it). Fixed
   (zero-init + NaN-mask); NorthSurface rungs regenerated (40 % valid);
   `smoke_test.py` PASS (F1 0.392/0/0.800, fusion AUC 0.990 — known-good).
2. Same NaN-accumulation bug class reproduced in make_void_mask.py during
   development (np.maximum.at into NaN array) — caught and fixed before
   final outputs.

## Files

- code: `01_WORKSPACE/code/wp1_analog/{io_analog,coarse_search,icp,register_cave,make_void_mask,explore_indian_tunnel}.py`
- registration outputs (repo): `data/outputs/wp1_analog/registration/`
  (coarse_search.json, registration_report.json, registration_validation.png,
  preflight_clouds.png)
- mask outputs (repo): `data/outputs/wp1_analog/void_mask/`
  (entrance_trench_skylight_mask.tif, entrance_trench_skylight_mask_footprint.geojson,
  entrance_trench_skylight_mask_stats.json, entrance_trench_skylight_mask_preview.png
  1920x1080; renamed from void_mask_gt.* / void_footprint.* on 2026-08-22)
- raster-scale data (outside repo): `~/lunarvoid/data/outputs/wp1_analog/indian_tunnel_cave_registered_to_NorthSurface.npz`

## Grid convention warning (inherited)

degrade.py fills rows south-to-north (row 0 = y_min) but writes a
north-up from_bounds transform; ALL ladder/sag rasters share this
array-space convention. The entrance-trench + skylight mask follows it
(documented in entrance_trench_skylight_mask_stats.json). North-up GIS
readers will show these rasters y-flipped unless transposed.

## GUARDRAILS (skeptic review, 2026-08-22)

This mask must NOT be used as ground truth for sag-rung F1 in LLTB-1
v0.5; NorthSurface cave rungs are reported separately from the v0.4
table; scale caveat: 0.49 m dense RMS ≈ half a 1 m cell — corridor
morphology informative, 1-2 m sag F1 not quantitatively transferable.
