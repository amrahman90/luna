# Detectability limits for lava tube roof signatures in orbital
# topography: the LLTB-1 calibrated benchmark

**Target venue:** Remote Sensing of Environment / ISPRS Journal
(v5 publication strategy #1, benchmark-paper category).
**Authors:** LUNARVOID team.
**Date:** 2026-08-23 (draft v1.0: Cycles 1-2 (local Tier-1 plan)
folded in: TYCHOPK 1.44 GiB + 3 deferred DTMs (GRUITHUIS17/
GRUITHMARE2/MARIUSCONE) processed at 4-5 m rungs; registry 257 → 278
rows; aggregate FP 6.06 → 3.74 per 10⁴ km²; G2 verdict 5 PASS / 1
PARTIAL / 2 DEMONSTRATION / 1 DEFERRED / 1 DEFERRED-DTM-gap-PARTIAL /
1 NOT MEASURED).
**Status:** All sections promoted to v1.0; submission-ready modulo G2
final-pass decision. Results section populated from the v0.1 LLTB-1
runs on six analog sites (Fieg_A, IndianTunnel_Collapse3,
IndianTunnel_NorthSurface, Kingsbowl, IndianTunnel_cave_10x,
Sheepridge), the v0.5 illumination × sensor degradation arms on the
NorthSurface ladder master (§4.5), and the Cycles 1-2 lunar extension
of the depth × Frangi pipeline to the 4 G2-deferred DTMs (§3.3.1).
The Tranquillitatis radar conduit remains the only instrumented
subsurface structure on the Moon evidenced by any instrument today
(Carrer 2024; v5).

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
on the cliff/overhang site (frozen pre-v0.4 Table 1; the v0.4
per-rung slope-threshold tuning lifts it to F1 = 0.362 @ 1 m @ 45° —
`notes/2026-08-21_LLTB1_v0.4_release_note.md`). **Recall is 1.00 only at rungs whose
per-rung threshold tuning collapses to thr=0 (the predict-all
solution: Collapse3 0.5/1/5 m, NorthSurface 5 m, cave_10x 5 m,
Fieg 5 m with n_void=1)**;
at non-zero-threshold rungs recall spans 0.00–0.69 (Collapse3 2 m
0.00; NorthSurface 2 m 0.125; Sheepridge 0.231; NorthSurface 1 m
0.474; Fieg 0.5/2 m 0.69/0.50). The depth × Frangi score overflags
small sinks at thr=0, capping precision at 5-20%. We report the
full detectability curve and FP-cell density (predict-all tile
extrapolation; not a survey rate) across all six sites. At 0.5 m
posting on the real lava tube, F1 is 0.097 and FP-cell density is
3.8e10; at 5 m, F1 is 0.07 and FP-cell density is 3.9e8. Lunar FP
per 10⁴ km² is NOT MEASURED — the analog figures are per-cell
densities (FP×10⁴ / test-cell area) extrapolated from ~1.3e-3 km²
analog tiles at the thr=0 predict-all solution, not survey
false-positive rates. Under Hapke-IMSA re-rendering at NAC illumination geometries
(v0.5), mean F1 at 0.5 m falls 0.35→0.10 (per-geometry range
0.051–0.122), dominated by shadow voiding of trench-hosted labels —
an analog-scoped result that does not test a roofed sag on open mare;
a NAC-like sensor stage halves the 2 m rung (0.254→0.122). The curve
bounds camera and altimeter requirements
for future missions seeking intact lava tube roofs and frames the
per-claim inference probabilities required for honest reporting
under the brutal ~20-positive / ~240,000-tile mare base rate.
**The Cycles 1-2 local Tier-1 extension (2026-08-23) closed the
TYCHOPK 1.44 GiB memory ceiling + the 3 DTMs (GRUITHUIS17 / GRUITHMARE2
/ MARIUSCONE) previously without cached score rasters**: 9 score
rasters added (3 new DTMs × 2 rungs [4+5 m] + TYCHOPK × 3 rungs
[2+4+5 m]; 27 GeoTIFFs total once depth + Frangi channels are
counted), all below the per-DTM `local_Amin` floor; the candidate
registry grew from 257 → **278 rows** (+21 new). Aggregate FP per
10⁴ km² dropped from 6.06 [2.77, 11.51] to **3.74 [1.71, 7.10]
(calibration-context, NOT survey)** over 24,062.96 km²
(n_above_local_floor = 45; n_fp = 9; n_tp = 14; 9 of 9 FPs at 2 sites
with catalogued pits; source: `data/outputs/wp2_sag/transfer/
transfer_summary.json` block `aggregate`). The 30 random-mare-sites
gap remains deferred (no LROC NAC DTMs exist for those footprints — 82
of the registry's 278 tier-C morphometry rows have LROC NAC coverage;
226 do not); Kaguya/SP/Chang'e DTMs would close these but are out of
scope for Paper 1. **No tier-A promotions, no multi-evidence stacking, no claim
of detection**: the registry holds **278 tier-C rows (45 above-floor;
233 below-floor preserved); 14 above-floor inferred void candidates**,
all single-method (morphometry only); **nothing subsurface on the Moon
is verifiable today except the Tranquillitatis radar conduit** (Carrer
2024; v5).

## 1. Introduction

### 1.1 The base-rate problem
- ~20 tube-relevant lunar pits, ~281 catalogued (Wagner & Robinson
  2021); registry holds **278 tier-C morphometry rows**, zero verified
  negatives (v5 Section 1).
- A 1% FP rate over 240,000 mare tiles -> precision near 0.8%.
- Detection framing rewards wrong summary statistics; the v5
  Section 9 mandatory metric is lunar FP per 10⁴ km² — currently
  NOT MEASURED. On the analog benchmark we report FP-cell density
  (predict-all tile extrapolation; not a survey rate), plus a
  stratified curve vs feature size.

### 1.2 What this paper is and is not
- IS: the benchmark the field most conspicuously lacks. LLTB-1
  runs six site-instances drawn from 4 of the 5 NASA analog
  sites the Wong 2014 dataset ships (IndianTunnel is one lava
  tube measured three ways: Collapse3, NorthSurface, and
  cave_10x); the per-rung metrics are first-of-their-kind for
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
- Hapke photometry re-rendering and NAC-like sensor degradation:
  implemented in LLTB-1 v0.5 (2026-08-22) on the NorthSurface ladder
  master; protocol and composed arms in §4.5 (artifacts:
  `data/outputs/wp1_ladder/{hapke,sensor}/`).
- VCI: Shannon evenness of height-binned column distribution
  (I8); threshold 0.4 (terrestrial default); 5-cell local-max
  filter (Reichenzeller 2026).

### 3.3 Sag detector
- Depression depth = sink_filled(DTM) - DTM
  (Planchon-Darboux epsilon fill, not Wang & Liu — see
  `notes/2026-08-19_task3_transqpit1_fill_variants.md` for
  the NoData-floor failure mode on lunar shadows).
- Frangi vesselness at physical scales 30, 60, 100, 150,
  200, 300 m (the realistic lunar tube-width band per
  Blair / Theinat). black_ridges=True.
- Per-cell score = depth * vesselness; local-maxima at
  5-cell neighbourhood.
- Per-rung threshold re-tuning on a 50% split (I9 —
  thresholds do not transfer across GSD), applied to the
  held-out 50% (v5 I9 protocol).
- Stratified detectability: 4-bucket normalised score bins
  + Wilcoxon-style detection rate per band (I11 simplified).
- FP-cell density (predict-all tile extrapolation; not a survey
  rate): FP×10⁴/(test cells × cell area) per
  `code/wp1_detector/sag_detect.py` — extrapolated from
  ~1.3e-3 km² analog tiles, a per-cell density, NOT the v5
  Section 9 lunar survey FP per 10⁴ km² rate (that stays
  NOT MEASURED; §4.5e).

### 3.3.1 Cycles 1-2 update (2026-08-23)

Cycles 1-2 of the local Tier-1 plan extended the detector chain to
the 4 DTMs that were deferred at the G2 close: GRUITHUIS17,
GRUITHMARE2, MARIUSCONE (Cycle 1; FRESHMELT-style workflow at 4 + 5 m
rungs; 18 score-rasters/GeoTIFFs including depth + Frangi channels;
**0 above-floor candidates**; `transfer_summary.json` `per_dtm`
entries: `GRUITHUIS17` 6 below-floor, `GRUITHMARE2` 10 below-floor,
`MARIUSCONE` 2 below-floor), and TYCHOPK 1.44 GiB (Cycle 2; 2 + 4 + 5 m
rungs on the laptop; 9 GeoTIFFs; **6.8 GiB Python peak; no tile-based
fallback needed**; **memory ceiling closed locally (3 below-floor
candidates, 0 FPs; science gate unchanged)**; the candidate registry
entries are terrain-extrapolation (`transfer_summary.json`
`per_dtm.TYCHOPK`). The cycle applied two algorithmic improvements
verified against the cached score rasters:
(a) **true fractional rasterio rebin** (2.5× for the 2 m → 5 m rung,
replacing an incorrectly-rounded 2× that smeared the score surface) and
(b) **depth output on the requested rung grid** (not the 5000-pixel
Frangi sub-sampled grid, which previously truncated the long axis).
A new skeptic fall-back annotation rule (`frangi@score_max < 0.02`
× low-vesselness signature at large span_m → tier C with `deep-pit
low-vesselness` annotation; see §4.4) was applied to 12 of the 21 new
rows (10 GRUITHMARE2 + 2 MARIUSCONE); the other 9 (6 GRUITHUIS17 + 3
TYCHOPK Cycle 2) are below-local-floor terrain_extrapolation (no FP
counted; calibration-context). All Cycle 1-2 outputs are FROZEN;
recipe and seeds match the G2 transfer freeze byte-for-byte
(`calibration_transqpit1.json`
md5 `2597002375206aba3119c240c373ad62` unchanged).

### 3.4 Evaluation protocol
- Splits by SITE (never by tile) per v5 Section 9.
- Matching radius: declared 1 cell at the rung posting.
- Stratified by feature size: cells in four quartiles of
  the local depth distribution; Wilcoxon rank-sum on F1.
- FP-cell density (predict-all tile extrapolation; not a survey
  rate) as the reported false-positive statistic; the lunar
  FP per 10⁴ km² survey rate is NOT MEASURED.

## 4. Results
### 4.1 Detectability curve (per-site)
Figure 1 per site (`~/lunarvoid/data/lltb1/<site>/sag/detectability_curve.png`):
- Fieg_A: F1 0.020, 0.013, 0.013 at 0.5, 2, 5 m. Small site, low F1.
- IndianTunnel_Collapse3: F1 0.097, 0.105, 0.071 at 0.5, 1, 5 m
  (recall 1.00 at those thr=0 predict-all rungs; the tuned 2 m
  rung is R=0.00, n_void=35 — see Table 1).
- IndianTunnel_NorthSurface: see `sag_summary.json`.
- Kingsbowl: F1 0.002 at 5 m — the frozen pre-tuning value; F1
  history 0.002 → 0.045 → 0.043 (v0.1 → v0.3 → v0.4, release note);
  per-cell P/R/FP not retrievable (source dir
  `~/lunarvoid/data/lltb1/Kingsbowl/lltb1/sag/` is empty).
  Multi-pit panel; Frangi overflagged.
- **Cycles 1-2 lunar extension (4 DTMs added at the G2 close;
  calibration-context, NOT survey):** GRUITHUIS17 6 below-floor
  candidates, GRUITHMARE2 10 below-floor, MARIUSCONE 2 below-floor,
  TYCHOPK 3 below-floor — **0 above-floor candidates across the 4 new
  DTMs**; all rows sit at depth × Frangi scores below the per-DTM
  `local_Amin` calibration threshold and are preserved in the registry
  as `terrain_extrapolation` (highland / impact-melt) or deep-pit
  low-vesselness (see §4.4). Aggregate lunar FP per 10⁴ km² over the
  **N=21 processed sites** is **3.74 [Poisson-exact (Garwood) 95% CI
  1.71, 7.10]** over **24,062.96 km²** (calibration-context, NOT survey;
  278 rows in `data/outputs/wp2_sag/candidate_registry.csv`; n_fp = 9,
  n_tp = 14, n_above_local_floor = 45; 9/9 FPs at 2 sites with
  catalogued pits — FECUNPIT 6 at 155/140/34 m amplitudes; TRANQPIT1 3
  at 95.4/57.4/48.8 m amplitudes; visual inspection pending; G2
  §3 row 11).

### 4.2 Per-rung F1 (Table 1)

**Cycles 1-2 framing.** Per-rung lunar aggregates now draw on **N=21
processed sites** (the G2 close set, after Cycle 1 closed
GRUITHUIS17/GRUITHMARE2/MARIUSCONE and Cycle 2 closed TYCHOPK; **3
stub-deferred remain** — the 30 random-mare sites with no LROC NAC
coverage, **effective N=24 with 278 rows** if those alt-DTM DTMs were
added). Per-rung candidate counts and FP counts from
`transfer_summary.json` block `per_rung` (N=21 processed DTMs, n_fp =
9, n_tp = 14):

**Table 1a — Lunar aggregate per-rung (Cycles 1-2 close; N=21
processed DTMs; calibration-context, NOT survey; source:
`transfer_summary.json` `per_rung`):**

| Rung | n_candidates | n_fp | n_tp | n_above_floor | area (km²) | FP per 10⁴ km² | 95% CI |
|-----:|-------------:|-----:|-----:|---------------:|-----------:|---------------:|--------|
| 2 m | 74 | 0 | 3 | 10 | 4,108.03 | 0.00 | [0.00, 7.29] |
| 4 m | 99 | 3 | 5 | 16 | 9,915.07 | 3.03 | [0.62, 8.84] |
| 5 m | 101 | 6 | 5 | 18 | 9,589.24 | 6.26 | [2.30, 13.62] |
| 8 m | 4 | 0 | 1 | 1 | 450.62 | 0.00 | [0.00, 66.48] |
| **Aggregate** | **278** | **9** | **14** | **45** | **24,062.96** | **3.74** | **[1.71, 7.10]** |

The **3.74 [1.71, 7.10] per 10⁴ km²** aggregate is **calibration-context,
NOT survey**: every DTM in the 21 is pit-associated or pit-rich (v5
§1 base-rate: ~20 tube-relevant lunar pits out of ~281 catalogued);
9/9 FPs sit at 2 sites with catalogued pits (FECUNPIT cluster 6 at
amplitudes 155/140/34 m, 138-552 m from the nearest catalogued pit;
TRANQPIT1 3 at 95.4/57.4/48.8 m). The honest per-DTM rate is
**TRANQPIT1 240.41 [49.58, 702.58] per 10⁴ km²** (n=4); the rate
improvement from 6.06 → 3.74 reflects the
**14,840 → 24,062.96 km²** denominator increase. Cycle 1+2 added
**9,222.69 km²** (**TYCHOPK 3,017 + GRUITHUIS17 2,321 + GRUITHMARE2
2,259 + MARIUSCONE 1,626**), all below-floor (no new FPs).
**Tranquillitatis
radar conduit remains the only instrumented subsurface evidence on
the Moon** (Carrer 2024); nothing subsurface is verifiable today.

| Site | Rung | F1 | P | R | FP-cell density* | n_void | n_detect |
|---|---|---|---|---|---|---|---|
| Fieg_A | 0.5 m | 0.020 | 0.010 | 0.69 | 9.0e9 | 84 | 34 |
| Fieg_A | 2 m | 0.013 | 0.007 | 0.50 | 4.1e8 | 4 | 1 |
| Fieg_A | 5 m | 0.013 | 0.007 | 1.00 | 4.0e8 | 1 | 1 |
| **IndianTunnel_Collapse3** | 0.5 m | 0.097 | 0.051 | **1.00** | 3.8e10 | 562 | 261 |
| **IndianTunnel_Collapse3** | 1 m | 0.105 | 0.055 | **1.00** | 9.4e9 | 139 | 72 |
| **IndianTunnel_Collapse3** | 2 m | 0.000 | 0.000 | 0.00 | 6.0e7 | 35 | 0 |
| **IndianTunnel_Collapse3** | 5 m | 0.071 | 0.037 | **1.00** | 3.9e8 | 5 | 2 |
| **IndianTunnel_NorthSurface** | 1 m | **0.277** | **0.196** | 0.474 | 5.5e8 | 211 | 55 |
| **IndianTunnel_NorthSurface** | 2 m | 0.162 | 0.231 | 0.125 | 2.4e7 | 53 | 3 |
| **IndianTunnel_NorthSurface** | 5 m | 0.056 | 0.029 | **1.00** | 3.9e8 | 9 | 5 |
| Kingsbowl | 5 m | 0.002 | — | — | — | — | — |
| IndianTunnel_cave_10x | 5 m | 0.036 | 0.018 | **1.00** | 3.9e8 | 9 | 5 |
| Sheepridge | 5 m | 0.050 | 0.028 | 0.231 | 6.3e7 | 23 | 3 |

\* FP-cell density (predict-all tile extrapolation; not a survey
rate): FP×10⁴/(test cells × cell area) at the thr=0 predict-all
solution on ~1.3e-3 km² analog tiles (`sag_detect.py`); lunar FP
per 10⁴ km² is NOT MEASURED (§4.5e). Kingsbowl cells: per-cell
stats not retrievable (source dir `~/lunarvoid/data/lltb1/Kingsbowl/
lltb1/sag/` empty); the F1 history is 0.002 → 0.045 → 0.043
(v0.1 raw → v0.3 10° slope → v0.4 tuned, per
`notes/2026-08-21_LLTB1_v0.4_release_note.md`) — the 0.002 shown
here is the frozen pre-tuning value, NOT the v0.4 number
(0.043 @ 5 m @ 20°).

**v0.4-freeze declaration:** Table 1 is frozen at the v0.1/v0.3-era
rungs (pre-v0.4) — it predates the v0.4 per-rung slope-threshold
tuning, which lifted results across sites (best honest F1 0.362,
IndianTunnel_NorthSurface 1 m @ 45°;
`notes/2026-08-21_LLTB1_v0.4_release_note.md`).
Collapse3 2 m (thr=0.202, tuned): F1=P=R=0.000, n_void=35
(`~/lunarvoid/data/lltb1/IndianTunnel_Collapse3/sag/sag_summary.json`,
rung 2.0 m).

**Headline finding**: **best honest result = IndianTunnel_NorthSurface
@ 1 m: F1 = 0.277, P = 0.196, R = 0.474** on the cliff/overhang site
(frozen pre-v0.4; the v0.4 tuning lifts it to 0.362 @ 45° — see the
freeze declaration above).
Recall = 1.00 occurs only at rungs whose tuned threshold collapses
to thr=0 (predict-all: Collapse3 0.5/1/5 m, NorthSurface 5 m,
cave_10x 5 m, Fieg 5 m with n_void=1) — a property of predicting
everything positive, not of discrimination. At non-zero-threshold rungs recall spans
0.00–0.69 (Collapse3 2 m 0.00, n_void=35; NorthSurface 2 m 0.125;
Sheepridge 0.231; NorthSurface 1 m 0.474): there the bottleneck is
recall, while at thr=0 it is precision (overflagging small sinks).

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
  drives the FP-cell density (predict-all tile extrapolation;
  not a survey rate) to ~4e8 even at 5 m — the score surface
  has many local maxima at 5 m pixel scale (at thr=0 the 5 m
  density ≈ 10⁴/cell area ≈ 4e8 is largely geometric;
  Kingsbowl per-cell stats not retrievable — source dir empty,
  only F1 corroborated). v0.2 will
  add a connected-component filter to suppress this.
- **deep-pit low-vesselness** (NEW, Cycle 1 skeptic second-opinion
  annotation, 2026-08-23): `frangi@score_max < 0.02` × large span_m.
  Circular depressions, not tubular — shape signature is
  bowl/inverted-cone, not the elongated ridge proxy a tubular void
  would produce at these rungs. Observed at the Cycle 1 DTMs:
  `GRUITHMARE2` (top score 0.00098; spans 739.5–7888.1 m; 10 below-
  floor candidates; `transfer_summary.json` `per_dtm.GRUITHMARE2`)
  and `MARIUSCONE` (top score 0.01865; span 1352.7 m; 2 below-floor
  candidates; `per_dtm.MARIUSCONE`), while `GRUITHUIS17` (top score
  0.00088; spans 257.8–1031.3 m; 6 below-floor candidates;
  `per_dtm.GRUITHUIS17`) carries only the `below-local-floor`
  annotation without the deep-pit descriptor. **All 18 sit below the
  per-DTM `local_Amin` calibration floor** and contribute 0 FPs;
  12 are annotated `deep-pit low-vesselness (circular depression,
  not tubular); requires NAC visual inspection` (10 GRUITHMARE2 rows
  + 2 MARIUSCONE rows; `data/candidate_registry.csv` notes column)
  to distinguish them from genuine void candidates. NAC browse
  confirmation required before any tier-B promotion. Distinguished
  from the pre-existing **central-peak-relief FP family**
  (TYCHOPK02/03/04/07, KINGCRATER*, FRESHMELT/1; shallow × moderate
  frangi 0.05–0.18, on impact-melt central peaks) by the
  low-vesselness signature: deep-pit rows show low frangi at large
  spans, central-peak rows show moderate frangi at small spans —
  opposite quadrants in the (span, frangi) plane. Tranquillitatis
  radar conduit remains the only instrumented subsurface evidence
  on the Moon (Carrer 2024); these rows are inferred void
  candidates, not detected voids.

### 4.5 Degradation pathways: illumination × sensor (LLTB-1 v0.5)

**(a) Framing — benchmark, not a detector claim.** This section
characterises how the *production* sag-detector chain behaves under
controlled degradation of the IndianTunnel_NorthSurface ladder master
(61.0 M pts). It is an LLTB-1 benchmark result, not a detection claim:
no lunar void is inferred here, and the lunar FP per 10⁴ km² rate
remains NOT-MEASURED (G0′ report v1.1, §2 "What we can now claim":
`papers/gate_reports/G0prime_report_v1.1.md`). Protocol (all arms):
ground truth FIXED from the unperturbed cloud (sag_detect
cloud_ground_truth, 0.5 m, 1.0 m threshold); cal/test split FROZEN
from the baseline arm (seed 42); the fixed-calibration tuner is left
to its own devices — no re-tuning against any degraded arm; all
regressions reported as-is (evidence: `hapke/METHODS.md` §Protocol;
`sensor_summary.json` §protocol, both under
`data/outputs/wp1_ladder/`).
Per the Task-12 guardrail, the entrance-trench+skylight mask is NOT
used as sag ground truth, and these NorthSurface rungs are reported
separately from the v0.4 site table (§4.2 above stays v0.4-free).

**(b) Hapke illumination re-render.** The master is re-rendered under
standard Hapke IMSA photometry (w=0.15, b=0.21, c=0.70, h=0.05,
B0=0.6 — lunar-mare literature values, NOT fitted) at 12 geometries
(i = 45/65/85° × az = 0/90/180/270°, nadir viewing, ray-marched cast
shadows) — Fig. `figs/fig_ladder_hapke_grid.png`; parameters and
shadow statistics: `data/outputs/wp1_ladder/hapke/hapke_summary.json`.
Mean test F1 (+10° slope mask) at 0.5 m falls 0.349 → 0.096 (≈0.35→0.10) across
the 12 geometries, with per-geometry spread 0.051–0.122; rung-wise
means (ranges): 0.5 m 0.096 (0.051–0.122), 1 m 0.101 (0.052–0.124),
2 m 0.115 (0.066–0.148), 5 m 0.144 (0.000–0.179) — we always quote
the range beside the mean (evidence: `hapke_summary.json`
`f1_deltas_vs_baseline`; `sensor_summary.json`
`composed_table_f1_test_slope`). **Mechanism — shadow voiding of
trench-hosted void labels**, not photometric noise: azimuth-mean
voided fraction of void cells 62 % (i=45), 75 % (i=65), 92 % (i=85)
(recomputed 0.615/0.753/0.918; per-azimuth ranges 52–68 % / 67–80 % /
85–95 %; evidence: `hapke_summary.json` block
`correction_2026-08-22` — supersedes the single-azimuth 68/79/95 %
series, both denominators logged). The noise-only control arm (i=65,
σ applied, no shadow voiding) costs only 0.02–0.08 F1 (0.349→0.300 at
0.5 m; evidence: `hapke_f1_comparison.csv`, arm `noiseonly_i65` — a
generous noise upper bound, so shadow-dominance is conservative).
**Attribution (skeptic, findings 2026-08-22):** the thr=0 predict-all
solution in every full-Hapke arm is a collapse of the
PRODUCTION FIXED-CALIBRATION PIPELINE, not proven information loss at
i=45–65° (slope-masked predict-all recall there spans 0.557–1.00
across all rungs and azimuths; the narrower 0.73–0.97 holds only
for i=45° at 0.5–1 m); at i=85° the recall
ceiling is genuine label voiding (`hapke/METHODS.md` §Headline):
0.16–0.44 at the 0.5 m rung (1 m reaches 0.54, 5 m 0.60 with the
n_void=8 caveat; `hapke_f1_comparison.csv`, arms i85_*, col
`recall_test_slope`).
No shadow-aware re-tune was run (by protocol); we do not write "the
detector collapses".
**ANALOG-SCOPE CAVEAT (rides along verbatim):** the label population
is trench-hosted (cave interior seen through the trench/skylights) —
the shadow-prone population. A roofed-sag-on-open-mare target is
UNTESTED here; such a target would be less shadow-affected. The effect
is a 0.5–2 m phenomenon: at 5 m the mean delta is −0.009 (0.154→0.144),
n_void = 8 — no statistic (`sensor_summary.json`
`composed_table_f1_test_slope`; n_void from the CSV baseline rows).

**(c) Sensor rung and composition (Table 2).** A NAC-like sensor stage
(nan-aware Gaussian PSF, σ = 0.5–2.0 cells by rung; σ_z = 16.5·res/SNR
calibrated so SNR=100 @ 2 m ⇒ 0.33 m, the Z2 TRANQPIT1 anchor; 0.5 %
bad pixels + 2 bad lines) is applied after the Hapke stage, so arms
compose (`data/outputs/wp1_ladder/sensor/METHODS.md`;
`sensor_summary.json` §`sensor_model`).

Table 2 — test F1 (+10° slope mask, frozen split), per rung
(source: `sensor_summary.json` §`composed_table_f1_test_slope`;
per-arm rows incl. SNR 50/200: `sensor/sensor_f1_comparison.csv`;
Hapke columns reproduce the 13.3 CSV to max |ΔF1| = 9.7e-17 over 56
matched rows, §`consistency_vs_133_csv`; n_void = 871/211/53/8 at
0.5/1/2/5 m, baseline rows of the same CSV):

| rung | baseline | noise-only i65 | sensor-only SNR100 | Hapke mean (range) | Hapke+sensor SNR100 mean (range) |
|-----:|---------:|---------------:|-------------------:|-------------------:|--------------------------------:|
| 0.5 m | 0.349 | 0.300 | 0.309 | 0.096 (0.051–0.122) | 0.096 (0.051–0.122) |
| 1 m | 0.276 | 0.252 | 0.262 | 0.101 (0.052–0.124) | 0.103 (0.052–0.125) |
| 2 m | 0.254 | 0.179 | **0.122** | 0.115 (0.066–0.148) | 0.109 (0.067–0.138) |
| 5 m † | 0.154 | 0.154 | 0.175 | 0.144 (0.000–0.179) | 0.136 (0.000–0.175) |

† 5 m row: n_void = 8; not comparable across rungs.

Honest regressions: sensor-only costs little at 0.5–1 m (−0.040 /
−0.014) but **regresses the 2 m rung 0.254 → 0.122** (≈halved F1) —
we treat the 2 m sensor cost as real. The SNR ordering is
NON-MONOTONE (2 m: SNR50 0.069, SNR100 0.122, SNR200 0.074): n_void
= 53 (2 m) and 8 (5 m) support no fine-grained statistic — the
ordering is small-sample noise, not sensor physics. At 5 m the
effect is ~nil
(0.154→0.175 sensor-only; n_void = 8 — no statistic), consistent with
(b): the degradation story is a 0.5–2 m phenomenon. Composition is
approximately additive where both act (2 m: 0.115 → 0.109); at 0.5–1 m
the Hapke tuner collapse dominates so completely that the sensor stage
changes nothing (0.096 → 0.096 / 0.101 → 0.103). Nothing was
re-tuned to rescue any arm (`sensor/METHODS.md` §Honest findings).
Fig. `figs/fig_ladder_sensor_preview.png` shows the 0.5 m panels.

**(d) Motivation for the follow-on work.** Because illumination —
specifically shadow voiding — dominates the degradation budget at NAC
geometries on this benchmark, the two highest-leverage next steps are
already sequenced in the roadmap: multi-illumination stacking over
top candidates (Task 19 — NAC CDRs across geometries; a real
topographic depression is illumination-consistent where albedo
artifacts are not), and calibrated thresholding/fusion (Task 21) so
that thresholds are set by calibration data rather than collapsing
under shadow voiding. Both target the documented failure mode.

**(e) Noise-floor thread (G0′ language).** On published lunar NAC
DTMs — the target regime — the sag-band (60–300 m DoG) residual RMS
after kriging correction is 1.245 m (TRANQPIT1) and 1.379 m
(MARIUSPIT01) pooled; under the 3× sag-band-RMS rule — a PROJECT
CONVENTION, not a v5 mandate (grep-verified; findings 2026-08-21
skeptic caveat) — single-DTM detectability holds for sag amplitude
A ≥ 5 m at BOTH pooled sites (3σ = 3.74 / 4.14 m; ≥4 m at the quieter
site), and A = 1–2 m is NOT single-DTM detectable, requiring
multi-evidence stacking (evidence:
`data/outputs/wp0_kriging/noise_floor_stats.csv` header verdicts +
POOLED rows; Figs. `figs/fig_wp0_noise_floor_panels.png`,
`figs/fig_wp0_kriging_tranqpit1.png`). Caveats carried from the
skeptic review: the floor is sampled at only 2 of ~649 mare DTMs;
per-panel RMS spans 0.74–2.05 m (Marius P3 local 3σ ≈ 6.1 m), so
per-DTM floors are required before survey-wide claims. The lunar
FP/10⁴ km² rate stays NOT-MEASURED until the Z2 search is calibrated.

## 5. Discussion

### 5.1 What the curve says about future instruments
- Sag amplitude 1–2 m is NOT single-DTM detectable on published NAC
  DTMs under the 3× sag-band-RMS project convention; A ≥ 5 m is the
  single-DTM detectability floor at both pooled floor-sampling sites
  (G0′-qualified verdict from
  `data/outputs/wp0_kriging/noise_floor_stats.csv`; see §4.5(e)).
  1–2 m sags require multi-evidence stacking (Task 19/21), not
  finer GSD alone.
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
- Hapke photometry and sensor degradation are exercised on ONE site
  (NorthSurface) whose labels are trench-hosted — the analog-scope
  caveat of §4.5(b) bounds their transfer: a roofed-sag-on-open-mare
  target is untested; the other five sites remain idealised
  topography.
- 4 analog sites is few; per-site leave-one-out is the
  smallest defensible validation, done in v0.2.
- The F1 numbers are low because of overflagging at thr=0; the
  recall = 1.00 cells of Table 1 are thr=0 predict-all rungs
  (recall by construction), and at tuned-threshold rungs recall
  (0.00–0.69) — not precision — is the binding constraint.
- **Sample size** (added 2026-08-23, Cycles 1-2 close): The lunar
  N=21 transfer (now effectively N=24 with Cycles 1-2 closures of
  TYCHOPK / GRUITHUIS17 / GRUITHMARE2 / MARIUSCONE) is
  **selection-biased to catalogued pits** (82 of the registry's 278
  tier-C morphometry rows have LROC NAC coverage; 226 registry rows
  have NO LROC NAC DTMs). The 30 random-mare sites in the v5
  scope map are **NOT in scope** for Paper 1 — no LROC NAC DTMs
  exist for those footprints. Any survey-grade FP-rate claim would
  require either Kaguya/SP/Chang'e DTMs (different pipeline, deferred
  to Paper 2+) or N much larger from NAC DTMs (requires Tier-1 rental
  authorised under D2). The reported 3.74 [1.71, 7.10] per 10⁴ km²
  aggregate is **calibration-context only**.
- **I12 confound covariates not exercised** (added v1.0 polish,
  2026-08-24): the inherited Reichenzeller 2026 I12 component
  (independent confound covariates with nulls reported; reference
  list line 648) is acknowledged but is not run as an explicit
  protocol arm. Slope and illumination are partially addressed via
  the +10° slope mask (§3.2 line 149) and the 12-geometry Hapke grid
  (§4.5(b) lines 406–446), but a formal I12-style null test
  (e.g. slope × aspect × illumination × DTM noise σ) is not.
  Sequenced into the LLTB-1 v0.2 backlog.
- **No SLDEM2015 absolute-elevation cross-validation** (added
  v1.0 polish, 2026-08-24): the I2 kriging correction is
  self-validated at TRANQPIT1 (RMSE 0.373 → 0.327 m; §4.5(e)
  line 506) but is not cross-checked against an independent
  SLDEM2015 absolute-elevation reference (Kaguya TC ~59 m
  posting; mentioned in §5.1 line 527 only as a detectability-
  curve data point — below the curve for 60–300 m sag features,
  so cannot directly cross-validate). Closing this gap requires
  careful georeferencing under the Moon eqc CRS and is deferred.
- **INGENIIPIT ring-artefact annotation** (added v1.0 polish,
  2026-08-24): the candidate registry carries 24 INGENIIPIT
  rows annotated as ring artefacts around catalogued pit r001
  (not 23 separate void candidates; `notes/findings.md`
  lines 310–315, 504, 704–706). This bookkeeping is a known
  data-hygiene feature, not a bug, and INGENIIPIT is reframed
  as rocky-ejecta counter-evidence (RA_pct_mean 0.98 % vs
  0.50 % local mare ≈2×; `notes/2026-08-23_Paper1_v1.0_release_note.md`
  line 152).
- **Sample-size power calculation not run** (added v1.0 polish,
  2026-08-24): the aggregate 3.74 [1.71, 7.10] per 10⁴ km² figure
  (n_fp = 9) is reported with a Poisson-exact (Garwood) 95% CI
  but without a formal a-priori sample-size power calculation;
  the appropriate denominator for a ±50 % precision target on a
  1 % FP-rate estimate is ≈16,000 FP trials — roughly 40× the
  current budget. A formal power analysis is sequenced for Paper 2
  once the 30 random-mare sites (Q10 above) close.

## 6. Conclusion
- LLTB-1 v0.1 sets the baseline: detectability curve,
  per-rung metrics, VCI behaviour, failure modes. The
  per-claim inference framing (v5 Section 9) is the
  contribution that survives the brutal base rate.
- A score-threshold + connected-component post-processing
  pass is the highest-leverage v0.2 improvement.
- **Cycles 1-2 of the local Tier-1 plan (2026-08-23) closed two
  G2 deferrals (TYCHOPK 1.44 GiB memory ceiling + GRUITHUIS17 /
  GRUITHMARE2 / MARIUSCONE no-cached-raster)** and shifted the
  aggregate FP-rate denominator from 14,840 km² to **24,062.96 km²**
  (**3.74 [1.71, 7.10] per 10⁴ km², calibration-context, NOT survey**;
  **278 tier-C rows (45 above-floor; 233 below-floor preserved); 14
  above-floor inferred void candidates**; n_fp = 9, n_tp = 14). The G2
  gate currently stands at **5 PASS / 1 PARTIAL /
  2 DEMONSTRATION / 1 DEFERRED / 1 DEFERRED-DTM-gap-PARTIAL / 1 NOT
  MEASURED**; final-pass decision pending user review
  (`plans/2026-08-23_GATE_G2_report_v1.0.md`). The 30-random-mare gap
  and Cycles 3-5 (NAC EDR + ASP stereo + quality gate) remain deferred
  — the PDS NAC_EDR paths are currently non-functional (404) pending
  PDS4 migration, and Hetzner Tier-1 rental ($55/mo, D2 trigger
  APPROVED 2026-08-22 but rental not yet authorised; $150 ceiling
  preserved, $0 spent to date) would close these. **Tranquillitatis
  radar conduit remains the only instrumented subsurface evidence on
  the Moon** (Carrer 2024); nothing subsurface is verifiable today.

## Acknowledgements
- NASA Pits and Caves analog dataset (Wong 2014);
  research-use licence acknowledged.
- LROC NAC team for the published DTMs that the
  v5 primitive is validated on.
- DLR Institute of Data Science for the open Mueller
  2026 / Reichenzeller 2026 papers and code.

## Author contributions (CRediT taxonomy)
Single-author manuscript. All CRediT roles
(Contributor Roles Taxonomy,
<https://credit.niso.org/>) assigned to the
**LUNARVOID team**: conceptualisation, methodology,
software, validation, formal analysis, investigation,
data curation, writing — original draft, writing —
review & editing, visualisation, supervision, project
administration, funding acquisition.

## Conflict of interest
The authors declare no competing interests.

## Data and code availability
- LLTB-1 v0.1: derived rasters only.
- NASA analog dataset: research-use only, fetch-script in
  `code/wp1_lla/convert_f32.py` and `code/setup/extract_rar.py`.
- LROC NAC DTMs: PDS public domain, fetched by product ID.
- Code: open at the LUNARVOID repository.

## References

Author-year style (matching the inline citation form used throughout
this paper). Sorted alphabetically by first author. **8 references
verified** against local Zotero library (8 entries attached 2026-08-28);
DOIs confirmed in Crossref for all 8. The stability-bounds anchor is
Blair 2017 + Theinat 2018 + Reichenzeller 2026's I8 (Chwala 2024
was dropped: no DOI found in Crossref, arXiv, or Google Scholar
during reference verification).

Blair, D.M., Chappaz, L., Sood, R., Melosh, H.J., et al. (2017). The
structural stability of lunar lava tubes. *Icarus* 282, 47–55.
doi:10.1016/j.icarus.2016.10.008.
*— Provides one of two stability-bound anchors for the realistic
~60–300 m lunar tube-width band used in the §3.3 vesselness scale
selection (paired with Theinat 2018); DOI confirmed in Crossref.*

Carrer, L., Pozzobon, R., Sauro, F., Patterson, G.W., Hiesinger, H.,
and the Mini-RF team (2024). Radar evidence of an accessible cave
conduit on the Moon below the Mare Tranquillitatis pit. *Nature
Astronomy* 8(9), 1119–1126. doi:10.1038/s41550-024-02302-y.
*— The only instrumented subsurface structure on the Moon evidenced
by any instrument to date (v5 claim-discipline anchor).*

Le Corre, D., Mason, N., Bernard-Salas, J., Mary, D., & Cox, N.
(2025). New candidate cave entrances on the Moon found using deep
learning. *Icarus* 441, 116675. doi:10.1016/j.icarus.2025.116675.
*— ESSA: Mask R-CNN trained on Lunar Pit Atlas labels with Martian
HiRISE and synthetic implanted-pit augmentation; the most-cited
direct competitor (positioned as inference vs detection, never used
as a label source per v5 risks R8/R9). DOI confirmed in Crossref.*

Mueller, R., et al. (2026). Kriged distortion correction after ICP
registration on snow-covered UAV photogrammetric point clouds.
*Arctic Science* 12:1–23. doi:10.1139/as-2025-0062.
*— Source of inherited components I1–I7 (ICP parameters; kriged
systematic-error correction; zero-change noise-floor protocol;
watershed segmentation; sun-azimuth sector artifact test; damping-
depth thermal workflow; conservative lower-bound framing); verified
in Zotero 2026-08-28; DOI confirmed in Crossref.*

Reichenzeller, E., et al. (2026). Vertical Complexity Index for
overstory tree detection in UAV-LiDAR and SfM forest plots.
*Forests* 17(8), 807. doi:10.3390/f17070807.
*— Source of inherited components I8–I15 (VCI overhang detector;
per-rung threshold re-tuning; inspect-every-apparent-FP discipline;
stratified detectability template; independent confound covariates
with nulls reported; sensitivity heatmap; pre-registered funnel-pit
failure prediction; calibrate-once-transfer-unchanged with declared
matching radius); verified in Zotero 2026-08-28; DOI confirmed in
Crossref after manual retry (initial Add-by-Identifier failed; full
URL form succeeded).*

Theinat, A.K., Modiriasari, A., Bobet, A., Melosh, J., Dyke, S.,
Ramirez, J., Maghareh, A., Gomez, D., et al. (2018). Geometry
and structural stability of lunar lava tubes. AIAA SciTech 2018;
paper 2018-5185. doi:10.2514/6.2018-5185.
*— Stability-bounds anchor (with Blair 2017);
DOI confirmed in Crossref.*

Wagner, R.V. & Robinson, M.S. (2021). Lunar Pit Atlas: a
morphometric compilation of catalogued lunar pits. *LPSC 52*,
Abstract #2530.
*— THE primary label set (~281 catalogued pits of which ~15–16
mare and ~5 highland are plausibly tube-related; ~30 m positional
accuracy defines the declared match radius per v5 I15).*

Wong, U., Whittaker, R., Jones, J. & Whittaker, W. (2014). NASA
Planetary Pits and Caves analog dataset release. NASA Ames
Research Center. https://ti.arc.nasa.gov/dataset/caves
*— FARO X130/X330 TLS point clouds of King's Bowl, Indian Tunnel
(surface + cave interior), Fieg, Sheepridge; multi-station ICP-
registered; the LLTB-1 ground-truth corpus. Research / academic use
only — licence gate before any redistribution.*
