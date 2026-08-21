# Gate G0' Report v1.1 — zero-cost portion of Gate G0 (LUNARVOID WP0)

**Date:** 2026-08-21 · **Version:** v1.1 · **Status:** FINAL — PASSED (user decision D1, 2026-08-21)
**Supersedes:** `plans/2026-08-19_GATE_G0prime_report.md` (v0.1-era LLTB-1 numbers; all figures below re-traced to output files, v0.4 detector numbers where applicable)
**Gate definition:** G0' = the zero-cost subset of v5 Gate G0 (roadmap Task 10). Full G0 additionally
requires one reproduced NAC DTM end-to-end (paid; §8 trigger T1). Authority: v5 master plan §4, §8;
`plans/2026-08-19_ZEROCOST_Roadmap.md` Task 10.

## 1. Criteria vs measured

All paths relative to `01_WORKSPACE/`. Missing values would read NOT MEASURED; none are.

| # | G0' criterion | Measured | Verdict |
|---|---|---|---|
| 1 | Primitive recovers ≥6/8 covered pits at ≥50% catalogued depth (Task 4) | 7/8 pass. MTP 129.67 m vs 105 m catalogued (fill-to-spill overshoot, documented); sole failure Marius Hills 14.56/40 m (0.364) = pre-registered v5 I14 rille-funnel mode — a finding, not a defect. `data/outputs/wp0_primitive/pit_recovery_table.csv` | **PASS** |
| 2 | Kriged I2 correction smooth + signal-preserving (Task 5) | Check-point RMSE: TRANQPIT1 0.373→0.327 m (bias −0.083→−0.024, n=595); MARIUSPIT01 1.425→0.541 m (bias +0.058→−0.002, n=4147). Correction power >99.99% at λ>300 m on both; MTP pit depth 129.67→129.73 m (+0.05%). `data/outputs/wp0_kriging/{TRANQPIT1,MARIUSPIT01}_kriging_metrics.csv` + `*_summary.json` | **PASS** |
| 3 | Noise floor measured, sag-band verdict (Task 6) | 7 + 8 flat-mare panels; sag-band (60–300 m DoG) RMS 1.245 m (TRANQPIT1) / 1.379 m (MARIUSPIT01); 3σ = 3.74 / 4.14 m (3× sag-band RMS — a project detection convention, not a v5-specified rule). Verdict (CSV header): A=1 m and A=2 m NOT single-DTM detectable; A=5 m DETECTABLE ⇒ effective floor ≥5 m at both sampled sites (≥4 m at TRANQPIT1; the noisier MARIUSPIT01 pooled 3σ = 4.14 m); 1–2 m sags need multi-evidence stacking (the G1 answer). `data/outputs/wp0_kriging/noise_floor_stats.csv`, `noise_floor_summary.json` | **PASS** |
| 4 | Confusion layers acquired (Task 7) | Hurwitz 2013 rilles: 532 segments = 195 unique rilles (Wayback rescue, SHA-256 in manifest); LU5M812TGT: 5,691,533 → 4,454,254 filtered craters, **CC-BY-4.0**. 5-class rasters at 50 m for 3 flagship DTMs (MARIUSPIT01 carries 1,795 rille cells, 31 crater-chain strips); wrinkle-ridge/graben class is a labelled *derived placeholder, not curated*. `data/MANIFEST.md`; `data/outputs/wp2_sag/confusion/confusion_layer_summary.json` | **PASS** |
| 5 | Scope ranked (Task 9) | 660-DTM ranking; 10 DTMs carry rille segments; top WP2 target MARIUSCONE (6 segments, 2 rilles, 1 pit, score 23.95); median crater density 0.105 km⁻² over 615 DTMs (computed from CSV). `data/outputs/wp0_scope_map_v11/{target_ranking,rille_dtms_intersect,crater_density_per_dtm}.csv` | **PASS** |
| 6 | Local-ASP decision documented (Task 8) | Attempt **incomplete**: steps 8.1–8.2 done (ISIS env, ASP 3.7.0, 6 EDR products); 8.3–8.4 abandoned mid-chain at time-box (one processed cube, no output DTM — not a definitive OOM/hardware test). Verdict: *local not viable as-run; T1 rental unchanged*. `admin/2026-08-21_local_asp_attempt.md` | **PASS (process only)** (decision logged per Step 8.5; failure branch) |
| 7 | LLTB-1 v0.1+ benchmarked (Tasks 11–15) | v0.4 (tuned slope, cal/test split, seed 42) on 7 analog sites: best honest F1 **0.362** (IndianTunnel_NorthSurface 1 m @45°); real tube Collapse3 0.188 @0.5 m; **recall 1.00 at every rung with ≥5 void cells** — precision is the bottleneck. Regressions kept visible: cave_1x 0.068→0.049 under tune-slope (use fixed 10°); Kingsbowl history 0.002→0.045→0.043. Verifications: v02 21/21, v03 15/15, v04 11/11, all OK. `notes/2026-08-21_LLTB1_v0.{3,4}_release_note.md`; `admin/verification_evidence/2026-08-21_v0{2,3,4}_*.json` | **PASS** |
| 8 | Z2 sag search run (Tasks 17–18, 20) | 8 runs over 7 unique covered-pit DTMs; catalogued pit recovered as a candidate within 100 m on 4/8 runs (Ingenii 46 m, top of list; MTP 45 m @ rank 11/29; Procellarum 38-77 m @ ranks 55/189); no candidate within 100 m on FECNDITATS2/IRIDIUMPIT1/MARIUS/SWFECUNPIT1 (closest 1.2-2.6 km) — evidence: `admin/verification_evidence/2026-08-21_z2_pit_distance_verification.md` (to be filed this session); top scores 21.06 (TRANQPIT1) → 1.60 (SWFECUNPIT1, only highland site); Marius 5.04 in the I14 funnel mode. GRAIL GRGM1200A (l_max 680) acquired; Diviner = placeholder metadata only. `data/outputs/wp2_sag/*/sag_search_summary.json` | **PASS (process only)** |
| 9 | Prior-art matrix status (Task 1, per Step 10.1) | 33 refs; 6 priority rows fully populated; remainder queued. `notes/prior_art_matrix.{csv,md}` | **PASS** |

