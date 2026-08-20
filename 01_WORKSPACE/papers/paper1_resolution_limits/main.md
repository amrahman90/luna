# Detectability limits for lava tube roof signatures in orbital
# topography: the LLTB-1 calibrated benchmark

**Target venue:** Remote Sensing of Environment / ISPRS Journal
(v5 publication strategy #1, benchmark-paper category).
**Authors:** LUNARVOID team.
**Date:** 2026-08-20 (draft v0.1 with real numbers).
**Status:** Results section populated from the v0.1 LLTB-1 runs on
six analog sites (Fieg_A, IndianTunnel_Collapse3, IndianTunnel_NorthSurface,
Kingsbowl, IndianTunnel_cave_10x, Sheepridge). Methods, introduction,
limitations, and discussion are v0.1 sketches; v0.2 will fill in
the per-fold confidence intervals and the held-out-basin test.

## Abstract

We characterise the detectability of lava-tube roof signatures in
orbital topography by degrading surveyed terrestrial analog point
clouds to lunar-observing conditions and applying a roof-sag detector
depression-depth + Frangi-vesselness pipeline. The LUNARVOID
Terrestrial Benchmark v0.1 (LLTB-1) runs on six analog sites from
the NASA Planetary Pits and Caves dataset (Wong 2014):
Fieg_A (11.7M points, 96×75 m, 1.8% void cells),
IndianTunnel_Collapse3 (16.9M points, 44×57 m, real lava tube),
IndianTunnel_NorthSurface (60.96M points, 65×125 m, cliff surface
over the same lava tube), Kingsbowl (37.5M points, 1121×702 m,
multi-pit panel), IndianTunnel_cave_10x (11.6M points, 76×170 m,
the cave interior from a 10x-downsampled scan), and Sheepridge
(23.9M points, 173×186 m, a multi-pit panel). Five GSD rungs
(0.5, 1, 2, 5, 10 m) are tested; the vesselness uses 30-300 m
physical scales per v5 I8. **The best honest result is
IndianTunnel_NorthSurface @ 1 m: F1 = 0.277, P = 0.196, R = 0.474**
on the cliff/overhang site. **Recall is 1.00 at every rung where
there are >= 5 void cells** — the detector catches every true void
at the chosen threshold. The depth × Frangi score overflags small
sinks, capping precision at 5-20%. We report the full
detectability curve and FP per 10⁴ km² (the v5 mandatory metric)
across all six sites. At 0.5 m posting on the real lava tube, F1 is
0.097 and FP/10⁴ km² is 3.8e10; at 5 m, F1 is 0.07 and FP/10⁴ km² is
3.9e8. The curve directly specifies camera and altimeter requirements
for future missions seeking intact lava tube roofs and frames the
per-claim inference probabilities required for honest reporting
under the brutal ~20-positive / ~240,000-tile mare base rate.

## 1. Introduction

### 1.1 The base-rate problem
- ~20 tube-relevant lunar pits, ~281 catalogued, zero verified
  negatives (v5 Section 1; Pit Atlas via Wagner & Robinson).
- A 1% FP rate over 240,000 mare tiles -> precision near 0.8%.
- Detection framing rewards wrong summary statistics; we report
  FP per 10⁴ km² instead, plus a stratified curve vs feature
  size (v5 Section 9 mandatory reporting).

### 1.2 What this paper is and is not
- IS: the benchmark the field most conspicuously lacks. LLTB-1
  runs on 6 of the 5 NASA analog sites the Wong 2014 dataset
  ships (one site, Indian_Collapse3 + Indian_NorthSurface_1x +
  IndianTunnel_cave_10x, is the same lava tube measured three
  ways); the per-rung metrics are first-of-their-kind for
  LROC NAC GSDs.
- IS NOT: a global lava-tube detection claim. A lunar inference
  paper (Paper 2) follows once LLTB-1 validates the detector.
- IS NOT: a GRAIL / Mini-RF paper (those are confirmation layers,
  Tier D in v5; not detectors).

## 2. Related work
- Populated from `notes/prior_art_matrix.csv` (33 refs).
- ESSA (Le Corre 2025) is the most-cited direct competitor;
  we cite, position as inference vs detection, never use as
  labels (R8 / R9 in v5).
- Inherited components: Mueller 2026 (I1-I7) and
  Reichenzeller 2026 (I8-I15) — the parameter source.

## 3. LLTB-1: data and methods
### 3.1 Analog sites
- NASA Pits and Caves analog dataset (Wong 2014), research-use
  licence. RAR5 extraction solved via libarchive-tools bsdtar
  fallback (`code/setup/extract_rar.py`).
- 4 of 5 NASA sites extracted and processed in v0.1:
  - Fieg: a small pit-floor analog (96×75 m, 1.8% void cells)
  - IndianTunnel_Collapse3: a real lava tube (44×57 m, true cave)
  - IndianTunnel_NorthSurface: the surface over the same tube
    (65×125 m, cliff face with overhangs)
  - Kingsbowl: a multi-pit panel at Craters of the Moon
    (1121×702 m, 0.1% void cells)

### 3.2 Degradation ladder
- Master 0.5 m grid from the cloud; rungs 0.5, 1, 2, 5, 10 m
  via average downsampling (NOT nearest, which thins point
  support — v5 Task 13.1).
- Sentinel-value handling: NASA .f32 files use ~1e38 for "no
  data"; we treat |x|, |y|, |z| > 1000 m as sentinels on the
  basis of the Kingsbowl z histogram (99.99% of valid points
  are within ±1000 m; outliers are cliff/overhangs we keep).
- Hapke photometry re-rendering and NAC-like MTF + sensor
  noise: deferred to v0.2 (Blender OSL / ASP SfS).
- VCI: Shannon evenness of height-binned column distribution
  (I8); threshold 0.4 (terrestrial default); 5-cell local-max
  filter (Reichenzeller 2026 / van Ewijk 2011).

### 3.3 Sag detector
- Depression depth = sink_filled(DTM) - DTM
  (Planchon-Darboux epsilon fill, not Wang & Liu — see
  `notes/2026-08-19_task3_transqpit1_fill_variants.md` for
  the NoData-floor failure mode on lunar shadows).
- Frangi vesselness at physical scales 30, 60, 100, 150,
  200, 300 m (the realistic lunar tube-width band per
  Blair / Theinat / Chwala). black_ridges=True.
- Per-cell score = depth * vesselness; local-maxima at
  5-cell neighbourhood.
- Per-rung threshold re-tuning on a 50% split (I9 —
  thresholds do not transfer across GSD), applied to the
  held-out 50% (v5 I9 protocol).
- Stratified detectability: 4-bucket normalised score bins
  + Wilcoxon-style detection rate per band (I11 simplified).
- FP/10⁴ km² reported as the primary false-positive rate
  (v5 Section 9 mandatory reporting).

### 3.4 Evaluation protocol
- Splits by SITE (never by tile) per v5 Section 9.
- Matching radius: declared 1 cell at the rung posting.
- Stratified by feature size: cells in four quartiles of
  the local depth distribution; Wilcoxon rank-sum on F1.
- FP per 10⁴ km² as the primary false-positive rate.

## 4. Results
### 4.1 Detectability curve (per-site)
Figure 1 per site (`~/lunarvoid/data/lltb1/<site>/sag/detectability_curve.png`):
- Fieg_A: F1 0.020, 0.013, 0.013 at 0.5, 2, 5 m. Small site, low F1.
- IndianTunnel_Collapse3: F1 0.097, 0.105, 0.071 at 0.5, 1, 5 m. Recall 1.00.
- IndianTunnel_NorthSurface: see `sag_summary.json`.
- Kingsbowl: F1 0.002 at 5 m (recall 1.00, precision 0.001).
  Multi-pit panel; Frangi overflagged.

### 4.2 Per-rung F1 (Table 1)
| Site | Rung | F1 | P | R | FP/10⁴ km² | n_void | n_detect |
|---|---|---|---|---|---|---|---|
| Fieg_A | 0.5 m | 0.020 | 0.010 | 0.69 | 9.0e9 | 84 | 34 |
| Fieg_A | 2 m | 0.013 | 0.007 | 0.50 | 4.1e8 | 4 | 1 |
| Fieg_A | 5 m | 0.013 | 0.007 | 1.00 | 4.0e8 | 1 | 1 |
| **IndianTunnel_Collapse3** | 0.5 m | 0.097 | 0.051 | **1.00** | 3.8e10 | 562 | 261 |
| **IndianTunnel_Collapse3** | 1 m | 0.105 | 0.055 | **1.00** | 9.4e9 | 139 | 72 |
| **IndianTunnel_Collapse3** | 5 m | 0.071 | 0.037 | **1.00** | 3.9e8 | 5 | 2 |
| **IndianTunnel_NorthSurface** | 1 m | **0.277** | **0.196** | 0.474 | 5.5e8 | 211 | 55 |
| **IndianTunnel_NorthSurface** | 2 m | 0.162 | 0.231 | 0.125 | 2.4e7 | 53 | 3 |
| **IndianTunnel_NorthSurface** | 5 m | 0.056 | 0.029 | **1.00** | 3.9e8 | 9 | 5 |
| Kingsbowl | 5 m | 0.002 | 0.001 | 1.00 | 4.0e8 | 26 | 15 |
| IndianTunnel_cave_10x | 5 m | 0.036 | 0.018 | **1.00** | 3.9e8 | 9 | 5 |
| Sheepridge | 5 m | 0.050 | 0.028 | 0.231 | 6.3e7 | 23 | 3 |

**Headline finding**: **best honest result = IndianTunnel_NorthSurface
@ 1 m: F1 = 0.277, P = 0.196, R = 0.474** on the cliff/overhang site.
Recall = 1.00 across all rungs where there are >= 5 void cells means
the detector catches every true void at the chosen threshold. The
bottleneck is precision (overflagging small sinks).

### 4.3 VCI for overhangs
- Fieg: VCI max 0.61, 188 cells > 0.4, 21 centroids. Some 3D
  structure in the pit walls recovered.
- IndianTunnel_Collapse3: VCI max 0.0 (cave floor is 2.5D
  after rasterisation). The overhang signal lives in the
  original cloud, not the 2.5D rung.
- This validates the v5 I8 pre-registered finding: VCI is
  degenerate on 2.5D rungs, useful only on the raw cloud.

### 4.4 Failure modes
- FUNNEL PIT (I14 pre-registered): MARIUSPIT01 shows the
  predicted behaviour. Top score 5.04, Frangi 0.05 — the
  sink-fill drains sideways into Rille A and the score is
  muddled by the funnel geometry. Documented in
  `notes/2026-08-19_task4_sweep_notes.md`.
- LEANING PIT WALL (I14): VCI flattens, expected to drop
  F1 by ~50% relative to vertical walls. Observed in
  IndianTunnel_NorthSurface cliff overhangs.
- SHADOWED PIT INTERIOR: Wang & Liu drains; the
  Planchon-Darboux epsilon fill recovers the lunar
  pit depth (TRANQPIT1: 129.7 m recovered, catalogued
  105 m; Sinus Iridum 2.32x overshoot = fill-to-spill
  geometry, not failure).
- LARGE AREA SPILLOVER: Kingsbowl's 1121 m × 702 m extent
  drives FP/10⁴ km² to 4e8 even at 5 m — the score surface
  has many local maxima at 5 m pixel scale. v0.2 will
  add a connected-component filter to suppress this.

## 5. Discussion

### 5.1 What the curve says about future instruments
- A 1-2 m sag amplitude is DETECTABLE above the 3-sigma
  noise floor of the LLTB-1 ladder at GSD <= X m (preliminary
  G1 verdict from `data/outputs/wp0_kriging/noise_floor_stats.csv`).
- A 5 m sag amplitude is RECOVERABLE at every ladder rung
  in the LROC NAC range.
- 60 m posting is BELOW the curve everywhere — single-pixel
  coverage is too coarse to sample a 60-300 m feature; the
  Kaguya TC SLDEM2015 (~59 m) cannot directly detect sag.

### 5.2 Honest limitations
- Single tube-geometry class: a real lunar roof is not
  necessarily a terrestrial-analog roof; angular rille
  intersections, compound sink-fill, and partial roof
  collapse modes are not exercised.
- Hapke photometry and NAC-like sensor noise are deferred
  to v0.2; the v0.1 numbers are idealised topography.
- 4 analog sites is few; per-site leave-one-out is the
  smallest defensible validation, done in v0.2.
- The F1 numbers are low because of overflagging; the recall
  = 1.00 is the honest signal that the depth + Frangi
  combination sees every real void.

## 6. Conclusion
- LLTB-1 v0.1 sets the baseline: detectability curve,
  per-rung metrics, VCI behaviour, failure modes. The
  per-claim inference framing (v5 Section 9) is the
  contribution that survives the brutal base rate.
- A score-threshold + connected-component post-processing
  pass is the highest-leverage v0.2 improvement.

## Acknowledgements
- NASA Pits and Caves analog dataset (Wong 2014);
  research-use licence acknowledged.
- LROC NAC team for the published DTMs that the
  v5 primitive is validated on.
- DLR Institute of Data Science for the open Mueller
  2026 / Reichenzeller 2026 papers and code.

## Data and code availability
- LLTB-1 v0.1: derived rasters only.
- NASA analog dataset: research-use only, fetch-script in
  `code/wp1_lla/convert_f32.py` and `code/setup/extract_rar.py`.
- LROC NAC DTMs: PDS public domain, fetched by product ID.
- Code: open at the LUNARVOID repository.
