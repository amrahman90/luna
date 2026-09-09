# Detectability limits for lava tube roof signatures in orbital topography: the LLTB-1 calibrated benchmark

**Authors:** LUNARVOID team (author list to be completed at submission)
**Affiliations:** [placeholder]
**Corresponding author:** [placeholder]
**Keywords:** lunar lava tubes; topographic detectability; terrestrial analogs; digital terrain models; degradation benchmark; roof sag; Frangi vesselness; false-positive rate; calibrated inference

---

## Abstract

Intact lunar lava tubes are high-priority targets for future surface exploration, yet no orbital observation today can verify a subsurface void: the only subsurface structure on the Moon evidenced by any instrument remains the radar conduit beneath the Mare Tranquillitatis pit. We therefore ask not whether lava tubes can be detected from orbit, but under what observing conditions a roof-sag signature can be inferred at all. We present a calibrated benchmark (LLTB-1) built from surveyed terrestrial laser scans of four volcanic-field sites (six map instances; three instances sample the same trench-hosted tube), degraded to lunar-observing conditions at ground-sample distances of 0.5–10 m, extended with Hapke-photometric shadow rendering at NAC-like illumination geometries and a NAC-like sensor stage, and processed with a depression-depth × Frangi-vesselness roof-sag detector under per-rung threshold calibration. The best honest result is F1 = 0.277 (precision 0.196, recall 0.474) at 1 m posting on the cliff-surface instance; per-rung slope-mask tuning lifts it to 0.362. Perfect recall occurs only where the tuned threshold collapses to the predict-all solution; at informative thresholds recall spans 0.00–0.69. Shadow voiding dominates the degradation budget: mean F1 at 0.5 m falls from 0.349 to 0.096 across twelve illumination geometries, and a sensor stage alone halves the 2 m rung (0.254 → 0.122). On published lunar DTMs, the 60–300 m band-passed residual noise floor makes single-DTM inference tenable only for sag amplitudes ≥ 5 m; 1–2 m sags require multi-evidence stacking. Across 21 pit-associated lunar DTMs (24,062.96 km²), the row-based calibration-context false-positive rate is 3.74 per 10⁴ km² (Poisson-exact 95% CI 1.71–7.10); the 14 above-floor true positives are re-detections of catalogued pits, and zero novel above-floor candidates exist in the calibration-context set. All lunar results are calibrated inference, never verified detection; the derived curves bound camera and altimeter requirements for missions seeking intact tube roofs.

---

## 1. Introduction

### 1.1. Motivation and the base-rate problem

Intact lunar lava tubes have been proposed as candidate sites for future surface infrastructure because their roofs would shield against radiation and thermal extremes, and the radar evidence for an accessible cave conduit beneath the Mare Tranquillitatis pit (Carrer et al., 2024) confirmed that void space of this kind exists and is, in principle, observable from orbit. That detection, however, is the single subsurface structure on the Moon evidenced by any instrument to date. Every other proposed lava tube — and every candidate roof signature identified in orbital topography or imagery — remains an inference, not a verified detection. The central problem this paper addresses is that such inferences are usually not reported as inferences.

The obstacle is a base-rate problem. Of the roughly 281 pits in the Lunar Pit Atlas (Wagner and Robinson, 2021), only about 20 are plausibly tube-related. A hypothetical detector with a 1% per-tile false-positive rate applied over the approximately 240,000 mare tiles at LROC NAC ground-sample distances would flag on the order of 2,400 tiles against at most a few tens of true tube sites, yielding a precision near 0.8%. Under these conditions a "detection" framing rewards exactly the wrong summary statistics: per-tile accuracy and F1 against a catalogued label set can look strong while the per-claim probability that any given flag is a void remains negligible. The honest primary metric is the false-positive count per unit area — FP per 10⁴ km² — reported with exact intervals, together with an explicit statement of what population was searched. No such measurement exists at survey grade today for any lunar tube-detection method, and this paper does not provide one either; it provides the calibrated analog benchmark and the calibration-context lunar accounting that such a measurement requires, with the boundaries of each claim stated explicitly.

We therefore adopt a strict claim discipline throughout: candidates are inferred voids with error bars, never verified detections, and nothing subsurface on the Moon is described as verified except the radar-evidenced Tranquillitatis conduit (Carrer et al., 2024).

### 1.2. Related work

**Catalogues and imagery-based detectors.** The Lunar Pit Atlas (Wagner and Robinson, 2021) is the primary morphometric compilation of catalogued lunar pits (~281 entries, positional accuracy ~30 m) and supplies the label set used by essentially all downstream machine-learning work. The most prominent recent entry is the ESSA detector of Le Corre et al. (2025), a Mask R-CNN trained on Atlas labels augmented with Martian HiRISE pits and synthetically implanted pits, which reports strong detection scores on NAC imagery. Two properties of that line of work motivate ours. First, its evaluation scores are detection metrics computed against the same catalogued pit population used in training, without per-claim void probabilities or false-positive-per-area reporting; at the lunar base rate (Section 1.1) such scores do not transfer into per-site confidence. Second, it is a two-dimensional imagery method: it finds pit-like *appearances*, not the roof-sag *topographic* signature of an intact tube whose interior is not exposed. We cite ESSA as the closest direct competitor, position our contribution as calibrated inference rather than detection, and never use its outputs as labels.

**Radar evidence.** Carrer et al. (2024) report radar evidence for a cave conduit extending below the Mare Tranquillitatis pit. This remains the only instrumented subsurface evidence on the Moon and defines the empirical ceiling of what any claim in this field can currently assert.

**Roof stability and target scales.** Structural analyses of lunar lava tubes (Blair et al., 2017; Theinat et al., 2018) bound the plausible width of stable intact tubes to roughly 60–300 m, with roof thicknesses and sag amplitudes of metres to a few tens of metres. These bounds anchor the physical scales of our detector (Section 3.2) and the interpretation of our noise-floor results (Section 4.6).

**Methodological inheritance.** Our pipeline inherits tested components from two terrestrial method papers. From Mueller et al. (2026) we take the ICP-registration and kriged distortion-correction protocol, the zero-change noise-floor discipline, and the conservative lower-bound framing. From Reichenzeller et al. (2026) we take the vertical-complexity overhang index, the per-rung threshold re-tuning protocol, the stratified detectability template, the independent-confound-covariate discipline, and the pre-registered failure-mode predictions — including the funnel-pit behaviour we indeed observe (Section 4.4).

