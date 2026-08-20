# Data Manifest — LUNARVOID WP0

All data acquired for the project is recorded here. Raw rasters/point clouds
live outside the repo (default: `~/lunarvoid/data/`); small index layers are
mirrored into `01_WORKSPACE/data/index_layers/`. Never mirror LROC EDR/CDR
archives — fetch by product ID only.

## Index layers

| Layer | Version / as-of | Source URL | Local copy | SHA-256 | Licence |
|---|---|---|---|---|---|
| NAC DTM footprints (global, -180..180) | releases through **2026-06-15**; 660 DTMs | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/EXTRAS/SHAPEFILE/NAC_DTMS/NAC_DTMS_180.ZIP` | `index_layers/nac_dtms/` + `~/lunarvoid/data/index_layers/` | `749325a5f3be13ef2141f79e04aa52ce6d31ec3ca954a6efafc5e923f8f00a7c` | PDS public domain |
| Lunar Pit Atlas locations (-180..180) | 278 pits | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/EXTRAS/SHAPEFILE/LUNAR_PIT_LOCATIONS/LUNAR_PIT_LOCATIONS_180.ZIP` | `index_layers/pit_atlas/` + `~/lunarvoid/data/index_layers/` | `b0d2e0123026979fae5b2865049900e7bcc3b2767ca31a36413423fdcae365bb` | PDS public domain |
| Hurwitz et al. 2013 sinuous rilles — ArcGIS shapefile outlines (532 line segments = walls of **195 unique rilles**, keyed by `RilleTable`; digitised on Kaguya TC) | downloaded **2026-08-19** via Wayback Machine (Brown server down) | orig `http://www.planetary.brown.edu/data/SinuousRilles_obs.zip`; fetched `https://web.archive.org/web/20151016230543id_/http://www.planetary.brown.edu/data/SinuousRilles_obs.zip` | `~/lunarvoid/data/index_layers/hurwitz_rilles/` (zip + extracted `shapefile/`) | `a38d57bad9b813a0ac28f1f726f990f188eac20c7d63736a4fee7b26a9f150b9` | no explicit licence on data page; cite Hurwitz, Head & Hiesinger 2013, PSS 79-80, 1-38 |
| Hurwitz et al. 2013 Table 1 (dimensions) + Table 2 (observations), XLSX | downloaded **2026-08-19** via Wayback Machine | orig `http://www.planetary.brown.edu/data/Table1_sinuousrilledimensions.xlsx`, `.../Table2_sinuousrilleobservations.xlsx`; fetched from `web.archive.org` captures 20151017032018 / 20151016231412 | `~/lunarvoid/data/index_layers/hurwitz_rilles/` | T1 `c6b81212e342682978de9f042ef407fcd8664dabeb2419c98ed12c9e6673a3e8`, T2 `a92564075360818c3c8d53a4904407c4c7196ae444371852ae11bf0a55e43d97` | same as above (reading needs `openpyxl`, not yet installed) |
| LU5M812TGT global crater catalogue v2 (`Moon_Diamond_catalog_4.csv`, 5,691,533 craters, YOLOLens; cols: Longitude 0-360, Latitude, Diameter_h/w (ellipse axes, km), Confidence) | downloaded **2026-08-19**; Zenodo md5 verified `338bf075afd3264cde1a1a546920b0ba` | `https://zenodo.org/records/13990480/files/Moon_Diamond_catalog_4.csv?download=1` (DOI 10.5281/zenodo.13990480) | `~/lunarvoid/data/index_layers/craters_lu5m812tgt/` | `032f60b72ab8e5811cbe1491b089bdf108752afb6fe96664fa82d5697610447b` | **CC-BY-4.0** (Zenodo licence field: `cc-by-4.0`) |
| LU5M812TGT filtered subset `craters_0p4_5km_pm60.csv.gz` — D_eq = sqrt(Diameter_h x Diameter_w) in [0.4, 5] km AND abs(lat) <= 60 deg | derived **2026-08-19**; 5,691,533 -> **4,454,254** rows (78.3%); + added `D_eq_km` column | derived from row above (regenerable) | `~/lunarvoid/data/index_layers/craters_lu5m812tgt/` | `63fa4eeea01c7bd45b78b9a2d1ab9925adf60b7981e036cbad3a9781199e292b` | CC-BY-4.0 (derivative; attribution = La Grassa et al. 2024/2025) |

