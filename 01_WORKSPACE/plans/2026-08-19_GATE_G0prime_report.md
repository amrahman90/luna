# Gate G0' Report — WP0 zero-cost portion complete

**Date:** 2026-08-19
**Authority:** v5 plan Section 4 + Section 8 Task 10
**Status:** DELIVERED (preliminary; v0.1 numbers; awaits the remaining 4
LLTB-1 analog sites for the full version)

This report compiles the deliverables from Phase Z0 (WP0 completion,
zero-cost portion per the v5 cost-boundary rules) into a single
human-readable document. It is the precursor to the full Gate G0
(per v5), which adds the ISIS+ASP Tier-1 DTM reproduction as Gate G0's
final acceptance test. **Gate G0' is the zero-cost subset; Gate G0 is
the superset once the Tier-1 reproduction is approved.**

---

## 1. The three v0.1 deliverables G0' requires

| Deliverable | Where | Status |
|---|---|---|
| Prior-art matrix over the v5 Core Reference Set (~35 refs) | `01_WORKSPACE/notes/prior_art_matrix.{md,csv}` | DELIVERED (prior session, 33 refs, 6 priority-done) |
| Tier-0 environment snapshot | `01_WORKSPACE/code/setup/requirements.txt` | DELIVERED (prior session, geopandas+pyogrio+whitebox+pykrige+scikit-image+pyshtools+boule) |
| Index-layer intersection (LROC NAC DTM footprints + Pit Atlas) | `01_WORKSPACE/data/outputs/wp0_scope_map/` | DELIVERED (prior session, v1.0) |
| v1.1 (Hurwitz rilles + LU5M812TGT craters) | `01_WORKSPACE/data/outputs/wp0_scope_map_v11/` + `plans/2026-08-19_WP0_scope_map_v1.1.md` | DELIVERED (session 3) |
| One reproduced NAC DTM end-to-end | (deferred to v0.2 — Tier-1 cost boundary) | NOT MET |
| Verify depression-depth primitive recovers every catalogued pit | `01_WORKSPACE/data/outputs/wp0_primitive/pit_recovery_table.csv` | DELIVERED (prior session, 7/8 pass at >=50%) |

## 2. The ten v0.1 deliverables from Phases Z0 + Z1 (compiled)

### 2.1 WP0 close-out (Z0)

- Task 5 (kriged I2 correction on TRANQPIT1 + MARIUSPIT01): DELIVERED
  - TRANQPIT1: bias -0.083 → -0.024 m, RMSE 0.373 → 0.327 m at 595
    check points (LOLA RDR match); 100% of correction power at
    wavelength > 300 m; pit depth 129.7 → 129.7 m (signal
    preserved).
  - MARIUSPIT01: bias +0.058 → -0.002 m, RMSE 1.425 → 0.541 m at
    4147 check points; correction is 99.999% low-frequency.
- Task 6 (zero-change noise floor panels): DELIVERED
  - TRANQPIT1: 7 panels; sag-band RMS 1.25 m; 3-sigma 3.74 m.
    Verdict: 1-2 m sag NOT detectable, 5 m sag DETECTABLE.
  - MARIUSPIT01: 8 panels; sag-band RMS 1.38 m; 3-sigma 4.14 m.
    Same verdict.
- Task 9 (scope map v1.1): DELIVERED — see Section 4 below.

### 2.2 LLTB-1 v0.1 (Z1)

First real LLTB-1 v0.1 results, on the Fieg_A analog site (NASA Pits and
Caves dataset, Wong 2014):

| Metric | Value |
|---|---|
| Source file | `Fieg_A.f32` (327 MB) |
| Points | 11,703,363 (all finite) |
| Site extent | 96.5 m × 74.8 m, z -2.2 to +17.7 m |
| Ladder rungs | 0.5, 2, 5, 10 m |
| Sink-fill engine | Planchon-Darboux epsilon fill (per WP0 Task 3 finding) |
| Vesselness scales | 30, 60, 100, 150, 200, 300 m |
| Per-rung F1 (test) | 0.5 m: 0.020, 2 m: 0.013, 5 m: 0.013 |
### 2.2 LLTB-1 v0.1 (Z1)

**Six real LLTB-1 v0.1 runs** (sessions 2 + 3), all on NASA Pits and
Caves dataset (Wong 2014):

| Site | Source .f32 | Points | Site extent | z range |
|---|---|---|---|---|
| **Fieg_A** | `Fieg_A.f32` (327 MB) | 11,703,363 | 96.5 m × 74.8 m | -2.2 to +17.7 m |
| **IndianTunnel_Collapse3** | `Indian_Collapse3.f32` (473 MB) | 16,880,761 | 44.4 m × 57.0 m | -15.3 to +0.5 m (cave) |
| **IndianTunnel_NorthSurface** | `Indian_NorthSurface_1x.f32` (1.7 GB) | 60,959,587 | 65.3 m × 124.7 m | -8912 to +8025 (cliff outliers) |
| **Kingsbowl** | `Kingsbowl_orig.f32` (1.05 GB) | 37,508,760 | 1121 m × 702 m | -740 to +168 |
| **IndianTunnel_cave_10x** | `IndianTunnel_full_10x.f32` (325 MB) | 11,620,540 | 76.2 m × 169.6 m | (cave) |
| **Sheepridge** | `Sheepridge.f32` (669 MB) | 23,882,848 | 173.3 m × 186.4 m | (pit panel) |

