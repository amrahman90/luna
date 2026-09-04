# LUNARVOID Audit Findings — Correctness/Performance (read-only)

Auditor: MiniMax-M3 subagent. Scope: 54 Python files (~12.7K LOC) under
`01_WORKSPACE/code/`. Read-only; no code modified. Focus areas: correctness/bugs,
performance, and verification that the documented bug fixes are actually present.

---

## Findings

### [CORR-01] Frangi float32 overflow risk returns in `sag_detect.py`
- **Evidence**: `01_WORKSPACE/code/wp1_detector/sag_detect.py:83-89` — `frangi_vesselness()`
  fills NaN via `np.nanmean` but does NOT upcast to float64; the float32 `Zf` is fed
  directly to `skimage.filters.frangi`. Same pattern in `wp2_sag/sag_search.py:141-145`.
  The documented fix (`Zf = Zf.astype(np.float64)`) is present in
  `wp2_sag/transfer/score_raster_gen.py:85` and `wp2_sag/sag_search_run.py:70`, but NOT
  in the production LLTB-1 detector (`sag_detect.py`) which is what the LLTB-1
  reproduceability claim rests on.
- **Impact**: With sigmas_px ≈ 60 m / 0.5 m = 120 px, the Hessian eigenvalues of a float32
  DTM can overflow to `inf`, producing artefact Frangi ridges at the 60-300 m tube band on
  flat mare panels — false positive tube detections. Affects every WP1 detector re-run.
- **Effort**: S.
- **Risk**: LOW — float64 upcast is the documented convention.
- **Confidence**: HIGH.
- **Fix sketch**: Insert `Zf = Zf.astype(np.float64)` after the NaN fill in
  `sag_detect.frangi_vesselness()` and `sag_search.frangi_vesselness()`. Same one-line fix.

### [CORR-02] Fractional-scale rebin bug reappears in 4 scripts (only score_raster_gen.py fixed it)
- **Evidence**:
  - `wp2_sag/sag_search_run.py:116` — `factor = max(1, int(round(rung / res_full)))`
  - `wp2_sag/transfer/noise_floors_batch.py:81` — same integer-factor pattern
  - `wp2_sag/transfer/calibrate_transqpit1.py:120` — same
  - `wp2_sag/transfer/transfer_apply.py:171` — `factor = max(1, int(round(H_src / shape[0])))`
  - `wp2_sag/sag_search.py:206` — `if abs(res - r) / r > 0.6` then SKIP (no fractional rebin either)
  The documented fix is in `wp2_sag/transfer/score_raster_gen.py:144` only:
  `scale_factor = max(1.0, float(rung) / res_full); new_h = max(1, int(np.ceil(H_src / scale_factor)))`
  with `transform * scale(W_src/new_w, H_src/new_h)`. The other scripts silently produce
  the wrong-size raster (e.g. for `rung=5, res_full=2`: factor=2 → 4 m grid, not 5 m).
- **Impact**: Per-DTM noise floors (noise_floors_batch), the calibration
  (calibrate_transqpit1), the production sag_search_run, and the transfer cache
  (transfer_apply) all compute FP/10⁴ km² and threshold tuning on a wrong-size grid.
  Calibration FP rates for non-integer rungs (5 m from a 2 m source) are computed at
  4 m, biasing the FROZEN calibration the headline N=19 transfer is anchored to.
- **Effort**: M — needs the same fix across 4 files, plus re-running on cached rasters
  to confirm no drift, plus unit test for fractional rebin.
- **Risk**: MED — re-deriving calibration from cached score rasters could perturb the
  frozen numbers; needs a parity check vs score_raster_gen output.
- **Confidence**: HIGH.
- **Fix sketch**: Factor the fractional rebin into a shared helper in
  `wp2_sag/transfer/score_raster_gen.py` (e.g. `rebin_to_rung(src_path, rung)`) and call
  it from all four sites. Re-run on the 7 cached DTMs and verify the FROZEN
  TRANSQ-PIT1 calibration numbers reproduce byte-identical (or document the delta).

