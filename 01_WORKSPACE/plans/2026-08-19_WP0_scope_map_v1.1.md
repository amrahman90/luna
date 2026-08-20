# WP0 Scope Map v1.1 — Hurwitz Rilles + LU5M812TGT Craters

**Date:** 2026-08-19
**Task:** Task 9, v5 roadmap
**Supersedes:** `plans/2026-08-19_WP0_scope_map.md` (v1.0; NAC DTM footprints + Pit Atlas only)
**Code:** `01_WORKSPACE/code/wp0_scope_map/scope_map_v11.py`
**Inputs:**
- `SHAPEFILE_NAC_DTMS` (660 DTMs, releases through 2026-06-15)
- `SHAPEFILE_LUNAR_PIT_LOCATIONS` (278 pits)
- `hurwitz_rilles/shapefile/SinuousRilles_obs.shp` (532 line segments = 195 unique rilles, Moon eqc cm=180)
- `craters_lu5m812tgt/craters_0p4_5km_pm60.csv.gz` (4,454,254 craters, 0.4-5 km, |lat|<=60°)

**Outputs:**
- `data/outputs/wp0_scope_map_v11/rille_dtms_intersect.csv`
- `data/outputs/wp0_scope_map_v11/crater_density_per_dtm.csv`
- `data/outputs/wp0_scope_map_v11/target_ranking.csv`
- `plans/figures/wp0_scope_map_v11_overview.png`
- `plans/figures/wp0_scope_map_v11_rille_density.png`

---

## Headline (delta from v1.0)

| Metric | v1.0 (2026-08-19) | v1.1 (2026-08-19) |
|---|---|---|
| DTMs in scope | 660 | 660 |
| Tube-relevant pits (mare + highland) | 21 | 21 |
| Pits inside good-tier published DTMs | 8 | 8 |
| **DTMs containing >=1 Hurwitz rille segment** | — | **10** (MARIUSCONE leads with 6) |
| **Tube-relevant pits within 60 km of a rille** | — | **3** |
| **Total craters in filtered subset** | — | **4,454,254** (from 5.69M) |
| **Median crater density across DTM footprints** | — | **0.10 craters/km²** (max 3.06) |
| **Top WP2 target DTM** | (not ranked) | **MARIUSCONE** (6 rille segs, 1 pit, flagship) |

The 10 DTM rille-bearing subset is the v1.0→v1.1 win: the WP2 sag search now has a ranked primary target list, and the 5 non-tube-relevant rille-bearing DTMs (Gruithuisen domes, Prinz, etc.) become free secondary targets for "rille as confuser" testing.

## 1. The 10 rille-bearing DTMs (sorted by segment count)

| DTM_NAME | n_rille_segments | n_unique_rilles | notes |
|---|---|---|---|
| MARIUSCONE | 6 | 2 | flagship #2 (Marius Hills Pit + Broken Cone) |
| GRUITHUIS17 | 4 | 2 | Gruithuisen Domes |
| MARIUSPIT01 | 4 | 2 | flagship #2 primary DTM |
| GRUITHMARE2 | 2 | 1 | Gruithuisen |
| GRUITHUIS14 | 2 | 1 | Gruithuisen |
| ISISOSIRIS | 2 | 1 | Isis-Osiris region |
| MARIUSCONE1 | 2 | 1 | second Marius Hills coverage |
| POSIDONIUS | 2 | 1 | Posidonius crater |
| PRINZVENT | 1 | 1 | Rimae Prinz Vent |
| (one more, see CSV) | | | |

Only 3 of 21 tube-relevant pits sit within 60 km of a rille segment. This is consistent with the v5 Section 6 finding that rilles are *unroofed* segments — the rille-bearing DTMs are mostly the rille *itself*, not a candidate intact-roof site.

## 2. Crater density per DTM (top 5 + median)

| Statistic | Value |
|---|---|
| Median crater density | 0.10 craters/km² |
| Max crater density | 3.06 craters/km² |
| 593 DTMs have >=1 "same-1-deg-lat-strip" with >=3 craters (loose chain proxy) | — |

The chain proxy is intentionally permissive (1-deg lat strips with >=3 craters). The v0.2 hardening will require aligned-azimuth triple detection.

## 3. Per-DTM target ranking for WP2 sag search

Score = `5 × n_pits_in_dtm + (2 × n_rille_segments + n_unique_rilles) + 3 × (1 - crater_density/max_density) + 2 × (quality == "good") + 3 × is_flagship`

| Rank | DTM | n_pits | n_rille_segs | crater/km² | quality | score |
|---|---|---|---|---|---|---|
| 1 | MARIUSCONE | 1 | 6 | 0.050 | good | 23.95 |
| 2 | MARIUSPIT01 | 1 | 4 | 0.047 | good | 22.95 |
| 3 | PRCLRMPIT01 | 2 | 0 | 0.062 | good | 14.94 |
| 4 | GRUITHUIS17 | 0 | 4 | 0.112 | good | 14.89 |
| 5 | INGENIIPIT | 1 | 0 | 0.027 | good | 12.97 |

MARIUSCONE and MARIUSPIT01 share the Marius Hills region; PRCLRMPIT01 carries two North Procellarum pits with low rille content; INGENIIPIT is the cleanest (lowest crater density).

## 4. Conclusions

1. **Marius Hills is the v1.1 hot zone** — both the primary and the alternate DTM carry rille content, and the flagship pit is already on the v5 calibration list. WP2 should *start* here, not at Tranquillitatis (which has no rille and is the cleanest stress-test case for "no confuser" detectability).
2. **Gruithuisen domes are a secondary confuser-rich target** — useful for benchmarking the rille-class confusion layer.
3. **The 5 NO_COVERAGE pits** (Schlüter, Mare Insularum, Highland 1/2/3, plus SW Tranquillitatis B at the catalogue edge) are not in this analysis — they require a Tier-1 DTM build (Roadmap Task 8, the optional local ISIS+ASP experiment) before they enter the WP2 confusion layer.
4. **Data hygiene finding (re-confirmed):** the Pit Atlas `DTM` attribute field still misses 2 of 8 covered pits (Ingenii, SW Fecunditatis) — the spatial join is the authoritative source, NOT the attribute.

## 5. Next step

Run `code/wp2_sag/sag_search_run.py --dtms MARIUSCONE MARIUSPIT01 PRCLRMPIT01 INGENIIPIT TRANQPIT1 SWFECUNPIT1 IRIDIUMPIT1 FECNDITATS2` (the 8 covered-pit DTMs) once the WP2 confusion layer (`code/wp2_sag/confusion_layer.py`) is integrated. The ranked target list above is the WP2 priority queue.