Downloaded 2026-08-19. READMEs (field dictionaries) alongside each layer.

Notes (2026-08-19, Task 7):
- Hurwitz shapefile CRS is **Moon equirectangular, central meridian 180, metres**
  (`Moon_EC` / GCS_Moon_2000) — reproject to geographic lon/lat (or -180..180
  longitudes) before intersecting LROC products. Source page warns outlines were
  drawn on Kaguya TC mosaics, so slight offsets vs LROC are expected (matches
  the WP2 offset-correction plan, Task 17.1).
- zenodo_parts.log / final_status.txt in the crater dir are download logs
  (8-way range download; md5 OK), kept as provenance.

## DTM products

| Product | Version / as-of | Source URL | Local copy | SHA-256 | Licence |
|---|---|---|---|---|---|
| NAC DTM TRANQPIT1 (Mare Tranquillitatis Pit, 32-bit float GeoTIFF, 2 m/px, 2372x14388, project 2019-03-05) | downloaded **2026-08-19** | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/TRANQPIT1/NAC_DTM_TRANQPIT1.TIF` | `~/lunarvoid/data/dtms/TRANQPIT1/NAC_DTM_TRANQPIT1.TIF` | `3cf53c33783cb43d8788d71837c43e322ce015d9ef4b3f0f61709e9e98fbc662` | PDS public domain |
| NAC DTM TRANQPIT1 PDS label | downloaded **2026-08-19** | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/TRANQPIT1/NAC_DTM_TRANQPIT1.LBL` | `~/lunarvoid/data/dtms/TRANQPIT1/NAC_DTM_TRANQPIT1.LBL` | `22854a291673835b55dd4d6968551d105c4c016311538b03c9c224682e9086eb` | PDS public domain |
| NAC DTM MARIUSPIT01 (Marius Hills Pit, 32-bit float GeoTIFF, 4 m/px, 3331x12529, project 2020-10-26) | downloaded **2026-08-19** | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/MARIUSPIT01/NAC_DTM_MARIUSPIT01.TIF` | `~/lunarvoid/data/dtms/MARIUSPIT01/NAC_DTM_MARIUSPIT01.TIF` | `db5daada9b38ae7a0316a6e289f2cfe9b78b708c52e3bafb345849e1975aa374` | PDS public domain |
| NAC DTM MARIUSPIT01 PDS label | downloaded **2026-08-19** | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/MARIUSPIT01/NAC_DTM_MARIUSPIT01.LBL` | `~/lunarvoid/data/dtms/MARIUSPIT01/NAC_DTM_MARIUSPIT01.LBL` | `5d3fa5ea9c32c6542e250aa9f5e08eca4b152b48c6ed36ac941849bb63a1354e` | PDS public domain |
| NAC DTM INGENIIPIT (Mare Ingenii Pit, 32-bit float GeoTIFF, 2 m/px, 3933x14105, project 2019-02-05) | downloaded **2026-08-19** | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/INGENIIPIT/NAC_DTM_INGENIIPIT.TIF` | `~/lunarvoid/data/dtms/INGENIIPIT/NAC_DTM_INGENIIPIT.TIF` | `b6a6be1a9612d15e9f7a6d642766b89a50467ec6dd36c0da665018a6d9f2c4a6` | PDS public domain |
| NAC DTM INGENIIPIT PDS label | downloaded **2026-08-19** | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/INGENIIPIT/NAC_DTM_INGENIIPIT.LBL` | `~/lunarvoid/data/dtms/INGENIIPIT/NAC_DTM_INGENIIPIT.LBL` | `b0ad649c03c2abe3b38ba0e0bb45f5ec4552a0e97a0f5921e6aaf2cbf5e451c5` | PDS public domain |
| NAC DTM SWFECUNPIT1 (SW Mare Fecunditatis Pit, 32-bit float GeoTIFF, 3 m/px, 4607x16308, project 2023-08-21) | downloaded **2026-08-19** | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/SWFECUNPIT1/NAC_DTM_SWFECUNPIT1.TIF` | `~/lunarvoid/data/dtms/SWFECUNPIT1/NAC_DTM_SWFECUNPIT1.TIF` | `568a6e86aed77558566e8c785747d6e8461388ef9e9864e52020e45e3aeeb622` | PDS public domain |
| NAC DTM SWFECUNPIT1 PDS label | downloaded **2026-08-19** | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/SWFECUNPIT1/NAC_DTM_SWFECUNPIT1.LBL` | `~/lunarvoid/data/dtms/SWFECUNPIT1/NAC_DTM_SWFECUNPIT1.LBL` | `07737237979991a5c8eb704099d9984d420b6ba59556864301241a4646d0f65f` | PDS public domain |
| NAC DTM FECNDITATS2 (Central Mare Fecunditatis Pit, 32-bit float GeoTIFF, 2 m/px, 6449x29329, project 2014-03-20) | downloaded **2026-08-19** | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/FECNDITATS2/NAC_DTM_FECNDITATS2.TIF` | `~/lunarvoid/data/dtms/FECNDITATS2/NAC_DTM_FECNDITATS2.TIF` | `6971ea044165a1405c8964b83794d3b5bec35e2f7a116e02e62dbbd9a84aabd4` | PDS public domain |
| NAC DTM FECNDITATS2 PDS label | downloaded **2026-08-19** | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/FECNDITATS2/NAC_DTM_FECNDITATS2.LBL` | `~/lunarvoid/data/dtms/FECNDITATS2/NAC_DTM_FECNDITATS2.LBL` | `ec3ca3e404f5bf704072776d971a0043f3a8ed6734ba92c08e6b05211208d4e3` | PDS public domain |
| NAC DTM PRCLRMPIT01 (North Procellarum Pits 1+2, 32-bit float GeoTIFF, 5 m/px, 3468x12833, project 2016-04-09) | downloaded **2026-08-19** | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/PRCLRMPIT01/NAC_DTM_PRCLRMPIT01.TIF` | `~/lunarvoid/data/dtms/PRCLRMPIT01/NAC_DTM_PRCLRMPIT01.TIF` | `8ad401c317127b9044c083816ad2078c76e4e4016e7c7a6bdc33b98875c2daad` | PDS public domain |
| NAC DTM PRCLRMPIT01 PDS label | downloaded **2026-08-19** | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/PRCLRMPIT01/NAC_DTM_PRCLRMPIT01.LBL` | `~/lunarvoid/data/dtms/PRCLRMPIT01/NAC_DTM_PRCLRMPIT01.LBL` | `5b6f6c4b27be50fb9dfa6248526b65f4cf949024a1cb68475cf9a31327d41245` | PDS public domain |
| NAC DTM IRIDIUMPIT1 (Sinus Iridum Pit, 32-bit float GeoTIFF, 5 m/px, 3131x13451, project 2018-01-20) | downloaded **2026-08-19** | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/IRIDIUMPIT1/NAC_DTM_IRIDIUMPIT1.TIF` | `~/lunarvoid/data/dtms/IRIDIUMPIT1/NAC_DTM_IRIDIUMPIT1.TIF` | `7add07d7f6e7d0383d814165a2776af04b3c929f1796d4767e60505cd9260bf3` | PDS public domain |
| NAC DTM IRIDIUMPIT1 PDS label | downloaded **2026-08-19** | `https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/SDP/NAC_DTM/IRIDIUMPIT1/NAC_DTM_IRIDIUMPIT1.LBL` | `~/lunarvoid/data/dtms/IRIDIUMPIT1/NAC_DTM_IRIDIUMPIT1.LBL` | `514aeec5286cdc7329e3801a6adc52aad022949b36f507981fad37772681903e` | PDS public domain |

Note: `pds.lroc.im-ldi.com` URLs now 301-redirect to
`pds.mcp.nasa.gov` (S3-backed); checksums above are of the redirected
content.

Derived (local, regenerable): `NAC_DTM_TRANQPIT1_filled.tif` +
`NAC_DTM_TRANQPIT1_depth.tif` via
`01_WORKSPACE/code/wp0_primitive/depression_depth.py` (Planchon-Darboux
epsilon fill) in `~/lunarvoid/data/outputs/TRANQPIT1/`. The same
derived pair for all six products above lives in
`~/lunarvoid/data/outputs/<NAME>/`, produced by the Task-4 sweep
(`01_WORKSPACE/code/wp0_primitive/sweep_pits.py`).

## LOLA reference data

Acquired 2026-08-19 via the PDS Geosciences Node **GDS LOLA RDR Query
Tool REST API** (`oderest.rsl.wustl.edu/livegds/?query=lolardr`), query
bbox westlon=33.10, eastlon=33.29, minlat=7.90, maxlat=8.88 (TRANQPIT1
footprint + margin); and 2026-08-19 (Task 6) bbox westlon=302.95,
eastlon=303.50, minlat=13.35, maxlat=15.10 (MARIUSPIT01 footprint +
margin). Raw per-shot LOLA RDR points — NOT a gridded merge,
so the kriging reference residual contains no gridding error. GDS
pre-filters to shot quality flag = 0. Coordinates are planetocentric
lon (0–360 E) / lat; `Pt_Radius` referenced here to the 1737.4 km
sphere to match the DTM's vertical datum.

| Product | Version / as-of | Source URL | Local copy | SHA-256 | Licence |
|---|---|---|---|---|---|
| LOLA RDR shot subset over TRANQPIT1 (8,488 shots, CSV: UTC, lon, lat, radius, range, pulse, flags...) | generated **2026-08-19** (result files valid until 2026-09-18) | `https://oderest.rsl.wustl.edu/livegds/?query=lolardr&source=GDSWebLOLARDR&odemetadb=moon&o=j&results=cp&westlon=33.10&eastlon=33.29&minlat=7.90&maxlat=8.88` -> `https://oderest.rsl.wustl.edu/output/20260819t120258916/LolaRDR_8N9N_33E33E_20260819T120304851_pts_csv.csv` | `~/lunarvoid/data/lola_tracks/TRANQPIT1/LolaRDR_8N9N_33E33E_20260819T120304851_pts_csv.csv` | `d1ae3b11fd9e25181138f8b88196f0c7cfce4d4183e0f56629d95e8e677f04dd` | PDS public domain |
| PDS3 label for the above GDS subset | generated **2026-08-19** | `https://oderest.rsl.wustl.edu/output/20260819t120258916/LolaRDR_8N9N_33E33E_20260819T120304851_pts_csv.lbl` | `~/lunarvoid/data/lola_tracks/TRANQPIT1/LolaRDR_8N9N_33E33E_20260819T120304851_pts_csv.lbl` | `a2114f0264904cdda7caa86ee4ee6ad20ab9327e55141491fca2527c93e63a35` | PDS public domain |
| LOLA RDR shot subset over MARIUSPIT01 (66,932 shots in query box, 34,767 inside DTM footprint; Task 6, same URL pattern with `westlon=302.95&eastlon=303.50&minlat=13.35&maxlat=15.10`) | generated **2026-08-19** (result files valid until 2026-09-18) | `https://oderest.rsl.wustl.edu/livegds/?query=lolardr&source=GDSWebLOLARDR&odemetadb=moon&o=j&results=cp&westlon=302.95&eastlon=303.50&minlat=13.35&maxlat=15.10` -> `https://oderest.rsl.wustl.edu/output/20260819t123017590/LolaRDR_13N15N_303E304E_20260819T123021634_pts_csv.csv` | `~/lunarvoid/data/lola_tracks/MARIUSPIT01/LolaRDR_13N15N_303E304E_20260819T123021634_pts_csv.csv` | `b163f3ee9b629a4ad87a688a8a5e9a134c9b1a3b8bd4aab562f6b572cad8041e` | PDS public domain |
| PDS3 label for the above GDS subset | generated **2026-08-19** | `https://oderest.rsl.wustl.edu/output/20260819t123017590/LolaRDR_13N15N_303E304E_20260819T123021634_pts_csv.lbl` | `~/lunarvoid/data/lola_tracks/MARIUSPIT01/LolaRDR_13N15N_303E304E_20260819T123021634_pts_csv.lbl` | `483156d619bec79a2687263827fd0f381155ece87a9bed3494a2986230ea7682` | PDS public domain |