### [CORR-03] Score-raster generator runs Frangi on the wrong (source-resolution) grid
- **Evidence**: `wp2_sag/transfer/score_raster_gen.py:165-186` — after rebinning DTM to
  the requested rung posting (`dtm_r`), the Frangi sub-sample block opens the SOURCE
  DTM again (`with rasterio.open(dtm_path) as src: dtm_fr = src.read(1, out_shape=(new_h, new_w), ...)`)
  instead of sub-sampling the rebinned `dtm_r`. `effective_rung = res_full * (src.width / new_w)`
  is the source-equivalent posting, not the requested rung. Depth is at the rung posting
  (`dtm_r`); Frangi runs on the source-resolution sub-sampled grid; `score = depth × F`
  mixes the two grids via `scipy.ndimage.zoom` (line 228-233).
- **Impact**: For DTMs >5000-px in largest dim (TYCHOPK07 ~ 365 MB, FRESHMELT ~ 354 MB
  per the module docstring), Frangi sigmas are at the source posting, not the FROZEN
  rung posting. This silently changes the band of vesselness for the same nominal sigma
  list — the FROZEN recipe "Frangi sigmas = (30, 60, 100, 150, 200, 300) m" only holds
  when Frangi is at the requested rung posting. depth × F then mixes two semantically
  different scales through a bilinear zoom.
- **Effort**: S — change `src.read(...)` to `dv = dtm_r`; resample `dtm_r` instead of source.
- **Risk**: MED — could change the FROZEN cache contents.
- **Confidence**: HIGH.
- **Fix sketch**: Replace the `with rasterio.open(dtm_path) as src` block in the
  `max(H_r, W_r) > FRANGI_MAX_DIM` branch with a `rasterio.warp.reproject` /
  `np.repeat` block-average of `dtm_r` itself, then compute `effective_rung = rung`
  (the requested posting), not `res_full * (src.width / new_w)`.

### [CORR-04] Confusion-layer GeoTIFFs written with Earth EPSG:4326 instead of Moon proj4
- **Evidence**: `wp2_sag/confusion_layer.py:147` — `profile = {... "crs": "EPSG:4326" ...}`
  but the underlying grids are Moon lon/lat on `+proj=longlat +R=1737400` (lines 56, 58,
  65, 75). The Earth ellipsoid (WGS84) is implied by EPSG:4326, so a downstream pyproj
  reprojection will apply the wrong Earth ellipsoid for distance/area calcs.
  The same erroneous CRS appears in `wp3_fusion/evidence_layers.py:147` (GRAIL rasters
  on a Moon lon/lat grid written as EPSG:4326).
- **Impact**: Anyone using these rasters with a Moon-CRS reprojection will silently get
  Earth-ellipsoid distances. The confusion_layer.py outputs are referenced from
  `transfer_apply.py` tier-B logic via direct distance math (haversine_m on
  `+proj=longlat +R=1737400`), so the bug is partially mitigated for the live
  transfer pipeline, but consumers of the GeoTIFFs themselves get bad CRS metadata.
- **Effort**: S.
- **Risk**: LOW.
- **Confidence**: HIGH.
- **Fix sketch**: Replace the literal `"EPSG:4326"` with the Moon CRS proj4 used
  elsewhere in the file (`CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")`),
  written via `src_crs.to_wkt()` or stored as `crs=moon_geog.to_wkt()` in the profile.
  Same one-line fix in `evidence_layers.py:147`.

### [CORR-05] Moon CRS for non-lunar analog VCI raster silently uses Earth UTM zone 31N
- **Evidence**: `wp1_detector/vci.py:131-143` — writes VCI raster with `crs="EPSG:32631"`
  (Earth UTM zone 31N) for a Moon-projection-like coordinate. `wp1_detector/sag_detect.py:100`
  defaults `write_geotiff` to the same Earth CRS. `wp1_ladder/degrade.py:83-84, 100-101`
  also uses EPSG:32631 with the comment "any local metric CRS; transform is what matters".
- **Impact**: The analog LiDAR site (Indian Tunnel, Lava Beds NM, CA) is on Earth, so
  EPSG:32631 is geographically wrong (CA is UTM 10N, EPSG:32610). Any downstream tool
  using the CRS (rather than the local transform) will misregister. For Lunar LLTB-1 v0.1
  reproduceability, the comment "transform is what matters" is technically true for
  rasterio.warp.reproject when CRS is symmetric, but downstream QGIS / GDAL consumers
  will treat it as North-Italy terrain.