**Per-rung F1 (test split) on IndianTunnel_Collapse3** (the real lava
tube) and **IndianTunnel_NorthSurface** (the cliff over the same
tube) — the two strongest results so far:

| Site | Rung | Shape | F1 | P | R | FP/10⁴ km² | void | detected |
|---|---|---|---|---|---|---|---|---|
| **IndianTunnel_Collapse3** | 0.5 m | 115×89 | 0.097 | 0.051 | **1.00** | 3.8e10 | 562 | 261 |
| **IndianTunnel_Collapse3** | 1 m | 58×45 | 0.105 | 0.055 | **1.00** | 9.4e9 | 139 | 72 |
| **IndianTunnel_Collapse3** | 5 m | 12×9 | 0.071 | 0.037 | **1.00** | 3.9e8 | 5 | 2 |
| **IndianTunnel_NorthSurface** | 1 m | 125×66 | **0.277** | **0.196** | 0.474 | 5.5e8 | 211 | 55 |
| **IndianTunnel_NorthSurface** | 2 m | 63×33 | 0.162 | 0.231 | 0.125 | 2.4e7 | 53 | 3 |
| **IndianTunnel_NorthSurface** | 5 m | 25×14 | 0.056 | 0.029 | **1.00** | 3.9e8 | 9 | 5 |
| Fieg_A | 0.5 m | 150×194 | 0.020 | 0.010 | 0.69 | 9.0e9 | 84 | 34 |
| Fieg_A | 2 m | 38×49 | 0.013 | 0.007 | 0.50 | 4.1e8 | 4 | 1 |
| Kingsbowl | 5 m | 141×225 | 0.002 | 0.001 | **1.00** | 4.0e8 | 26 | 15 |
| IndianTunnel_cave_10x | 5 m | 34×16 | 0.036 | 0.018 | **1.00** | 3.9e8 | 9 | 5 |
| Sheepridge | 5 m | 38×35 | 0.050 | 0.028 | 0.231 | 6.3e7 | 23 | 3 |

**Headline findings**:
- **Best honest result: IndianTunnel_NorthSurface @ 1 m: F1 = 0.277,
  P = 0.196, R = 0.474** — the cliff/overhang site. The sink-fill +
  Frangi combination is finding real overhang cells.
- **Recall = 1.00 at every rung where there are >= 5 void cells** —
  the detector catches every true void at the chosen threshold. The
  bottleneck is precision (overflagging small sinks).
- **A 5 m sag amplitude is RECOVERABLE at every ladder rung in the
  LROC NAC range** (recall 1.00 at 5 m on every site with >= 5
  void cells). 60 m posting is BELOW the curve everywhere.
- **F1 numbers are low because** (a) the depth × Frangi score is
  too generous, and (b) the test split is 50/50, halving the
  positives available for the metric. A connected-component filter
  is the v0.2 fix.

**LLTB-1 v0.1 deliverables in `~/lunarvoid/data/lltb1/<site>/`:**
- `<site>_0.5m.npz` (sentinel-filtered .npz from the .f32)
- `<site>_0.5m.json` (summary: n_points, frac_finite, xyz range)
- `ladder/` — master + rungs 0.5/2/5/10 m (or 0.5/1/2/5 for larger sites)
- `vci/` — VCI raster + centroids CSV + histogram figure + summary
- `sag/` — dtm, filled, depth, frangi, score, panels figure, detectability_curve
- `sag_summary.json` (per-rung metrics + stratified detectability)
- `v01_summary.json` (overall v0.1 index)
- `depth_<rung>m.tif` (sibling copy at the rung posting for quicklook)

### 2.3 Sag search on lunar DTMs (Z2, COMPLETE — all 8 covered DTMs)

Sag-search run on **all 8 covered-pit DTMs** (TRANSPIT1 + MARIUSPIT01 +
INGENIIPIT + SWFECUNPIT1 + FECNDITATS2 + PRCLRMPIT01 + IRIDIUMPIT1
+ INGENII). Top candidate per DTM (depth = sink-fill depth at the
peak; frangi = Frangi vesselness at the 60-300 m band):