Note: acquisition-path audit — ODE product-search pages
(`ode.dm.asu.edu` DNS-dead; `ode.rsl.wustl.edu/ode/*` REST paths 404)
failed from CLI; the GDS granular REST service (found via the query
tool's own JS at `oderest.rsl.wustl.edu/GDSWeb/`) succeeded
synchronously with direct CSV download, so options (a) and (b) merged
into one path and the GDR gridded fallback (c) was never needed.

Derived (local, regenerable): `NAC_DTM_TRANQPIT1_krigcorr.tif` +
`_krigcorr_depth.tif` + `_krigcorr_filled.tif` via
`01_WORKSPACE/code/wp0_kriging/kriging_correction.py` in
`~/lunarvoid/data/outputs/TRANQPIT1/` (Task 5, I2 kriged correction).

## Blocked / pending

|| Layer | Status | Blocking issue | Fallback plan |
||---|---|---|---|
|| Hurwitz et al. sinuous rille shapefile (195 rilles) | **RESOLVED 2026-08-19** — acquired via Wayback Machine (see Index layers) | `planetary.brown.edu` still down (connect timeout, http+https); Wayback `available` API 429 twice, then OK with no snapshot listed — CDX API (`web.archive.org/cdx/search/cdx`) found page + data-file captures | Done. USGS Astropedia / LPI browser-UA paths not needed. |
|| NAC Stereo Catalog (PDF) | Deferred | PDF parsing; the Pit Atlas `StereoIDs` field already covers the pit-centric need | Full catalog only when planning DTM builds beyond pits |
|| NASA Pits and Caves analog dataset (Wong 2014) | **ACQUISITION IN PROGRESS 2026-08-19 (session 2)** | ti.arc.nasa.gov/dataset/caves serves 9 RARs (total ~4.5 GB); CAVES_code (7 KB, code stub), FiegHighwallVolume (38 MB), SheepridgeVolume (11 MB), Fieg (243 MB), Kingsbowl (530 MB), Sheepridge (328 MB), IndianTunnel_surface (1.1 GB), IndianTunnel_cave (2.07 GB), HDR panos (175 MB). Download started with `curl --max-time 1200-3600`; partial files yield 0-byte extracts via 7z. | Re-run `curl -C -` to resume. When complete, extract via 7z and feed `code/wp1_lla/convert_f32.py`. |
|| CAVES_code.rar | EXTRACTED 2026-08-19 but contents are 0-byte placeholders (downsample_pc_voxel.m, downsample_point_cloud.m); source server is stale | The .f32 format is fully documented in the dataset HTML page (read it once in `analog/index.html`); the .m files were never populated. Defer CAVES_code. |
|| GRAIL GRGM1200A coefficient table | **ACQUIRED 2026-08-19** | `~/lunarvoid/data/evidence/grail/GRGM1200A_SHA.TAB` (36 MB, l_max=680 in current partial download). Used by `code/wp3_fusion/evidence_layers.py`. | Full l_max=1200 download was killed by the 600s timeout; the l_max=680 subset is sufficient for v0.1 evaluation (10-30 km gravity resolution, well below l=680's ~6 km Rayleigh limit). Re-resume for v0.2 if higher resolution is needed. |

## Code modules (2026-08-19, session 2)

Staged 12 new modules under `01_WORKSPACE/code/`:

|| Module | Path | Status |
||---|---|---|---|
|| scope_map_v11 | `wp0_scope_map/scope_map_v11.py` | DELIVERED, smoke-tested |
|| convert_f32 | `wp1_lla/convert_f32.py` | written; awaits first RAR |
|| degrade | `wp1_ladder/degrade.py` | written, smoke-tested (synthetic) |
|| vci | `wp1_detector/vci.py` | written, smoke-tested (synthetic) |
|| sag_detect | `wp1_detector/sag_detect.py` | written, smoke-tested (synthetic F1=0.39→0.80) |
|| lltb1 | `wp1_lla/lltb1.py` | written; awaits first LLTB-1 site |
|| run_lltb1 | `wp1_lla/run_lltb1.py` | written; awaits first RAR |
|| paper1_skeleton | `wp1_lla/paper1_skeleton.py` | DELIVERED, results sections are placeholders |
|| sag_search | `wp2_sag/sag_search.py` | written; awaits run on real DTM |
|| confusion_layer | `wp2_sag/confusion_layer.py` | DELIVERED, 3 flagship DTMs processed |
|| evidence_layers | `wp3_fusion/evidence_layers.py` | DELIVERED, MTP region processed (gr_r 1.62-1.67 m/s^2) |
|| fusion | `wp3_fusion/fusion.py` | written, smoke-tested (synthetic AUC=0.990) |
|| smoke_test | `smoke_test.py` | DELIVERED, exercises whole pipeline on a 200x200 synthetic cloud |

## Licence notes (from dataset assessment, 00_SOURCE_ORIGINALS)

- PDS holdings: public domain, not analysis-ready (raw EDR needs ISIS chain).
- LROC *web* products (quickmap, previews): ASU terms differ from PDS archive.
- NASA analog LiDAR: research/academic use only — no redistribution.
- ISRO (OHRC/TMC-2): prescribed acknowledgement mandatory.