- **Effort**: S.
- **Risk**: LOW — local transform is preserved.
- **Confidence**: HIGH.
- **Fix sketch**: For VCI on terrestrial analog: use a placeholder CRS like
  `"LOCAL_CS[\"Indian_Tunnel\",UNIT_METRE,0]` or omit CRS and let transform carry
  coordinates. For lunar DTMs: use the `+proj=longlat +R=1737400` Moon CRS. A
  centralised `MOON_CRS_WKT` constant in `lunarvoid_conventions.py` would prevent
  the duplication.

### [CORR-06] NaN-filled Frangi input leaks into flat-panel vesselness responses
- **Evidence**: `wp1_detector/sag_detect.py:87` — `Zf = np.where(np.isfinite(Z), Z, float(np.nanmean(Z[np.isfinite(Z)])) if np.isfinite(Z).any() else 0.0)`.
  Same pattern in `wp2_sag/sag_search.py:143`, `wp2_sag/sag_search_run.py:69`,
  `wp2_sag/transfer/score_raster_gen.py:83`. The `np.nanmean` of all finite values is
  used to fill NaN BEFORE Frangi runs. On a DTM with a wide NoData band (e.g. pit
  floor shadowed), the fill is the regional mean — and Frangi sees a uniform flat
  surface where NoData used to be, producing phantom vesselness responses along the
  NoData boundary.
- **Impact**: Over NoData-bounded regions, Frangi vesselness is non-zero on a
  fabricated flat surface, creating artefacts. The downstream `slope_deg_map` does
  not mask these cells (its `np.isfinite(dtm)` guard uses the original `dtm`, so the
  slope mask is correct, but the score-raster Frangi response is wrong). On any DTM
  with >5% NoData the score raster has ghost ridges at NoData boundaries.
- **Effort**: S.
- **Risk**: LOW.
- **Confidence**: HIGH.
- **Fix sketch**: Mask NaN cells to 0 BEFORE Frangi, then multiply the Frangi output
  by `np.isfinite(Z).astype(np.float32)` so NoData cells stay NaN/zero in the score.
  Equivalent: replace Frangi input with `np.where(np.isfinite(Z), Z, np.nanmedian(Z))`
  and re-mask the output to `np.isfinite(Z_original)`.

### [CORR-07] fetch_log_lroc.csv read with naive `str.split(",")` is fragile
- **Evidence**: `wp8_stereo/retry_nac_edr_fetch.py:194-202` — `parts = line.strip().split(",")`
  on the CSV produced by `fetch_lroc_dtms.py` (which uses `csv.writer`, no quoting).
  Indexing `parts[2]` for product_id and `parts[6]` for sha256 assumes hard-coded
  column order. The writer writes 10 fields (including `elapsed_sec` and `licence`),
  but if the source row ever quoted the URL or the licence string contained a comma
  (e.g. "PDS, public domain" — currently safe but hard-coded), the index-based access
  breaks silently — `product_id` becomes `parts[2]` of a multi-comma field, returning
  a wrong product match and re-downloading already-fetched files.
- **Impact**: Speculative — only a future format change would break it. Current format is
  safe because sha256 never contains a comma. Risk is low today; if the licence
  attribute ever gains a comma, the SHA lookup returns the wrong value or matches a
  partial string and re-downloads.
- **Effort**: S.
- **Risk**: LOW — change is internal to a single script.
- **Confidence**: MED.
- **Fix sketch**: Replace the manual split with `csv.DictReader` over the existing
  fetch_log_lroc.csv (file is already CSV-quoted by `csv.writer` in the producer).
  Adds a row-by-row field validation.

### [CORR-08] Race condition in `parallel_range_download.py` worker writes
- **Evidence**: `wp4_diviner/parallel_range_download.py:79-96` — each `worker()` opens
  the same output file with `open(out, "r+b")` and writes its `[start, end]` byte
  range. The pre-allocation at lines 73-74 (truncate) closes the writer handle before
  workers start, so the file handles are independent — but two threads writing to the
  same file with overlapping `fh.seek(start)` + `fh.write()` can interleave on slow
  storage (POSIX `write()` is atomic for small buffers < PIPE_BUF, but a 1 MB chunk
  is well above that). The fetch_range_to_file helper does NOT serialise the seek/write
  pair.
