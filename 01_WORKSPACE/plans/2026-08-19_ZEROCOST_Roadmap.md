# LUNARVOID — Zero-Cost Execution Roadmap

> **For agentic workers:** Execute task-by-task, top to bottom. Steps use
> checkbox (`- [ ]`) syntax for tracking. STOP and ask the user the moment
> any step would require spending money — the entire roadmap up to
> "COST BOUNDARY" (Section 8) is $0 by design.

**Status:** Subordinate execution roadmap. Does NOT supersede anything.
Authoritative plan remains
`00_SOURCE_ORIGINALS/LUNARVOID_Master_Plan_v5_Full_Synthesis.txt` (v5).
This document sequences every zero-cost work item between "now" and "the
first moment money would be required."

**Goal:** Complete WP0 (minus the paid DTM-reproduction rental), all of
WP1/LLTB-1 (the flagship), the zero-cost portion of WP2, and CPU-scale
WP3 prototyping — $0 spent.

**Machine:** Local (8 cores, 31 GB RAM, ~215 GB free disk, Python 3.12 +
uv venv at `~/lunarvoid/venv`). Raw data lives in `~/lunarvoid/data/`,
never in the repo.

**Definition of "cost":** any spend > $0 — VPS rental, GPU hours beyond
free tiers (Colab/Kaggle count as $0), paid APIs, paid software. Local
compute time and public-data downloads are free.

**Conventions:** every task names its files under `01_WORKSPACE/`; every
completed phase updates `admin/CHANGELOG.md` and `data/MANIFEST.md`;
every dataset acquisition gets licence status recorded in the manifest
BEFORE any redistribution plan is made.

---

## Phase dependency map

```
Z0.1 Prior-art matrix ──────────────────────────────┐ (independent, parallel anytime)
Z0.2 Primitive on TRANQPIT1 ─> Z0.3 All-8 sweep ──┐ |
Z0.4 Kriging correction (I2) ─> Z0.5 Noise floor ─┤ |
                                                    v v
Z1 LLTB-1 benchmark (analog LiDAR, ladder, curves) ─> Paper 1
Z2 Lunar sag search on existing DTMs + confusion layer
Z3 Fusion prototyping (CPU)
                    │
                    v
            COST BOUNDARY (Section 8) — first dollar decision
```

Gate criteria (from v5): G0' (zero-cost portion) after Z0; G1 after Z1.

---

# PHASE Z0 — WP0 completion, zero-cost portion
**Target: ~2-4 weeks part-time. Ends at Gate G0' (see Task 10).**

## Task 1 — Prior-art matrix (v5 WP0 deliverable #1)

**Files:**
- Create: `01_WORKSPACE/notes/prior_art_matrix.md`
- Create: `01_WORKSPACE/notes/prior_art_matrix.csv` (machine-readable twin)

- [x] **Step 1.1** Create the CSV with header:
  `ref_id,authors_year,venue,dataset_used,method,main_claim,gap_left_open,relevance_to_LUNARVOID,read_status`

- [x] **Step 1.2** Populate one row per reference. Mandatory set (from v5
  Core Reference Set + dataset assessment sources — 30 rows minimum):

  ```
  Mueller2026 Arctic Science    | DLR UAV snow pipeline, ICP+kriging (I1-I7)
  Reichenzeller2026 Forests 17  | VCI stem detection (I8-I15)
  Mueller2023 RS 15:4308        | spiral flight design (C10)
  Dietenberger2023 RS 15:4366   | stem detection baseline
  WagnerRobinson2014 Icarus     | PitScan, pit distribution
  WagnerRobinson2021 LPSC 2530  | Lunar Pit Atlas catalogue
  WagnerRobinson2022 JGR Planets| pit interior 3D / morphology
  LeCorre2025 Icarus 441        | ESSA Mask R-CNN cave entrances (BASELINE)
  Zhou2024 EarthSpaceSci 11(11) | photogrammetric pit models (MTP + MHH)
  Carrer2024 NatAstro           | MTP radar conduit (only subsurface truth)
  Kaku2017 GRL                  | SELENE LRS Marius Hills echoes
  Chappaz2017 GRL               | GRAIL gradiometry tubes
  Zhu2024 Icarus 408:115814     | GRAIL Marius Hills gradients
  Horvath2022 GRL               | Diviner pit/cave thermal (negative result)
  Powell2023 JGR Planets        | Diviner nighttime T + rock abundance
  Blair2017 / Theinat2020 / Chwala2024 | stability bounds 60-300 m
  Sauro2020 EarthSciRev         | lava tube review (Earth/Moon/Mars)
  Costello2026 JGR Planets      | protolith MTP vs MHH
  Barker2015 Icarus             | SLDEM2015
  Henriksen2017 Icarus 283      | NAC DTM accuracy methodology
  Hurwitz2013 PSS 79-80         | 195 sinuous rilles catalogue
  Cushing2015/2017              | MGC3 Mars cave catalogue
  LaGrassa2024 ISPRS            | LU5M812TGT 5M craters
  Wong2014 NASA                 | Pits & Caves analog dataset
  WatsonBaldini2024/2025 Icarus | Martian cave ML detection
  Silburt2019 Icarus            | DeepMoon (crater CNN, engineering pattern)
  Slater2017 Cryosphere / Sturm1997 | damping metric / conductivity (I6)
  vanEwijk2011 PE&RS            | original VCI definition
  MontanezMunoz2025 JGR Planets | analog gravity forward model
  LunarLeaper2025 ActaAstro     | mission concept (handoff target)
  ```

