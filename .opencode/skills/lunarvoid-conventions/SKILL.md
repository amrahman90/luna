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
- Versioned verifications live in
  `01_WORKSPACE/admin/verification_evidence/scripts/`
  (`verify_v02_f32dir_and_filter.py`, `verify_v03_slope_mask.py`,
  `verify_v04_tune_slope.py`). Run the latest after touching
  `extract_rar.py`, `convert_f32.py`, `sag_detect.py`, or
  `run_lltb1.py`; each prints `PASS: N/N (ALL OK)` and writes a
  deterministic JSON evidence record (commit those records).
- Always subprocess the venv Python for checks (sandbox Python lacks
  numpy). Test against the REAL on-disk artifacts under
  `~/lunarvoid/data/lltb1/<site>/` — they are the documented ground
  truth, stronger than synthetic tests.
- Sanity-check geodesy BEFORE bulk processing: transform a known pit
  coordinate and confirm it lands inside the raster.
- Plots: verify PNG dimensions programmatically if image preview is
  unavailable.

## 8. LLTB-1 build know-how (ported from the parallel Hermes
   agent's skill, 2026-08-21; content merged here — single truth)

### Pipeline bug catalog (fixes already in code)

1. **RAR5**: system 7z can't decode RAR5; `code/setup/extract_rar.py`
   installs bsdtar from a .deb with a **4-mirror fallback**
   (DEB_URL → archive.ubuntu → launchpad → snapshot.ubuntu). A single
   mirror 403s (seen live); the fallback is load-bearing.
2. **WhiteboxTools**: needs
   `wbt.set_whitebox_dir(dirname(whitebox.__file__))`,
   `wbt.set_working_dir('/tmp')`, absolute input paths, AND geokeys
   in the GeoTIFF — copy `src.profile.copy()`, never build a fresh
   CRS-less profile.
3. **Frangi**: float32 overflows on large sigmas — cast to
   `np.float64`, mask NaN after, sub-sample to ≤5000 px max dim
   (Frangi is O(n²) in the larger dimension).
4. **f32 sentinels**: NASA .f32 uses ~1e38 no-data; treat
   |x|,|y|,|z| > 1000 m as NaN; weight bins by `np.isfinite(z)`;
   use nanmin/nanmax on the finite subset.
5. **Pit Atlas hygiene**: the `DTM` attribute misses 2 of 8 covered
   pits (Ingenii, SW Fecunditatis) — **trust the spatial join, not
   the attribute**. Atlas positional accuracy ~30 m; v5 I15 match
   radius ≥ 30 m.
6. GRAIL/pyshtools 4.x details are in §4 of session-2 summary; the
   `gggrx_1200a_sha.tab` header's l_max is wrong — derive from data.

### LLTB-1 v0.4 site table (7 sites, --tune-slope)

| Site | F1 (v0.4 tuned) | Best recall | Note |
|---|---|---|---|
| IndianTunnel_NorthSurface (cliff) | **0.362 @ 1 m @ 45°** | 0.474 | best honest result |
| IndianTunnel_Collapse3 (real tube) | 0.188 @ 0.5 m @ 45° | 1.00 | |
| Fieg_A | 0.137 @ 0.5 m @ 45° | 0.69 | |
| Sheepridge | 0.091 @ 5 m @ 45° | 0.231 | |
| IndianTunnel_cave_10x | 0.085 @ 5 m @ 10° | 1.00 | |
| Kingsbowl | 0.043 @ 5 m @ 20° | 1.00 | |
| IndianTunnel_cave_1x (full res) | 0.049 @ 5 m @ 45° | 1.00 | **tune-slope REGRESSES here — use fixed `--slope-mask-degrees 10` (F1 0.068)** |

Recall = 1.00 at every rung with ≥5 void cells; the bottleneck is
precision (overflagged small sinks on gentle slopes).

### Z2 sag-search scores (all 8 covered DTMs, 2026-08-21; CORRECTED
   2026-08-21 after verifier refutation)

Top-scored candidate is NOT generally the catalogued pit (it lies
5-29 km away on 6/8 runs — the top score usually picks other
terrain). The pit itself surfaces as a candidate within 100 m on
4/8: Ingenii 46 m (rank 1, score 19.33), MTP 45 m (rank 11/29,
score 3.72 vs top 21.06), Procellarum 38-77 m (ranks 55/189); no
candidate within 100 m on FECNDITATS2 / IRIDIUMPIT1 / MARIUS /
SWFECUNPIT1 (closest 1.2-2.6 km). Max scores per run: TRANQPIT1
21.06, INGENIIPIT 19.41, IRIDIUMPIT1 12.86, FECNDITATS2 9.49,
PRCLRMPIT01 8.09, MARIUSPIT01 5.04, SWFECUNPIT1 1.60.

### Pre-existing bugs — RESOLUTION LOG (both closed 2026-08-21, Phase 0)

1. `code/wp1_ladder/degrade.py` `axes[i]` subscript — FIXED
   2026-08-21: `squeeze=False` + 4 sites `axes.flat[i]`; single-rung
   runs verified; smoke test unchanged (F1 0.392/0/0.800, AUC 0.990).