**Analog corpus.** The NASA Planetary Pits and Caves analog dataset (Wong et al., 2014) provides ICP-registered terrestrial laser scans of skylighted lava tube systems; it is the ground-truth corpus of our benchmark (Section 2.1).

### 1.3. Scope and contributions

This paper is the benchmark the field conspicuously lacks: a surveyed-ground-truth, degradation-calibrated characterisation of how a topographic roof-sag signature survives the observing conditions of lunar orbit. It is *not* a global lava-tube detection claim, and it is *not* a gravity or radar paper — gravity and radar are confirmation layers on candidate sites, not survey detectors, and lie outside our scope. A companion data paper will carry the lunar candidate registry forward under multi-evidence accounting.

Our contributions are:

1. **LLTB-1, a calibrated terrestrial analog benchmark**: surveyed laser scans of four field sites (six map instances) degraded to 0.5–10 m ground-sample distance (GSD), re-rendered under Hapke photometry at twelve NAC-like illumination geometries, and composed with a NAC-like sensor stage — with all thresholds calibrated per rung and frozen before any degraded arm was evaluated.
2. **The first per-rung detectability metrics for the LROC NAC GSD band** on surveyed ground truth, reported as F1/precision/recall with per-rung false-positive densities, and with the predict-all collapse of the threshold tuner reported as a finding rather than hidden.
3. **A calibration-context lunar false-positive rate with exact intervals** — 3.74 FP per 10⁴ km² (Poisson-exact 95% CI [1.71, 7.10]) over 24,062.96 km² of pit-associated NAC DTMs — together with an honest accounting in which all 14 above-floor true positives are re-detections of catalogued pits and zero novel above-floor candidates exist in the calibration-context set.
4. **A residual noise-floor verdict** on published lunar DTMs: single-DTM sag inference is tenable only for amplitudes ≥ 5 m at both floor-sampling sites; 1–2 m sags require multi-evidence stacking.
5. **A failure-mode taxonomy** — funnel pits incised into rilles, leaning pit walls, shadowed interiors, large-area spillover, and deep low-vesselness depressions — with the pre-registered prediction of the funnel mode confirmed.

Everything lunar in this paper is calibrated inference with error bars. We claim no subsurface detection.

## 2. Data

### 2.1. Terrestrial analog sites

LLTB-1 is built on the NASA Planetary Pits and Caves analog dataset (Wong et al., 2014): FARO X130/X330 terrestrial laser scans, multi-station ICP-registered, of pit and cave sites at volcanic fields in the western United States. The dataset is released for research and academic use only; we do not redistribute it, and our release provides fetch and conversion scripts instead (Data availability).

We processed **four field sites, represented as six map instances**. Three of the instances sample the same trench-hosted tube — the collapsed-roof interior, the overlying cliff surface, and a downsampled cave-interior scan — so the six instances do not provide six independent terrains; site-level independence is four, not six, and leave-one-site-out validation was not performed (Section 5.4). The instances are:

- **Fieg** — a small pit-floor analog; 11.7 M points, 96 × 75 m footprint, 1.8% void cells.
- **Indian Tunnel interior (Collapse3)** — a real lava tube surveyed through its collapse trench; 16.9 M points, 44 × 57 m.
- **Indian Tunnel north surface** — the cliff surface over the same lava tube, with overhangs; 60.96 M points, 65 × 125 m. This instance is the master for the illumination and sensor experiments (Sections 3.4 and 4.5).
- **Kingsbowl** — a multi-pit panel at Craters of the Moon; 37.5 M points, 1121 × 702 m, 0.1% void cells.
- **Indian Tunnel cave interior (10× downsampled)** — the cave interior from a 10×-downsampled scan; 11.6 M points, 76 × 170 m.
- **Sheepridge** — a multi-pit panel; 23.9 M points, 173 × 186 m.

Void-cell ground truth is defined on the unperturbed master grid: cells whose local depression depth exceeds a 1.0 m threshold at 0.5 m posting. Registration of the analog clouds was validated against the dataset's own control points (Fig. 1).

### 2.2. Lunar DTM suite