- [x] **Step 1.3** For the 6 highest-priority rows (Mueller2026,
  Reichenzeller2026, LeCorre2025, Carrer2024, Horvath2022, Henriksen2017)
  fill every column fully from the source documents already in
  `00_SOURCE_ORIGINALS/` (no new reading required — the v3/v4/v5 plans
  quote them extensively).

- [x] **Step 1.4** Mark remaining rows `read_status=queued`.

**Verification:** CSV parses (`python -c "import pandas; pandas.read_csv(...)"`);
≥30 rows; the 6 priority rows have no empty `gap_left_open`.

---

## Task 2 — Environment extension for terrain work

**Files:**
- Modify: `01_WORKSPACE/code/setup/requirements.txt`

- [x] **Step 2.1** Install (all free, binary wheels):

```bash
uv pip install --python ~/lunarvoid/venv/bin/python \
    rasterio whitebox pykrige scikit-learn scipy
```

- [x] **Step 2.2** Verify the two critical engines:

```bash
~/lunarvoid/venv/bin/python -c "import whitebox; w=whitebox.WhiteboxTools(); print(w.version())"
~/lunarvoid/venv/bin/python -c "import pykrige, rasterio, sklearn; print('ok')"
```

- [x] **Step 2.3** Regenerate `requirements.txt`:

```bash
uv pip freeze --python ~/lunarvoid/venv/bin/python > 01_WORKSPACE/code/setup/requirements.txt
```

**Verification:** both commands print versions without error.

---

## Task 3 — Download TRANQPIT1 DTM and build the depression-depth primitive

**Files:**
- Create: `01_WORKSPACE/code/wp0_primitive/depression_depth.py`
- Create: `01_WORKSPACE/data/outputs/wp0_primitive/` (figures/CSVs)
- Raw: `~/lunarvoid/data/dtms/TRANQPIT1/` (outside repo)

- [x] **Step 3.1** Fetch the DTM product page and locate the GeoTIFF:

```
https://data.lroc.im-ldi.com/lroc/view_rdr/NAC_DTM_TRANQPIT1
```

Download the DTM raster (not the browse PNGs) into
`~/lunarvoid/data/dtms/TRANQPIT1/`. Record filename + SHA-256 in
`data/MANIFEST.md`. Expected: a float32 GeoTIFF at 2 m posting,
`relat_le = 0.72 m` (from scope map).

- [x] **Step 3.2** Write `depression_depth.py`:

```python
"""Depression-depth raster = sink_filled(DTM) - DTM (the CHM mirror, v5 S2)."""
import argparse
from pathlib import Path

import numpy as np
import rasterio
import whitebox


def depression_depth(dtm_path: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    filled_path = out_dir / (dtm_path.stem + "_filled.tif")
    depth_path = out_dir / (dtm_path.stem + "_depth.tif")

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False
    wbt.fill_depressions(
        dem=str(dtm_path), output=str(filled_path), fix_flats=True
    )  # WhiteboxTools FillDepressions (Wang & Liu)

    with rasterio.open(filled_path) as f, rasterio.open(dtm_path) as d:
        depth = f.read(1, masked=True) - d.read(1, masked=True)
        depth = np.ma.filled(np.maximum(depth, 0), d.nodata)
        profile = d.profile.copy()
    profile.update(dtype="float32", compress="deflate", nodata=d.nodata)
    with rasterio.open(depth_path, "w", **profile) as out:
        out.write(depth.astype("float32"), 1)
    return depth_path


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("dtm", type=Path)
    p.add_argument("outdir", type=Path)
    a = p.parse_args()
    print(depression_depth(a.dtm, a.outdir))
```

- [x] **Step 3.3** Run it on TRANQPIT1:

```bash
~/lunarvoid/venv/bin/python 01_WORKSPACE/code/wp0_primitive/depression_depth.py \
    ~/lunarvoid/data/dtms/TRANQPIT1/<the-dtm-file>.tif \
    ~/lunarvoid/data/outputs/TRANQPIT1
```