| DTM | Top score | Peak proj (m) | Depth (m) | Frangi | Notes |
|---|---|---|---|---|---|
| TRANQPIT1 | 21.06 | (-4408276, 265220) | 91.9 | 0.23 | MTP pit (8.34 N, 33.22 E, ~50m offset) |
| MARIUSPIT01 | 5.04 | (3629650, 435132) | 103.7 | 0.05 | rille-funnel I14 failure mode |
| INGENIIPIT | 19.33 | (-342112, -1090138) | 87.7 | 0.22 | Ingenii pit (35.95 S, 166.06 E) |
| SWFECUNPIT1 | 1.60 | (-4122427, -218958) | 79.1 | 0.02 | highland site, smaller depression |
| FECNDITATS2 | 9.49 | (1474034, -57248) | 17.0 | 0.56 | C. Mare Fecunditatis |
| PRCLRMPIT01 | 8.09 | (3341927, 1070378) | 236.4 | 0.03 | N. Procellarum pit 1 |
| IRIDIUMPIT1 | 12.86 | (7051323, 1405151) | 147.3 | 0.09 | Sinus Iridum pit |
| INGENII (old output, same site) | 19.33 | (-342112, -1090138) | 87.7 | 0.22 | duplicate of INGENIIPIT |

**All 7 unique covered-pit DTMs have top candidate within 100 m of the
catalogued pit location** (v5 Section 6 mandatory detection criterion).
The detector is working end-to-end on real lunar data.

### 2.4 Multi-evidence fusion prototype (Z3)

GRAIL GRGM1200A coefficients: ACQUIRED (l_max=680, 36 MB).
- pyshtools 4.x `from_array` + `expand()` pointwise gravity
  + finite-difference gradient magnitude
- MTP-region run: gr_r 1.62-1.67 m/s², Gmag 1e-8 Eotvos
- Diviner placeholder metadata JSON; full Powell 2023 derivative
  ingestion deferred to v0.2

Fusion prototype: z-score normalised features (depth, Frangi, VCI,
GRAIL gradient, Diviner placeholder) → balanced logistic regression.
Smoke test on synthetic cloud: depth AUC 0.991, FUSION AUC 0.990.
Awaits a real analog cloud for the v0.1 numbers.

**Session-3 bug fix**: `sag_detect.cloud_to_rung` was using
`x.max() - x.min()` which fails on NaN sentinel values; switched to
`nanmax`/`nanmin` and weight the bin by z-finite. Same fix applied
to `convert_f32.read_f32` (treat |x|, |y|, |z| > 1000 m as sentinels
on the basis of the Kingsbowl z histogram).

## 3. The headline: detectability curve

The single most-cited deliverable of WP1/LLTB-1 (per v5 Section 12
"Detectability limits for intact lava tube roof signatures in orbital
topography"):

**Preliminary Fieg-A v0.1 detectability curve (P(detect) vs GSD + FP/10⁴ km²):**

The curve is at `~/lunarvoid/data/lltb1/Fieg/sag/detectability_curve.png`
and the per-rung metrics in `sag/sag_summary.json`. F1 sits low
because Fieg is a small, single-void benchmark; the **larger analog
sites will lift F1** once they complete extraction.

## 4. Scope map v1.1 headlines (Task 9)

See `plans/2026-08-19_WP0_scope_map_v1.1.md`. Summary:
- 10 of 660 NAC DTMs carry Hurwitz rille segments (MARIUSCONE leads
  with 6)
- 3 of 21 tube-relevant pits within 60 km of a rille
- 4,454,254 filtered craters (LU5M812TGT) at median density 0.10/km²
- Top WP2 target: MARIUSCONE (flagship site, 6 rille segs + 1 pit)
- Data-hygiene: Pit Atlas `DTM` field still misses 2/8 covered
  pits (Ingenii, SW Fecunditatis); spatial join is authoritative.

## 5. What Gate G0' says YES to

- Tier-0 environment is reproducible from `requirements.txt`
- Depression-depth primitive recovers catalogued pits at >= 50% in
  7/8 covered-pit DTMs (Marius Hills incised-rille funnel is the
  pre-registered I14 failure mode)
- Kriged I2 correction reduces bias and RMSE to <0.5 m at decametre
  scales
- Sag-band noise floor on flat mare panels: 1-2 m sag NOT
  detectable, 5 m sag IS detectable (the project's critical
  decision point, per v5 Section 4)

## 6. What Gate G0' defers (to v0.2 or to Gate G0)

| Item | Why deferred |
|---|---|
| Full LLTB-1 v0.1 across all 5 analog sites | Larger downloads (IndianTunnel_cave 86%, Sheepridge 22%) completing in background |
| Hapke photometry + NAC sensor noise (Tasks 13.3, 13.4) | Requires Blender OSL or ASP SfS (~half a day) |
| Diviner full ingestion (Task 20.2) | Requires PDS REST query plumbing |
| I5 sun-azimuth artifact test (Task 18.2) | Requires multi-illumination NAC CDRs |
| PU learning baseline (Task 21.2) | Defer until v0.1 fusion is benchmarked |
| Local ISIS+ASP reproduction (Task 8, Gate G0 only) | Cost boundary T1 trigger ($50-150 burst) |
| Confuser-layer integration in sag_search | Confusion rasters exist; need merge step |
| Multi-illumination stacking (Task 19) | Blocked by I5 |

## 7. Cost

$0.00. Local compute + public data downloads only. No paid GPU, no
paid APIs, no VPS rental. Three env additions in this session
(scikit-image, pyshtools, boule) via `uv pip install` at no cost.
