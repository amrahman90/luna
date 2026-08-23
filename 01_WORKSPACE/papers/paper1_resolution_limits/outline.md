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

## v1.0 additions (2026-08-23, Cycles 1-2)

- §3.3.1 (new): Cycles 1-2 update — TYCHOPK 1.44 GiB + 3 deferred DTMs
  processed locally; 21 score rasters + 27 GeoTIFFs total; new
  `deep-pit low-vesselness` fall-back annotation rule (skeptic Cycle 1).
- T1a (new): lunar aggregate per-rung table at N=21 (n_above_local_floor
  45 / 14 inferred / 233 below-floor; aggregate FP 3.74 [1.71, 7.10] per
  10⁴ km² over 24,063 km²; calibration-context, NOT survey). Located
  in §4.2 of main.md.
- §4.4 new entry: `deep-pit low-vesselness` failure-mode classification
  (frangi@score_max < 0.02 AND depth@score_max ≥ 100 m; circular
  depression, not tubular).
- §1.1, §5.2, §6: updated to ~281 catalogued pits (Wagner & Robinson
  2021), 278 tier-C registry rows (45 above-floor; 233 below-floor
  preserved); Cycles 1-2 + G2 PARTIAL closure narrative.
- References section added: 10 entries, author-year style, alphabetical
  by first author (Blair 2017, Carrer 2024, Chwala 2024, Le Corre 2025,
  Mueller 2026, Reichenzeller 2026, Theinat 2020, van Ewijk 2011,
  Wagner & Robinson 2021, Wong 2014). Zotero attach pending.

## v1.0 submission status

- Verifier PASS-with-notes (1 submission blocker: References; added).
- Skeptic SOUND-with-objections (4 language fixes applied).
- 0 forbidden phrases; 8 "calibration-context"; 11 "Cycles 1-2";
  5 "Tranquillitatis radar conduit"; 11 "278"; 4 "3.74 [1.71, 7.10]".
- Submission target: Remote Sensing of Environment / ISPRS Journal.
- Submission-ready modulo: (a) G2 user pass decision; (b) Zotero
  attach of the 10 References.