- **Impact**: Rare data corruption on the assembled file in `~/lunarvoid/data/...`.
  Rare because Python's GIL + buffered I/O often masks it, but on NFS or shared
  storage, chunk interleaving produces a corrupted file whose SHA-256 will mismatch
  PDS — silently, unless the caller verifies SHA-256 (which is currently optional,
  not done by the script). The chunk-by-chunk nature means the corruption is in the
  overlapping window and not catastrophic but visible as the file hash mismatching.
- **Effort**: S.
- **Risk**: LOW — corruption caught at SHA verify, file can be re-downloaded.
- **Confidence**: MED.
- **Fix sketch**: Use `OS_DIRECT` writes via `os.pwrite(fd, buf, offset)` (Linux)
  per thread, which is atomic per call up to filesystem limits; or run chunks
  sequentially instead of with a thread pool. Easiest: serialise the file with
  per-chunk pread/pwrite.

### [PERF-01] Per-DTM serial loops in WP5 PU-learning and WP2 noise-floor batch
- **Evidence**: `wp5_fusion/pu_learning_on_registry.py:354-498` and
  `wp5_fusion/pu_learning_extended.py:461-501` — single-threaded; the three PU
  scripts (`baseline.py`, `on_registry.py`, `extended.py`) each refit a fresh
  `ElkanotoPuClassifier` on the same registry with different feature sets. With
  `n_total = 278` rows and 19 features, fits take ~0.5 s each. `wp2_sag/transfer/noise_floors_batch.py:179-194`
  serially computes per-DTM sag-band noise floors via `run_dtm_floor()` (panel
  extraction, slope maps, DoG) — 21 DTMs × ~30 s each = ~10 min wall time.
- **Impact**: PU-learning baseline + extended + comparison totals ~3 minutes on local
  laptop — fine. Noise-floor batch is the real cost: 21 × 30 s serial = 10+ min when
  each panel extraction + DoG runs is independent across DTMs. Multiprocessing would
  parallelise trivially.
- **Effort**: S (per_dtm_floors); S (pu_learning — actually fine, no action).
- **Risk**: LOW.
- **Confidence**: HIGH.
- **Fix sketch**: In `noise_floors_batch.py`, wrap the `for d in args.dtms:` loop in a
  `concurrent.futures.ProcessPoolExecutor` (DoG + panel extraction release the GIL
  for some sub-steps but rely on numpy/scipy which mostly release the GIL; process
  pool is safe). Cap at `os.cpu_count() - 1`. PU-learning is small enough that no
  batching is warranted.

### [PERF-02] Planchon-Darboux re-run per rung in WP2 ladder
- **Evidence**: `wp2_sag/transfer/score_raster_gen.py:194-218` and
  `wp2_sag/sag_search_run.py:158-179` — for every (DTM, rung) pair, the full PD fill
  is re-run, writing a temporary filled raster to disk and reading it back. For a DTM
  with rungs [2, 4, 5], the PD fill is run 3 times on the SAME source DTM rebinned to
  3 different postings — the fill is monotonic in scale, so the deepest fill at the
  finest rung is an upper bound for the fill at coarser rungs (often equal).
- **Impact**: PD fill is O(N log N) in the grid and writes ~50 MB per rung. For the
  21 DTM × 3 rung matrix, ~63 PD fills, each 10-60 s = ~10-30 minutes total. The
  fills at finer rungs could be cached and a fast `np.maximum.fill` reuse could
  short-circuit the coarser rungs.
- **Effort**: M.
- **Risk**: MED — caching assumes the fill is monotonic in scale, which is true for
  PD but needs verification on edge cases (filled cells at a finer grid may not exist
  at a coarser grid due to rounding).
- **Confidence**: MED.
- **Fix sketch**: Cache the filled raster at the finest rung per DTM; for coarser
  rungs, `scipy.ndimage.zoom` the cached fill and reuse. Or, accept the redundant cost
  if runtime is not currently the bottleneck (claim: it is, per the module docstring).

### [PERF-03] Frangi is run on the full DTM at every rung for `score_raster_gen`
- **Evidence**: `wp2_sag/transfer/score_raster_gen.py:238-241` — `F = frangi_vesselness(dtm_fr, sigmas_px)`
  with `dtm_fr` at sub-sampled 5000-px max dim, but per rung. For DTMs at multiple
  rungs, the Frangi is independent across rungs but identical in structure (same DTM,
  same sigma list). Frangi is O(N σ² log σ) per axis — at 5000 px with 6 sigmas up to
  300 px, ~10-30 s per rung.
