# Session 2 (2026-08-19) — Z0 close-out + Z1/Z2/Z3 staging

This note captures the second agent session's work in a single
human-readable document. It supplements the CHANGELOG (which records
the same events in a strict timeline).

## What was done in this session

### 1. Task 9 — Scope map v1.1 (Hurwitz + craters added)

Script: `01_WORKSPACE/code/wp0_scope_map/scope_map_v11.py`

Key learnings (encoded in the module):
- Hurwitz shapefile CRS is Moon equirectangular with central meridian
  180 in metres; reprojection to geographic lon/lat must use a Moon
  sphere (R=1737400), not Earth's EPSG:4326 (PROJ refuses Moon→Earth
  by default; workarounds are PIT_DISABLE_CELESTIAL_BODY=1 or explicit
  proj4 strings).
- `gpd.sjoin_nearest` warns when input is geographic; for v0.2 use a
  projected frame.
- Pit-Crater matching: DTM_NAME != DTM (the atlas attribute is a
  subset of the full join).

Outputs:
- `data/outputs/wp0_scope_map_v11/rille_dtms_intersect.csv`
  (10 DTMs with rilles, MARIUSCONE has 6 segments / 2 unique rilles)
- `data/outputs/wp0_scope_map_v11/crater_density_per_dtm.csv`
  (4.45M craters; median 0.10 craters/km^2 across DTMs; max 3.06)
- `data/outputs/wp0_scope_map_v11/target_ranking.csv`
  (top target: MARIUSCONE flagship site with 23.95 score)
- `plans/figures/wp0_scope_map_v11_overview.png` + `_rille_density.png`

### 2. Phase Z1 — LLTB-1 modules (all 5 written, awaiting a real RAR)

| Module | File | Tested? |
|---|---|---|
| f32 reader | `code/wp1_lla/convert_f32.py` | synth (smoke test) |
| degradation ladder | `code/wp1_ladder/degrade.py` | synth (smoke test) |
| VCI detector | `code/wp1_detector/vci.py` | synth (smoke test, 0/0.4% cells) |
| sag detector | `code/wp1_detector/sag_detect.py` | synth (smoke test, F1=0.39→0.80) |
| LLTB-1 loader | `code/wp1_lla/lltb1.py` | import + load from smoke test |
| End-to-end driver | `code/wp1_lla/run_lltb1.py` | written; awaits first RAR |
| Paper 1 skeleton | `papers/paper1_resolution_limits/main.md` + `outline.md` | written |

Notable design decisions:
- Sink-fill engine: Planchon-Darboux (epsilon fill). Wang & Liu
  drains the NoData floor in shadowed pit interiors. v5 WP0 Task 3
  log has the full variant table.
- VCI: Shannon evenness of height-binned column distribution
  (I8). Code is at 0/0.4% VCI on a 2.5D synthetic (as expected:
  VCI only spikes where the cloud is genuinely 3D within a column;
  a rasterised surface gives VCI ≈ 0).
- Sag detector score: depth * Frangi(30-300 m) — Frangi with
  `black_ridges=True` so a void (low Z) is "dark".
- Per-rung threshold re-tuning (I9) on a 50/50 random split, seed 42.
- FP/10^4 km² reported as the primary false-positive rate (v5
  Section 9 mandatory reporting).

### 3. Phase Z2 — lunar sag search + confusion layer (both written)

| Module | File | Notes |
|---|---|---|
| Sag search | `code/wp2_sag/sag_search.py` | Reuses kriging + Planchon-Darboux + Frangi; emits per-candidate CSV |
| Confusion layer | `code/wp2_sag/confusion_layer.py` | 5-class rasters (rille, chain, ridge, graben, bg); MARIUSPIT01 has 1795 rille cells |

Tested on TRANQPIT1, MARIUSPIT01, INGENIIPIT; outputs in
`data/outputs/wp2_sag/confusion/`.

Deferred:
- I5 azimuth test (needs multi-illumination NAC CDRs)
- SLDEM2015 normalisation (Step 18.1 detail — v5 says normalise
  against SLDEM, not self-fitted; deferred to v0.2 since the kriging
  output is the natural starting point for v0.1)
- Multi-illumination stacking (Task 19) — blocked by Task 18.

### 4. Phase Z3 — fusion prototype (CPU, GRAIL done, Diviner placeholder)

| Module | File | Status |
|---|---|---|
| Evidence layers | `code/wp3_fusion/evidence_layers.py` | working |
| Fusion | `code/wp3_fusion/fusion.py` | written + smoke test PASS |

GRAIL evidence layers:
- Parses GRGM1200A coefficient table (l_max=680 in current file)
- Overrides the file's non-standard GM/R header with the published
  Konopliv 2013 Moon constants: GM=4.9048695e12 m^3/s², R=1737.4 km
- Evaluates gr_r + gr_theta + gr_phi via `pyshtools.expand()` +
  `boule.Moon2015`
