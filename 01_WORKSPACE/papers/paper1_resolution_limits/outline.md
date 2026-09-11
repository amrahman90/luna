# Paper 1 — manuscript outline (v2.0, journal format)

Rewritten 2026-09-06 per Next-Level Plan v2 Phase A1 (+A3/A4/A5): v1.2
internal gate-report format → submission-shaped IMRaD manuscript for
*Remote Sensing of Environment* / *ISPRS Journal*. All numbers carried
over unchanged from main.md v1.2; no new scientific claims.

## Section map (v1.2 → v2.0)

| v2.0 section | Content | v1.2 source |
|---|---|---|
| Title page | title, authors (placeholder), keywords | v1.2 header (venue/status block stripped) |
| Abstract | ≤300 words, single paragraph, all headline numbers | v1.2 Abstract (A3 sentence added; A4 site count added) |
| 1.1 Base-rate problem | ~20/~300 pits, 240k tiles, 0.8% precision, FP per 10⁴ km² | v1.2 §1.1 |
| 1.2 Related work | Atlas, ESSA, radar, stability bounds, inherited methods, analog corpus | v1.2 §2 (scaffolding refs removed) |
| 1.3 Scope & contributions | 5 contributions; IS/IS-NOT framing | v1.2 §1.2 |
| 2.1 Analog sites | four field sites, six map instances (A4), per-instance stats | v1.2 §3.1 |
| 2.2 Lunar DTM suite | 21 DTMs, 24,062.96 km², selection bias stated | v1.2 §3.3.1 + §5.2 sample-size bullet |
| 3.1 Degradation ladder | rungs, average downsampling, sentinels | v1.2 §3.2 |
| 3.2 Roof-sag detector | PD fill vs Wang & Liu, Frangi scales, slope mask, CC filter v0.2 | v1.2 §3.3 |
| 3.3 Threshold protocol | per-rung 50/50 cell splits, fixed seed, matching radius; FP-cell-density definition | v1.2 §3.3/§3.4 (A5: split described as cell-level, not site-level) |
| 3.4 Illumination & sensor model | Hapke IMSA 12 geometries, PSF/σ_z model, fixed protocol | v1.2 §4.5(a,b,c) protocol parts |
| 3.5 Lunar transfer & FP accounting | frozen A_min anchor, Garwood CIs, ring-artefact + deep-pit annotations | v1.2 §3.3.1/§4.4 annotation rules |
| 3.6 Kriging & noise floor | RMSE 0.373→0.327 m, 60–300 m band, 3× convention | v1.2 §4.5(e) |
| 4.1 Analog detectability (Table 1) | per-instance per-rung; best honest 0.277/0.362; predict-all analysis | v1.2 §4.2 Table 1 |
| 4.2 Lunar accounting (Table 2) | per-rung 2/4/5/8 m; aggregate 3.74 [1.71, 7.10]; A3 sentence | v1.2 §4.1/§4.2 Table 1a |
| 4.3 VCI | degenerate on 2.5-D rungs | v1.2 §4.3 |
| 4.4 Failure modes | funnel, leaning walls, shadowed interiors, spillover, deep-pit low-vesselness, ring artefacts | v1.2 §4.4 |
| 4.5 Illumination × sensor (Table 3) | composed arms, shadow voiding, attribution, analog-scope caveat | v1.2 §4.5(b,c) |
| 4.6 Noise floor | 1.245/1.379 m pooled, A≥5 m verdict, 2-of-649 caveat | v1.2 §4.5(e)/§5.1 |
| 5.1 Instrument implications | A≥5 m; 5 m recoverable all rungs; ~60 m below curve | v1.2 §5.1 |
| 5.2 Re-detections, not discoveries | A3 discussion; what a novel candidate would require | new framing of A3 fix |
| 5.3 Positioning vs imagery detectors | ESSA contrast; inference vs detection | v1.2 §2 + cover letter positioning |
| 5.4 Limitations | 12 explicit limits incl. A4 LOO-not-performed + criterion, A2 deferral sentence | v1.2 §5.2 (rephrased, none deleted) |
| 5.5 Future work | stacking, fusion, CC filter, LOO, random-mare | v1.2 §4.5(d)/§6 |
| 6. Conclusions | 5 numbered conclusions + claim-discipline close | v1.2 §6 |
| Data availability | licences, registry (`data/candidate_registry.csv`), software versions (LLTB-1 v0.5 + CC filter v0.2), frozen TRANQPIT1 anchor | v1.2 §"Data and code availability" + compressed scaffolding |
| Acknowledgements / CRediT / Competing interests | standard | v1.2 equivalents |
| References | the 8 verified entries, verbatim, no annotations | v1.2 References |

## Tables

| Tag | Content | Source artifacts |
|---|---|---|
| T1 | Per-instance per-rung analog results (F1/P/R, FP-cell density, n_void) | per-instance sag summaries |
| T2 | Lunar per-rung accounting (2/4/5/8 m; aggregate 278/9/14/45) | `data/candidate_registry.csv` + transfer summaries |
| T3 | Composed degradation arms (baseline/noise/sensor/Hapke/composed) | composed-arm summary statistics |

## Figures (10, matching committed `figs/` set)

| Tag | File | Cited in |
|---|---|---|
| F1 | `figs/fig_analog_registration_validation.png` | §2.1 |
| F2 | `figs/fig_scope_map_v11_overview.png` | §2.2 |
| F3 | `figs/fig_scope_map_v11_rille_density.png` | §2.2 |
| F4 | `figs/fig_ladder_hapke_grid.png` | §3.4, §4.5 |
| F5 | `figs/fig_ladder_sensor_preview.png` | §3.4, §4.5 |
| F6 | `figs/fig_wp0_kriging_tranqpit1.png` | §3.6 |
| F7 | `figs/fig_wp0_kriging_mariuspit01.png` | §3.6 |
| F8 | `figs/fig_wp0_noise_floor_panels.png` | §3.6, §4.6 |
| F9 | `figs/fig_wp0_pit_recovery.png` | §4.4 |
| F10 | `figs/fig_wp0_transqpit1_depth_check.png` | §4.4 |

Per-site analog detectability curves (one per instance) are generated
by the benchmark runner and ship with the released summaries; they are
not separately enumerated in the manuscript.

## Change log for this rewrite

- P1-1 (FATAL): all internal scaffolding stripped — absolute paths,
  md5 hashes, gate verdicts, budget/cost text, session and review
  references, roadmap/task language, internal site IDs (replaced by
  neutral geographic descriptions; TRANQPIT1 retained once in Data
  availability as the calibration anchor name).
- P1-3 / A3: "14 above-floor candidates" → "14 re-detections of
  catalogued pits; zero novel above-floor candidates" (Abstract, §4.2,
  §5.2, Conclusions).
- P1-4 / A4: four field sites / six instances / three-same-tube stated
  in §2.1, Abstract, Limitations; LOO explicitly not performed with
  the transfer-generalization criterion (§5.4).
- P1-6 / A5: registry path updated to `data/candidate_registry.csv`.
- P1-2 / A2 (NOT done here by instruction): current per-row FP
  accounting kept; one §5.4 sentence defers unique-feature
  re-accounting to the companion data paper.
- P1-7 (partial): "lifted results across sites" scoped to "raises F1
  at every instance reported in Table 1".
- References: the 8 verified entries kept verbatim; internal
  verification annotations removed (Zotero/Crossref status now lives
  only in this outline note).
- Stats: 297 lines, ~8,130 words, abstract 299 words.