2. `code/wp0_scope_map/scope_map_v11.py` EPSG:4326 — found ALREADY
   FIXED at HEAD (Moon proj4 CRS in place; roadmap bug list was
   stale). Re-run byte-identical: 660 rows, MARIUSCONE 23.950567.

### Failure triage (symptom → fix)

| Symptom | Fix |
|---|---|
| NaN→int ValueError in cloud_to_rung | f32 sentinels — see §8 bug 4 |
| WBT "TIFF does not contain geokeys" | copy src.profile with CRS |
| WBT "No such file or directory" | set_working_dir('/tmp') + abs paths |
| Frangi 0/NaN | float64 + NaN mask (bug 3) |
| `grav.expand()` 'int' not iterable | r must be an array |
| projError Moon vs Earth | explicit +R=1737400 proj4 |
| 403 on bsdtar install | 4-mirror fallback (bug 1) |
| "no .f32 files in dir" | re-run; v0.2 auto-discovers the f32 dir |

## 9. Obsidian knowledge layer (vault at `01_WORKSPACE/`, atomic notes in `01_WORKSPACE/Lunar Lavatube knowledge/`)

The whole workspace `01_WORKSPACE/` is the Obsidian vault (canonical
markdown in `notes/`, `plans/`, `papers/`, `admin/` becomes graph
nodes automatically). The curated atomic-notes layer lives at
`01_WORKSPACE/Lunar Lavatube knowledge/` (the user's chosen folder).
Obsidian's `.obsidian/` config lives at `01_WORKSPACE/.obsidian/` (gitignored;
per-machine).

### Folder layout (atomic layer)

```
01_WORKSPACE/Lunar Lavatube knowledge/
├── 00_HOME.md                     # entry MOC: project state, current gate, blockers
├── mocs/                          # Maps of Content (5)
│   ├── MOC Gates & Decisions.md
│   ├── MOC Sites & Candidates.md
│   ├── MOC Data & Code.md
│   ├── MOC Concepts & Methods.md
│   └── MOC Sessions & Ops.md
├── gates/    G0prime.md, G1.md, G2.md
├── decisions/  D1.md, D2.md, ...
├── sites/    TRANQPIT1.md, ... TYCHOPK.md (21 site notes)
├── backlog/  FECUNPIT cluster, TRANQPIT1 12-km FPs, INGENIIPIT rings, deferred items
├── artifacts/ LLTB-1 v0.5, calibration freeze, registry, MANIFEST, smoke test, ...
├── concepts/  calibration-context FP, terrain extrapolation, I14 funnel, claim discipline, ...
├── refs/     Powell 2023, Williams 2017, Robinson 2010, Hurwitz 2013, ...
└── sessions/ session_<NN>.md (one per CHANGELOG entry)
```

### Wikilink conventions

- Within the atomic layer: `[[sites/TRANQPIT1]]` or `[[sites/TRANQPIT1|TRANQPIT1]]` (alias for readability).
- To canonical files in `01_WORKSPACE/`: use Obsidian's relative-path wikilinks — `[[../notes/findings|Findings log]]`, `[[../plans/2026-08-23_GATE_G2_report_v1.0|G2 report]]`. These resolve as graph edges to the canonical node.
- Spaces in filenames are OK in wikilinks: `[[../plans/2026-08-23_GATE_G2_report_v1.0|G2]]`.

### Tag taxonomy (use liberally — color-codes the graph)

- Domain: `#gate`, `#decision`, `#site`, `#artifact`, `#backlog`, `#concept`, `#ref`, `#session`
- Evidence: `#fp`, `#tp`, `#below-floor`, `#visual-inspection`
- Terrain: `#mare`, `#highland`, `#impact-melt`, `#catalogued-pit`, `#random-mare`
- Status: `#deferred`, `#frozen`, `#calibration-context`, `#calibration-context-fp`, `#inconclusive`
- Cycle: `#g0prime`, `#g1`, `#g2`, `#phase-6`

Use hierarchical prefixes for grouping in tag-pane: `#gate/g2`, `#site/mare`, etc.

### Append-only discipline (preserved)

Never retro-add wikilinks to `notes/findings.md` historical entries — the
file is append-only. Atomic notes link OUT to canonical notes;
Obsidian's backlinks pane surfaces all incoming edges (this is the
most useful view for canonical notes anyway).

### Anti-drift generator

`code/tools/regen_site_notes.py` rebuilds `Lunar Lavatube knowledge/sites/*.md`
from `data/candidate_registry.csv` + `data/outputs/wp2_sag/transfer/transfer_summary.json`.
Mechanical regeneration = the vault never hand-drifts from data.
Site-note bodies are short tables + flag annotations + wikilinks to
backlog/gates/concepts. Geo-coder owns this script.

### File-tree hygiene (`.obsidian/ignore`)

Vault's `.obsidian/ignore` excludes non-markdown from the file tree
(graph and search unaffected). Required entries:

```
**/*.csv
**/*.json
**/*.py
**/*.pyc
**/*.tif
**/*.tiff
**/*.npz
**/*.npy
**/__pycache__/**
```

### Cost / tracking

Vault is untracked by user instruction (2026-08-23) — like the R1
roadmap draft. `.gitignore` lines for `.obsidian/` and `knowledge/atomic/.trash/`
added 2026-08-23. No git history on the vault; re-runnable from
canonical sources if corrupted.