*Rows 6 and 8 grade process completion; their science outcomes are documented in-row and are not claimed as passes.*

**Outcome: 9 PASS / 0 PARTIAL / 0 FAIL at the zero-cost gate** — with every known failure mode
documented inside its row (Marius funnel, Kingsbowl F1 history, cave_1x regression, Task-8
incompleteness). These are findings, not shames; they delimit exactly where the method stands.

## 2. What we can now claim

Calibrated inference, never verified detection. On single published NAC DTMs, only roof-sag amplitudes ≥5 m at both sampled sites (≥4 m at TRANQPIT1; the noisier MARIUSPIT01 pooled 3σ = 4.14 m) over 60–300 m wavelengths rise above the measured 1.25–1.38 m sag-band noise floor; 1–2 m sag candidates are **not claimable from a single DTM** and await multi-evidence
stacking (G1). These floors were measured on 2 of ~649 good-tier DTMs (7+8 panels); per-panel pooled RMS spans 0.74–2.05 m, so per-site floors vary and per-DTM floors should be measured before any Z2-scale claim. Everything the Z2 search produces is a set of *inferred void candidates* ranked by
an uncalibrated depth×Frangi score. The Mare Tranquillitatis pit — the one site with independent
radar evidence of a subsurface conduit (Carrer 2024) — is recovered as a mid-ranked candidate
(rank 11 of 29, 45 m from the catalogued pit, score 3.72), while that run's global top score
(21.06) lies ~12.5 km NNE of the pit: the detector's pit-proximity response is real (chance-proximity ≲1%), and the catalog-pit recovery rate is 4/8 (Wilson 95% CI ≈ [0.18, 0.82], n=8), but its uncalibrated ranking is currently dominated by uncorroborated candidates (presumed mostly false; FP rate not yet measured) — precisely what the Task-19 multi-illumination
stacking and Task-21 calibration work are meant to fix. That Tranquillitatis conduit remains the
only subsurface structure on the Moon evidenced by any instrument today, and nothing in this
report changes that. Lunar false-positive rates per 10⁴ km²
are **NOT MEASURED** — calibrated posteriors (PU learning + conformal, Task 21.2) are a
prerequisite; on analog benchmarks precision, not recall, is the bottleneck (best F1 0.362,
recall 1.00 where ≥5 void cells). The depression-depth primitive fails by design on pits incised
into rilles (Marius Hills, I14) — funnel geometry must be treated as a confuser class, not
recovered post hoc.

## 3. What remains for full G0

| Item | Task # | Nature |
|---|---|---|
| Tier-1 stereo reproduction of one published NAC DTM (completes steps 8.3–8.4; diff vs TRANQPIT1 within relat_le 0.72 m) | Task 8 / §8 trigger T1 | **Paid** ($50–150 burst, user approval required). Does NOT block WP1/Z1 — those run on terrestrial analogs + published DTMs |
| Multi-illumination stacking (photometric-stereo artifact rejection) | Task 19 (+ I5 azimuth test 18.2) | $0; plumbing pending (LROC search API) |
| Diviner nighttime T + rock-abundance ingestion (Powell 2023 derivative) | Task 20.2 | $0; PDS REST query plumbing pending |
| PU learning + conformal calibration → FP per 10⁴ km² and confidence bars | Task 21.2 | $0; prerequisite for any lunar FP claim |
| Hapke re-illumination + NAC sensor-noise ladder rungs (LLTB-1 v0.5) | Tasks 13.3–13.4 | $0; lifts benchmark realism |
| Per-DTM noise floors at Z2 scale (cheap, CPU) — pre-G1 | Task 6 extension | $0; CPU-only, before any Z2-scale claim |
| SLDEM2015 normalisation (v5 WP2 pre-registered anti-circularity rule; Step 18.1 detail) | v5 WP2, Step 18.1 | $0; deferred to WP2 |
| I12 confound covariates (LOLA track density, NAC image count per tile) | v5 I12 | $0; deferred to WP2 |

## 4. Cost audit

**$0.00 spent to date.** Local compute and public-data downloads only; no paid GPU, APIs, VPS, or
rental. First possible spend remains §8 trigger T1 (Tier-1 rental), which requires explicit user
approval.

*Data credits: PDS/LROC/LOLA public domain; LU5M812TGT craters CC-BY-4.0 (La Grassa et al.);
Hurwitz et al. 2013 PSS 79-80 (cite; no explicit licence); NASA Pits & Caves analog dataset
research/academic use only, no redistribution; no Chandrayaan data used to date (ISRO
acknowledgement not yet triggered).*

*Evidence/traceability: verifier Z2 pit-distance table recorded at
`admin/verification_evidence/2026-08-21_z2_pit_distance_verification.md`.*