The lunar side of the benchmark draws on published LROC NAC digital terrain models (DTMs) from the Planetary Data System (public domain), fetched by product ID rather than mirrored. The suite comprises **21 processed DTMs totalling 24,062.96 km²**, spanning the 2–8 m rung band, selected as pit-associated or pit-rich targets: mare pits with catalogued entries (including the Mare Tranquillitatis pit, a Mare Fecunditatis pit cluster, the Marius Hills pit, and the Mare Ingenii pit), plus four highland and impact-melt DTMs added in the final extension of the suite: two Gruithuisen-domain products (2,321 and 2,259 km²), a Marius Hills cone product (1,626 km²), and a large Tycho central-peak product (3,017 km²) — 9,222.69 km² added in total. The suite is deliberately *not* a survey sample: it is selection-biased toward catalogued pits by construction, which is why every lunar false-positive statistic we report is labelled calibration-context and not survey (Sections 3.5, 4.2, 5.4). Thirty random-mare control footprints from the project scope map have no existing NAC DTMs at all; closing that gap requires alternative-sensor DTMs (Kaguya TC, Chang'e) or new stereo processing, and is deferred to the companion data paper.

Every DTM was processed with the same frozen chain as the analog sites (Section 3), at the rungs its posting supports, and every scored local maximum is preserved in a candidate registry — 278 tier-C morphometry rows in total, of which 45 sit above the per-DTM calibration floor and 233 below it (Sections 3.5, 4.2). The 278 registry rows correspond to 117 unique morphometric features (duplicates co-located within ~30 m; median 3 rows per feature across rungs). All 278 rows derive from these 21 processed DTMs; the atlas-level coverage gap — only a subset of the ~281 catalogued pits have NAC DTMs at all — is a scope limitation (Section 5.4), and the terrains the NAC archive actually covers are summarised in Figs. 2 and 3.

## 3. Methods

### 3.1. Degradation ladder

From each registered cloud we build a 0.5 m master grid and derive rungs at 0.5, 1, 2, 5, and 10 m GSD by average downsampling. Averaging — not nearest-neighbour decimation — is mandatory here: nearest sampling thins point support at coarse rungs and fabricates both relief and voids. Sentinel-value handling follows the dataset's own structure: the published float files encode "no data" near 1e38, and we treat |x|, |y|, |z| > 1000 m as invalid, a cut justified by the Kingsbowl height histogram, in which 99.99% of valid points lie within ±1000 m and the retained outliers are exactly the cliff and overhang structure we wish to keep. Lunar DTM rungs (2–8 m) enter the same chain at their native and degraded postings.

### 3.2. Roof-sag detector

The detector is the product of two complementary responses evaluated on each rung:

- **Depression depth** — the sink-filled minus the observed surface, using the Planchon–Darboux epsilon fill. The fill algorithm is not interchangeable: breach-based fills of the Wang & Liu type drain the NoData floors of shadowed pit interiors and return near-zero depth where the true floor is ~130 m down (quantified at a lunar pit in Section 4.4), whereas the epsilon fill recovers shadowed-floor depth.
- **Frangi vesselness** — computed at physical scales of 30, 60, 100, 150, 200, and 300 m, the realistic lunar tube-width band implied by the stability bounds of Blair et al. (2017) and Theinat et al. (2018), with the black-ridge convention (a tubular void beneath the surface produces an elongated ridge-proxy response in the filled-depth surface).

The per-cell score is depth × vesselness, with local maxima taken in a 5-cell neighbourhood. Two refinements were added after the baseline runs and are reported separately wherever they differ from the frozen baseline: a ≥10° slope mask (which removes gentle-slope false positives and leaves recall unchanged) and per-rung slope-threshold tuning (which lifts F1 further; Section 4.1). A connected-component post-processing filter (v0.2), designed to suppress the large-area spillover failure mode (Section 4.4), has been developed and validated standalone but is *not* applied to the frozen results reported here.

A vertical-complexity index (VCI; Reichenzeller et al., 2026) — the Shannon evenness of the height-binned column distribution, thresholded at 0.4 with a 5-cell local-maximum filter — is computed alongside for overhang detection. As pre-registered, we expected VCI to be degenerate on rasterised 2.5-D rungs and informative only on the raw cloud; Section 4.3 confirms this.

### 3.3. Threshold calibration and evaluation protocol

Detection thresholds do not transfer across GSD — the same physical sag produces different score distributions at each posting — so thresholds are re-tuned per rung. The protocol is a per-rung cell split: within each rung, cells are partitioned 50/50 into calibration and test subsets with a fixed seed, frozen before any evaluation (and, for the degradation experiments, frozen from the baseline arm before any degraded arm existed). Thresholds are tuned on the calibration half only and applied unchanged to the test half. No site is withheld from tuning in the experiments reported here — leave-one-site-out validation was not performed (Section 5.4) — so all per-rung results are within-site detectability results, not transfer results.

Matching uses a declared radius of one cell at the rung posting, a choice consistent with the ~30 m positional accuracy of the atlas labels. Pit–candidate matching uses a 100 m radius (frozen-calibration convention); one Fecunditatis false positive lies at 138.1 m from its nearest catalogued pit and would reclassify as a true positive under a 150 m tolerance. Per-instance metrics are reported per site and rung; no cross-site threshold transfer is claimed anywhere.

Because the analog instances are small (~1.3 × 10⁻³ km² tiles at the finest rungs), we report analog false positives as an **FP-cell density** — FP × 10⁴ / (test cells × cell area) — evaluated at the tuner's solution. Where the tuner collapses to a zero threshold this is a *predict-all tile extrapolation*, a geometric property of the tile and posting, not a survey rate. The lunar survey-grade FP per 10⁴ km² rate is a different quantity and remains not measured; the calibration-context lunar rate we do report is defined in Section 3.5.

### 3.4. Illumination and sensor degradation model

The illumination and sensor experiments characterise how the production detector chain behaves under controlled degradation of the Indian Tunnel north-surface master (60.96 M points); they are benchmark results, not detection claims, and no lunar void is inferred from them. The protocol holds three things fixed. First, ground truth is fixed from the unperturbed cloud (cells with local depression depth ≥ 1.0 m on the 0.5 m master). Second, the calibration/test split is frozen from the baseline arm; the fixed-calibration tuner is left entirely alone — no threshold is re-tuned against any degraded arm, and every regression is reported as-is. Third, the entrance-trench and skylight mask is not used as sag ground truth, and these rungs are reported separately from the per-instance table of Section 4.1 so that no table mixes configurations.

The **illumination stage** re-renders the master under Hapke IMSA photometry with lunar-mare literature parameters (w = 0.15, b = 0.21, c = 0.70, h = 0.05, B₀ = 0.6 — literature values, deliberately not fitted) at twelve geometries: incidence 45°, 65°, and 85° × azimuth 0°, 90°, 180°, 270°, at nadir viewing, with ray-marched cast shadows (Fig. 4). The **sensor stage** composes after the Hapke stage: a NaN-aware Gaussian point-spread function (σ = 0.5–2.0 cells by rung) with vertical noise σ_z = 16.5 · res / SNR, calibrated so that SNR = 100 at 2 m implies 0.33 m vertical noise — anchored to the residual noise measured at the Mare Tranquillitatis pit DTM — plus 0.5% bad pixels and 2 bad lines (Fig. 5).

### 3.5. Lunar transfer and false-positive accounting

For each lunar DTM, the frozen chain produces score rasters at the supported rungs, from which local maxima are extracted into the candidate registry with per-row rung, span, depth-at-maximum, and vesselness-at-maximum. Each DTM carries a calibration amplitude floor (local A_min) anchored on the Mare Tranquillitatis pit calibration anchor and frozen thereafter — no threshold was re-tuned on any lunar product after anchoring. Rows whose score sits below the per-DTM floor are preserved in the registry as below-floor context (terrain extrapolation at highland and impact-melt sites, with two annotation families described below); rows above the floor enter the FP/TP accounting:

- A row is a **true positive** if it matches a catalogued pit within the declared radius.
- Otherwise it is a **false positive**, and the per-rung and aggregate rates are FP per 10⁴ km² with Poisson-exact (Garwood) 95% confidence intervals — appropriate for small FP counts — over the processed area.

Two annotation families keep the accounting honest. First, rows forming rings *around* a catalogued pit at multiple rungs are annotated as ring artefacts of that pit (Section 4.4), not as independent candidates; at the Mare Ingenii pit, 24 above-floor rows exist, of which 21 carry the ring-artefact annotation and 3 are pit re-detections. Second, a deep-pit low-vesselness rule flags rows with vesselness-at-maximum < 0.02 at large span: circular bowl or inverted-cone signatures rather than the elongated ridge proxy a tubular void would produce. These rows remain below-floor context unless visual inspection promotes them; none were promoted, because systematic NAC image inspection of the flagged rows is still pending (Section 5.4). All 21 DTMs are pit-associated or pit-rich, so every lunar rate reported here is a *calibration-context* rate — a measure of how the frozen chain behaves where pits are known or expected — and never a survey rate.

### 3.6. Kriging correction and noise-floor estimation

Published NAC DTMs carry registration-related long-wavelength error against LOLA tracks. Following Mueller et al. (2026), we estimate a kriged systematic-error correction from the DTM–LOLA residuals, constrained to remain low-frequency (more than 99% of correction power at wavelengths > 300 m) and to preserve pit depth to within ±10% (Figs. 6 and 7). At the Mare Tranquillitatis pit anchor the correction is small, as expected for a LOLA-registered product: check RMSE against independent tracks falls from 0.373 m to 0.327 m, establishing a residual noise floor of approximately 0.33 m at 2 m-class posting.

Detectability, however, is not set by per-pixel noise but by noise *in the sag band*. We therefore filter the corrected residual to the 60–300 m difference-of-Gaussians band — the band a 60–300 m tube-width sag occupies — and take its root-mean-square as the competing amplitude. Under a conservative project convention that a sag must exceed three times the sag-band RMS to be inferable from a single DTM, we compute verdicts per site (Section 4.6). The floor has so far been sampled at only two of the roughly 649 mare DTMs, and per-panel RMS spans 0.74–2.05 m across those panels — so the verdicts are floor-sampling results, not survey-wide guarantees, and per-DTM floors are required before any survey-wide detectability claim.

## 4. Results

### 4.1. Analog detectability across ground-sample distances

Table 1 reports the frozen baseline per-rung metrics for the six instances (pre-slope-tuning configuration throughout; the tuned variant is quoted separately below so that no table mixes configurations).

**Table 1 — Per-instance, per-rung baseline results.** F1/precision/recall on the held-out test split; FP-cell density at the tuner's solution (see Section 3.3 for the predict-all caveat). Source: per-instance summary statistics in the repository (Data availability).

| Instance | Rung | F1 | P | R | FP-cell density* | n_void | n_detect |
|---|---|---|---|---|---|---|---|
| Fieg | 0.5 m | 0.020 | 0.010 | 0.69 | 9.0e9 | 84 | 34 |
| Fieg | 2 m | 0.013 | 0.007 | 0.50 | 4.1e8 | 4 | 1 |
| Fieg | 5 m | 0.013 | 0.007 | 1.00 | 4.0e8 | 1 | 1 |
| Indian Tunnel interior | 0.5 m | 0.097 | 0.051 | 1.00 | 3.8e10 | 562 | 261 |
| Indian Tunnel interior | 1 m | 0.105 | 0.055 | 1.00 | 9.4e9 | 139 | 72 |
| Indian Tunnel interior | 2 m | 0.000 | 0.000 | 0.00 | 6.0e7 | 35 | 0 |
| Indian Tunnel interior | 5 m | 0.071 | 0.037 | 1.00 | 3.9e8 | 5 | 2 |
| Indian Tunnel north surface | 1 m | **0.277** | **0.196** | 0.474 | 5.5e8 | 211 | 55 |
| Indian Tunnel north surface | 2 m | 0.162 | 0.231 | 0.125 | 2.4e7 | 53 | 3 |
| Indian Tunnel north surface | 5 m | 0.056 | 0.029 | 1.00 | 3.9e8 | 9 | 5 |
| Kingsbowl | 5 m | 0.002 | — | — | — | — | — |
| Indian Tunnel cave interior (10×) | 5 m | 0.036 | 0.018 | 1.00 | 3.9e8 | 9 | 5 |
| Sheepridge | 5 m | 0.050 | 0.028 | 0.231 | 6.3e7 | 23 | 3 |

\* FP-cell density is FP × 10⁴ / (test cells × cell area) — a per-cell density extrapolated from ~1.3 × 10⁻³ km² analog tiles at the tuner's solution; where that solution is the zero-threshold predict-all, it is a tile-geometry property, **not** a survey false-positive rate. Kingsbowl per-cell statistics are not retrievable (the derived per-cell outputs for that instance were not retained); the F1 value shown is the frozen baseline, which predates two post-processing refinements that raise it to 0.045 (≥10° slope mask) and 0.043 (slope-tuned at a 20° mask). The tuned 2 m rung of the interior instance (threshold 0.202) returns F1 = P = R = 0.000 at n_void = 35.

Three findings organise this table.

**The best honest result.** The strongest non-trivial performance is the cliff-surface instance at 1 m: **F1 = 0.277 with precision 0.196 and recall 0.474**. Per-rung slope-threshold tuning raises F1 at every instance reported in Table 1, with the best honest tuned result **F1 = 0.362 at 1 m with a 45° slope mask** on the same instance. We quote both configurations because the tuned variant was introduced after the baseline runs; neither is cherry-picked, and both fall far short of any deployed-system requirement.

**Perfect recall is a predict-all artefact.** Recall of exactly 1.00 occurs only at rungs where the tuned threshold collapses to zero — the interior instance at 0.5/1/5 m, the north surface at 5 m, the cave interior at 5 m, and Fieg at 5 m with n_void = 1 — where predicting every cell positive trivially recalls every void. At rungs with informative (non-zero) thresholds, recall spans 0.00–0.69 (interior 2 m: 0.00 at n_void = 35; north surface 2 m: 0.125; Sheepridge 5 m: 0.231; north surface 1 m: 0.474; Fieg 0.5/2 m: 0.69/0.50). The binding constraint flips by regime: at zero thresholds it is precision (the score overflags small sinks, capping precision at 5–20%); at informative thresholds it is recall.

**FP-cell densities are posting-dominated.** Densities fall from 3.8 × 10¹⁰ at 0.5 m on the real tube to 3.9 × 10⁸ at 5 m — an almost pure cell-area effect at the predict-all solution (10⁴ / cell area) — which is precisely why we label them extrapolations rather than rates (Section 3.3) and why the connected-component filter targets this regime (Section 4.4).

### 4.2. Lunar calibration-context candidate accounting and false-positive rate

Table 2 gives the per-rung lunar accounting across the 21 processed DTMs (24,062.96 km²; calibration-context, not survey).

**Table 2 — Lunar aggregate per-rung accounting, 21 pit-associated DTMs** (calibration-context, not survey; Poisson-exact (Garwood) 95% CIs). Source: candidate registry (`data/candidate_registry.csv`) and per-rung transfer summaries (Data availability).

| Rung | n_candidates | n_fp | n_tp | n_above_floor | Area (km²) | FP per 10⁴ km² | 95% CI |
|-----:|-------------:|-----:|-----:|--------------:|-----------:|---------------:|--------|
| 2 m | 74 | 0 | 3 | 10 | 4,108.03 | 0.00 | [0.00, 7.29] |
| 4 m | 99 | 3 | 5 | 16 | 9,915.07 | 3.03 | [0.62, 8.84] |
| 5 m | 101 | 6 | 5 | 18 | 9,589.24 | 6.26 | [2.30, 13.62] |
| 8 m | 4 | 0 | 1 | 1 | 450.62 | 0.00 | [0.00, 66.48] |
| **Aggregate** | **278** | **9** | **14** | **45** | **24,062.96** | **3.74** | **[1.71, 7.10]** |

The aggregate row-based rate is **3.74 FP per 10⁴ km² (95% CI [1.71, 7.10])** over 24,062.96 km². It fell from an earlier 6.06 [2.77, 11.51] over 14,840 km² when the four highland and impact-melt DTMs were added — a purely denominator-driven improvement: the 9,222.69 km² of added terrain (Tycho 3,017; Gruithuisen 2,321 and 2,259; Marius cone 1,626 km²) produced 21 new registry rows, **every one below-floor** (18 below-floor candidates at the three Gruithuisen/Marius products — 6, 10, and 2 respectively — and 3 at the Tycho product), and not a single new false positive.

The FP numerator itself is instructive. All nine false positives sit at just two sites with catalogued pits: six at a Mare Fecunditatis pit cluster (sag amplitudes 155, 140, and 34 m; 138–552 m from the nearest catalogued pit) and three at the Mare Tranquillitatis pit DTM (amplitudes 95.4, 57.4, and 48.8 m); the three false-positive rows form two spatial structures: a row pair co-located within 17 m (one structure scored at two rungs) and a third row 133 m away. The single-site rate at the Tranquillitatis DTM is 240.41 [49.58, 702.58] per 10⁴ km² — an honest illustration of how concentrated calibration-context FP production is, and why the aggregate must not be read as an expectation over random mare.

The accounting is equally explicit about the true positives: **all 14 above-floor true positives are re-detections of catalogued pits at above-floor scores; zero novel above-floor candidates exist in the calibration-context set.** The 45 above-floor rows comprise these 14 re-detections, the 9 false positives, 21 ring-artefact rows around the Mare Ingenii pit (annotated, not independent candidates; Section 4.4), and 1 funnel-mode row at the Marius Hills pit (Section 4.4). The remaining 233 registry rows sit below their per-DTM floors and are preserved as context.

### 4.3. Vertical complexity on 2.5-D rungs

The VCI overhang index behaves exactly as pre-registered. At Fieg, the raw-cloud VCI reaches a maximum of 0.61 with 188 cells above the 0.4 threshold and 21 centroids — real three-dimensional wall structure is recovered. At the interior instance, the rasterised rung yields a maximum VCI of 0.0: the cave floor is genuinely 2.5-D after rasterisation, and the overhang signal lives only in the original cloud. VCI is therefore degenerate on all raster rungs and useful only on the raw cloud — a negative result we report because it bounds what any column-statistics method can extract from gridded lunar DTMs, where no raw cloud exists at all.

### 4.4. Failure modes

Five failure modes, one of them pre-registered, characterise the limits of the score chain:

1. **Funnel pits incised into rilles (pre-registered).** Pits formed *on* a sinuous rille drain sideways: the sink-fill spills into the adjacent rille channel and muddles the score. The Marius Hills pit shows the predicted behaviour — top score 5.04 with vesselness only 0.05, the depression leaking into the adjacent rille rather than closing on the pit. This mode was predicted before observation; its confirmation is a validation of the benchmark's diagnostic value.
2. **Leaning pit walls.** Where pit walls lean rather than fracture vertically, VCI flattens and detection degrades — an expected drop of roughly 50% in F1 relative to vertical walls, observed at the cliff overhangs of the north-surface instance.
3. **Shadowed pit interiors.** The fill-algorithm contrast of Section 3.2 is quantified at the Mare Tranquillitatis pit: the epsilon fill recovers 129.7 m against 105 m catalogued, and a Sinus Iridum pit shows a 2.32× overshoot — a fill-to-spill geometry at large aspect ratio, a documented behaviour of the method rather than a failure (Figs. 9 and 10).
4. **Large-area spillover.** Kingsbowl's 1121 × 702 m multi-pit panel drives FP-cell density to ~4 × 10⁸ even at 5 m: at the predict-all solution the density is almost purely geometric (10⁴ / cell area), because a panel of that extent contains many local maxima at 5 m pixel scale. This is the failure mode the connected-component filter (v0.2) is designed to suppress; it is not applied to the frozen results here.
5. **Deep-pit low-vesselness depressions.** Rows with vesselness-at-maximum < 0.02 at large span carry a circular bowl or inverted-cone signature — not the elongated ridge proxy a tubular void would produce. The family appears at the Gruithuisen-mare product (top score 0.00098; spans 739.5–7888.1 m; 10 rows), the Marius cone product (top score 0.01865; span 1352.7 m; 2 rows), and — without the deep-pit descriptor — the second Gruithuisen product (top score 0.00088; spans 257.8–1031.3 m; 6 rows). All 18 rows sit below their per-DTM calibration floors, contribute zero false positives, and are annotated for visual inspection before any status change. The family is separated cleanly from the **central-peak-relief** false-positive family (moderate vesselness 0.05–0.18 at small spans, on Tycho, King, and fresh impact-melt central peaks): the two families occupy opposite quadrants of the (span, vesselness) plane — deep circular depressions show low vesselness at large spans, central-peak relief shows moderate vesselness at small spans.

A sixth, bookkeeping-level family completes the taxonomy: **ring artefacts**. At the Mare Ingenii pit, 21 ring-annotated above-floor rows form rings around the catalogued pit at multiple rungs (24 above-floor rows exist at the site, of which 21 carry the ring-artefact annotation and 3 are pit re-detections). They are annotated as artefacts of that pit, not counted as 21 candidates — and the same terrain carries rocky-ejecta counter-evidence (rock-ankle fraction 0.98% versus a 0.50% local-mare background, roughly twofold), which is why the site is treated as negative context rather than as candidate-bearing.

### 4.5. Illumination × sensor degradation

Table 3 reports the composed degradation arms on the north-surface master, with the +10° slope mask and the frozen split throughout (test F1; n_void = 871/211/53/8 at 0.5/1/2/5 m).

**Table 3 — Composed degradation arms, test F1 (+10° slope mask, frozen split).** Hapke columns are means across the twelve geometries with per-geometry ranges in parentheses. Source: composed-arm summary statistics in the repository (Data availability).

| Rung | Baseline | Noise-only (i = 65°) | Sensor-only (SNR 100) | Hapke mean (range) | Hapke + sensor (SNR 100) mean (range) |
|-----:|---------:|---------------:|-------------------:|-------------------:|--------------------------------:|
| 0.5 m | 0.349 | 0.300 | 0.309 | 0.096 (0.051–0.122) | 0.096 (0.051–0.122) |
| 1 m | 0.276 | 0.252 | 0.262 | 0.101 (0.052–0.124) | 0.103 (0.052–0.125) |
| 2 m | 0.254 | 0.179 | **0.122** | 0.115 (0.066–0.148) | 0.109 (0.067–0.138) |
| 5 m † | 0.154 | 0.154 | 0.175 | 0.144 (0.000–0.179) | 0.136 (0.000–0.175) |

† n_void = 8; not comparable across rungs.

**Illumination dominates.** Across the twelve Hapke geometries, mean test F1 at 0.5 m falls from 0.349 to 0.096, with rung-wise means (ranges) of 0.096 (0.051–0.122) at 0.5 m, 0.101 (0.052–0.124) at 1 m, 0.115 (0.066–0.148) at 2 m, and 0.144 (0.000–0.179) at 5 m. The mechanism is **shadow voiding of void labels**, not photometric noise: the azimuth-mean fraction of void cells lost to cast shadows is 62% at i = 45°, 75% at i = 65°, and 92% at i = 85° (per-azimuth ranges 52–68%, 67–80%, 85–95%). A noise-only control at i = 65° (noise applied, no shadow voiding) costs only 0.02–0.08 F1 (0.349 → 0.300 at 0.5 m) — a generous noise upper bound, so the shadow-dominance conclusion is conservative.

**Attribution is qualified.** The zero-threshold predict-all solution in every full-Hapke arm is a collapse of the fixed-calibration pipeline, not proven information loss at moderate incidence: slope-masked predict-all recall at i = 45–65° spans 0.557–1.00 across rungs and azimuths (0.73–0.97 for i = 45° at 0.5–1 m). At i = 85° the recall ceiling is genuine label voiding: 0.16–0.44 at the 0.5 m rung (1 m reaches 0.54; 5 m reaches 0.60 with the n_void = 8 caveat). No shadow-aware re-tuning was attempted, by protocol; we do not describe this as detector collapse.

**The sensor stage is regime-dependent.** Sensor-only degradation costs little at 0.5–1 m (−0.040 / −0.014) but regresses the 2 m rung from 0.254 to 0.122 — approximately halved, and we treat it as real. The SNR ordering at 2 m is non-monotone (SNR 50: 0.069; SNR 100: 0.122; SNR 200: 0.074); with n_void = 53 (2 m) and 8 (5 m) this ordering is small-sample noise, not sensor physics. At 5 m the effect is ~nil (0.154 → 0.175 sensor-only; n_void = 8), consistent with shadow voiding being a 0.5–2 m phenomenon on this benchmark. Composition is approximately additive where both stages act (2 m: 0.115 → 0.109); at 0.5–1 m the Hapke collapse dominates so completely that the sensor stage changes nothing (0.096 → 0.096; 0.101 → 0.103). Nothing was re-tuned to rescue any arm.

**Analog-scope caveat.** The label population here is trench-hosted — the cave interior is seen through the collapse trench and skylights — which is exactly the shadow-prone population. A roofed sag on open mare, the actual lunar target, is untested by this experiment and would be less shadow-affected; the result should be read as a worst-case bound on illumination sensitivity, not as a prediction for open-mare surveys.

### 4.6. Residual noise floor on lunar DTMs

On published lunar NAC DTMs — the target regime — the sag-band (60–300 m) residual RMS after kriging correction is 1.245 m at the Mare Tranquillitatis pit and 1.379 m at the Marius Hills pit, pooled. Under the 3× sag-band-RMS convention (Section 3.6), single-DTM detectability holds for sag amplitudes **A ≥ 5 m at both** floor-sampling sites (3σ = 3.74 and 4.14 m respectively; A ≥ 4 m at the quieter site), and **A = 1–2 m is not single-DTM detectable** — such sags require multi-evidence stacking (Fig. 8). Two caveats bound these verdicts: the floor has been sampled at only two of roughly 649 mare DTMs, and per-panel RMS spans 0.74–2.05 m within those two (a local Marius panel implies 3σ ≈ 6.1 m). Per-DTM floors are therefore required before any survey-wide detectability statement, and the lunar survey-grade FP rate per 10⁴ km² remains not measured until a calibrated search is run over a genuinely sampled DTM population.

## 5. Discussion

### 5.1. Implications for instrument requirements

The degradation ladder and noise floor jointly bound what future missions must carry to find intact tube roofs. Three concrete implications follow directly from Sections 4.1, 4.5, and 4.6. First, a 5 m sag amplitude is recoverable at every ladder rung in the LROC NAC range — posting is not the binding constraint at that amplitude. Second, 1–2 m sags are not single-DTM detectable on published NAC DTMs under the 3× convention; the remedy is multi-evidence stacking (illumination-consistent repeat observations, co-registered gravity or radar), not finer ground-sample distance alone. Third, ~60 m posting is below the curve everywhere: a single pixel cannot sample a 60–300 m sag feature, so the Kaguya TC SLDEM2015 (~59 m) cannot directly detect roof sag at all — global coarser archives constrain context, not candidates. Within the NAC band, illumination geometry matters more than sensor noise (Section 4.5): mission planning for tube prospecting should prioritise multiple illumination geometries over marginal SNR improvements, because shadow voiding — not photometric noise — dominates the error budget at NAC geometries on trench-hosted targets.

### 5.2. Re-detections, not discoveries

The lunar accounting of Section 4.2 deserves emphasis because it inverts the usual presentation of candidate lists. **All 14 above-floor true positives are re-detections of catalogued pits at above-floor scores; zero novel above-floor candidates exist in the calibration-context set.** Read as a search, the frozen chain found nothing new — and that is the correct result to report, for two reasons. First, the 21-DTM population is pit-associated by construction, so the informative quantity is not novelty but behaviour: the chain re-finds known pits (14 of them, above floor), avoids false positives across 9,222.69 km² of highland and impact-melt terrain, and concentrates its errors at two pit-bearing sites. Second, the base rate of Section 1.1 makes any claim of novel discovery from single-method morphometry untenable — at ~20 tube-relevant features in the population, a handful of above-floor scores at uncatalogued locations would be far more likely false positives than discoveries. A novel candidate in this framework would require, at minimum, an above-floor score at a location without a catalogued pit, surviving visual inspection and a second, independent evidence leg; none exist in this set. The nine above-floor false positives (Section 4.2) remain pending systematic visual inspection, and we report them as calibration-context findings, not as candidate voids.

### 5.3. Positioning relative to imagery-based detectors

Our results quantify why detection-style reporting is insufficient at the lunar base rate, and what a calibrated alternative looks like in practice. The ESSA detector of Le Corre et al. (2025) reports strong F1 against Lunar Pit Atlas labels — but those are detection scores against the training label population, with no per-claim void probability and no false-positive-per-area reporting, and the method responds to pit appearance in 2D imagery rather than to the topographic sag signature of a roofed, unexposed tube. LLTB-1 complements that line of work: it fixes surveyed ground truth, degrades it under controlled photometry and sensor models, reports per-rung detectability with the tuner's failures included, and expresses lunar results as a calibration-context FP rate with exact intervals (3.74 [1.71, 7.10] per 10⁴ km² over 24,062.96 km²) plus an explicit statement of what is not measured. The two approaches are not competitors for the same claim: imagery methods find candidate entrances; calibrated morphometry bounds when a roof signature can be inferred at all. A survey-grade synthesis would combine them and report per-claim probabilities with area-normalised false-positive rates — the reporting standard this paper is built to enable.

### 5.4. Limitations

The honesty apparatus of this benchmark is a results section of its own; we state each limit explicitly.

- **Selection-biased lunar sample.** The 21 processed DTMs are pit-associated or pit-rich by construction. The 30 random-mare control footprints in the project scope map have no existing NAC DTMs, so no survey-grade FP rate is possible from the current archive; all 278 registry rows derive from these 21 processed DTMs, and the atlas-level coverage gap — only a subset of the ~281 catalogued pits have NAC DTMs at all — is itself a scope limitation. Every lunar rate in this paper is calibration-context only. A survey-grade claim would require alternative-sensor DTMs (a different pipeline, deferred to the companion data paper) or a substantially larger NAC DTM population.
- **Per-row false-positive accounting.** FP counts are per candidate row; the same physical depression scored at two rungs is counted twice where both rows fall above floor. The registry now annotates rung duplicates (278 rows → 117 unique features; 45 above-floor rows → 21 unique features); the frozen row-based accounting of Table 2 is retained, with the full unique-feature re-accounting deferred to the companion data paper. The rates reported here are therefore an upper-bound-style accounting under the row definition, and the per-rung table (Table 2) is the finest granularity at which the definition is unambiguous.
- **Four field sites, six instances, one tube.** The analog corpus provides four independent field sites; three of the six map instances sample the same trench-hosted tube, and the Hapke/sensor arms run on that one instance alone. Leave-one-site-out validation was not performed; it would become necessary — and is planned — before any claim of transfer generalisation, i.e. that thresholds and scales calibrated on some field sites carry to a wholly withheld site. All per-rung results here are within-site detectability results.
- **Degradation arms on one trench-hosted instance.** Illumination and sensor results (Section 4.5) inherit the trench-hosted label population; a roofed sag on open mare is untested, and the other five instances remain idealised topography (no photometric or sensor stage).
- **Single tube-geometry class.** A real lunar roof is not necessarily a terrestrial-analog roof; angular rille intersections, compound sink-fill, and partial roof-collapse modes are not exercised.
- **Low absolute F1, by construction of the honest reporting.** The F1 values are low because the tuner collapses to predict-all at several rungs (recall trivially 1.00, precision 5–20%) while at informative thresholds recall (0.00–0.69) binds. Score-threshold and connected-component post-processing is the highest-leverage remediation and is in progress (v0.2 filter; Section 4.4).
- **Small FP counts, no a-priori power calculation.** The aggregate rate rests on nine false positives; a ±50% precision target on a 1% FP-rate estimate would require on the order of 16,000 FP trials — roughly 40× the current calibration-context population. A formal power analysis accompanies the random-mare closure in the companion paper.
- **Confound covariates not exercised as a formal null test.** Slope and illumination are partially addressed (the +10° slope mask; the 12-geometry Hapke grid), but a formal null test over slope × aspect × illumination × DTM noise (the independent-confound-covariate discipline of Reichenzeller et al., 2026) has not been run as an explicit protocol arm.
- **Self-validated kriging correction.** The distortion correction is validated against independent LOLA tracks at the Mare Tranquillitatis anchor (RMSE 0.373 → 0.327 m) but has not been cross-checked against an independent absolute-elevation reference; the coarser global archives sit below the detectability curve for 60–300 m features (Section 5.1) and cannot serve as that reference.
- **Noise floor sampled at two sites.** The A ≥ 5 m verdict rests on 2 of ~649 mare DTMs with per-panel RMS spanning 0.74–2.05 m (Section 4.6).
- **Visual inspection pending.** The nine above-floor false positives and the deep-pit low-vesselness rows await systematic NAC image inspection; no row can change status before that inspection is recorded.
- **Retrievability gaps.** Kingsbowl per-cell statistics were not retained and only its F1 history is corroborated (Table 1 note); the failure is documented rather than papered over.

### 5.5. Future work

The degradation budget of Section 4.5 dictates the two highest-leverage next steps: multi-illumination stacking over top candidates — a real topographic depression is illumination-consistent where albedo artefacts are not — and calibrated thresholding and fusion, so that thresholds are set by calibration data rather than collapsing under shadow voiding. Both target the documented failure mode. Beyond them: the connected-component filter enters the production chain; leave-one-site-out validation runs across the four field sites; the random-mare control population closes the selection-bias gap (via alternative-sensor DTMs or new stereo processing), converting the calibration-context FP rate into a survey rate; and per-DTM noise floors replace the two-site pooled verdict. A second, independent evidence leg (gravity or radar at candidate scale) is the prerequisite for any tier above morphometric inference.

## 6. Conclusions

We built LLTB-1, a calibrated benchmark that degrades surveyed terrestrial laser scans of four volcanic-field sites (six map instances) to lunar-observing conditions and measures what a depth × vesselness roof-sag detector can and cannot infer. The measurable conclusions are:

1. On surveyed ground truth, the best honest per-rung result at NAC-class posting is F1 = 0.277 (precision 0.196, recall 0.474) at 1 m, lifted to 0.362 by per-rung slope-mask tuning; perfect recall occurs only at predict-all thresholds, and at informative thresholds recall spans 0.00–0.69. Topographic roof-sag inference from a single observation at NAC conditions is, at present, a weak-signal discipline.
2. Illumination dominates the degradation budget: mean F1 at 0.5 m falls from 0.349 to 0.096 across twelve NAC-like geometries through shadow voiding of void labels (62–92% of labels voided by incidence 45–85°), while a NAC-like sensor stage alone halves the 2 m rung (0.254 → 0.122). The effect is a 0.5–2 m phenomenon on trench-hosted targets; roofed sags on open mare are untested.
3. On published lunar DTMs, the sag-band residual noise floor makes single-DTM inference tenable only for sag amplitudes ≥ 5 m at both floor-sampling sites; 1–2 m sags require multi-evidence stacking. Coarse global topography (~60 m posting) sits below the detectability curve for 60–300 m features.
4. Across 21 pit-associated lunar DTMs (24,062.96 km²), the row-based calibration-context false-positive rate is 3.74 per 10⁴ km² (Poisson-exact 95% CI [1.71, 7.10]); all nine false positives sit at two pit-bearing sites; all 14 above-floor true positives are re-detections of catalogued pits, and zero novel above-floor candidates exist in the calibration-context set.
5. The per-claim inference framing — calibrated scores, area-normalised false-positive rates with exact intervals, and explicit statements of what is not measured — is the contribution that survives the lunar base rate, and the reporting standard we propose for the field.

The Tranquillitatis radar conduit remains the only instrumented subsurface evidence on the Moon (Carrer et al., 2024). Nothing subsurface is verifiable today, and every lunar result in this paper is calibrated inference with error bars — never verified detection.

## Data availability

The NASA Planetary Pits and Caves analog dataset (Wong et al., 2014) is third-party data licensed for research and academic use only; it is not redistributed here, and fetch and conversion scripts are provided instead. LROC NAC DTMs were obtained from the NASA Planetary Data System (public domain) and were fetched by product ID rather than mirrored. The derived candidate registry (`data/candidate_registry.csv`, 278 rows), all per-rung and per-arm summary statistics underlying every table and figure, the processing methods documentation, and the analysis code — the roof-sag detector (LLTB-1 v0.5) and the connected-component post-processing filter (v0.2, not applied to the frozen results reported here) — are available from the authors and via repository-on-request. All lunar score thresholds use an amplitude floor calibrated on the Mare Tranquillitatis pit calibration anchor (TRANQPIT1) and frozen thereafter: no threshold was re-tuned on any lunar product after anchoring.

## Acknowledgements

The analog benchmark is built on the NASA Planetary Pits and Caves analog dataset (Wong et al., 2014), used here under its research/academic-use licence. We thank the LROC NAC team for the published digital terrain models on which the lunar transfer and noise-floor analyses rest, and the DLR Institute of Data Science for the open publication of the Mueller et al. (2026) and Reichenzeller et al. (2026) methods and code that this pipeline inherits. No Chandrayaan data were used in this work.

## CRediT author contributions

**LUNARVOID team:** Conceptualisation, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing — original draft, Writing — review & editing, Visualisation, Supervision, Project administration, Funding acquisition.

## Declaration of competing interests

The authors declare no competing interests.

## References

Blair, D.M., Chappaz, L., Sood, R., Melosh, H.J., et al. (2017). The structural stability of lunar lava tubes. *Icarus* 282, 47–55. doi:10.1016/j.icarus.2016.10.008.

Carrer, L., Pozzobon, R., Sauro, F., Patterson, G.W., Hiesinger, H., and the Mini-RF team (2024). Radar evidence of an accessible cave conduit on the Moon below the Mare Tranquillitatis pit. *Nature Astronomy* 8(9), 1119–1126. doi:10.1038/s41550-024-02302-y.

Le Corre, D., Mason, N., Bernard-Salas, J., Mary, D., & Cox, N. (2025). New candidate cave entrances on the Moon found using deep learning. *Icarus* 441, 116675. doi:10.1016/j.icarus.2025.116675.

Mueller, R., et al. (2026). Kriged distortion correction after ICP registration on snow-covered UAV photogrammetric point clouds. *Arctic Science* 12:1–23. doi:10.1139/as-2025-0062.

Reichenzeller, E., et al. (2026). Vertical Complexity Index for overstory tree detection in UAV-LiDAR and SfM forest plots. *Forests* 17(8), 807. doi:10.3390/f17070807.

Theinat, A.K., Modiriasari, A., Bobet, A., Melosh, J., Dyke, S., Ramirez, J., Maghareh, A., Gomez, D., et al. (2018). Geometry and structural stability of lunar lava tubes. AIAA SciTech 2018; paper 2018-5185. doi:10.2514/6.2018-5185.

Wagner, R.V. & Robinson, M.S. (2021). Lunar Pit Atlas: a morphometric compilation of catalogued lunar pits. *LPSC 52*, Abstract #2530.

Wong, U., Whittaker, R., Jones, J. & Whittaker, W. (2014). NASA Planetary Pits and Caves analog dataset release. NASA Ames Research Center. https://ti.arc.nasa.gov/dataset/caves