- Finite-differences the gradient magnitude (note: this is NOT the
  full gravity gradient tensor; that's a v0.2 addition)
- Successful MTP-region run: gr_r 1.62-1.67 m/s², Gmag 1e-8 Eotvos

Diviner placeholder: metadata JSON only; full Powell 2023
derivative needs the PDS Geosciences REST query plumbing (~half a
day, deferred).

Fusion:
- Per-feature z-score normalisation
- LogisticRegression(class_weight='balanced') on each feature
  + 1 fused model
- Metrics: AUC, F1, P, R, Brier; ROC + 10-bin reliability figure
- Smoke test result: depth AUC 0.991, FUSION AUC 0.990 (depth
  dominates this synthetic; in real data the additional streams
  should add value)

### 5. Smoke test (`code/smoke_test.py`)

Exercises the whole pipeline on a 200x200 synthetic cloud with a
4m-radius void 5m below flat ground:
- 156 void cells (0.4%) — correct
- Per-rung F1: 0.39 (0.5 m) → 0 (2 m, threshold collapses) → 0.80
  (5 m — void visible at coarse res)
- Fusion AUC 0.990 (depth signal dominates)

This catches wiring bugs. Re-run after any module change.

## What's left for the next session

| Priority | Item | Why |
|---|---|---|
| High | Wait for analog RARs to finish, then run LLTB-1 v0.1 end-to-end on a real site | produces the first real LLTB-1 deliverable for Paper 1 |
| High | Run `sag_search.py` end-to-end on TRANQPIT1 + the 7 other covered DTMs | produces the first real candidate CSV |
| Med  | LLTB-1 I12 independent confound covariates (LOLA track density, NAC image count per tile) | per v5 mandatory reporting |
| Med  | I5 sun-azimuth sector test on TRANQPIT1 (needs at least 2 NAC CDRs of same site, different illumination) | per v5 I5 |
| Low  | Diviner full ingestion via Powell 2023 derivative | completes the evidence hierarchy |
| Low  | Local ISIS+ASP reproduction attempt (Task 8) | the v5 cost-boundary experiment |
| Low  | PU learning baseline + conformal calibration (Z3.2, 21.2) | the honest-uncertainty deliverable |
| Low  | Hapke photometry + NAC sensor noise (Z1.3, 13.3) | the lunar-realism deliverable |

## Files added this session

```
01_WORKSPACE/code/wp0_scope_map/scope_map_v11.py
01_WORKSPACE/code/wp1_lla/convert_f32.py
01_WORKSPACE/code/wp1_lla/lltb1.py
01_WORKSPACE/code/wp1_lla/run_lltb1.py
01_WORKSPACE/code/wp1_lla/paper1_skeleton.py
01_WORKSPACE/code/wp1_ladder/degrade.py
01_WORKSPACE/code/wp1_detector/vci.py
01_WORKSPACE/code/wp1_detector/sag_detect.py
01_WORKSPACE/code/wp2_sag/sag_search.py
01_WORKSPACE/code/wp2_sag/confusion_layer.py
01_WORKSPACE/code/wp3_fusion/evidence_layers.py
01_WORKSPACE/code/wp3_fusion/fusion.py
01_WORKSPACE/code/smoke_test.py
01_WORKSPACE/notes/2026-08-19_session2_summary.md  (this file)
01_WORKSPACE/papers/paper1_resolution_limits/main.md
01_WORKSPACE/papers/paper1_resolution_limits/outline.md
```

Outputs:
```
01_WORKSPACE/data/outputs/wp0_scope_map_v11/{rille_dtms_intersect.csv, crater_density_per_dtm.csv, target_ranking.csv}
01_WORKSPACE/data/outputs/wp2_sag/confusion/confusion_*.{tif,json,png}
01_WORKSPACE/data/outputs/wp3_fusion/MTP/{grail_*.tif,grail_gradients_overview.png,diviner_placeholder.json,evidence_layers_summary.json}
/tmp/ll_smoke/{synthetic_cloud.npz,ladder/,sag/,smoke_summary.json}
```

## What was BROKEN and is now fixed

1. `sag_detect.cloud_ground_truth` was using a 5x5 minimum filter for
   the local envelope, which equals the per-cell min for a flat cloud
   with a single void. Fixed to a 21x21 nan-robust median envelope
   (5-10x the largest expected void cell).
2. Same bug existed in `fusion.cloud_ground_truth` (a copy of the
   same function). Fixed identically.
3. `evidence_layers.py`:
   - The GRAIL coefficient parser was whitespace-splitting a
     comma-delimited file. Switched to `csv.reader`.
   - The pyshtools 4.x API uses `from_array()` instead of the
     positional constructor; switched.
   - The pyshtools axis layout is `coeffs[i, l, m]` with `i=0 -> Clm`
     and `i=1 -> Slm`; was previously putting both in `i=0`.
   - The PDS shadr file's header GM/R values are in non-standard
     units; overrode with the published Konopliv 2013 Moon constants.
   - `grav.tensor()` returns a 2D map of the full tensor (not pointwise);
     use `grav.expand(lat, lon, r)` for pointwise gravity vector, then
     finite-difference the gradient magnitude.
   - `expand()` requires `r` to be an array (one entry per point), not
     a scalar.
4. `sag_search.py` had `class A: pass` instead of `argparse.Namespace`;
   fixed.

## Open file-process handles worth knowing

| Process | PID (was) | Status |
|---|---|---|
| ISIS+rclone LRO data pull | 719001, 719014 | background, idle (rclone running) |
| GRAIL download (curl) | 826562 | killed (file is complete at 36 MB) |
| Analog downloads (4) | 826479, 826516, 826673, 826708 | still running |

## Cost

$0.00 (per v5 cost-boundary rules). Local compute + public data
downloads only. Colab/Kaggle GPU tiers not yet invoked.
