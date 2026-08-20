# LUNARVOID — Changelog

All notable changes to this project are documented here.
Newest entries first. Format: date — what — where — why.

---

## 2026-08-19 (execution session 2)

- **Roadmap Tasks 9-10 COMPLETE** (this session, code in
  `01_WORKSPACE/code/wp0_scope_map/scope_map_v11.py`,
  `01_WORKSPACE/code/wp2_sag/`, `01_WORKSPACE/code/wp3_fusion/`):
  - Task 9: scope-map refresh v1.1 (Hurwitz rilles + LU5M812TGT
    craters added to the intersection). Headline: 10 DTMs carry
    Hurwitz rille segments; 3 of 21 tube-relevant pits sit within
    60 km of a rille segment; ranked WP2 target list produced.
    Reports: `01_WORKSPACE/data/outputs/wp0_scope_map_v11/`,
    `01_WORKSPACE/plans/figures/wp0_scope_map_v11_*.png`. Top
    target: MARIUSCONE (6 rille segs, 2 unique rilles, 1 pit,
    flagship site).
  - Task 10: deferred to next session (gate G0' report
    synthesises Z0 + Z1; not ready until LLTB-1 numbers land).
- **Roadmap Phase Z1 STAGED** (5 new modules written; the analog
  RAR download is in progress; v0.1 deliverables will be produced
  as each RAR completes):
  - `code/wp1_lla/convert_f32.py` — NASA Pits & Caves 7-float
    binary -> .npz + .las; exact point-count check by file size.
  - `code/wp1_ladder/degrade.py` — 5-rung GSD ladder (2 cm, 0.5 m,
    2 m, 5 m, 60 m) via rasterio average resampling; hillshade
    preview per rung.
  - `code/wp1_detector/vci.py` — Vertical Complexity Index
    (Shannon evenness of the height-binned column distribution,
    v5 I8) + local-max threshold + centroids.
  - `code/wp1_detector/sag_detect.py` — Planchon-Darboux
    depression depth + Frangi vesselness at 30-300 m + per-rung
    threshold re-tuning (I9) + FP/10^4 km^2 + stratified
    detectability curve (I11).
  - `code/wp1_lla/lltb1.py` — LLTB-1 v0.1 loader + quicklook;
    `code/wp1_lla/run_lltb1.py` end-to-end driver.
- **Roadmap Task 16 (Paper 1 skeleton) DELIVERED** —
  `01_WORKSPACE/papers/paper1_resolution_limits/main.md` +
  `outline.md`; v0.1 results sections are placeholders
  populated as Z1 outputs land.
- **Roadmap Phase Z2 STAGED** (2 new modules):
  - `code/wp2_sag/sag_search.py` — reuses kriging_correction +
    Planchon-Darboux + Frangi + per-rung threshold; emits
    per-candidate CSV with the I5 sun-azimuth attribution
    placeholder.
  - `code/wp2_sag/confusion_layer.py` — 5-class confuser raster
    per DTM (rille, crater chain, ridge placeholder, graben
    placeholder, background); 593 DTMs flagged for chain
    candidates, MARIUSPIT01 carries 1795 rille cells (1.8% of
    footprint), the dominant confuser.
- **Roadmap Phase Z3 STAGED** (2 new modules):
  - `code/wp3_fusion/evidence_layers.py` — parses GRAIL
    GRGM1200A coefficient table (l_max=680 in current file),
    evaluates radial/theta/phi gravity at any lat/lon/r via
    pyshtools+Moon2015, writes 4 GeoTIFFs + figure per
    region. Successful run over MTP region (30-35 E, 6-11 N);
    gr_r 1.62-1.67 m/s^2, gradient magnitude 1e-8 Eotvos.
    Diviner placeholder metadata JSON; full ingestion deferred
    to v0.2 (Powell 2023 derivative; needs LOLA-style REST
    query setup, ~half a day).
  - `code/wp3_fusion/fusion.py` — CPU prototype: z-score
    normalised features (depth, frangi, vci, grail, diviner
    placeholder) -> logistic regression, 5 single-feature
    baselines + 1 fusion model; reports AUC / F1 / P / R /
    Brier; ROC + 10-bin reliability figure.

