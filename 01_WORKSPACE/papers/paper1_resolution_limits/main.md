# Detectability limits for lava tube roof signatures in orbital
# topography: the LLTB-1 calibrated benchmark

**Target venue:** Remote Sensing of Environment / ISPRS Journal
(v5 publication strategy #1, benchmark-paper category).
**Authors:** LUNARVOID team.
**Date:** 2026-08-22 (draft v0.2: Task 16.3 — degradation-ladder v0.5
folded in; §4.5 + figs/ index).
**Status:** Results section populated from the v0.1 LLTB-1 runs on
six analog sites (Fieg_A, IndianTunnel_Collapse3, IndianTunnel_NorthSurface,
Kingsbowl, IndianTunnel_cave_10x, Sheepridge), plus the v0.5
illumination × sensor degradation arms on the NorthSurface ladder
master (§4.5). Introduction, related work, and discussion remain
v0.1 sketches; per-fold confidence intervals and the held-out-basin
test are still deferred.

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

## 1. Introduction

### 1.1 The base-rate problem
- ~20 tube-relevant lunar pits, 278 catalogued, zero verified
  negatives (v5 Section 1; Pit Atlas via Wagner & Robinson).
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
- FP-cell density (predict-all tile extrapolation; not a survey
  rate): FP×10⁴/(test cells × cell area) per
  `code/wp1_detector/sag_detect.py` — extrapolated from
  ~1.3e-3 km² analog tiles, a per-cell density, NOT the v5
  Section 9 lunar survey FP per 10⁴ km² rate (that stays
  NOT MEASURED; §4.5e).

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

### 4.2 Per-rung F1 (Table 1)
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
