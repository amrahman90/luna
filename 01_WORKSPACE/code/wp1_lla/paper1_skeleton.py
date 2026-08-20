"""LLTB-1 Paper 1 skeleton (Z1, Task 16; v5 publication strategy #1).

Title, target venue, abstract, sections, figure plan, and the actual
results-narration drafts populated from the v0.1 outputs once they
exist. This is the paper the field most conspicuously lacks (per v5
Section 12): a public degradation ladder + detectability curve for
lava tube signatures in orbital topography.

Skeleton only — fleshed out incrementally; tables and figures are
populated as the corresponding outputs land. Supersedes nothing.
"""
from pathlib import Path
from datetime import date

REPO = Path(__file__).resolve().parents[3]
PAPERS = REPO / "01_WORKSPACE" / "papers" / "paper1_resolution_limits"
PAPERS.mkdir(parents=True, exist_ok=True)


def write_main():
    text = f"""# Detectability limits for lava tube roof signatures in orbital
# topography: the LLTB-1 calibrated benchmark

**Target venue:** Remote Sensing of Environment / ISPRS Journal
(v5 publication strategy #1, benchmark-paper category).
**Authors:** LUNARVOID team.
**Date:** {date.today().isoformat()} (draft).
**Status:** skeleton — populated as Z1 outputs land.

## Abstract (working draft, ~200 words)

We characterise the detectability of lava-tube roof signatures in
orbital topography by degrading surveyed terrestrial analog point
clouds to lunar-observing conditions and applying a roof-sag detector
depression-depth + Frangi-vesselness pipeline. The LUNARVOID
Terrestrial Benchmark v0.1 (LLTB-1) ships with five analog sites
(NASA Planetary Pits and Caves dataset, Wong 2014), five GSD rungs
(2 cm -> 0.5 m -> 2 m -> 5 m -> 60 m), a per-rung re-tuned
detection threshold (the v5 I9 protocol), and a stratified
detectability curve as a function of feature size. At 2 m / 5 m
posting (the LROC NAC range), recovered F1 sits at X.X with Y.Y
false positives per 10^4 km^2. The curve directly specifies
camera and altimeter requirements for future missions seeking
intact lava tube roofs and frames the per-claim inference
probabilities required for honest reporting under the brutal
~20-positive / ~240,000-tile mare base rate. The benchmark is
code + fetch-script + derived degraded rasters only; the raw
analog data remains research-use-only and is not redistributed.

## 1. Introduction

### 1.1 The base-rate problem
- ~20 tube-relevant lunar pits, ~281 catalogued, zero verified
  negatives (v5 Section 1; Pit Atlas via Wagner & Robinson).
- A 1% FP rate over 240,000 mare tiles -> precision near 0.8%.
- Detection framing rewards wrong summary statistics; we report
  FP per 10^4 km^2 instead, plus a stratified curve vs feature
  size (v5 Section 9 mandatory reporting).

### 1.2 What this paper is and is not
- IS: the benchmark the field most conspicuously lacks.
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
- NASA Pits and Caves analog dataset (Wong 2014).
- Research-use only — LLTB-1 ships *code + fetch-script +
  derived degraded rasters only*. Derived rasters are
  regenerable from the public fetch.

### 3.2 Degradation ladder
- Master 0.5 m grid from the cloud; rungs 0.5, 2, 5, 60 m
  (the 2 cm rung is included for the v0.2 release).
- Average downsampling (NOT nearest, which thins point
  support — v5 Task 13.1).
- Hapke photometry re-rendering and NAC-like MTF + sensor
  noise: deferred to v0.2 (Blender OSL / ASP SfS).
- VCI: Shannon evenness of the height-binned column point
  distribution; threshold 0.4 (terrestrial default); 5-cell
  local-max filter (Reichenzeller 2026 / van Ewijk 2011).

### 3.3 Sag detector
- Depression depth = sink_filled(DTM) - DTM
  (Planchon-Darboux epsilon fill, not Wang & Liu — see
  `notes/2026-08-19_task3_transqpit1_fill_variants.md` for
  the NoData-floor failure mode on lunar shadows).
- Frangi vesselness at physical scales 30, 60, 100, 150,
  200, 300 m (the realistic lunar tube-width band per
  Blair / Theinat / Chwala).
- Per-cell score = depth * vesselness; local-maxima at
  5-cell neighbourhood.
- Per-rung re-tuning of the score threshold on a 50% split
  (I9 — thresholds do not transfer across GSD).

### 3.4 Evaluation protocol
- Splits by SITE (never by tile) per v5 Section 9.
- Matching radius: declared 1 cell at the rung posting.
- Stratified by feature size: cells in four quartiles of
  the local depth distribution; Wilcoxon rank-sum on F1.
- FP per 10^4 km^2 as the primary false-positive rate.

## 4. Results
### 4.1 Detectability curve
- Figure 1 (auto-generated at `data/outputs/wp1/detectability_curve.png`):
  P(detect) vs GSD, with confidence intervals from a 5-fold
  per-site split (added in v0.2).
- The headline number: at 2 m / 5 m posting, F1 = ?, FP/10^4
  km^2 = ?. Populated by hand from `sag_summary.json` after
  the v0.1 run completes.

### 4.2 Per-rung F1
- Table 1 (auto-generated at
  `data/outputs/wp1/per_rung_metrics.csv`): GSD, n cells,
  threshold, F1, precision, recall, FP/10^4 km^2.
- Expected: threshold trajectory per v5 I9; F1 drops with
  GSD as the depth signal aliases below the 60-300 m band.

### 4.3 VCI for overhangs
- Figure 2 (`plans/figures/vci_overview.png`): the VCI
  histogram + raster for the best-resolved site.
- The qualitative finding: VCI is degenerate over 2.5D
  rasterised rungs but recovers the overhang signature on
  the original cloud — direct evidence for the v5 I8
  pre-registered transfer.

### 4.4 Failure modes
- FUNNEL PIT (I14 pre-registered): expected to fail the
  depression-depth primitive on small rungs. Documented in
  `notes/2026-08-19_task4_sweep_notes.md` — same mode on
  lunar data.
- LEANING PIT WALL (I14): VCI flattens, expected to drop
  F1 by ~50% relative to vertical walls.
- SHADOWED PIT INTERIOR: Wang & Liu drains; the
  Planchon-Darboux epsilon fill recovers the lunar
  pit depth (TRANQPIT1: 129.7 m recovered, catalogued
  105 m; Sinus Iridum 2.32x overshoot = fill-to-spill
  geometry, not failure).

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
- 5 analog sites is few; per-site leave-one-out is the
  smallest defensible validation, done in v0.2.

## 6. Conclusion
- LLTB-1 v0.1 sets the baseline: detectability curve,
  per-rung metrics, VCI behaviour, failure modes. The
  per-claim inference framing (v5 Section 9) is the
  contribution that survives the brutal base rate.

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
  `code/wp1_lla/convert_f32.py`.
- LROC NAC DTMs: PDS public domain, fetched by product ID.
- Code: open at the LUNARVOID repository.
"""
    (PAPERS / "main.md").write_text(text)
    print(f"wrote {PAPERS / 'main.md'}")


def write_outline():
    text = """# LLTB-1 Paper 1 — figure and table outline

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
"""
    (PAPERS / "outline.md").write_text(text)
    print(f"wrote {PAPERS / 'outline.md'}")


if __name__ == "__main__":
    write_main()
    write_outline()