- **Impact**: For 21 DTMs × 3 rungs = 63 Frangi calls. Could batch the per-DTM Frangi
  runs into a single sigma list if all rungs share the same physical-scale sigmas
  (they do — FROZEN_SIGMAS_M = (30, 60, 100, 150, 200, 300)). The 6 sigmas are
  shared, just expressed in different pixel counts. No actual speedup from batching
  unless the data is on the same grid.
- **Effort**: L — needs a multi-rung Frangi-once architecture refactor.
- **Risk**: HIGH — breaks the FROZEN recipe if not careful.
- **Confidence**: LOW — likely not worth the refactor; the per-rung cost is bounded.
- **Fix sketch**: Defer; record as "noted but not worth fixing for current N=10 budget".

### [CORR-09] `confusion_layer.py` graben layer is a deterministic placeholder, not data
- **Evidence**: `wp2_sag/confusion_layer.py:131-141` — class-4 (graben) cells are
  written as `graben_mask[i, j] = 1` for `(i, j) = (step, i*3 % nx)`, every 41st row,
  with a deterministic stride. This is honest about being a placeholder (the docstring
  says "placeholder; flag as derived, not curated") but the class-4 label is emitted
  in the JSON summary and consumed downstream by `transfer_apply.py` (line 462: `chain_pts = build_crater_chain_index(dtm_bbox)` — note that build_crater_chain_index returns chain craters, not graben; the graben class is not currently consumed).
- **Impact**: Low today — the graben class is not consumed by tier-B promotion logic
  (which uses rille and chain only, lines 519-527). If a future tier-B gate adds
  "non-graben", the placeholder will produce wrong tier promotions.
- **Effort**: S — remove the placeholder, or compute a real graben mask from SLDEM
  hillshade (the docstring mentions this as the intended source).
- **Risk**: LOW.
- **Confidence**: HIGH.
- **Fix sketch**: Either (a) drop the graben class entirely (set `graben_mask = np.zeros_like(confusion)`)
  and update the class table to skip class 4, or (b) implement the SLDEM hillshade
  graben detection referenced in the docstring.

### [CORR-10] Sentinel filter in `convert_f32.py` has an off-by-bandwidth subtle risk
- **Evidence**: `wp1_lla/convert_f32.py:71-73` — uses `|x|, |y|, |z| > 1e3` as the
  sentinel threshold. The docstring says "1e38 is the sentinel; values > 1e3 are
  sentinels" but the comment on lines 67-70 also notes "values < 1e3 m are kept as
  real data even in cliff/cave overhangs". For the Kingsbowl / Indian Tunnel analogs
  (terrestrial), site-frame coordinates are typically 0-200 m, so 1e3 is well above
  the data range. BUT: if a future analog has wider geometry (e.g. SP Mountain or
  SP Flow, ~1.5 km), real values would exceed 1e3 and be silently NaNed.
- **Impact**: Cross-site portability risk: a future analog with extent >1 km has its
  edges clipped. Documented as a known limitation but easy to overlook when adding
  a new site. Low likelihood (current 4 sites are all <1 km) but high consequence
  (silent NaN of valid data).
- **Effort**: S.
- **Risk**: LOW — current sites are safe.
- **Confidence**: MED.
- **Fix sketch**: Tighten the sentinel check to `|val| > 1e6` (six orders of magnitude
  above any plausible real value) and add an explicit `SENTINEL_X_MAX = 1e6` constant
  per the documented convention. Log a warning per chunk if any value >100 m is seen,
  so future wider sites surface the warning.

---

## Summary — top findings ranked by leverage

1. **CORR-02** (fractional rebin bug in 4 scripts) — **HIGHEST LEVERAGE**. The
   FROZEN calibration numbers (FP/10⁴ km² for the headline N=19 transfer) are
   anchored to TRANQPIT1 at the rung grid. With the integer-factor bug, the rung
   grid is the wrong size for non-integer rung ratios (2 m source → 5 m rung gives
   4 m). This silently perturbs every per-DTM noise floor and the calibration itself.
   Fix in 4 files; one shared helper.