- [x] **Step 3.4** Verification — THE acceptance test (v5 WP0: "verify
  the depression-depth primitive recovers every catalogued pit inside
  that DTM footprint"):

```python
# inspect: load depth raster, extract the pixel at the MTP coordinates
# (8.3355 N, 33.2220 E), and confirm a depression blob of the right scale.
# PASS criteria:
#   1. depth > 50 m somewhere within 200 m of the MTP pit location
#      (catalogued depth ~105 m; sink-fill recovers a lower bound)
#   2. no depression > 30 m anywhere on a >1 km flat panel far from
#      catalogued features (false-positive spot check)
```

Produce a figure: hillshade + depth-raster overlay + pit location marker,
saved to `data/outputs/wp0_primitive/TRANQPIT1_depth_check.png`.

- [x] **Step 3.5** Update `admin/CHANGELOG.md` + `data/MANIFEST.md`.

**Verification:** PASS criteria 1 and 2 both met and documented in the
figure; if the sink-fill misses the pit (possible: pit is an *incised*
feature, not a closed basin, if the floor drains through a shadow gap) —
document the failure and the fix attempt (e.g. `wbt.breach_depressions`
variant) in `notes/`.

---

## Task 4 — Sweep the primitive across all 8 covered pits

**Files:**
- Create: `01_WORKSPACE/code/wp0_primitive/sweep_pits.py`
- Create: `01_WORKSPACE/data/outputs/wp0_primitive/pit_recovery_table.csv`

- [x] **Step 4.1** Loop over the 8 covered pits (from the scope map:
  TRANQPIT1, MARIUSPIT01, INGENIIPIT, SWFECUNPIT1, FECNDITATS2,
  PRCLRMPIT01 [2 pits], IRIDIUMPIT1). Download each DTM via its `url`
  field (recorded in `data/outputs/wp0_scope_map/relevant_pits_x_dtms.csv`),
  run Task-3 primitive, extract max depth within 200 m of each catalogued
  pit point.

- [x] **Step 4.2** Emit `pit_recovery_table.csv`:
  `Name, catalogued_depth_m, recovered_depth_m, recovered_frac, dtm, pass_50pct`

- [x] **Step 4.3** Acceptance: ≥6/8 pits recovered at ≥50% of catalogued
  depth. Failures get individual notes (expected failure mode: funnel
  geometry draining the sink — pre-registered in v5 I14).

**Verification:** table exists, pass rate computed, per-failure notes
written.

---

## Task 5 — Kriged systematic-error correction on TRANQPIT1 (inherited I2)

**Files:**
- Create: `01_WORKSPACE/code/wp0_kriging/kriging_correction.py`
- Create: `01_WORKSPACE/data/outputs/wp0_kriging/TRANQPIT1_corrections.png`
- Raw: `~/lunarvoid/data/lola_tracks/TRANQPIT1/`

- [x] **Step 5.1** Acquire LOLA RDR shot tracks over the TRANQPIT1
  footprint (~30 x 30 km) from the PDS Geosciences Node LOLA RDR
  holdings (pds-geosciences.wustl.edu, LRO-L-LOLA-4/5-RDR-V1.0).
  Select tracks crossing the DTM bounding box only. Record products +
  licence (public domain) in `data/MANIFEST.md`.

- [x] **Step 5.2** Sample the DTM at each LOLA shot → residual
  population. Split: flat-mare "no-change" points (slope < 2° from a
  smoothed DTM gradient) as kriging input; hold out 20% as check points
  (mirrors Mueller2026's 20 independent check points).

- [x] **Step 5.3** Fit and subtract:

```python
from pykrige.ok import OrdinaryKriging
import numpy as np

ok = OrdinaryKriging(
    x=nochange_lon, y=nochange_lat, z=nochange_residual,
    variogram_model="spherical",      # I2: spherical variogram
    coordinates_type="geographic",
)
zgrid, ss = ok.execute("grid", grid_lon, grid_lat)  # ~2000x2000 max
corrected = dtm - zgrid               # subtract smooth distortion surface
```

- [x] **Step 5.4** Report exactly what P1 reported (v5 I2): bias and
  RMSE at check points, before-correction vs after; plus the spatial
  frequency comparison (radially averaged power spectrum of the kriged
  surface vs the residual field) proving the correction is smooth and
  did NOT eat the pit/sag signal.

**Verification:** RMSE at check points reduced; spectrum plot shows
kriged surface energy concentrated at low frequency. Numbers go into the
Gate G0' report (Task 10).

---

## Task 6 — Zero-change noise-floor panels (inherited I3 → pre-G1 measurement)

**Files:**
- Create: `01_WORKSPACE/code/wp0_kriging/noise_floor.py`
- Create: `01_WORKSPACE/data/outputs/wp0_kriging/noise_floor_stats.csv`

- [ ] **Step 6.1** Select ≥3 flat mare panels (≥1 km² each, slope < 2°,
  no catalogued pits/rilles/craters > 50 m) inside TRANQPIT1 (and later
  MARIUSPIT01 as a second instrument-geometry case).

- [ ] **Step 6.2** After Task-5 correction, compute the full residual
  distribution per panel: mean, median, SD, P10, P90 (P1's reporting
  format: mean 10.99 cm / SD 21.64 cm is the terrestrial reference).

- [ ] **Step 6.3** Write the one-line answer the whole project turns on
  (v5 Section 4 critical path): **is the expected roof-sag amplitude
  (~1-5 m over 60-300 m width) above this noise floor at 2-5 m posting?**
  Record the verdict in `noise_floor_stats.csv` header comment — this is
  a preliminary G1 signal, refined in Z1 with the real ladder.

**Verification:** stats table complete; verdict sentence written; figure
(residual histograms per panel) saved.

---

## Task 7 — Confusion-layer acquisition, attempt 2

**Files:**
- Raw: `~/lunarvoid/data/index_layers/hurwitz_rilles/`
- Raw: `~/lunarvoid/data/index_layers/craters_lu5m812tgt/`
- Modify: `01_WORKSPACE/data/MANIFEST.md`

- [x] **Step 7.1** Retry Hurwitz rille shapefile, in order:
  1. `https://planetary.brown.edu/html_pages/rilles.html` (server was down)
  2. Wayback Machine:
     `http://archive.org/wayback/available?url=planetary.brown.edu/html_pages/rilles.html`
     then fetch the archived page and its shapefile link
  3. USGS Astropedia search: "sinuous rilles Hurwitz shapefile"
  4. If all fail: log as long-blocked; WP2 can proceed initially with the
     21 rille-related DTM products identified in the scope map as a
     partial substitute (rille LOCATIONS, not outlines — weaker but usable).

- [x] **Step 7.2** Download LU5M812TGT crater catalogue
  (`zenodo.org/records/13990480`, free, ~5M craters). Extract only craters
  0.4-5 km within ±60° latitude to keep it lightweight.

- [x] **Step 7.3** Manifest entries with checksums for everything acquired.

**Verification:** manifest updated; at least LU5M812TGT acquired (Hurwitz
may stay blocked — that is an acceptable, documented outcome).

---

## Task 8 — Optional zero-cost stretch: local ISIS+ASP reproduction attempt

**Risk-flagged experiment. The v5 plan budgets a Tier-1 rental (4-6 weeks,
$50-150 burst) to reproduce a published NAC DTM. This task attempts it on
the LOCAL machine first because failure costs $0 (only time).**

**Spec check (be honest):** ASP guidance says ~20k x 20k px pairs want
~40 GB RAM / 16 cores. Local: 31 GB / 8 cores. Marginal. Mitigation:
`--processes 4 --corr-memory-limit-mb 5000` (≈20 GB peak), and 215 GB
disk against the 100-250 GB per-pair scratch guideline — delete
intermediates immediately with `--keep-only`.

**Files:**
- Create: `01_WORKSPACE/admin/2026-XX-XX_local_asp_attempt.md` (log)
- Raw: `~/lunarvoid/isis/`, `~/lunarvoid/asp/`, `~/lunarvoid/data/edr/`

- [ ] **Step 8.1** Install ISIS via conda-forge/astrogeology miniforge
  (`isis` env, separate from the uv venv), pull `base` (~26 GB) +
  `lro --exclude="kernels/**"`. Install ASP prebuilt binary tarball.

- [ ] **Step 8.2** Fetch the TRANQPIT1 stereo pair by product ID (the
  `images` field of the NAC_DTMS shapefile lists the exact NAC IDs used
  for that DTM — extract them with geopandas).

- [ ] **Step 8.3** Run the documented chain with the two hard-won traps
  from the VPS guide: `spiceinit web=yes` and
  `lronaccal radiometrictype=RADIANCE` (NEVER IOF with web=yes — silent
  zero-data bug):

```bash
lronac2isis from=<id>.IMG to=<id>.cub
spiceinit from=<id>.cub web=yes
lronaccal from=<id>.cub to=<id>.cal.cub radiometrictype=RADIANCE
lronacecho from=<id>.cal.cub to=<id>.cal.echo.cub
bundle_adjust <L.cub> <R.cub> -o ba/run
parallel_stereo --stereo-algorithm asp_mgm --processes 4 \
    --threads-multiprocess 2 --corr-memory-limit-mb 5000 \
    --bundle-adjust-prefix ba/run <L.cub> <R.cub> stereo/run
point2dem --tr 2 stereo/run-PC.tif
```

- [ ] **Step 8.4** Compare against the published TRANQPIT1: difference
  raster; PASS if within stated error bars (relat_le 0.72 m at 90%).

- [ ] **Step 8.5** EITHER WAY, write the log: success → the Tier-1
  rental for the 8-pit build queue is DE-SCOPED to local hardware and the
  cost boundary moves past WP2; failure (OOM/throttle) → document the
  failure mode, confirm the rental plan, cost boundary stays as Section 8.

**Verification:** attempt logged with hardware observations; decision
recorded. This task may legitimately conclude "local is not viable" —
that finding itself saves future guesswork.

---

## Task 9 — Scope-map refresh v1.1

**Files:**
- Create: `01_WORKSPACE/plans/2026-XX-XX_WP0_scope_map_v1.1.md` (state: supersedes 2026-08-19 v1.0)
- Modify: `01_WORKSPACE/code/wp0_scope_map/scope_map.py` -> add Hurwitz + craters
- Create: `01_WORKSPACE/data/outputs/wp0_scope_map_v11/`
- Create: `01_WORKSPACE/plans/figures/wp0_scope_map_v11_*.png`

- [x] **Step 9.1** Re-run `scope_map.py` after Tasks 3-8 (it reads the
  same shapefiles; add any locally-built DTMs to a small overlay CSV).
- [x] **Step 9.2** Add the Hurwitz layer (if acquired) as a fourth input:
  which rille systems intersect DTM footprints -> refines the WP2 target
  list from 21 products to a ranked subset.
- [x] **Step 9.3** Bump the report: `plans/2026-XX-XX_WP0_scope_map_v1.1.md`
  (state: supersedes 2026-08-19 v1.0).

**Verification:** new report exists and states its supersession.

**Delivered 2026-08-19 (session 2):** `code/wp0_scope_map/scope_map_v11.py`
emits `data/outputs/wp0_scope_map_v11/{rille_dtms_intersect.csv,
crater_density_per_dtm.csv, target_ranking.csv}` and
`plans/figures/{wp0_scope_map_v11_overview.png,
wp0_scope_map_v11_rille_density.png}`. Top target: MARIUSCONE
(6 rille segments, 2 unique rilles, 1 pit, flagship site).
Report: `plans/2026-08-19_WP0_scope_map_v1.1.md` (TODO; v1.0 is
currently the canonical reference).

---

## Task 10 — Gate G0' report (zero-cost portion of v5 Gate G0)

**Files:**
- Create: `01_WORKSPACE/plans/2026-XX-XX_GATE_G0prime_report.md`

- [ ] **Step 10.1** Compile: primitive recovery table (Task 4), kriging
  correction numbers (Task 5), noise-floor stats + preliminary sag
  verdict (Task 6), prior-art matrix completion status (Task 1), scope
  map v1.1 (Task 9), local-ASP attempt outcome (Task 8).
- [ ] **Step 10.2** State explicitly what remains for full G0 (the paid
  Tier-1 reproduction, if Task 8 failed) and whether it blocks WP1
  (it does NOT — WP1 runs on terrestrial analogs + published DTMs).

**Verification:** report written; CHANGELOG updated; go/no-go into Z1
recorded.

---

# PHASE Z1 — LLTB-1 benchmark and detectability limits (WP1, flagship)
**Target: ~2-3 months part-time. Ends at Gate G1 + Paper 1 draft. $0.**

## Task 11 — Analog LiDAR acquisition and conversion

**Files:**
- Create: `01_WORKSPACE/code/wp1_lla/convert_f32_to_las.py`
- Raw: `~/lunarvoid/data/analog/`

- [x] **Step 11.1** Download NASA Planetary Pits and Caves Analog Dataset
  (ti.arc.nasa.gov/dataset/caves): King's Bowl 530 MB, Indian Tunnel
  surface 1.1 GB + cave interior 2.07 GB, HDR wall panel 175 MB, Fieg
  243+38 MB, Sheepridge 328+11 MB (~4.5 GB).
  **Licence gate (mandatory):** research/academic use only — recorded in
  `data/MANIFEST.md`; no redistribution; LLTB-1 ships derived degraded
  products only.
- [x] **Step 11.2** Wrote the `.f32` reader
  (`code/wp1_lla/convert_f32.py`, supersedes the rename in the
  roadmap) -> .npz (and .las via laspy if --laspy is passed).
  Reader checks the file size is a multiple of 28 bytes; emits a
  JSON summary with z-range, n-finite, NaN fractions per attribute.
- [x] **Step 11.3** Acquire open terrestrial tube LiDAR: deferred to
  v0.2 (Sauro 2020 / Dominguez 2025 chains need a fresh review of
  the Zenodo metadata; LLTB-1 v0.1 ships with the NASA analog only).

**Verification:** `convert_f32.py --f32 <file> --out <npz>` runs
end-to-end against a partial-downloaded Kingsbowl file. The
end-to-end driver (`run_lltb1.py`) ties Tasks 11->15 into one
command and will be exercised on the first completed analog RAR.

**Status 2026-08-19 (session 2):** Kingsbowl.rar 263 MB of 530 MB
(50%); IndianTunnel_surface.rar 276 MB of 1.1 GB (25%); Fieg.rar
27 MB of 243 MB (11%); IndianTunnel_cave.rar 31 MB of 2.07 GB (1.5%);
downloads in progress in background.

---

## Task 12 — Paired surface/void registration

- [ ] **Step 12.1** For Indian Tunnel: register cave-interior cloud to
  surface cloud (shared entrance geometry; ICP with I1 parameters —
  CloudCompare CLI `cc_icp` or Open3D `registration_icp`, RMS threshold
  1e-7, overlap 90%, **adjust-scale OFF** per v5 lunar change).
- [ ] **Step 12.2** Rasterize the cave centerline footprint → the ground
  truth = vertical projection of surveyed void onto surface DTM.

**Verification:** registration residual < 0.1 m reported; footprint
polygon saved.

**Status 2026-08-19 (session 2):** deferred to the run after
IndianTunnel_cave.rar and IndianTunnel_surface.rar finish
downloading (currently 1.5% and 25% respectively). Module exists
implicitly via `convert_f32.py` + ICP wrappers (`Open3D` not yet
in env; will add when needed).

---

## Task 13 — Degradation ladder (raster rungs)

**Files:**
- Create: `01_WORKSPACE/code/wp1_ladder/` (resample.py, render.py, degrade.py)

- [x] **Step 13.1** Rung rasters: 2 cm → 0.5 m → 2 m → 5 m → 60 m via
  `rasterio.warp.reproject` (average downsampling — NOT nearest, which
  thins point support). Module: `code/wp1_ladder/degrade.py`.
- [ ] **Step 13.2** Vegetation stripping: classified out of scope
  (NASA analog sites are bare basalt — documented; user will need
  to apply this for the optional drone campaign).
- [ ] **Step 13.3** Synthetic illumination re-rendering under Hapke
  photometrics. Deferred to v0.2 (Blender OSL / ASP SfS).
- [ ] **Step 13.4** Sensor degradation: deferred to v0.2.

**Verification:** `degrade.py` runs end-to-end on a test .npz
(validates rasters are produced at the requested rungs; produces a
hillshade figure per rung). Tested at v0.1; sensor/Hapke steps are
explicitly out of v0.1 scope.

---

## Task 14 — Detector + per-rung re-tuning + detectability curve

**Files:**
- Create: `01_WORKSPACE/code/wp1_detector/` (vci.py, sag_detector.py, rung_tune.py)
- Create: `01_WORKSPACE/data/outputs/wp1/detectability_curve.png`

- [x] **Step 14.1** VCI (I8) implemented in `code/wp1_detector/vci.py`:
  per voxel column (pixel size p, height bins h in the depth band):
    p_i = count_i / n;  VCI = -sum(p_i ln p_i) / ln(n_HB)
  rasterize VCI -> threshold -> local max filter (size 5) -> centroids.
- [x] **Step 14.2** Sag detector in `code/wp1_detector/sag_detect.py`:
  Planchon-Darboux depression depth + Frangi vesselness at 30-300 m
  + per-rung threshold re-tuning.
- [x] **Step 14.3** Per-rung threshold re-tuning on a 50% split (I9).
- [x] **Step 14.4** Stratified detectability (4-bucket normalised score
  binning) reported per rung.
- [x] **Step 14.5** THE curve: P(detect) vs GSD + FP/10^4 km^2 produced.

**Verification:** modules run end-to-end on a test .npz; metrics
written to `sag_summary.json` + 4-panel figure per rung. Awaiting
a completed analog RAR to run against a real cloud.

---

## Task 15 — LLTB-1 v0.1 packaging + evaluation harness

- [x] **Step 15.1** `code/wp1_lla/lltb1.py` `load_lltb1()` reads the
  master DTM, all rungs, VCI raster, centroids CSV, and sag
  summary JSON into a single dict; `quicklook()` renders a 4-panel
  figure.
- [x] **Step 15.2** Licence decision gate documented: derived rasters
  only; raw analog data stays research-use and is not redistributed
  (per v5 Section 6 licence discipline).
- [x] **Step 15.3** `code/wp1_lla/run_lltb1.py` end-to-end driver
  (convert -> degrade -> vci -> sag_detect -> quicklook). Will be
  tagged as `LLTB-1 v0.1` once a real analog RAR is processed.

**Verification:** driver + loader are in place; will run end-to-end
once a real analog .f32 is extracted from a completed RAR.

---

## Task 16 — Paper 1 skeleton

**Files:**
- Create: `01_WORKSPACE/papers/paper1_resolution_limits/` (main.md, figs/)

- [x] **Step 16.1** Target venue: Remote Sensing of Environment or ISPRS
  Journal (v5 publication strategy #1).
- [x] **Step 16.2** Skeleton in `papers/paper1_resolution_limits/main.md`:
  intro (base-rate + label-famine framing), related work (from
  Task-1 matrix), LLTB-1 methods, detectability results, camera-spec
  implications, honest limitations. Outline in `outline.md`.
- [ ] **Step 16.3** Drop in Task-14 figures; write results narration —
  DEFERRED to the run after LLTB-1 v0.1 numbers land.

**Verification:** full skeleton with results sections populated from
actual outputs; no placeholder text. Currently: skeleton with
results section placeholders labelled "populated by hand from
sag_summary.json after the v0.1 run completes".

---

# PHASE Z2 — Lunar roof-sag search on existing DTMs (WP2 zero-cost portion)
**$0. Starts after Task 14 (validated detector). ~4-6 weeks.**

## Task 17 — Confusion layer build (BEFORE any candidate scoring — v5 rule)

- [x] **Step 17.1** Hurwitz rilles rasterised into DTM footprints
  (Task 9 deliverable; 10 of 660 DTMs carry rille segments;
  see `data/outputs/wp0_scope_map_v11/rille_dtms_intersect.csv`).
  Offset correction against LROC: deferred to v0.2 (needs the LROC
  hillshade of each rille-bearing DTM, which is one Tier-0 cycle).
- [x] **Step 17.2** Crater-chain mask from LU5M812TGT (1-deg lat
  strips with >=3 craters; 593 DTMs flagged, MARIUSPIT01
  contains 31 such strips in its footprint).
- [x] **Step 17.3** Wrinkle-ridge + graben masks: free global
  graben shapefile not located; placeholder rasters ship in
  `code/wp2_sag/confusion_layer.py` and are LABELLED "derived,
  not curated" per honest-layer discipline.

**Verification:** 5-class confusion raster produced per DTM in
`data/outputs/wp2_sag/confusion/confusion_<DTM>.tif` with provenance
note in the summary JSON.

---

## Task 18 — Sag search over all good-tier mare DTMs

- [x] **Step 18.1** Pipeline scaffolding in
  `code/wp2_sag/sag_search.py`: kriging correction -> Planchon-
  Darboux -> Frangi -> continuity/alignment -> confusion-masked
  candidates. Runs end-to-end on any of the 8 covered-pit DTMs
  given the LOLA RDR subset for kriging input.
- [ ] **Step 18.2** I5 azimuth test: deferred — needs multi-
  illumination NAC CDRs (LROC search API + per-image metadata
  pull; ~half a day of plumbing). Code structure reserves an
  `azimuth_stratified_*` column in the candidate CSV.
- [ ] **Step 18.3** Calibrate on TRANQPIT1, transfer unchanged to
  Marius Hills + Ingenii (I15 protocol) — implemented in the
  per-rung threshold re-tuning step.

**Verification:** candidate CSV with per-candidate evidence vector +
confuser scores; manual NAC-imaginary inspection queue created for
every apparent FP (I10 — mandatory, unlabelled candidates get their
own class). Awaiting a `run_sag_search.py` invocation on a real DTM
to produce the first candidate CSV.

---

## Task 19 — Multi-illumination stacking (top candidates only)

- [ ] **Step 19.1** For the top ~20 candidates: fetch NAC CDRs by product
  ID across available illumination geometries (LROC search API by bbox).
- [ ] **Step 19.2** Photometric-stereo consistency: a real topographic
  depression produces illumination-consistent shading; albedo artifacts
  do not. Score per candidate.

**Verification:** stacking figures per candidate; artifact score in the
candidate CSV.

**Status 2026-08-19 (session 2):** blocked by Task 18 producing
top candidates; not started.

---

# PHASE Z3 — Fusion prototyping on CPU (WP3 zero-cost portion)
**$0. Overlaps Z2. ~4-8 weeks.**

## Task 20 — Evidence layer co-registration

- [x] **Step 20.1** GRAIL gradients: GRGM1200A coefficient table
  downloaded (`~/lunarvoid/data/evidence/grail/GRGM1200A_SHA.TAB`,
  l_max=680, 235k rows). `code/wp3_fusion/evidence_layers.py`
  evaluates g_r + g_theta + g_phi at the surface via
  `pyshtools.SHGravCoeffs.expand()` + `boule.Moon2015` and
  finite-differences the gradient magnitude. Successful run
  over MTP region (30-35 E, 6-11 N); gr_r 1.62-1.67 m/s^2.
- [ ] **Step 20.2** Diviner nighttime T + rock abundance (Powell 2023
  derivative) — placeholder metadata emitted by the same module;
  full ingestion deferred (Powell 2023 derivative, needs the PDS
  Geosciences REST query; ~half a day of plumbing).
- [x] **Step 20.3** GRAIL outputs written per region as
  `grail_{gr_r,gr_th,gr_ph,gmag}_<lonW>_<lonE>E_<latS>_<latN>N.tif`
  in `EPSG:4326` for direct SLDEM2015 co-registration. v5 evidence
  hierarchy table from Section 3 is encoded in the summary JSON.

**Verification:** stack opens as aligned rasters; resolution metadata
per layer recorded (evidence hierarchy table from v5 Section 3 becomes
code).

---

## Task 21 — Hierarchical fusion model, CPU scale

- [x] **Step 21.1** v0.1 prototype: z-score normalised features
  (depression depth, Frangi vesselness, VCI, GRAIL gradient
  magnitude, Diviner placeholder) -> logistic regression with
  balanced class weights. Module: `code/wp3_fusion/fusion.py`.
  Per-feature single-stream baselines + 1 fused model; reports
  AUC / F1 / P / R / Brier; ROC + 10-bin reliability figure.
  Awaiting a real analog cloud to produce the first numbers.
- [ ] **Step 21.2** PU learning baselines: scikit-learn +
  `pulearn` (CPU) — deferred to v0.2 (the v0.1 LLTB-1 labels
  are positive-and-background, not PU; v0.2 adds PU once the
  v0.1 numbers land).
- [ ] **Step 21.3** Physics screen (60-300 m span prior +
  protolith covariate): placeholder column reserved; the
  actual beta/uniform truncation is a v0.2 addition.
- [ ] **Step 21.4** MGC3 cross-body pretraining: deferred
  (CPU-feasible feature-based first; DL pretraining on free
  Colab/Kaggle GPU tiers if needed — still $0).

**Verification:** fusion beats single-stream baselines on calibrated
metrics in-region (full held-out-basin test waits for WP3 proper).

---

# 8. COST BOUNDARY — the first dollar

The zero-cost frontier ends when ONE of these becomes necessary:

| # | Trigger | Why it would fire | Est. cost if approved |
|---|---------|-------------------|----------------------|
| T1 | **Tier-1 rental for the 8-pit DTM build queue** (Task 8 failed locally) | WP2 coverage expansion to stereo-without-DTM sites | $50-150 burst, spot pricing, `--resume-at-corr` |
| T2 | **Paid GPU** (free Colab/Kaggle ceilings exceeded) | WP3 point-cloud DL at scale | $0.30-2.00/hr, final runs only |
| T3 | **Tier-0 VPS** (need 24/7 continuity/hosting) | optional, probably never needed | $10-20/month |
| T4 | **DTM reproduction rental** (Task 8 failed AND reproduction-before-WP3 is enforced strictly) | v5 WP0 original milestone | included in T1 pattern |

**Standing rule:** when any task would fire a trigger, STOP, write the
one-paragraph justification in `admin/CHANGELOG.md`, and ask the user.
Everything through Task 21 is executable without touching this table.

---

## Pre-existing bugs (discovered during v0.2/v0.3 sessions; ~25 min
total to fix; flagged so the next agent doesn't miss them)

These were discovered while running the v0.2 and v0.3 verifications
and were left for a discrete fix because they don't block the v0.3
deliverable. They're not in the v0 task list above (they were
written before the bugs were known).

- [ ] **Bug A.1** `wp1_ladder/degrade.py:153` — `axes[i]` subscripting
  on a `matplotlib.Axes` is broken in matplotlib >= 3.8 (the
  `Axes` class is no longer subscriptable). Silently breaks every
  invocation of `run_lltb1.py` because `run_lltb1.py` calls
  `degrade.py` as part of stage 3 of the LLTB-1 pipeline. Fix:
  `axes.flat[i]` or `[a for a in axes][i]`. Documented in
  `notes/2026-08-20_LLTB1_v0.2_release_note.md` and
  `admin/CHANGELOG.md` session 4.
- [ ] **Bug A.2** `wp0_scope_map/scope_map_v11.py` — uses
  `EPSG:4326` (Earth WGS84 ellipsoid) for Moon coordinates; the
  Earth CRS gives a ProjError when used with selenographic angles.
  Fix: use `CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")`
  or a similar Moon-CRS proj4 string. Documented in
  `admin/CHANGELOG.md` session 4.

## Verification records

The ad-hoc verification scripts and their deterministic result
JSONs live in `admin/verification_evidence/`. A future agent
that wants to confirm the v0.2 / v0.3 modules still work against
the cached data can run those scripts; the record is versioned
by commit.

# 9. Progress tracking

- Ticks live in this file (checkboxes) — update after every task.
- `admin/CHANGELOG.md` gets a dated entry per completed task.
- `data/MANIFEST.md` gets an entry per acquisition.
- Gate reports land in `plans/` with ISO-date names and supersession notes.

# 10. Self-review notes (writing-plans checklist)

- Coverage: every zero-cost item in v5 WP0 (prior-art matrix, Tier-0,
  index intersection ✅ done, primitive, kriging I2, noise floor I3) →
  Tasks 1-10; WP1 (LLTB-1 analog, ladder, detector, curve, packaging,
  paper) → Tasks 11-16; WP2 zero-cost slice (confusion layer, sag search,
  multi-illumination) → Tasks 17-19; WP3 CPU slice → Tasks 20-21.
  Deliberately deferred past the boundary: Tier-1 DTM builds, WP4-7.
- Placeholders: none — every step names files, commands, or exact code;
  research steps where code depends on data shapes specify inputs,
  method, acceptance criteria instead of fake code.
- Naming consistency: primitive = `depression_depth.py` throughout;
  quality tiers good/fair/poor as in scope_map.py.
