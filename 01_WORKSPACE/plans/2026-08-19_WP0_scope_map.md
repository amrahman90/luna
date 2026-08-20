# WP0 Scope Map — Pit Atlas × Published NAC DTMs

**Date:** 2026-08-19
**Task:** WP0 index-layer intersection (LUNARVOID Master Plan v5, WP0)
**Inputs:** `SHAPEFILE_NAC_DTMS` (660 DTMs, releases through 2026-06-15) ×
`SHAPEFILE_LUNAR_PIT_LOCATIONS` (278 pits). See `data/MANIFEST.md`.
**Code:** `code/wp0_scope_map/scope_map.py`
**Outputs:** `data/outputs/wp0_scope_map/*.csv`, `plans/figures/wp0_scope_map_overview.png`

---

## Headline numbers

| Quantity | Value |
|---|---|
| Published NAC DTMs in shapefile | **660** (through 2026-06-15) |
| Quality tiers (relat_le ≤5 m & triang_rms ≤20 m) | good **649** / fair 9 / poor 2 |
| Tube-relevant pits (mare + highland) | **21** (16 mare + 5 highland) — matches v5 plan exactly |
| Relevant pits **inside** a published DTM footprint | **8** (all "good" tier) |
| Relevant pits with **stereo IDs but no DTM** | **8** (future Tier-1 build list, product IDs captured) |
| Relevant pits with **no coverage at all** | **5** |
| DTM coverage, all pits by terrain | mare 7/16 (44%), highland 1/5 (20%), impact melt 74/257 (29%) |

## 1. The 8 covered pits — the analysis-ready core (WP2 can start on these)

| Pit | Terrain | DTM | Res (m) | relat_le (m) | Note |
|---|---|---|---|---|---|
| Mare Tranquillitatis | Mare | NAC_DTM_TRANQPIT1 | 2 | 0.72 | flagship calibration site |
| Mare Ingenii | Mare | INGENIIPIT | 2 | 1.74 | **discovered via join — absent from atlas `DTM` field** |
| SW Mare Fecunditatis | Highland | SWFECUNPIT1 | 3 | 1.58 | also absent from atlas `DTM` field |
| Central Mare Fecunditatis | Mare | NAC_DTM_FECNDITATS2 | 4 | 2.11 | |
| Marius Hills | Mare | NAC_DTM_MARIUSPIT01 | 4 | 3.43 | flagship #2 |
| North Procellarum 1 | Mare | NAC_DTM_PRCLRMPIT01 | 5 | 3.36 | |
| North Procellarum 2 | Mare | NAC_DTM_PRCLRMPIT01 | 5 | 3.36 | shares DTM with NP1 |
| Sinus Iridum | Mare | NAC_DTM_IRIDIUMPIT1 | 5 | 3.97 | GRAIL cross-correlation site |

All three v5 flagship sites (Tranquillitatis, Marius Hills, Ingenii) have
2–4 m DTMs. **WP1/WP2 need no new photogrammetry to begin.**

## 2. The 8 buildable-but-unbuilt sites — the Tier-1 priority queue

With stereo product IDs from the Pit Atlas (fetch-by-ID only):

| Pit | Terrain | Stereo product IDs |
|---|---|---|
| West Marius Hills | Mare | M1313401618L, M1313394599L |
| SW Mare Tranquillitatis | Mare | M1341063036R, M1297582135L |
| Runge | Mare | M190036923R, M190022623R |
| Lacus Mortis | Mare | M1317542330L, M1317528271L |
| Compton | Mare | M1225299477R, M1225278371L |
| Mare Moscoviense | Mare | M1319088918L, M1319074859L |
| Mare Serenitatis | Mare | M1345798646L, M1345784596R |
| Schlüter | Highland | M1311225886R, M1114710368L |

## 3. No coverage (5)

SW Tranquillitatis B, Mare Insularum, Highland 1, Highland 2, Highland 3.
Note the atlas shows SW Tranquillitatis A/B as near-coincident points
(~0.0004° apart) — A is covered, B misses the footprint edge. Treat B as
covered-by-proximity for practical purposes.

## 4. Data-hygiene finding: atlas `DTM` field is incomplete

Spatial join vs atlas attribute: **19/21 agreement**. The join found DTM
coverage for **Mare Ingenii (INGENIIPIT)** and **SW Mare Fecunditatis
(SWFECUNPIT1)** that the atlas `DTM` field does not record. Always trust
the geometric intersection, not the attribute.

## 5. Rille-related DTMs (WP2 sag-search substrate) — 21 products

Matches to v5 target list: **Rima Sharp (4 DTMs, incl. one at 2 m /
relat_le 1.23)**, **Vallis Schroteri (2)**, **Rimae Prinz Vent and Rille**,
**Lacus Mortis / Rimae Burg (2)**, plus Vallis Inghirami (4), Rimae Hippalus,
Rimae Grimaldi (2, 2 m), Mons Hadley area. Full table:
`data/outputs/wp0_scope_map/rille_related_dtms.csv`.
One quality outlier: RIMPARRY1 (relat_le 32 m — poor tier; excluded from
analysis use).

## 6. Known gaps / next actions

1. **Hurwitz rille shapefile not acquired** — Brown server down, LPI
   403s bots (details + fallbacks in `data/MANIFEST.md`). Required for the
   WP2 confusion layer, not blocking WP0/WP1.
2. Stereo Catalog PDF not parsed — Pit Atlas `StereoIDs` covers the
   pit-centric need for now.
3. Encoding artifact: "Schlüter" renders as mojibake in the DBF; harmless,
   noted for fuzzy matching later.
4. Next zero-cost step per plan: **depression-depth primitive on
   TRANQPIT1** (download DTM by ID, sink-fill minus DTM, verify it
   recovers the catalogued pit) → WP0 Gate G0 component.

## Conclusion

The scope map confirms the v5 plan's premise: the label bottleneck (21
relevant pits) is real, but **38% of those pits already sit on
good-tier published DTMs**, including every flagship site — and the 8-pit
Tier-1 build queue comes with exact product IDs. The project's WP1/WP2
substrate exists today at zero cost.