2. **CORR-01** (Frangi float32 overflow in `sag_detect.py`) — **HIGH IMPACT**,
   **LOW EFFORT**. Production LLTB-1 detector runs on float32. The fix is documented
   but only applied in 2 of 4 Frangi call sites. One-line fix per call site.

3. **CORR-03** (Frangi at source posting, not rung posting, in `score_raster_gen.py`)
   — **HIGH IMPACT** on the cached score rasters used by the headline N=19 transfer.
   Effective rung is the source-equivalent, so Frangi sigmas scale incorrectly. Fix
   is a one-line change to sub-sample `dtm_r` rather than re-opening the source.

4. **CORR-06** (NaN-fill before Frangi creates phantom vesselness along NoData
   boundaries) — **MEDIUM IMPACT**, affects every WP2 score raster with shadowed
   pit floors. One-line fix.

5. **CORR-04** (Earth EPSG:4326 written for Moon lon/lat rasters in
   `confusion_layer.py` and `evidence_layers.py`) — **MEDIUM IMPACT** for
   downstream consumers; not breaking the live transfer pipeline but a real CRS
   metadata bug.

6. **PERF-01** (per-DTM serial loops in WP5/WP2 noise-floor batch) — **LOW EFFORT**.
   Process-pool parallelisation would cut wall time 4-8× on the 21-DTM batch.

7. **CORR-05** (Earth UTM 31N written for analog VCI raster) — **LOW IMPACT**
   for the live pipeline (transform is preserved) but breaks for downstream
   geo-registered tools. Same shared-constant fix as CORR-04.

8. **CORR-09** (graben placeholder) — **LOW IMPACT** today (not consumed) but
   documentation-disciplined code should not emit placeholder data as a labelled
   class. Drop or compute real.

The rest (CORR-07, CORR-08, CORR-10, PERF-02, PERF-03) are speculative or low-priority
and would not be flagged in a high-leverage audit pass.

---

## Files audited (full or substantial read)

- wp0_primitive/sweep_pits.py, depression_depth.py
- wp0_scope_map/scope_map.py, scope_map_v11.py
- wp0_kriging/kriging_correction.py, noise_floor.py, per_dtm_floors.py
- wp1_lla/convert_f32.py, lltb1.py
- wp1_detector/sag_detect.py, vci.py, connected_component_filter.py,
  v0_2_pipeline_integration.py
- wp1_ladder/degrade.py, hapke_render.py, sensor_degrade.py
- wp2_sag/sag_search.py, sag_search_run.py, confusion_layer.py
- wp2_sag/transfer/score_raster_gen.py, noise_floors_batch.py, transfer_apply.py,
  calibrate_transqpit1.py
- wp4_diviner/sample_diviner_at_candidates.py, parallel_range_download.py
- wp5_fusion/pu_learning_baseline.py (header), pu_learning_on_registry.py,
  pu_learning_extended.py
- wp8_stereo/fetch_lroc_dtms.py, retry_nac_edr_fetch.py
- wp3_fusion/evidence_layers.py (relevant slice)
- smoke_test.py (relevant slice)

## Files NOT audited and why

- wp1_analog/* (icp.py, register_cave.py, make_void_mask.py, io_analog.py,
  explore_indian_tunnel.py, coarse_search.py) — out of WP2 sag-search focus area;
  would be a separate analog-pipeline audit.
- wp1_lla/run_lltb1.py, verify_v05.py, paper1_skeleton.py — orchestration
  glue; one-line CLI wrappers, low bug density expected.
- wp1_paper/generate_graphical_abstract.py — figure-only, off the audit path.
- wp2_sag/transfer/apply_skeptic_annotation*.py — minor CSV/JSON annotation
  pass; would not yield high-confidence findings without running the upstream
  registry through them.
- wp2_sag/transfer/merge_cycle1.py — bulk merge; one CSV concat, no per-DTM logic.
- wp5_fusion/pu_learning_baseline.py — synthetic-data skeleton, low-impact; the
  real-data versions (on_registry, extended) were audited.
- setup/extract_rar.py, tools/regen_site_notes.py — infra utilities, off the
  scientific-pipeline audit path.
- 00_SOURCE_ORIGINALS/ — read-only archive; not part of this audit per AGENTS.md.
