# Z2 sag-search vs catalogued pits — distance verification (Task 10, verifier run 2026-08-21)

**Method:** venv python + geopandas; Pit Atlas shapefile vs each run's
`sag_candidates.csv`; Moon equirectangular frames per the
lunarvoid-conventions skill. Geodesy cross-checked 3 ways.

| run | top score | top-candidate distance to atlas pit (m) | pit recovered? | pit rank/score/distance |
|---|---|---|---|---|
| TRANQPIT1/MTP | 21.06 | 12,485 | YES (≤100 m) | rank 11/29, score 3.72, 44.7 m |
| INGENIIPIT | 19.408 | 5,682 | YES (top of list) | rank 1, score 19.334, 46.2 m (first-listed) |
| INGENII (same DTM run, duplicate dir) | 19.408 | 5,682 | YES (top of list) | same as INGENIIPIT |
| FECNDITATS2 | 9.489 | 29,433 | NO | no candidate within 100 m; closest 2,579 m |
| IRIDIUMPIT1 | 12.859 | 22,004 | NO | no candidate within 100 m; closest 1,562 m |
| MARIUS | 5.036 | 8,742 | NO | no candidate within 100 m; closest 2,023 m (I14 funnel mode) |
| PRCLRMPIT01 | 8.093 | 5,045 | YES (≤100 m) | ranks 55/189, 38–77 m |
| SWFECUNPIT1 | 1.598 | 16,380 | NO | no candidate within 100 m; closest 1,211 m (highland) |

**Verdict:** Claim "top candidate within 100 m on all 8" REFUTED
(6/8 top-candidates 5–29 km from pit; pit recovered ≤100 m on 4/8 runs).

Report wording corrected same session; conventions skill §8 and
findings.md corrected.