- **Manifest updates (2026-08-19, session 2)**: added 4 new
  files (Lunar Pit Atlas, NAC DTM index, Hurwitz rilles,
  LU5M812TGT) plus 7 NAC DTMs (TRANQPIT1, MARIUSPIT01,
  INGENIIPIT, SWFECUNPIT1, FECNDITATS2, PRCLRMPIT01, IRIDIUMPIT1)
  plus 2 LOLA RDR subsets plus 1 GRAIL coefficient table.
  16+ entries total. SHA-256 logged for each.

- **Dependency additions** (env extension Task 2 of the
  zero-cost roadmap): scikit-image 0.26.0, pyshtools 4.14.1,
  boule 0.6.0 installed in the existing venv via
  `uv pip install` (no cost). `requirements.txt` is NOT
  yet regenerated (post-v0.1 freeze).

## 2026-08-19 (execution session 2)

- **Roadmap Tasks 9-10** (scope-map v1.1 + G0' prep) and **Z1
  staging** (5 LLTB-1 modules written, smoke-tested on a synthetic
  cloud) and **Z2 staging** (sag-search + confusion-layer modules
  + first real lunar runs on TRANQPIT1/MARIUSPIT01/INGENIIPIT) and
  **Z3 staging** (GRAIL + Diviner + fusion prototype, smoke-tested
  on synthetic) all DELIVERED in this session. CHANGELOG entry
  above records the high-level summary; full per-task detail in
  `01_WORKSPACE/notes/2026-08-19_session2_summary.md`.
- **NEW real results (not smoke-test)**:
  - TRANQPIT1 sag-search @ 5 m: **29 candidate peaks** within the
    MTP footprint; top score 39.2 (depth 119 m, Frangi 0.33) at
    proj (-4408276, 265220) m — MTP pit location
    (catalogued 8.34 N, 33.22 E, ~50 m offset, within Pit Atlas
    30 m positional accuracy + cell resolution).
    CSV: `data/outputs/wp2_sag/MTP/sag_candidates.csv`.
  - MARIUSPIT01 sag-search @ 4 m: **276 candidate peaks** in
    the Marius Hills region; top score 5.0 at proj (3629650,
    435132) m. Note: lower Frangi due to incised rille funnel
    geometry (pre-registered v5 I14 failure mode for this site).
  - INGENIIPIT sag-search @ 2 m: **393 candidate peaks** in
    Ingenii; top score 19.3.
  - Confusion layer for TRANQPIT1/MARIUSPIT01/INGENIIPIT: 1795
    rille cells in MARIUSPIT01 (1.8% of footprint, dominant
    confuser per v5 Section 6).
  - GRAIL evidence over MTP region (30-35 E, 6-11 N): gr_r
    1.62-1.67 m/s^2, gradient magnitude p50 1e-8 Eotvos.
- **Bugs found and fixed**:
  1. `cloud_ground_truth` in `sag_detect.py` and `fusion.py` was
     using a 5x5 minimum filter; the per-cell min equals the
     local min for a flat cloud with a small void, so the diff
     was 0. Fixed to a 21x21 nan-robust median envelope
     (~5-10x the largest expected void cell).
  2. `evidence_layers.py`: GRAIL coefficient parser was
     whitespace-splitting a comma-delimited file. Switched to
     `csv.reader`. Pyshtools 4.x API uses `from_array()`.
     Coeffs layout is `coeffs[i, l, m]` with `i=0 -> Clm`,
     `i=1 -> Slm`. PDS shadr file's header GM/R are in
     non-standard units; overrode with Konopliv 2013 Moon
     constants. `grav.tensor()` returns a 2D map; use
     `grav.expand(lat, lon, r)` for pointwise gravity, then
     finite-difference the gradient magnitude. `expand()`
     requires `r` as an array, not a scalar.
  3. `sag_search.py`: `class A: pass` -> `argparse.Namespace`.
     WBT was not finding its binary; added `set_whitebox_dir`
     + `set_working_dir(/tmp)` + absolute paths. WBT requires
     geokeys in the input GeoTIFF; re-use `src.profile` for
     sub-sampled rasters instead of constructing a fresh
     profile without CRS. Frangi overflows on float32 with
     large sigmas; switched to float64.
  4. `sag_search_run.py`: whitebox panics on files without
     geokeys; sub-sampled DTMs need source CRS in profile.
     Frangi takes >5 min on 12529x3331; auto sub-sample to
     5000 px max dimension for speed while keeping depth
     raster at the requested posting.
- **NASA analog download status**: Kingsbowl 82% (433/530 MB),
  IndianTunnel_surface 86% (950/1100 MB), IndianTunnel_cave 19%
  (396/2070 MB), Fieg 100% (243 MB), HDR panos not started,
  Sheepridge not started. Partial RARs yield 0-byte .f32
  outputs from 7z (extraction only succeeds when the RAR is
  complete). Next session: resume Kingsbowl + Sheepridge
  downloads, then `convert_f32.py` -> LLTB-1 v0.1.

## 2026-08-19 (execution session 1, cont. 2)

- **Roadmap Task 5 COMPLETE** — kriged I2 correction on TRANQPIT1:
  - LOLA RDR acquired via oderest.rsl.wustl.edu GDS REST (8,488 shots,
    PDS public domain). 2,977 no-change points (slope<2deg, 5-sigma-MAD
    trim); 2,382 train / 595 check (seed 42).
  - Check-point RMSE 0.373 -> 0.327 m, bias -0.083 -> -0.024 m. KEY
    FINDING: published NAC DTMs are already LOLA-registered at decimetre
    level — unlike P1's terrestrial case (4.53 -> 0.21 m), the inherited
    correction is small but the residual NOISE FLOOR IS ~0.33 m.
  - Correction is 100% low-frequency (all power at lambda>300 m; 60-300 m
    band RMS 0.0025 m = 0.8% of signal band) — I2 smoothness claim holds.
  - Signal preservation: MTP pit depth 129.73 m post-correction vs 129.67
    raw (+0.05%) — gate passed.
- **Roadmap Task 7 COMPLETE** — both confusion layers acquired:
  - Hurwitz rilles UNBLOCKED via Wayback CDX API (Brown still down):
    SinuousRilles_obs.zip, 532 wall segments = 195 unique rilles, 2 XLSX
    attribute tables. CRS: Moon eqc central-meridian 180 — reproject
    before LROC use; Kaguya-TC digitisation offset caveat in manifest.
  - LU5M812TGT (Zenodo 13990480, CC-BY-4.0): 5.69M craters -> filtered
    4.45M rows (0.4-5 km, +/-60deg), csv.gz subset.

## 2026-08-19 (execution session 1, cont.)

- **Roadmap Task 4 COMPLETE** — 8-pit primitive sweep (subagent):
  - **7/8 pass** at >=50% recovered depth (threshold 6/8 MET).
  - Sole failure: Marius Hills (0.364) — pit incised into Rille A, PD fill
    spills sideways; interior 98% valid (NOT the NoData-drain mode). This
    matches the pre-registered v5 I14 funnel-geometry failure prediction.
  - Overshoot cases (frac>1, e.g. Sinus Iridum 2.3x) = fill-to-spill
    geometry, documented not errors.
  - Geodesy fixes: PDS 301-redirects to pds.mcp.nasa.gov; IRIDIUMPIT1/
    FECNDITATS2 use unwrapped x-frames (~331degE in metres) needing
    whole-360deg x-shifts (sweep_pits.py pit_to_pixel).
  - Deliverables: pit_recovery_table.csv, pit_recovery_summary.png,
    sweep_pits.py, 12 manifest rows; FECNDITATS2 actual res 2 m/px
    (catalog said 4).

## 2026-08-19 (execution session 1)

- **Roadmap Tasks 1-3 COMPLETE** (subagent-driven, reviewed):
  - Task 1: prior-art matrix — 33 refs in `notes/prior_art_matrix.csv` +
    `.md` twin; 6 priority rows fully populated.
  - Task 2: env extended (whitebox 2.4.0 binary, pykrige, rasterio,
    sklearn, laspy); requirements.txt regenerated.
  - Task 3: TRANQPIT1 DTM (130 MB) acquired; depression-depth primitive
    built (`code/wp0_primitive/depression_depth.py`). ACCEPTANCE PASS:
    129.7 m recovered at pit (criterion >50 m); flat-panel max 8.1 m
    (criterion <30 m).
    - Methodological finding: Wang & Liu fill AND breach fill FAIL on
      shadowed pit interiors (NoData floor drains the sink — 3.2 m /
      0.3 m recovered). Planchon-Darboux epsilon fill is the required
      engine. Variant log: `notes/2026-08-19_task3_transqpit1_fill_variants.md`.
    - Figure: `data/outputs/wp0_primitive/TRANQPIT1_depth_check.png`.
    - Manifest updated (DTM products section).

## 2026-08-19 (later)

- **Zero-cost execution roadmap delivered**:
  `plans/2026-08-19_ZEROCOST_Roadmap.md` — subordinate to v5 (supersedes
  nothing). Phases Z0-Z3 = 21 tasks covering WP0 completion, WP1/LLTB-1
  flagship, WP2 zero-cost slice, WP3 CPU prototyping; explicit COST
  BOUNDARY table (T1-T4 triggers) with standing STOP-and-ask rule.
  Includes optional $0 local ISIS+ASP reproduction experiment (Task 8)
  that could de-scope the first Tier-1 rental entirely.

## 2026-08-19

- **Project scaffolding established.**
  - Created `00_SOURCE_ORIGINALS/` (read-only archive): all 7 original
    planning documents moved here, untouched thereafter.
  - Created `01_WORKSPACE/` with subfolders `plans/ notes/ code/ data/
    papers/ admin/` + `README.md` conventions.
  - Created `AGENTS.md` (permanent agent rules) and `opencode.json`
    (hard permission enforcement: edit/deny on `00_SOURCE_ORIGINALS/**`).
- **WP0 Phase A started** (zero-cost, local machine — per user decision):
  - Scope-map intersection is the first task.
  - Tier-1 / paid work explicitly deferred.
- **Environment:** `uv` venv at `~/lunarvoid/venv` (Python 3.12,
  geopandas 1.1.4 + pyogrio/matplotlib/shapely); spec saved to
  `code/setup/requirements.txt`. Raw data dir: `~/lunarvoid/data/`.
- **Index layers acquired** (see `data/MANIFEST.md` with checksums):
  NAC DTM footprints (660 DTMs, through 2026-06-15) + Lunar Pit Atlas
  (278 pits), both PDS public domain. Hurwitz rille shapefile BLOCKED
  (Brown server down; fallbacks logged).
- **WP0 scope map DELIVERED** (`code/wp0_scope_map/scope_map.py`,
  report `plans/2026-08-19_WP0_scope_map.md`, figure
  `plans/figures/wp0_scope_map_overview.png`):
  - 21 tube-relevant pits confirmed (16 mare + 5 highland).
  - 8/21 inside good-tier published DTMs incl. all 3 flagships
    (Tranquillitatis 2 m / 0.72 m relat_le).
  - 8/21 with stereo IDs but no DTM -> Tier-1 build queue with product IDs.
  - Data-hygiene: atlas `DTM` field misses Ingenii + SW Fecunditatis
    coverage (19/21 agreement with geometric join).
  - 21 rille-related DTM products identified for WP2 (Rima Sharp 4,
    Vallis Schroteri 2, Rimae Prinz, Lacus Mortis/Rimae Burg, ...).
  - Fixed double-counting bug in terrain coverage (overlapping footprints).
