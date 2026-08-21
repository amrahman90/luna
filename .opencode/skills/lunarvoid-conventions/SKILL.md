---
name: lunarvoid-conventions
description: LUNARVOID lunar lava-tube project technical conventions — environment paths, terrain-engine rules (Planchon-Darboux mandate), lunar DTM geodesy gotchas, PDS/Zenodo data-acquisition patterns, statistics and claim discipline, licence rules. Use when writing, running, or debugging ANY code, downloading ANY data, or interpreting terrain/detection results in this project.
---

# LUNARVOID Technical Conventions

Hard-won rules from execution sessions 1–5. Violating any of these has
already produced silent-wrong-answer bugs. Read fully before coding.

## 1. Environment

- **Python**: `/home/frostflux/lunarvoid/venv/bin/python` (3.12; geopandas
  1.1.4, rasterio, whitebox 2.4.0, pykrige, scikit-learn, scipy, pyshtools,
  laspy). Spec: `01_WORKSPACE/code/setup/requirements.txt`.
- **Raw + derived rasters** live ONLY under `~/lunarvoid/data/`:
  `dtms/` (published NAC DTMs), `edr/`, `lltb1/` (analog LiDAR npz),
  `lola_tracks/`, `index_layers/`, `evidence/`, `analog/`,
  `outputs/<DTMNAME>/` (per-site derived GeoTIFFs).
- **Repo gets**: code, small CSVs, PNGs, JSON summaries, manifest, notes.
  Never mirror LROC archives; never put rasters/RARs in the repo.
- **Disk floor**: keep ≥40 GB free on `/` (check `df -h` before big pulls).

## 2. Terrain engine (non-negotiable)

- Depression fill MUST be `fill_depressions_planchon_and_darboux`
  (whitebox). Wang & Liu and breach fills DRAIN the NoData pit floor and
  return ~0.3 m where the true floor is ~130 m. Full variant table:
  `notes/2026-08-19_task3_transqpit1_fill_variants.md`.
- Reference implementations: `code/wp0_primitive/depression_depth.py`,
  `sweep_pits.py`; kriging: `code/wp0_kriging/kriging_correction.py`;
  sag detector: `code/wp1_detector/sag_detect.py`.
- Always record the NoData fraction within the analysis window — it
  changes fill semantics.
- Local-envelope ground truth for detectors: 21×21 nan-robust median
  (NOT a 5×5 min filter — historical bug, session 2).

## 3. Lunar geodesy

- NAC DTM GeoTIFFs use LOCAL equirectangular CRS:
  `+proj=eqc +lat_ts=<center_lat> +lon_0=180 +R=1737400` (metres).
- Pit geodesy: build lon/lat CRS via
  `pyproj.CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")` → transform
  to raster CRS → row/col. NEVER assume Earth EPSG:4326 semantics.
- Longitude traps: frames may be −180..180 or 0..360; some DTM frames are
  UNWRAPPED metres needing whole-360° x-shifts (IRIDIUMPIT1,
  FECNDITATS2 — see `sweep_pits.py` pit_to_pixel).
- Hurwitz rille shapefile CRS is Moon eqc central-meridian 180, metres.
  Moon→geographic reprojection needs R=1737400 sphere
  (`PIT_DISABLE_CELESTIAL_BODY=1` workaround exists; explicit proj4 is
  safer). `gpd.sjoin_nearest` on geographic CRS warns — use projected.
- Pit atlas depth fields are messy strings ("105", ">25", "N/A") — parse
  defensively.

## 4. Data acquisition (what actually works)

- PDS URLs 301-redirect to `pds.mcp.nasa.gov` — always `curl -L`.
- **LOLA RDR by bbox**: `oderest.rsl.wustl.edu/livegds/?query=lolardr`
  REST (pattern in `kriging_correction.py`). Planetocentric lat;
  `Pt_Radius` on R=1737400 m sphere. PDS = public domain.
  (`ode.dm.asu.edu` is DNS-dead; old REST paths 404.)
- Zenodo: list files via `https://zenodo.org/api/records/<id>`; parallel
  range-streams beat single curl ~50×. LU5M812TGT craters = CC-BY-4.0.
- Dead/403 sites (Brown planetary, LPI) → Wayback **CDX API**
  (`web.archive.org/cdx/search/cdx?url=...`) then fetch snapshots.
- Politeness: browser UA only where needed, back off on 429, ≤3 retries.
- Every acquisition MUST get a MANIFEST row (URL, SHA-256, licence).

## 5. Interpretation semantics

- Recovered depth can EXCEED catalogued (fill-to-spill of valid pixels) —
  document, not an error.
- Funnel failure mode: pits incised into rilles (Marius Hills) spill
  sideways — the pre-registered v5 I14 prediction. It is a FINDING.
- Kriged I2 correction on published NAC DTMs is small (already
  LOLA-registered): TRANQPIT1 check RMSE 0.373→0.327 m; residual noise
  floor ≈0.33 m. Correction must stay low-frequency (>99% power at
  λ>300 m) and preserve pit depth to ±10%.
- Detectability: sag amplitude A competes with the **60–300 m band-passed
  residual RMS** (sag-band RMS ~1.25–1.38 m on flat mare), NOT per-pixel
  SD. 3× sag-band RMS ⇒ only A≥4 m single-DTM detectable — 1–2 m sags
  need matched-filter/multi-evidence stacking (this is the G1 result).
- Slope mask ≥10° lifts detector F1 by removing gentle-slope FPs
  (v0.3); recall unaffected.

## 6. Statistics & claim discipline

- Seeds fixed at 42. 50/50 cal/test splits for threshold tuning.
- Report FP per 10^4 km² (primary FP metric), P1-comparable residual
  tables in cm (P1 ref: mean 10.99 / median 8.24 / SD 21.64 cm).
- Core thesis language: "**calibrated inference, never verified
  detection**". Nothing subsurface on the Moon is verifiable today
  except the radar-evidenced Tranquillitatis conduit. Never write
  "detected a lava tube"; write "inferred a void candidate at
  confidence X".
- Budget: **$0 until a §8 cost trigger is user-approved** (roadmap §8:
  T1 Tier-1 rental, T2 paid GPU, T3 VPS, T4 reproduction rental).
- Licences: NASA analog dataset = research/academic only (gate before
  redistribution); ISRO acknowledgement mandatory if Chandrayaan data
  used; LU5M812TGT = CC-BY-4.0; PDS = public domain.

## 7. Verification habits

- After ANY module change: run
  `~/lunarvoid/venv/bin/python 01_WORKSPACE/code/smoke_test.py`
  (known-good: per-rung F1 0.39/0/0.80 on synthetic; fusion AUC 0.990).
- Sanity-check geodesy BEFORE bulk processing: transform a known pit
  coordinate and confirm it lands inside the raster.
- Plots: verify PNG dimensions programmatically if image preview is
  unavailable.
