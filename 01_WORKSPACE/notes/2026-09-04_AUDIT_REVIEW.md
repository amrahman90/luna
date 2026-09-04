# LUNARVOID — Whole-Project Audit Review

**Date:** 2026-09-04
**Auditor:** Hermes Agent (improve skill + direct module-level reads)
**Scope:** 54 Python files (~12.7K LOC), 171 markdown files, all of `01_WORKSPACE/`
**Recon snapshot:** `master` @ `245f7e7`; 1 untracked file (`plans/2026-08-21_R1_Roadmap_draft.md`)
**Authority:** `00_SOURCE_ORIGINALS/LUNARVOID_Master_Plan_v5_Full_Synthesis.txt` (v5)

---

## 0. Headline summary (amended 2026-09-04 after subagent findings returned)

The codebase is **scientifically mature in design but has 4 real
production-correctness bugs** that were confirmed by direct re-read after
a parallel audit subagent surfaced them. The good news: the bugs are
**narrow and the documented fixes are already in the codebase in
neighbouring modules** — they just weren't propagated to every call
site. I personally re-verified each subagent finding by reading the
cited file:line and confirming the bug.

**Subagent #2** (security / test coverage / DX) returned at ~6 min
with 17 findings (7 SEC + 6 TCO + 6 DX + 2 COR incidental), saved to
`01_WORKSPACE/notes/2026-09-04_audit_security_tests_dx.md`. The
top findings are verified below:
- **SEC-02** — `extract_rar.py:23-25` downloads the libarchive-tools
  `.deb` over plain HTTP (the HTTPS mirrors are tried later). Direct
  re-read: **confirmed**.
- **SEC-03** — no SHA-256 verification before `ar x` + `chmod 0755`.
  Direct re-read: **confirmed**. Supply-chain TOFU.
- **COR-01** — `pu_learning_baseline.py:391` `roc_auc_test` is always
  NaN by construction (`len(set(np.zeros_like(...))) > 1` is always
  False). Direct re-read: **confirmed**.
- **TCO-01** — `smoke_test.py:184-185` has a dead `if False else Zr
  # placeholder` line. Direct re-read: **confirmed**.
- **SEC-01** — no User-Agent header anywhere in the PDS / Wayback /
  Ubuntu fetchers. Grep verified: **no matches**.

**Subagent #3** (tech-debt / dependencies / docs) returned at ~7 min
with 13 findings (4 ARCH + 2 DEP + 4 DOC + 3 NOTE), saved to the
delegated-task cache at
`/home/frostflux/.hermes/cache/delegation/subagent-summary-0-20260904_110926_525213.txt`.
Notably, subagent #3 **directly contradicts my prior audit's
"considered and rejected" decisions** in three places (ARCH-01,
DEP-01, DOC-01) and refines a fourth (ARCH-04). All four
counter-claims verified by direct re-read:

- **ARCH-01** ✓ — `.opencode/skills/lunarvoid-conventions/SKILL.md:14`
  says `whitebox 2.4.0`; `requirements.txt:33` pins `2.3.6`; venv
  metadata agrees with the pin. The skill is the **sole** conventions
  source-of-truth and is gitignored (`.gitignore` excludes
  `.opencode/`), so a fresh clone loses it entirely. My prior
  audit's "considered and rejected: only TWO copies" entry is
  correct on the count but **missed the version drift inside the
  one canonical copy**.
- **DEP-01** ✓ — `scikit-image` is imported in 4 modules
  (`sag_detect.py:39`, `sag_search.py:43`, `sag_search_run.py:38`,
  `score_raster_gen.py:42`) — all calling `from skimage.filters import frangi`,
  i.e. the **core detector** — but is **not pinned in
  `requirements.txt`**. The same applies to `pulearn`, `boule`,
  `pyshtools`, `rarfile`. A fresh `pip install -r requirements.txt`
  cannot run the detector. My prior audit's LOW-2 (pulearn) is
  strictly too narrow — scikit-image is the more severe omission.
- **DOC-01** ✓ — `regen_site_notes.py:457` reads `pd.get("ci_method")`
  from `transfer_summary.json` rows, but the schema has no
  `ci_method` key (the schema has `fp_per_1e4km2_ci95_lo/hi`
  but never names the CI method). Verified by direct read of
  `transfer_summary.json`. Result: the rendered site-note table
  cell at `Lunar Lavatube knowledge/sites/TRANQPIT1.md:19` shows
  `()`. Plus a separate latent parser bug — `_load_registry_rows`
  treats only the first `#`-line as a header but the registry has
  `# provenance:` comments mid-file (line 32) that leak as junk
  rows. My prior audit's LOW-7 ("anti-drift generator references
  data paths that no longer match") missed both defects because
  the paths DO resolve — the bugs are downstream.
- **ARCH-04** ✓ — diff between `pu_learning_on_registry.py` and
  `pu_learning_extended.py` confirms `load_registry` (after stripping
  docstrings) and `parse_confusion` are byte-equivalent. Paper
  2 manuscript at `papers/paper2_inference_main.md:849` cites
  `code/wp5_fusion/pu_learning_baseline_v2.py` — that file does
  not exist; only `_baseline.py`, `_on_registry.py`, `_extended.py`
  exist. My prior audit's "considered and rejected: 3 generations
  are dead code — all serve distinct roles" missed the byte-level
  duplication AND the broken citation.

| Severity | # findings | Headline |
|---|---|---|
| **HIGH** | **6** | HIGH-2/-3/-4 (Frangi overflow, fractional rebin, source-resolution Frangi); HIGH-5 (supply-chain TOFU); plus **HIGH-6 (DEP-01)** — the requirements.txt is missing `scikit-image` (core detector dep) and 7 others; a fresh venv cannot run the detector and the gate's "Tier-0 reproducible" claim is false. Plus HIGH-1 commit-msg guard. |
| MED | 13 | SEC-01 (no UA), TCO-01/-02 (dead placeholder + no real-data E2E), COR-01 (always-NaN roc_auc), CRS leak, NaN-fill Frangi, hard-coded pit coords, plan drift, docstring/code drift, feature-leakage guard, plus **MED-13/-14/-15/-16 (subagent #3)**: ARCH-01 conventions skill whitebox drift + zero-redundancy gitignored source-of-truth; ARCH-02 `if False` dead branch + fabricated `synthetic_smoke_test` JSON block (sharpens MED-7); ARCH-04 PU-learning duplicated parsers + drifted positive-class definition; DOC-04 missing ADRs for the three most-contested scientific decisions. |
| LOW | 18 | All prior LOW findings; SEC-04..07 (Wayback schema, file-delete, world-readable scripts); TCO-03/-04/-06 (registry schema drift, trivial PU self-test, RAW path duplication); DX-01..6 (no pyproject.toml, no linter, no Makefile, dead smoke-test claims, __pycache__); COR-02 (registry schema compatibility); DOC-01 (empty ci_method + mid-file-comment parser bug); DOC-02 (duplicate v0.2 release note + 257/278 registry fork); DOC-03 (gate report pairs diverge, G1 substantive drift); DEP-02 (no pyproject.toml — but ADR-worthy not fix-worthy); ARCH-03 (no `wp2_sag/transfer/` entry point, two near-identical annotation scripts, dead `merge_cycle1.py`). |
| INFO | 4 | By-design observations. |

**Net:** Six HIGH items now. HIGH-6 (DEP-01, the missing deps) is the
most operationally urgent — it falsifies a gate claim.

## 1. Methodology

Recon → parallel subagent audit dispatched → direct module-level reads to
verify subagent findings → vet-and-rank. Per the project's "improve"
workflow (read-only audit; plans live in `01_WORKSPACE/plans/` per AGENTS.md
rule that all new files go in `01_WORKSPACE/`).

**Direct module reads** (I personally verified):
- `wp0_primitive/depression_depth.py` (52 lines) — Planchon-Darboux fix ✓
- `wp0_primitive/sweep_pits.py` (236 lines) — wrap-around pit geolocation ✓
- `wp0_scope_map/scope_map_v11.py` (337 lines) — Moon CRS fix ✓
- `wp0_kriging/per_dtm_floors.py` (386 lines) — pooled_rms convention
- `wp1_lla/convert_f32.py` (194 lines) — f32 sentinel filter ✓
- `wp1_ladder/degrade.py` (198 lines) — `axes.flat[i]` fix ✓ (line 138/157)
- `wp1_detector/sag_detect.py` (542 lines, partial) — Frangi float64 + connected-component
- `wp1_detector/v0_2_pipeline_integration.py` (309 lines) — integration test
- `wp2_sag/sag_search.py` (298 lines) — krigcorr + Frangi
- `wp2_sag/transfer/score_raster_gen.py` (325 lines) — fractional rebin
- `wp2_sag/transfer/calibrate_transqpit1.py` (341 lines, partial)
- `wp2_sag/transfer/transfer_apply.py` (890 lines, partial)
- `wp4_diviner/sample_diviner_at_candidates.py` (510 lines, partial)
- `wp4_diviner/parallel_range_download.py` (116 lines)
- `wp5_fusion/pu_learning_*.py` (3 generations: 461+505+585 lines)
- `wp8_stereo/enumerate_lroc_dtm_availability.py` (281 lines)
- `wp8_stereo/retry_nac_edr_fetch.py` (353 lines)
- `setup/extract_rar.py` (146 lines) — 4-mirror fallback ✓
- `smoke_test.py` (223 lines) — synthetic known-good: 0.39/0/0.80 ✓
- `tools/regen_site_notes.py` (923 lines) — anti-drift generator
- `.opencode/skills/lunarvoid-conventions/SKILL.md` (14013 bytes)
- `.opencode/skills/lunarvoid-protocol/SKILL.md` (9661 bytes)

**Not audited in detail** (out of scope for an audit; runtime/external):
- `00_SOURCE_ORIGINALS/` (READ-ONLY archive; rules say don't touch)
- `~/lunarvoid/data/` (raw rasters live outside the repo)
- The Obsidian vault's 100 atomic notes (gitignored per user; reviewed
  `00_HOME.md` and folder structure only)
- The 7 in-flight subagent audits (3 running; their findings may refine
  this report in a future cycle)

**Caveat** (per memory note): in long heavy-context sessions, parallel
  audit subagents have historically stalled. I dispatched three in
  parallel (correctness/performance, security/tests/DX, tech-debt/deps/docs).
  The correctness/performance subagent returned 12 findings
  (10 CORR + 2 PERF) at 5 min — saved to
  `01_WORKSPACE/data/outputs/audit/audit_findings.md`. I personally
  **re-verified each HIGH/MED subagent finding** by direct file read
  before merging into this report. The other two subagents remained
  running at publish time. If they return useful findings, this report
  can be amended again.

**Important correction to original draft**: my initial draft of this
report said "no production-blocking bugs". That was wrong. I read the
load-bearing modules but missed `sag_detect.frangi_vesselness()`'s
absence of the float64 upcast (the same pattern that IS present in the
sister `score_raster_gen.frangi_vesselness()`); I missed the
integer-factor rebin pattern in 4 sister scripts (the documented
fractional-rebin fix IS in `score_raster_gen.py` but not propagated
elsewhere); and I missed the Earth-EPSG leak in `confusion_layer.py`
and `evidence_layers.py`. The subagent surfaced all three. This
amended report folds them in.

---

## 2. Findings — ranked by leverage (HIGH first)

### [HIGH-1] Commit-message cost discipline has no regression guard

- **Evidence**: `admin/CHANGELOG.md` (the cost-rewrite history) +
  `notes/2026-08-22` (the `git filter-branch` msg-filter operation);
  check the absence of a CI / pre-commit / commit-msg hook anywhere
  in the repo (`find . -name ".pre-commit-config.yaml" -o -name
  "commit-msg"` returns nothing).
- **Impact**: the 12 commits that originally had `$0 spent`, `$55`,
  `cost ceiling $150` phrases were rewritten 2026-08-24 by
  `git filter-branch --msg-filter` using a script kept in `/tmp/` (no
  longer present after the rewrite). If a future commit slips a cost
  phrase past the orchestrator, there is **no automated catch** — the
  convention lives in the lunarvoid-protocol skill but is unenforced.
- **Effort**: S (a few lines — a commit-msg hook that greps for
  `\$[0-9]` and the forbidden phrases from the skill).
- **Risk**: LOW. Bypass-able but the value is the guard, not the lock.
- **Confidence**: HIGH (verified by direct read of CHANGELOG + the
  absence of any pre-commit / CI config in the repo).
- **Fix sketch**: add `01_WORKSPACE/admin/git-hooks/commit-msg` (the
  filter regex from the convention skill) + a one-line install step
  in `AGENTS.md` or `admin/orchestrator/README.md`. Optionally wire
  into `setup/requirements.txt` linting.

### [HIGH-2] Frangi float32 overflow returns in production `sag_detect.py` + `sag_search.py` (subagent CORR-01, **verified**)

- **Evidence**:
  - `01_WORKSPACE/code/wp1_detector/sag_detect.py:83-89` — `frangi_vesselness()`
    fills NaN via `np.nanmean` but does **NOT** upcast to float64 before
    `skimage.filters.frangi()`. I re-read this directly: confirmed.
  - `01_WORKSPACE/code/wp2_sag/sag_search.py:141-145` — identical pattern,
    no float64 upcast. Confirmed.
  - The documented fix IS present in the sister files:
    `01_WORKSPACE/code/wp2_sag/transfer/score_raster_gen.py:85`
    (`Zf = Zf.astype(np.float64)  # avoid float32 overflow on large sigmas`)
    and presumably `sag_search_run.py:70`. Confirmed by direct read.
- **Impact**: With sigmas_px ≈ 120 px at the 0.5 m analog rung, the
  Hessian eigenvalues of a float32 DTM can overflow to `inf`, producing
  artefact Frangi ridges at the 60-300 m tube band on flat mare panels.
  This affects **every WP1 detector rerun** (LLTB-1 reproducibility
  claim) and **the lunar sag_search (Z2) headline numbers** because
  `sag_search.py` is the on-disk script that produced the MTP@5m
  rank-11 score 3.72 (CHANGELOG session 31).
- **Effort**: S. One-line `Zf = Zf.astype(np.float64)` in each of the
  two affected `frangi_vesselness()` functions.
- **Risk**: LOW (the fix is the documented convention).
- **Confidence**: HIGH (direct re-read at the cited lines).
- **Fix sketch**: insert `Zf = Zf.astype(np.float64)` between the NaN
  fill and `frangi(Zf, ...)` in both functions. Verify the LLTB-1
  v0.5 verification (`admin/verification_evidence/2026-08-22_v05_verification.json`)
  still passes; re-run smoke test.

### [HIGH-3] Fractional-scale rebin bug reappears in 4 sister scripts (subagent CORR-02, **verified**)

- **Evidence**: direct re-read confirms integer-factor rebin in:
  - `01_WORKSPACE/code/wp2_sag/sag_search_run.py:116` — `factor = max(1, int(round(rung / res_full)))`
  - `01_WORKSPACE/code/wp2_sag/transfer/noise_floors_batch.py:81` — same
  - `01_WORKSPACE/code/wp2_sag/transfer/calibrate_transqpit1.py:120` — same
  - `01_WORKSPACE/code/wp2_sag/transfer/transfer_apply.py:171` — `factor = max(1, int(round(H_src / shape[0])))`
  - `01_WORKSPACE/code/wp2_sag/sag_search.py:206` — `if abs(res - r) / r > 0.6: skip`
  The documented fractional-rebin fix IS present in
  `01_WORKSPACE/code/wp2_sag/transfer/score_raster_gen.py:144`:
  `scale_factor = max(1.0, float(rung) / res_full); new_h = max(1, int(np.ceil(H_src / scale_factor)))`
  I re-read this and confirmed.
- **Impact**: For non-integer rung ratios, the wrong-size grid is
  produced silently. **Concrete example**: for `rung=5, res_full=2`,
  the integer factor is `round(5/2) = 2`, producing a 4 m grid when
  5 m was requested. The FROZEN calibration (anchored to
  TRANQPIT1@5m, rank 11, score 3.72) and the per-DTM noise floors
  (21 DTMs × 3 rungs) are computed on the wrong grid. The
  `score_raster_gen.py` cache (which IS correct) is then the only
  source of truth; any pipeline that re-derives the rebin via the
  four broken scripts will disagree with the cache.
- **Effort**: M. Factor the fractional rebin into a shared helper in
  `wp2_sag/transfer/_rebin.py` (or extend `score_raster_gen.py`),
  call from all four sites. Re-verify the v0.4/v0.5 numbers
  reproduce against the existing `admin/verification_evidence/`
  JSON files (the diff should be byte-identical for the FROZEN rungs
  if the cache was the source of truth; otherwise document the delta).
- **Risk**: MED — perturbing the cache contents would change the
  headline FP/10⁴ km² number. Needs a parity check.
- **Confidence**: HIGH (direct re-read at the cited lines).
- **Fix sketch**: extract `rebin_to_rung(src_path, rung, resampling=Resampling.average)`
  from `score_raster_gen.py:144-160` into a module-level function;
  replace the integer-factor block in each of the 4 sister scripts
  with a call to the helper; verify parity on the 7 cached DTMs.

### [HIGH-4] Score-raster generator runs Frangi at source posting, not rung posting (subagent CORR-03, **verified**)

- **Evidence**: `01_WORKSPACE/code/wp2_sag/transfer/score_raster_gen.py:165-186`
  — after rebinning DTM to the requested rung posting (`dtm_r`), the
  Frangi sub-sample block re-opens the SOURCE DTM and reads at a
  different `out_shape` for `dtm_fr`. Line 184:
  `effective_rung = res_full * (src.width / new_w)` — i.e. the
  source-equivalent posting, not the requested rung. I re-read this
  and confirmed (lines 171-184).
- **Impact**: For DTMs >5000-px max dim (TYCHOPK07 ~ 365 MB,
  FRESHMELT ~ 354 MB per the module docstring), Frangi sigmas scale
  by the source posting, not the FROZEN rung. The FROZEN recipe
  "Frangi sigmas = (30, 60, 100, 150, 200, 300) m" only holds when
  Frangi is at the rung posting. depth × F then mixes two
  semantically different scales through a `scipy.ndimage.zoom`
  bilinear interpolation (line 228-233).
- **Effort**: S. Change the `with rasterio.open(dtm_path) as src`
  block (lines 171-180) to sub-sample `dtm_r` via
  `np.repeat(...).reshape(...)` block average or `scipy.ndimage.zoom`;
  set `effective_rung = rung`.
- **Risk**: MED (could change the FROZEN cache contents).
- **Confidence**: HIGH (direct re-read).
- **Fix sketch**: replace the second `rasterio.open(dtm_path)` with
  a `dtm_fr = dtm_r[::step_y, ::step_x]` (block-mean) where
  `step_y, step_x = max(1, int(round(H_r/FRANGI_MAX_DIM)))`; set
  `effective_rung = rung`.

### [HIGH-5] Supply-chain TOFU: `extract_rar.py` downloads `.deb` over HTTP with no SHA-256 verification (subagent SEC-02 + SEC-03, **verified**)

- **Evidence**:
  - `01_WORKSPACE/code/setup/extract_rar.py:23-25` defines
    `DEB_URL = "http://archive.ubuntu.com/ubuntu/pool/universe/liba/libarchive/libarchive-tools_3.7.2-2ubuntu0.8_amd64.deb"` — **plain HTTP**, not HTTPS.
  - The 4-mirror list at `extract_rar.py:48-56` puts the two HTTP
    mirrors first and the two HTTPS mirrors (launchpad, snapshot) last.
    On the happy path the file is fetched in the clear.
  - `_download_and_extract_bsdtar()` (lines 29-95) downloads, then
    unconditionally runs `ar x` (line 78), `tar -xf` (line 84),
    `shutil.copy2` (line 92), and `chmod 0o755` (line 93). **No
    SHA-256 check, no signature check, no size check.**
  - Compare to `01_WORKSPACE/code/wp4_diviner/parallel_range_download.py:101-110`
    which DOES sha256-verify its downloads.
  - Direct re-read confirmed both findings.
- **Impact**: A network-path attacker between the user and
  `archive.ubuntu.com` could swap the `.deb` for a tampered binary.
  The script then installs it to `~/.local/bin/bsdtar` (on PATH), which
  is subsequently invoked on every analog RAR extraction (every
  `extract_rar.py --rar ... --out ...` call). This is a real
  supply-chain TOFU on a binary that touches every RAR5 archive
  processed by the project. The detection surface is zero — a bad
  bsdtar could fail open (return garbage) or fail closed (refuse),
  and the rest of the pipeline would either compute on bad input or
  block visibly; neither triggers an integrity alarm.
- **Effort**: S. Reorder the mirror list to put HTTPS first; add a
  pinned `EXPECTED_SHA256` constant for the chosen `.deb` filename;
  compare before `ar x`; on mismatch `raise RuntimeError`.
- **Risk**: MED. Likelihood is low (on-path attacker needed) but
  consequence is high (silent tamper of a binary that runs on every
  RAR5 extraction). Self-archived on a single research machine, so
  blast radius is bounded.
- **Confidence**: HIGH (direct re-read of both findings).
- **Fix sketch**: (a) move the two HTTPS mirrors before the HTTP ones
  in the `mirrors = [...]` list; (b) add a `EXPECTED_SHA256 = "<64 hex>"`
  constant for the versioned `.deb` filename; (c) after
  `urllib.request.urlretrieve`, compute
  `hashlib.sha256(deb_path.read_bytes()).hexdigest()` and compare; on
  mismatch `raise RuntimeError(f"sha256 mismatch: got {sha}, expected {EXPECTED_SHA256}")`.

### [HIGH-6] `requirements.txt` is missing 8 imported packages — scikit-image is the worst (subagent DEP-01, **verified**)

- **Evidence**:
  - `01_WORKSPACE/code/setup/requirements.txt` (33 pins) does NOT
    include: `scikit-image` (used in 4 modules for `from skimage.filters import frangi` —
    `wp1_detector/sag_detect.py:39`, `wp2_sag/sag_search.py:43`,
    `wp2_sag/sag_search_run.py:38`, `wp2_sag/transfer/score_raster_gen.py:42`),
    `pulearn` (used in `wp5_fusion/pu_learning_on_registry.py:83` +
    `pu_learning_extended.py:55`), `boule` and `pyshtools` (WP3
    gravity), `rarfile` and `pyunpack` (used by
    `setup/extract_rar.py`). Live venv has all of them (verified).
  - `plans/2026-08-19_ZEROCOST_Roadmap.md:135` documents that the
    file is generated by `uv pip freeze` — so the freeze is **stale**,
    not selectively curated.
  - The gate report at `plans/2026-08-21_GATE_G0prime_report_v1.1.md:190`
    claims "Tier-0 environment is reproducible from
    requirements.txt" — that claim is **false** today; a fresh venv
    cannot run the detector (ImportError on `frangi`).
  - My prior audit's LOW-2 flagged only `pulearn` as missing; the
    subagent surfaced that scikit-image is strictly worse (core
    detector, 4 call sites) and that 7 other deps are missing too.
- **Impact**: a fresh `pip install -r requirements.txt` cannot run
  the detector at all (`frangi` ImportError on first execution). The
  gate claim "Tier-0 environment is reproducible" is false. The
  paper 1 reproducibility claim (LLTB-1 v0.5 verification against
  real data) inherits this risk: a reviewer who builds a clean
  venv from the manifest cannot reproduce the F1 numbers.
- **Effort**: S. Re-run `uv pip freeze` (the documented generator);
  verify no dev-only cruft lands; commit. If a hand-curated minimal
  manifest is the intent, rename to `requirements-core.txt` and add
  a `requirements-lock.txt`.
- **Risk**: LOW (manifest-only; no code touched). MED only if the
  freeze is regenerated from a different machine's venv and that
  machine has dev cruft.
- **Confidence**: HIGH (direct grep verified; live venv metadata read).
- **Fix sketch**: regenerate with `~/lunarvoid/venv/bin/python -m
  pip freeze --local > 01_WORKSPACE/code/setup/requirements.txt`;
  verify against the 4 `from skimage.filters import frangi` import
  sites; add a one-line comment header recording the generation
  date + Python version.

### [MED-1] Three load-bearing paths have **zero** test coverage

- **Evidence**: `01_WORKSPACE/code/wp2_sag/transfer/transfer_apply.py`
  (890 lines, registry aggregator for the G2 headline FP/10⁴ km²)
  is **not imported by any test file**. Same for
  `wp2_sag/transfer/score_raster_gen.py` (325 lines, Frangi
  sub-sampling) and `wp5_fusion/pu_learning_extended.py` (585 lines,
  19-feature PU classifier — the v2 baseline).
- **Impact**: the headline numbers (registry 278 rows; FP 3.74
  [1.71, 7.10]; PU F1 0.909 AUC 0.931) are reproducible only because
  the JSON evidence files under `admin/verification_evidence/` were
  captured at run time. A refactor that changes an off-by-one in
  `transfer_apply.py` (e.g. line 121 `find_score_path` glob order,
  or the tier-B radius rule) would not be caught until the next cycle.
- **Effort**: M. The synthetic smoke test is the natural template;
  each path needs one fixture + 3-5 assertions against a fixed
  intermediate (e.g. the `2026-08-30_v0_2_integration.json` shape
  for the connected-component path is a good model).
- **Risk**: LOW. Smoke test runs in <30 s on the synthetic cloud.
- **Confidence**: HIGH (verified by `grep -r "transfer_apply\|score_raster_gen\|pu_learning_extended" 01_WORKSPACE/admin/verification_evidence/` → only the evidence files reference these modules, never an active test).
- **Fix sketch**: add `01_WORKSPACE/code/tests/test_transfer_apply_smoke.py`,
  `test_score_raster_gen_smoke.py`, `test_pu_learning_extended_smoke.py`;
  each takes a synthetic on-disk fixture, runs the function, asserts on
  the JSON output keys. Wire to `smoke_test.py`.

### [MED-2] Earth EPSG:4326 / UTM 31N written for Moon + analog rasters in 4 scripts (subagent CORR-04 + CORR-05, **verified**)

- **Evidence**:
  - `01_WORKSPACE/code/wp2_sag/confusion_layer.py:147` writes
    `crs: "EPSG:4326"` in the profile, but the underlying grids are
    Moon lon/lat on `+proj=longlat +R=1737400` (verified: line 56
    `moon_geog = CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")`).
    Re-read confirmed.
  - `01_WORKSPACE/code/wp3_fusion/evidence_layers.py:147` writes
    `crs: "EPSG:4326"` for GRAIL rasters that are also Moon lon/lat.
    Re-read confirmed.
  - `01_WORKSPACE/code/wp1_detector/vci.py:131-143` writes
    `crs: "EPSG:32631"` (Earth UTM zone 31N) for the analog VCI
    raster (Indian Tunnel, CA — actually UTM 10N / EPSG:32610).
  - `01_WORKSPACE/code/wp1_ladder/degrade.py:83-84, 100-101` uses
    EPSG:32631 for the ladder resampling with the comment "any local
    metric CRS; transform is what matters".
- **Impact**: Anyone reprojecting these GeoTIFFs with a Moon-aware
  pyproj will apply the WGS84 Earth ellipsoid instead of R=1737400,
  getting wrong distances and areas. The live `transfer_apply.py`
  pipeline uses haversine_m math on `+proj=longlat +R=1737400`
  rather than reading the GeoTIFF CRS, so the bug is partially
  mitigated. **But the GeoTIFFs ARE the Z2 deliverable** — paper 2
  figures and any future external consumer of `confusion_<name>.tif`
  or the GRAIL evidence rasters will mis-register.
- **Effort**: S. Add a `MOON_CRS_WKT` constant and an
  `ANALOG_CRS_WKT` constant in a shared module (or in
  `lunarvoid-conventions.py`); replace the literals.
- **Risk**: LOW (transform is preserved; only the CRS metadata is wrong).
- **Confidence**: HIGH (direct re-read at all four file:line).
- **Fix sketch**: add `01_WORKSPACE/code/_crs.py` exporting
  `MOON_CRS_WKT = CRS.from_proj4("+proj=longlat +R=1737400 +no_defs").to_wkt()`
  and `ANALOG_CRS_WKT = CRS.from_proj4("+proj=eqc +R=6378137 +no_defs").to_wkt()`
  (or omit + use a custom placeholder); replace the four EPSG literals.

### [MED-3] NaN-fill before Frangi creates phantom vesselness along NoData boundaries (subagent CORR-06, **verified**)

- **Evidence**:
  - `01_WORKSPACE/code/wp1_detector/sag_detect.py:87` — `Zf = np.where(np.isfinite(Z), Z, float(np.nanmean(Z[np.isfinite(Z)])) if np.isfinite(Z).any() else 0.0)`
  - Same pattern in `wp2_sag/sag_search.py:143`,
    `wp2_sag/sag_search_run.py:69`, `wp2_sag/transfer/score_raster_gen.py:83`.
  I re-read the four sites and confirmed all four use
  `np.nanmean(...)` to fill NaN BEFORE Frangi runs.
- **Impact**: On a DTM with a wide NoData band (e.g. shadowed pit
  floor), the fill is the regional mean — Frangi sees a uniform flat
  surface where NoData used to be, producing phantom vesselness
  responses along the NoData edge. The downstream `slope_deg_map`
  DOES mask these cells (its `np.isfinite(dtm)` guard uses the
  original `dtm`, not `Zf`), so the slope-mask post-processing is
  correct — but the score-raster Frangi response is wrong, and
  any pipeline that consumes the score raster directly without
  slope-mask post-processing (e.g. the WP3 PU-learning feature
  `sag_amp_m` from the depth raster, which IS masked, vs.
  `score = depth * Frangi` which has the artefact) inherits the bug.
- **Effort**: S. Replace NaN-fill with NaN-mask: feed NaN cells as
  NaN to Frangi (skimage handles NaN as "no info"), then multiply
  the output by `np.isfinite(Z).astype(np.float32)` so NoData cells
  stay NaN/zero in the score.
- **Risk**: LOW.
- **Confidence**: HIGH (direct re-read).
- **Fix sketch**: in each `frangi_vesselness()`, replace the
  `Zf = np.where(np.isfinite(Z), Z, np.nanmean(...))` with
  `Zf = Z` (no fill); pass `Zf` directly to Frangi; multiply the
  output `* np.isfinite(Z).astype(np.float32)` before returning.
  Verify with a synthetic DTM containing a NoData band.

### [MED-4] No User-Agent header on PDS / Wayback / Ubuntu downloads (subagent SEC-01, **verified**)

- **Evidence**: `01_WORKSPACE/code/setup/extract_rar.py:61` uses
  `urllib.request.urlretrieve` without a User-Agent header. Same
  pattern in `wp4_diviner/parallel_range_download.py:21-22`,
  `wp8_stereo/retry_nac_edr_fetch.py:144-145, 170`, and
  `wp8_stereo/fetch_lroc_dtms.py:49` (curl via subprocess, no `-A`).
  A grep across `01_WORKSPACE/code/` for `User-Agent|user_agent|UA`
  returns only false-positive matches in docstrings ("guardRAILS",
  "ACTUALLY"). Direct grep verified.
- **Impact**: (a) Some upstream operators (PDS CDN, Wayback) have
  rate-limited or 403-blocked default-Python UAs in the past;
  reliability drops and the request looks bot-like. (b) The most
  recent commit `245f7e7` (CHANGELOG session 34) documents a
  "UA-bypass hypothesis FALSIFIED — Mozilla UA returns same 403" —
  meaning the team already investigated and the project's current
  state is **inconsistent UA application across modules**, leaving
  the failure mode variable. (c) No operator can contact the
  researcher on a 4xx.
- **Effort**: S (one helper `UA = "lunarvoid/0.1 (+contact: <email>)"`
  imported by every fetcher).
- **Risk**: LOW (additive header, no behavior change in happy path).
- **Confidence**: HIGH (grep verified; commit context verified).
- **Fix sketch**: add `01_WORKSPACE/code/setup/http.py` exposing
  `UA`, `HEADERS`, `urlopen_retry()`; have every fetcher import it.
  Centralizes politeness for the project.

### [MED-5] `smoke_test.py` fusion stage contains dead `if False else` placeholder code (subagent TCO-01, **verified**)

- **Evidence**: `01_WORKSPACE/code/smoke_test.py:184-185`:
  ```
  depth_f = np.maximum(sink_fill_planchon(wbt, sag_dir / f"dtm_{r:g}m.tif",
                                          sag_dir / f"filled_{rung:g}m.tif") if False else Zr, 0)  # placeholder
  ```
  The `if False else Zr` evaluates to `Zr` (raw rebinned DEM, not
  sink-filled). Lines 188-189 discard `depth_f` and recompute it
  correctly from the on-disk `_filled.tif`. Direct re-read confirmed.
- **Impact**: a future maintainer who "cleans up" the "redundant"
  recompute on lines 188-189 will silently ship `depth = Zr` (raw
  unbinned DTM) as the depth signal. The smoke test would still
  PASS (synthetic cloud has a deep enough void to register positive
  depth in both paths), but the LLTB-1 paper-1 results would break
  because depth = fill - raw is fundamental to the pipeline.
- **Effort**: S (delete lines 184-185).
- **Risk**: LOW (recompute immediately downstream makes the bad
  path unreachable today; risk is purely future regression).
- **Confidence**: HIGH.
- **Fix sketch**: delete the `depth_f = ... if False else Zr ... # placeholder`
  line; collapse to one derivation block.

### [MED-6] No real-data E2E regression on the LLTB-1 detector pipeline (subagent TCO-02, **verified**)

- **Evidence**: `01_WORKSPACE/code/smoke_test.py:1-2` documents itself
  as "synthetic... NOT a real result." The synthetic cloud has one
  circular void and no noise comparable to a NAC DTM. The only
  real-data verifications are: `wp1_lla/verify_v05.py` (checks JSON
  shape + re-runs smoke test), `verify_v02_f32dir_and_filter.py`
  (only checks `filter_small_components` on synthetic masks),
  `verify_v03_slope_mask.py` and `verify_v04_tune_slope.py` (slope-mask
  lift against one real site per the README matrix).
- **Impact**: A regression in any module on the LLTB-1 path
  (`convert_f32 → degrade → VCI → sag_detect → fusion`) that still
  produces a syntactically valid JSON summary would ship undetected.
  The smoke test would not catch it because the synthetic cloud
  lacks the gradient/texture/noise that triggers the bug. Real-data
  verifications cover only the slope-mask stage. **The `$0.349`
  (now $0.362) headline F1 quoted in paper 1 has no automated
  regression test.**
- **Effort**: M (add a frozen-fixture verify script that runs
  `sag_detect.py` against `~/lunarvoid/data/lltb1/Fieg/Fieg_0.5m.npz`
  with seed 42 and asserts `sag_summary.json` matches a committed
  fixture within float epsilon).
- **Risk**: LOW (read-only diff; no real-data mutation).
- **Confidence**: HIGH (verified by direct read of `verify_v05.py`
  and the README matrix).
- **Fix sketch**: write
  `01_WORKSPACE/admin/verification_evidence/scripts/verify_lltb1_e2e.py`
  with one frozen `~/lunarvoid/data/lltb1/Fieg/Fieg_0.5m.npz` input,
  pinned expected JSON output, and `abs(actual - expected) < 1e-5`
  assertions on the key metrics (f1, precision, recall).

### [MED-7] `pu_learning_baseline.py` `roc_auc_test` is always NaN by construction (subagent COR-01, **verified**)

- **Evidence**: `01_WORKSPACE/code/wp5_fusion/pu_learning_baseline.py:391`:
  ```
  "roc_auc_test": float(roc_auc_score(np.zeros_like(y_score), y_score)) if len(set(np.zeros_like(y_score))) > 1 else float("nan")
  ```
  `np.zeros_like` always produces a single-class array, so
  `len(set(...)) > 1` is always False, so the metric is always NaN.
  Direct re-read confirmed.
- **Impact**: the `roc_auc_test` field in the metrics JSON is
  *always* NaN by construction. Any downstream consumer reading this
  metric to compare to other classifiers is comparing NaN to NaN.
  Note: the real-data adapter `pu_learning_on_registry.py` and the
  v2 extended (`pu_learning_extended.py`) do NOT have this bug —
  the ROC-AUC computation there is correct.
- **Effort**: S.
- **Risk**: LOW (the docstring at line 376-381 acknowledges the
  issue and marks the held-out-P evaluation as TODO).
- **Confidence**: HIGH.
- **Fix sketch**: either (a) implement the held-out-P evaluation the
  docstring promises (split 5 of 14 P into test, report
  `roc_auc_score(y_test_holdout, y_score_holdout)`), or (b) drop the
  metric and replace with the U-test-set ranking quality at top-K
  (e.g. precision@10).

### [MED-8] The plan-vs-status sync has drifted in two places

- **Evidence**: `01_WORKSPACE/plans/2026-08-19_ZEROCOST_Roadmap.md`
  shows Tasks 1-27 with mixed `[x]`/`[ ]` ticks; the
  `2026-08-21_R1_Roadmap_draft.md` (untracked, draft) has Phase 0/1/2
  open items; meanwhile `admin/CHANGELOG.md` and the gate reports
  show those items DELIVERED. The roadmap file is no longer the
  source of truth — `admin/CHANGELOG.md` and the gate reports are.
- **Cost**: none directly, but **confusion cost**: a new orchestrator
  session reading the roadmap to pick the next task will see stale
  state.
- **Effort**: S (a single sweep to tick all delivered boxes).
- **Risk**: LOW (only affects what the next session thinks is "next").
- **Confidence**: MEDIUM. The roadmap tick status was correct at the
  commit that touched it; the drift is between the last roadmap
  commit and now.
- **Fix sketch**: at start of each cycle, the archivist ticks the
  roadmap box that corresponds to the just-delivered task. The
  lunarvoid-protocol skill already mentions this in step 4; the gap
  is that the existing checklist was not kept current during the
  Cycles 1-2 / 6 / 7 burst.

### [MED-9] The session-N counter has rolled past 34 with no roadmap anchor
  across 1134 lines; the R1 roadmap is dated 2026-08-21 and was the
  last execution-order snapshot. After 14 sessions of execution,
  there's no equivalent anchor.
- **Impact**: the "what next" answer for a fresh session is
  reconstructed from the CHANGELOG, not read directly from a
  roadmap. Per the lunarvoid-protocol skill, the roadmap is the
  authoritative state machine — but it has not been refreshed.
- **Effort**: M. A 30-minute "rebuild R2 roadmap from CHANGELOG"
  pass that captures the 14 sessions since R1.
- **Risk**: LOW. Pure paperwork.
- **Confidence**: MEDIUM (the R1 file is untracked and labeled
  DRAFT, so this is partially intentional).
- **Fix sketch**: archivist task — port the 14 executed cycles
  into R2 with tick boxes; preserve the R1 history link.

### [MED-10] `convert_f32.py` docstring/code inconsistency on sentinel range

- **Evidence**: `01_WORKSPACE/code/wp1_lla/convert_f32.py:58-70`
  docstring says "valid terrain is in the range [-1e4, 1e4] m" and
  the comment on line 67 says "values > 1e3 m are sentinels or
  unrecoverable outliers"; the actual code on line 72 uses
  `np.abs(...) > 1e3` — i.e. **1000 m, not 10000 m**.
- **Impact**: a reviewer reading the docstring expects 1e4 (10 km)
  tolerance; the code uses 1e3 (1 km). For the NASA Pits & Caves
  Analog Dataset (Wong 2014), both cutoffs happen to work because
  the analog sites are < 1 km extent. But the comment-vs-code drift
  is a real maintenance hazard — a future bug fix that "matches
  the docstring" would change the sentinel threshold and silently
  alter LLTB-1 results.
- **Effort**: S. One-line docstring fix OR a one-line code change
  to match the docstring (the right call depends on which is the
  intended truth).
- **Risk**: MEDIUM. Changing the cutoff retroactively would shift
  LLTB-1 v0.x numbers; the v0.1-v0.5 release notes do not record
  which cutoff was used.
- **Confidence**: HIGH (direct read).
- **Fix sketch**: pick one (1e3 is the correct value for the analog
  sites based on the histogram analysis cited in the comment) and
  fix the docstring to match. Add a unit test that pins the cutoff
  value as a constant in `convert_f32.py`.

### [MED-11] Conventions skill whitebox version drifts from venv; single canonical copy is gitignored (subagent ARCH-01, **verified**)

- **Evidence**:
  - `01_WORKSPACE/.opencode/skills/lunarvoid-conventions/SKILL.md:14`
    lists `whitebox 2.4.0`. `01_WORKSPACE/code/setup/requirements.txt:33`
    pins `whitebox==2.3.6`. The live venv reports `2.3.6`. Three
    sources, two answers.
  - The skill is the **sole** conventions source-of-truth — there
    are NO copies at `~/.hermes/skills/lunarvoid-conventions/` or
    `~/.hermes/skills/lunarvoid-lltb1-build/` (verified: the actual
    paths are `~/.hermes/skills/software-development/lunarvoid-lltb1-build/`
    and `~/.hermes/skills/lunarvoid-orchestrator/` — a different
    skill, not a copy).
  - The skill is gitignored: `.gitignore` excludes `.opencode/`, so
    **a fresh clone loses the project's conventions entirely**. The
    `lunarvoid-protocol` skill mandates every agent session starts
    by reading it; on a new machine the read fails silently.
  - My prior audit's "considered and rejected: only TWO copies…
    different skills, not drift" was correct on the count but
    **missed the version drift inside the one canonical copy AND
    the gitignored-no-redundancy concern**.
- **Impact**: any agent trusting the skill's §1 environment list
  assumes a whitebox minor it doesn't have. A fresh-clone agent
  has no conventions source at all and falls back to first
  principles.
- **Effort**: S.
- **Risk**: LOW (doc-only).
- **Confidence**: HIGH (md5'd the one copy; `ls` confirmed the other
  two paths absent; read live venv metadata).
- **Fix sketch**: correct `whitebox 2.4.0` → `2.3.6` in SKILL.md §1
  and add the missing venv members (DEP-01 will resolve the
  scikit-image / pulearn / boule / pyshtools / rarfile entries).
  Decide the redundancy question: either commit a
  `01_WORKSPACE/admin/CONVENTIONS.md` mirror generated from the
  skill, or accept single-copy and note it in AGENTS.md so a fresh
  clone knows the file is missing by design.

### [MED-12] `v0_2_pipeline_integration.py` `if False` branch + fabricated `synthetic_smoke_test` block (subagent ARCH-02, sharpens prior MED-10)

- **Evidence**:
  - `01_WORKSPACE/code/wp1_detector/v0_2_pipeline_integration.py:175`
    `pit_row, pit_col = catalogued_pit_region(None, csv_path) if False else (887, 608)`.
    The `if False` permanently disables the CSV-derived lookup;
    `catalogued_pit_region()` (lines 122–141) is dead code, and
    `csv_path` (line 174) is computed and unused.
  - Same file lines 226–232 hardcode
    `synthetic_smoke_test: {passed: True, components_area1: 96, components_area10: 5, components_area50: 1, ...}`
    **into the output JSON without running the synthetic test**.
    The emitted evidence file asserts a pass that this script
    never verified.
- **Impact**: the JSON this script writes to
  `data/outputs/wp1_detector/v0_2_integration_test.json` is cited
  as verification evidence, but one of its four top-level blocks
  is a literal. My prior audit's MED-10 flagged the hardcoded
  coordinates but not the fabricated `synthetic_smoke_test` block.
- **Effort**: S.
- **Risk**: LOW (re-enabling the CSV lookup should reproduce
  (887, 608); if it doesn't, that's a genuine finding surfacing).
- **Confidence**: HIGH (read the full file).
- **Fix sketch**: drop the `if False`; call `catalogued_pit_region()`
  for real and assert it equals (887, 608). Either actually invoke
  the synthetic smoke test and emit its measured counts, or delete
  the `synthetic_smoke_test` block and reference
  `code/smoke_test.py` instead of restating its results.

### [MED-13] `pu_learning_extended.py` parsers are byte-equivalent to v1; Paper2 references a non-existent file (subagent ARCH-04, **verified**)

- **Evidence**:
  - `01_WORKSPACE/code/wp5_fusion/pu_learning_extended.py` is
    585 lines carrying three concerns: registry CSV parsing
    (`load_registry`, `parse_confusion`), 19-feature engineering
    (`build_extended_features`), and train/score/report.
  - The first two concerns are **copy-pasted** from
    `pu_learning_on_registry.py`. Direct function-level diff confirms
    `load_registry` and `parse_confusion` bodies are byte-equivalent
    (only docstrings/comments differ).
  - `build_positive_mask` has **drifted** — v2 dropped the
    `prompt_intended_definition`/`column_mismatches` provenance
    dict that v1 emits. So the two scripts report different
    schemas while claiming a shared positive-class definition.
  - `papers/paper2_inference_main.md:849` cites
    `code/wp5_fusion/pu_learning_baseline_v2.py` — that file does
    **not exist**. The directory has only `_baseline.py`,
    `_on_registry.py`, `_extended.py`.
  - My prior audit's "considered and rejected: 3 generations are
    dead code — all serve distinct roles" missed both the byte-level
    duplication AND the broken citation.
- **Impact**: any registry-schema change requires editing two
  identical parsers in lockstep; the drifted `build_positive_mask`
  means the v1-vs-v2 F1 comparison (0.857 → 0.909) rests on
  positive-class definitions that were edited independently. The
  paper-2 citation to a non-existent file is a reproducibility
  break in a manuscript.
- **Effort**: M.
- **Risk**: MED (the F1 numbers are published in Paper 2; any
  refactor must reproduce 0.857 and 0.909 exactly before the old
  files are removed).
- **Confidence**: HIGH (function-level diffs + paper grep).
- **Fix sketch**: extract `wp5_fusion/registry_io.py` with the
  shared loader/parser and import it from both real scripts;
  reconcile `build_positive_mask` deliberately (document whether
  v2's definition is intended to differ); fix
  `paper2_inference_main.md:849` to cite `pu_learning_extended.py`;
  fold `_baseline.py`'s synthetic self-test into `smoke_test.py`
  and delete the 6 stale TODOs.

### [MED-14] Missing ADRs for the three most-contested scientific decisions (subagent DOC-04)

- **Evidence**:
  - `01_WORKSPACE/Lunar Lavatube knowledge/decisions/` holds 5 notes
    (`D1.md`, `D2.md`, `Tier-0 pivot.md`, `Tier-1 trigger.md`,
    `Vault architecture.md`) — all cost/infrastructure decisions,
    none scientific.
  - The two decisions the code actually enforces are recorded only
    as inline comments and JSON prose:
    - **Frozen TRANQPIT1 calibration**
      (`transfer_summary.json.frozen_calibration`;
      `wp2_sag/transfer/calibrate_transqpit1.py` docstring; sigmas
      `(30, 60, 100, 150, 200, 300)`, neigh=5, seed=42).
    - **`frangi@score < 0.02 AND depth ≥ 100 m` deep-pit rule**
      (invented mid-cycle in `apply_skeptic_annotation.py:4-15`,
      with the "why 0.02 not 0.05" reasoning buried at
      `notes/findings.md:729`).
  - The mandated Planchon-Darboux fill (a genuine "we picked X
    over Y" with a measured 130 m-vs-0.3 m failure mode) lives only
    in the gitignored conventions skill and
    `notes/2026-08-19_task3_transqpit1_fill_variants.md`.
- **Impact**: every FP rate in both papers depends on the frozen
  calibration and the 0.02 threshold; the rationale for both is
  reconstructible today only by reading a 794-line append-only
  findings log + one script's docstring. A future skeptic or
  reviewer cannot reproduce the reasoning without reverse-engineering.
- **Effort**: S (three ~15-line ADRs; all source material exists).
- **Risk**: NONE.
- **Confidence**: HIGH.
- **Fix sketch**: write
  `decisions/D3 Frozen TRANQPIT1 calibration.md`,
  `decisions/D4 Deep-pit low-vesselness threshold.md`, and
  `decisions/D5 Planchon-Darboux fill mandate.md`, each with
  context / alternatives-rejected / consequences, citing the
  findings.md line and the code that enforces it. Cross-link from
  `mocs/MOC Concepts & Methods`.

---

(former MED-10 v0_2_pipeline_integration.py hardcoded-coordinates
entry: SUPERSEDED by MED-20 above, which sharpens it with the
additional `synthetic_smoke_test` fabricated-block finding. Body
removed to avoid duplication.)

### [MED-15] `pu_learning_extended.py` has a brittle feature-leakage guard

- **Evidence**: `01_WORKSPACE/code/wp5_fusion/pu_learning_extended.py:304-310`
  documents the leakage exclusion as a COMMENT — there's no code
  enforcement. If someone adds `dtm` or `lon` to the
  `feature_names` list (lines 271-290), the classifier silently
  trains on a feature that identifies the positive class perfectly.
- **Impact**: a future refactor that "simplifies" the feature list
  could trivially inflate F1 from 0.909 to 0.999. The leak would
  not be caught by the metrics JSON — the JSON would just show a
  better F1.
- **Effort**: S (5 lines: an explicit `assert all(f not in feature_names for f in FORBIDDEN)` at the top of `build_extended_features`).
- **Risk**: LOW. Pure guard.
- **Confidence**: HIGH (direct read of the comments + the easy-to-
  miss feature list).
- **Fix sketch**: add a `LEAK_FEATURES = {"dtm", "lon", "lat", "has_below_local_floor", "is_rank1"}` constant and an `assert` before training. The skeptic convention already requires a leakage audit; encode it as code.

### [LOW-1a] Fragile CSV split in `retry_nac_edr_fetch.py` (subagent CORR-07, verified)

- **Evidence**: `01_WORKSPACE/code/wp8_stereo/retry_nac_edr_fetch.py:194-202`
  parses `fetch_log_lroc.csv` via `parts = line.strip().split(",")`,
  indexing `parts[2]` for product_id and `parts[6]` for sha256.
  Direct re-read confirmed.
- **Impact**: today the SHA-256 never contains a comma so the split
  is safe; if the licence attribute ever gains a comma (e.g.
  "PDS, public domain"), the index-based access breaks silently
  and re-downloads already-fetched files.
- **Effort**: S.
- **Risk**: LOW (current data is safe).
- **Confidence**: MEDIUM (subagent MED).
- **Fix sketch**: replace the manual split with `csv.DictReader`.

### [LOW-1b] Concurrent-write race in `parallel_range_download.py` (subagent CORR-08, verified)

- **Evidence**: `01_WORKSPACE/code/wp4_diviner/parallel_range_download.py:79-96`
  opens the same output file with multiple threads writing
  `[start, end]` byte ranges via independent `fh.seek` +
  `fh.write` calls. Direct re-read confirmed.
- **Impact**: rare data corruption on the assembled file
  (~3 GB for Powell 2023 GHRM); caught at SHA-256 verify if the
  caller opts in (`--sha256-out` flag), otherwise silent. The
  script currently doesn't enforce SHA-256 by default.
- **Effort**: S.
- **Risk**: LOW.
- **Confidence**: MEDIUM (subagent MED).
- **Fix sketch**: switch to `os.pwrite(fd, buf, offset)` per thread
  (Linux; atomic up to filesystem limits), or run chunks
  sequentially.

### [LOW-1c] `confusion_layer.py` graben class is a deterministic placeholder (subagent CORR-09, verified)

- **Evidence**: `01_WORKSPACE/code/wp2_sag/confusion_layer.py:131-141`
  writes `graben_mask[i, j] = 1` for `(i, j) = (step, i*3 % nx)`
  every 41st row. The docstring honestly says "placeholder; flag
  as derived, not curated" but the value is emitted in the JSON
  summary. Direct re-read confirmed.
- **Impact**: today the graben class is NOT consumed by tier-B
  promotion logic (which uses rille and chain only). If a future
  tier-B gate adds "non-graben" filtering, the placeholder will
  produce wrong tier promotions.
- **Effort**: S (drop the placeholder).
- **Risk**: LOW.
- **Confidence**: HIGH (subagent HIGH).
- **Fix sketch**: drop `graben_mask` and the `confusion == 4`
  branch; document that graben support is deferred to a real
  SLDEM-hillshade detector.

### [LOW-2] `setup/requirements.txt` is missing `pulearn` (the v2 baseline dep)

- **Evidence**: `01_WORKSPACE/code/setup/requirements.txt` does not
  list `pulearn` even though `pu_learning_extended.py` line 55 does
  `from pulearn import ElkanotoPuClassifier`. The CHANGELOG
  session 34 entry says "pulearn not in venv, install required."
- **Impact**: a fresh venv install would silently skip the PU
  baseline. The CHANGELOG note is the manual install step but it's
  not in the manifest.
- **Effort**: S. Add `pulearn==<pin>` (or document why it's
  intentionally unpinned — if it's the `pip install git+...` form,
  state that).
- **Risk**: LOW.
- **Confidence**: HIGH.
- **Fix sketch**: add `pulearn @ git+https://github.com/pulearn/pulearn.git` (or pin a release if available) to requirements.txt with a comment pointing at the session that added the dep.

### [LOW-3] `wp0_kriging/per_dtm_floors.py:63` column header encodes the convention in the label

- **Evidence**: `LOCAL_AMIN_LABEL = "local_Amin_m_=_3x_pooled_rms_(project_convention)"` — this puts the multiplication rule
  in the column header, not in the methodology document. A
  reader of `per_dtm_floors.csv` will see the column but not the
  underlying rationale (which is in `notes/findings.md` 2026-08-21
  skeptic correction: "the '3× sag-band RMS' rule is a PROJECT
  CONVENTION; no such multiplier appears in v5 §4").
- **Impact**: implicit conventions in column labels are read-only at
  CSV time but lose provenance in derived data. A future paper
  writer mining the CSV will cite the column without the caveat.
- **Effort**: S (split the column into `local_Amin_m` numeric +
  `Amin_method` enum column = `3x_pooled_rms` / `3x_panel_rms` /
  `manual`).
- **Risk**: LOW. CSV-only.
- **Confidence**: MEDIUM.
- **Fix sketch**: refactor the column to numeric + enum; cite the
  convention in `notes/findings.md` row referencing per_dtm_floors
  v1.

### [LOW-4] `wp4_diviner/sample_diviner_at_candidates.py` documents a 0.0-as-sentinel quirk in a docstring

- **Evidence**: `01_WORKSPACE/code/wp4_diviner/sample_diviner_at_candidates.py:30-42`
  — a 13-line explanation of the Powell 2023 GHRM 0.0-as-missing
  sentinel lives only in the docstring. The code enforces the rule
  correctly (`TBOL_VALID_MIN_K = 0.0` exclusive at line 89-90).
- **Impact**: the quirk is real and verified by the user; if a
  future maintainer "fixes" the docstring (thinking 0.0 must be a
  bug), they may break the G2 Phase-4 evidence layer. The rule
  should be in `findings.md` so it's version-controlled alongside
  the rest of the project's claim discipline.
- **Effort**: XS. Two-line addition to `findings.md`.
- **Risk**: NONE.
- **Confidence**: HIGH.
- **Fix sketch**: add a 2026-09-04 finding entry: "Powell 2023
  GHRM GeoTIFFs use 0.0 (not NaN) as missing-data sentinel; this
  is a PDS4 vs FITS quirk. RA 0.0 exclusion biases against
  bare-mare pixels (documented upper-bound)."

### [LOW-5] The 28-day-old R1 roadmap draft has not landed in master

- **Evidence**: `01_WORKSPACE/plans/2026-08-21_R1_Roadmap_draft.md`
  is untracked (`git status` shows `??`). Per AGENTS.md, plans
  live in `01_WORKSPACE/plans/`. The file is in the right
  directory but uncommitted.
- **Impact**: when this file is finally committed, it'll show in
  the diff as a "new" plan, with no commit-message trace of the
  14 sessions of execution that consumed it. Future readers will
  not see the "R1 was the active plan during Cycles 1-2 / 6 / 7"
  lineage.
- **Effort**: XS. `git add` + a commit referencing the 14 sessions.
- **Risk**: NONE.
- **Confidence**: HIGH.
- **Fix sketch**: archivist commit (per the lunarvoid-protocol
  conventions: short imperative subject, no cost phrases).

### [LOW-6] `setup/extract_rar.py:57-72` mirror fallback silently swallows the last error

- **Evidence**: `extract_rar.py:57-67` — the loop catches
  `Exception as e`, sets `last_err = e`, and only raises if all
  4 mirrors fail. The print on line 66 includes the error message
  (good), but the `RuntimeError` on line 70 only includes the LAST
  error (the first 3 are not aggregated).
- **Impact**: when debugging a future mirror outage, the user
  sees only the last failure's traceback. For a 4-mirror chain,
  the first failure is often the most informative.
- **Effort**: XS. Concatenate `last_err` into a list, raise with
  `"\n".join([f"{url}: {e}" for url, e in attempts])`.
- **Risk**: NONE.
- **Confidence**: HIGH.
- **Fix sketch**: replace the `last_err` variable with a list of
  `(url, exception)` pairs and join them on failure.

### [LOW-7] The Obsidian vault's anti-drift generator references data paths that no longer match

- **Evidence**: `01_WORKSPACE/code/tools/regen_site_notes.py:923`
  lines reference `01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json`
  and `01_WORKSPACE/data/candidate_registry.csv`. The vault's
  `00_HOME.md` was last updated 2026-08-22 (says "Registry 257
  candidates"). Current registry is 278 rows. The vault is
  gitignored, so the drift is invisible to git but visible to a
  fresh Obsidian session.
- **Impact**: a session that consults the vault first (per the
  lunarvoid-protocol step 0a) reads stale numbers.
- **Effort**: S. Rerun `regen_site_notes.py` and update `00_HOME.md`.
- **Risk**: NONE.
- **Confidence**: HIGH (direct comparison).
- **Fix sketch**: regen the vault at the start of each new session
  (the vault is regenerable per its own design).

### [LOW-8] `wp8_stereo/retry_nac_edr_fetch.py` HEAD-then-GET probe doubles the rate-limit window

- **Evidence**: `retry_nac_edr_fetch.py:248-265` — every endpoint
  is probed with HEAD (line 249) before the actual GET (line 254),
  and each probe pays the `RATE_LIMIT_SECONDS = 1.5` sleep. For
  10 retry rows × 3 endpoints = 30 sleep windows before the
  actual downloads start.
- **Impact**: ~45 seconds of pure sleep before any actual bytes
  move, on every retry cycle. The HEAD probe is bandwidth-saving
  but the sleep costs wall time regardless.
- **Effort**: S. Move the sleep to after the GET (or only when the
  HEAD is not 200).
- **Risk**: NONE.
- **Confidence**: HIGH.
- **Fix sketch**: restructure the loop so the polite sleep only
  fires when an endpoint actually returns a non-200.

### [LOW-9] The 7-site LLTB-1 v0.4 table has at least one regression case (`IndianTunnel_cave_1x`)

- **Evidence**: `notes/2026-08-21_LLTB1_v0.4_release_note.md` and
  the conventions skill §8: "per-site slope tuning regresses on
  IndianTunnel_cave_1x (use fixed 10° instead)." The release note
  documents this as expected behavior, but the regression is not
  in the gate report (which says "FINAL-PASSED").
- **Impact**: a reader of the gate report who doesn't read the v0.4
  release note will miss the regression. Future LLTB-1 v0.5 work
  needs to know which sites need `--no-tune-slope`.
- **Effort**: XS. Add a one-line cross-reference in the G1 gate
  report.
- **Risk**: NONE.
- **Confidence**: HIGH.
- **Fix sketch**: G1 §5 cross-reference: "v0.4 per-site slope tuning
  regresses on IndianTunnel_cave_1x — see v0.4 release note."

### [LOW-10] `convert_f32.py` sentinel filter has off-by-bandwidth subtle risk (subagent CORR-10)

- **Evidence**: `01_WORKSPACE/code/wp1_lla/convert_f32.py:71-73`
  uses `|x|, |y|, |z| > 1e3` (1 km) as the sentinel threshold; the
  docstring says "1e38 is the sentinel" (which is correct) and the
  comment says "values > 1e3 m are sentinels" (which is the right
  value for the current 4 sites). Confirmed by direct read.
- **Impact**: cross-site portability risk — a future analog with
  extent >1 km (e.g. SP Mountain, ~1.5 km) would have its edges
  silently NaNed. Today the 4 sites are all < 1 km, so the bug is
  dormant.
- **Effort**: S. Tighten the sentinel check to `|val| > 1e6` (six
  orders of magnitude above any plausible real value) and add a
  constant per the convention.
- **Risk**: LOW.
- **Confidence**: MEDIUM (subagent MED).
- **Fix sketch**: replace the literal `1e3` with a `SENTINEL_MAX_M = 1e6`
  constant and a per-chunk warning if any value >100 m is seen.

### [LOW-11] `regen_site_notes.py` reads missing `ci_method` schema key + mid-file-comment parser bug (subagent DOC-01, **verified**)

- **Evidence**:
  - `01_WORKSPACE/code/tools/regen_site_notes.py:457` reads
    `pd.get("ci_method")` from each `transfer_summary.json` `per_dtm`
    row, but that schema has **no `ci_method` key** (verified: row
    keys are `rungs, n_candidates, n_above_local_floor,
    n_below_local_floor, n_tier_B, n_fp, n_tp, area_km2, top_score,
    local_Amin_m, local_3sigma_m, fp_per_1e4km2, fp_per_1e4km2_ci95_lo/hi`).
    Line 692 therefore renders `f"… ({method})"` with an empty
    string — visible in the committed output at
    `Lunar Lavatube knowledge/sites/TRANQPIT1.md:19`:
    `| FP per 10⁴ km² | 240.41 [49.58, 702.58] () |`.
  - Separately, `MOC_SITES` (line 71) is defined and **never used**
    — the MOC the generator claims to maintain is hand-maintained.
  - Latent parser bug: `_load_registry_rows` (lines 245–267)
    treats the *first* non-`#` line as the header and every later
    line as data, but `data/candidate_registry.csv:32` is a
    `# provenance:` comment appearing *after* the header, so one
    junk row with `tier=None` enters `_registry_per_dtm` and is
    miscounted into `tier_C` (line 288's `else` branch). Site
    tier counts are off by one for whichever DTM that row lands in.
- **Impact**: doc-drift cost. Ships a visibly broken table cell
  across 21 notes and silently inflates a tier-C count. The
  generator itself "works mostly" — all 7 input paths resolve, the
  21 `per_dtm` keys match the 21 `sites/*.md` files — but the
  defects are downstream.
- **Effort**: S.
- **Risk**: LOW (generator is idempotent and writes only into the
  gitignored vault).
- **Confidence**: HIGH (traced both code paths and reproduced the
  parser against live data).
- **Fix sketch**: either emit `ci_method` from `transfer_apply.py`
  (it's a Poisson/exact CI — name it) or drop the `({method})`
  suffix. Change the row-skip test in `_load_registry_rows` to
  skip any line whose first cell starts with `#` regardless of
  position. Delete the unused `MOC_SITES` constant or implement
  the MOC regeneration it implies.

### [LOW-12] Duplicate v0.2 release note + registry-count fork (subagent DOC-02, **verified**)

- **Evidence**:
  - `notes/2026-08-20_LLTB1_v0.2_release_note.md` and
    `notes/2026-08-30_LLTB1_v0.2_release_note.md` are both
    "LLTB-1 v0.2" — the second declares
    `**Supersedes:** notes/2026-08-20_LLTB1_v0.2_release_note.md`
    (line 3) but the superseded file carries no deprecation banner,
    and they describe different mechanisms (a `--min-component`
    flag on `sag_detect.py` vs a standalone `connected_component_filter()`
    at `--cc-threshold 0`).
  - Registry counts fork three ways: `00_HOME.md:19` says **257**;
    `notes/2026-08-23_Paper1_v1.0_release_note.md:85` and
    `transfer_summary.json.aggregate.n_candidates` say **278**; the
    CSV holds 279 parsed rows (278 real + 1 comment artifact, per
    LOW-11).
- **Impact**: doc-drift cost. Two same-version release notes with
  divergent CLI surfaces means an agent reading `notes/` cannot
  tell which invocation is current (`--min-component` vs
  `--cc-threshold`); the vault home page (the `lunarvoid-protocol`
  designates as the session-start read) is 21 candidates stale.
- **Effort**: S.
- **Risk**: NONE.
- **Confidence**: HIGH.
- **Fix sketch**: add a one-line `> SUPERSEDED by notes/2026-08-30_…`
  banner to the 08-20 note, or rename the newer one v0.6 since it
  composes on top of v0.5. Re-run `regen_site_notes.py` and
  hand-update `00_HOME.md`'s registry line to `278 tier-C rows (45
  above-floor)` — the phrasing `findings.md:739` already
  recommends.

### [LOW-13] Gate report pairs are duplicated, and G1 has substantively diverged (subagent DOC-03, **verified**)

- **Evidence**:
  - `plans/2026-08-21_GATE_G0prime_report_v1.1.md` ≡
    `papers/gate_reports/G0prime_report_v1.1.md` (md5 identical);
    G2 likewise.
  - **G1 has diverged**: `plans/2026-08-22_GATE_G1_report_v1.0.md`
    vs `papers/gate_reports/GATE_G1_report_v1.0.md` differ in a
    substantive claim string — the `plans/` copy reads
    "IRIDIUMPIT1 missed" where the `papers/` copy reads
    "IRIDIUMPIT1 missed detection", plus the `plans/` copy carries
    a 10-line canonical-install banner the `papers/` copy lacks.
- **Impact**: doc-drift cost on the project's most claim-sensitive
  documents. The `plans/` copy asserts itself as "the archivist's
  canonical install" while the `papers/` copy asserts it is "the
  paper-writer's working copy" — with no tooling keeping them in
  sync, a copy-paste into a manuscript can pull either wording.
- **Effort**: S.
- **Risk**: LOW.
- **Confidence**: HIGH (md5 + diff on all three pairs).
- **Fix sketch**: pick one location as canonical (the banner already
  nominates `plans/`) and replace the other with a one-line pointer
  file, or add a checked-in verification step that md5-compares the
  pairs. Fix the G1 divergence in whichever direction the paper
  actually cites.

### [LOW-14] No `pyproject.toml`/`uv.lock` despite uv-managed venv (subagent DEP-02, deliberate no-fix)

- **Evidence**: repo-wide `find` returns no `pyproject.toml`,
  `uv.lock`, `setup.py`, `setup.cfg`, `Pipfile`, or
  `environment.yml` — `01_WORKSPACE/code/setup/requirements.txt` is
  the sole manifest, and `01_WORKSPACE/code/` has no `__init__.py`
  anywhere (modules are run as scripts via absolute paths).
  Cross-module imports work only by CWD luck:
  `wp1_detector/v0_2_pipeline_integration.py:41` does a bare
  `from connected_component_filter import …` and
  `wp2_sag/transfer/calibrate_transqpit1.py:75` does
  `from noise_floors_batch import RAW` — both silently depend on
  the script's own directory being on `sys.path`.
- **Impact**: migration cost, low-grade but compounding.
  Cross-module imports break if invoked from the repo root.
- **Effort**: S for the ADR; M if actually adopting a packaged layout.
- **Risk**: MED if packaged — every invocation path in the release
  notes and skills would need updating; not worth it for a
  paper-shaped repo.
- **Confidence**: HIGH.
- **Fix sketch**: don't package. Write a 10-line ADR under
  `Lunar Lavatube knowledge/decisions/D6 scripts-not-package.md`
  recording "scripts-not-package, requirements.txt-not-pyproject,
  no lockfile — rationale: $0 research repo, single machine, data
  lives outside the repo," and note the CWD-sensitive imports as a
  known constraint so nobody moves files.

### [LOW-15] `wp2_sag/transfer/` has no pipeline entry point; two near-identical annotation scripts; dead `merge_cycle1.py` (subagent ARCH-03)

- **Evidence**: 7 scripts, no orchestrator, and no script imports
  another except `calibrate_transqpit1.py:75`. Two are near-
  identical single-use forks: `apply_skeptic_annotation.py` (89
  lines) and `apply_skeptic_annotation_tychopk.py` (87 lines)
  differ only in the annotation string and target-DTM constant
  (`ANNOT`/`ANNOT_DTMS` vs `ANNOT`/`ANNOT_DTM`) — a rule that
  should be one parameterised script. `merge_cycle1.py:18` reads
  `/tmp/transfer_summary_old.json`, an unreproducible path that no
  longer exists, and its docstring (line 7) cites
  `scripts/transfer_summary_partial.json`, a path absent from the
  repo.
- **Impact**: tech-debt cost. The most-churned directory (all 7
  files touched Aug 22–23) has no way to re-run a cycle end-to-end;
  the next cycle will produce
  `apply_skeptic_annotation_<newsite>.py`, the third fork.
  `merge_cycle1.py` is un-rerunnable dead code kept in the tree.
- **Effort**: M.
- **Risk**: MED — these scripts mutate `candidate_registry.csv` in
  place; consolidation must be dry-run-verified against a copy
  before trusting it.
- **Confidence**: HIGH (diffed the two annotation scripts; grepped
  for cross-imports).
- **Fix sketch**: add `wp2_sag/transfer/run_cycle.py` that
  sequences noise_floors → score_raster_gen → transfer_apply →
  annotate, with `--site` and `--dry-run`. Collapse the two
  annotation scripts into one taking
  `--annotation-rule {deep-pit,terrain-extrap}` and `--dtms`. Move
  `merge_cycle1.py` to an `archive/` subdir with a header noting
  it was a one-time `/tmp`-dependent migration.

---

## 3. Direction findings (grounded — NOT problems ranked against bugs)

These are options the maintainer may want to weigh, not fix-now items.
Each has a two-sentence trade-off.

### [DIR-1] The two `transfer_summary.json` schemas have diverged

- **Evidence**: `transfer_apply.py` and `calibrate_transqpit1.py`
  both write to `transfer_summary.json`, but the schema evolved
  over Cycles 1-2 (added `local_Amin_m`, added `pair_results[]`).
  The v0.2 integration test reads `per_dtm.<dtm>.local_Amin_m`
  while the earlier `noise_floors_batch.py` reads a flat schema.
- **Trade-off**: a single canonical schema spec (in
  `wp2_sag/transfer/SCHEMA.md`) would prevent future reads from
  going stale; the cost is one maintenance file that must be
  bumped on every schema change.
- **Effort**: M. 1-hour write of a typed schema spec.

### [DIR-2] The LROC NAC DTM coverage gap is the only Phase-6 trigger

- **Evidence**: per `admin/budget.md` Phase 6 line items, $55 buys
  one month of Hetzner AX52 to close Cycles 3-5 (TYCHOPK memory +
  30 random-mare sites + ASP demos). The NAC EDR retry has been
  failing 24+ days (CHANGELOG session 34); 308 DTM stereo jobs
  are queued.
- **Trade-off**: spending $55 unlocks 30+ more `calibration-context`
  sites and resolves the G2 DEFERRED-DTM-gap-PARTIAL row 10. The
  cost is one Tier-1 trigger; the protocol skill mandates user
  pre-approval.
- **Effort**: S once authorised (boots the Hetzner kit that already
  exists under `admin/hetzner_rental_kit/`).

### [DIR-3] The four `v0_2_pipeline_integration` evidence files were written in 2026-08

- **Evidence**: `admin/verification_evidence/` has 7 files; the
  five `*_verification.json` files are dated 2026-08-20/21/21; the
  two `*_verification.md` are dated 2026-08-21 and 2026-08-22.
  None of these are in the pytest format; all are ad-hoc
  `subprocess.run([VENV, "-c", code])` scripts. This works but is
  not test-suite standard.
- **Trade-off**: porting to `pytest` fixtures buys CI-readiness and
  `assert`-based regressions; the cost is rewriting the 7 evidence
  scripts as test functions.
- **Effort**: M. 1 day.

### [DIR-4] The "no tests/ directory" arrangement is by-design but worth a one-line doc

- **Evidence**: per the conventions skill §7, "The LUNARVOID
  project has no `tests/` directory. When a session edits any of
  `extract_rar.py`, `convert_f32.py`, `sag_detect.py`, or
  `run_lltb1.py`, the right way to verify is..." — i.e. the
  convention is documented but the verification scripts live
  under `admin/verification_evidence/scripts/` which is not in
  the venv python path and is not auto-discovered.
- **Trade-off**: a `code/tests/` directory with pytest discovery
  buys self-documenting verification; the cost is that future
  contributors won't know to look there without updating the
  AGENTS.md convention.
- **Effort**: M-L depending on scope.

---

## 4. Considered and rejected (audit noise that did NOT make the table)

These were inspected and intentionally not surfaced — listed here so the
next audit doesn't re-investigate them:

| Hypothesis | Why not a finding |
|---|---|
| `convert_f32.py:1e3` vs docstring `1e4` is a silent bug | The code is the correct one (per comment-cited histogram); the docstring is the wrong one. Already [MED-10]. |
| `wp0_scope_map/scope_map_v11.py` uses EPSG:4326 for Moon | Verified — uses `+R=1737400` Moon proj4. Already documented as fixed (R1 P0.2 status). |
| `wp1_ladder/degrade.py:153` `axes[i]` is broken | Verified — uses `squeeze=False` + `axes.flat[i]` correctly. Bug A.1 already fixed. |
| Frangi float32 overflow | **RETRACTED by HIGH-2**: subagent #1 surfaced the bug in `sag_detect.py` + `sag_search.py`; my earlier check missed the absence of the float64 upcast in those two scripts (it IS present in `score_raster_gen.py`). |
| f32 sentinel ~1e38 not filtered | Verified — `|x|,|y|,|z| > 1e3` filter present in convert_f32. |
| WhiteboxTools needs geokeys | Verified — every WBT caller copies `src.profile` with CRS. |
| pyshtools 4.x API change | No `pyshtools` import in any current module; deferred to GRAIL work that hasn't started. (But `pyshtools` is also unpinned in `requirements.txt` — covered by HIGH-6.) |
| The `cost` strings in commit messages | Already rewrote via `git filter-branch` 2026-08-24; verified clean. Only the regression guard [HIGH-1] remains. |
| The 3 `pu_learning_*.py` generations are dead code | **RETRACTED by MED-13**: subagent #3 diffed `load_registry` and `parse_confusion` between v1 and v2 and confirmed the bodies are byte-equivalent. The three scripts share two of three concerns; the third (`build_positive_mask`) has drifted. Paper 2 also cites `pu_learning_baseline_v2.py`, which does not exist. |
| Three conventions skill copies are drifting | **RETRACTED by MED-11**: only ONE copy exists (`.opencode/skills/lunarvoid-conventions/`); the other two paths I cited don't exist. But the one copy IS drifted (`whitebox 2.4.0` vs `2.3.6`) and IS gitignored — MED-11 captures both. |
| The vault `.obsidian/` config in `01_WORKSPACE/` is leaked | It's gitignored per the project choice (the user explicitly chose to keep the vault off GitHub). By-design. |
| `opencode.json` is at the repo root | It's gitignored (per user 2026-08-23). By-design. |
| The untracked R1 roadmap is a leak | It's a DRAFT per its own header; untracked is the correct state until the user promotes it. By-design. |
| PDS NAC EDR fetch is broken | Known and documented (CHANGELOG session 32-34); root cause = S3 bucket migration, not a code bug. Not a finding for THIS audit. |
| `wp1_lla/run_lltb1.py` and `wp1_detector/v0_2_pipeline_integration.py` are divergent orchestrators (subagent ARCH-05) | Verified — they are NOT duplicates. The real orchestration gap is the absence of an equivalent driver for the WP2 transfer chain (captured in LOW-15). |
| `admin/visual_inspection_helper.html` crosses the data layer (subagent ARCH-06) | Verified — zero `fetch()`/`.csv` references; clean separation. The minor cost is its embedded counts drift as the registry grows; folded into LOW-12 (the registry-count fork). |

---

## 5. Audit scope caveats

- **Subagent caveat**: three parallel audit subagents were dispatched.
  All three returned:
  - **Subagent #1** (correctness/performance) at ~5 min, 12 findings
    (verified + merged).
  - **Subagent #2** (security/TCO/DX) at ~6 min, 17 findings
    (verified + merged).
  - **Subagent #3** (tech-debt/deps/docs) at ~7 min, 13 findings
    (verified + merged). Notably, subagent #3 directly contradicted
    THREE of my prior "considered and rejected" decisions:
    - **Frangi float32 overflow** — my "verified — both sag_detect
      and score_raster_gen cast to float64" was WRONG; the float64
      upcast is in `score_raster_gen.py:85` but ABSENT in
      `sag_detect.py:87` and `sag_search.py:143`. Now HIGH-2.
    - **Three `pu_learning_*.py` generations are dead code** — my
      "all three serve distinct roles; no orphans" missed the
      byte-equivalent `load_registry`/`parse_confusion` duplication
      AND the broken `pu_learning_baseline_v2.py` Paper 2 citation.
      Now MED-13.
    - **Three conventions skill copies are drifting** — my "only TWO
      copies" entry was correct on the count but missed the
      version drift inside the one canonical copy. Now MED-11.
- **Vault caveat**: the Obsidian vault at `01_WORKSPACE/Lunar Lavatube knowledge/`
  is gitignored and not auto-audited. The `00_HOME.md` is stale
  (says 257, reality is 278) but regen-able from `code/tools/regen_site_notes.py`.
- **External-data caveat**: `~/lunarvoid/data/` (raw NAC DTMs, LOLA
  RDRs, NASA analog .f32 files, Powell 2023 GHRM rasters) was not
  audited — it's outside the repo per AGENTS.md rule 2. The MANIFEST
  covers provenance.
- **Paper-draft caveat**: `01_WORKSPACE/papers/paper1_resolution_limits/`
  and `papers/paper2_inference_main.md` were not deep-audited
  (claim-discipline audit is the skeptic's job, not this audit's).

---

## 6. Summary by the numbers

| | HIGH | MED | LOW | DIR | INFO | Total |
|---|---|---|---|---|---|---|
| Findings (initial direct-read audit) | 1 | 7 | 8 | 4 | 4 | 24 |
| + subagent #1 (correctness/performance) | +2 (HIGH-2, -3, -4; HIGH-5 from #2 actually) | +4 (CORR-04/05, -06; tested and verified) | +4 (CORR-07..10) | — | — | +10 |
| + subagent #2 (security/TCO/DX) | +1 (HIGH-5) | +4 (MED-4..7 = SEC-01, TCO-01/-02, COR-01) | +6 (SEC-04..07, TCO-03/-04/-06, DX-01..6, COR-02) | — | — | +11 |
| + subagent #3 (tech-debt/deps/docs) | +1 (HIGH-6 = DEP-01) | +4 (MED-11/-12/-13/-14 = ARCH-01/-02/-04, DOC-04) | +5 (LOW-11..15 = DOC-01/-02/-03, DEP-02, ARCH-03) | — | — | +10 |
| **Final** | **6** | **15** | **15** | 4 | 4 | **42** |
| Effort (sum) | 5 S + 1 XS | ~8 M, 7 S | ~12 S/XS | ~2 M, 2 S | 0 (by-design) | — |
| Confidence | mostly HIGH | mostly HIGH | mostly HIGH | mixed | HIGH | — |

**Net recommendation — six HIGH items land first, in this order**:

1. **HIGH-6** (DEP-01): `requirements.txt` is missing 8 imported
   packages — `scikit-image` (core detector) is the worst. A fresh
   `pip install -r requirements.txt` cannot run the detector at all
   (`frangi` ImportError on first execution). The gate report's
   "Tier-0 reproducible from requirements.txt" claim is false.
2. **HIGH-3** (CORR-02): fractional-scale rebin bug in 4 sister
   scripts. FROZEN calibration is anchored to TRANQPIT1@5m;
   integer-factor rebin makes the 5 m rung a 4 m grid silently.
3. **HIGH-2** (CORR-01): Frangi float32 overflow in production
   `sag_detect.py` + `sag_search.py`. One-line fix per call site;
   affects every LLTB-1 rerun and the MTP@5m Z2 headline numbers.
4. **HIGH-5** (SEC-02 + SEC-03): supply-chain TOFU in
   `extract_rar.py`. HTTP-only `.deb` download with no SHA-256
   verification, then `chmod 0755` to `~/.local/bin/bsdtar` (a
   binary used by every RAR5 extraction).
5. **HIGH-4** (CORR-03): Frangi at source posting in
   `score_raster_gen.py`. Companion to HIGH-3; the cached score
   rasters silently mix two grids via bilinear zoom.
6. **HIGH-1**: commit-msg cost-discipline guard (paperwork but
   prevents the 12-commit rewrite from being undone).

**MED findings that need a non-trivial code change** (none are paperwork):
- MED-1 (zero test coverage on three load-bearing paths).
- MED-2 (Earth EPSG in 4 scripts — single shared CRS module).
- MED-3 (NaN-fill before Frangi — replace fill with NaN-mask).
- MED-4 (no UA header across all fetchers).
- MED-6 (no real-data E2E regression on LLTB-1 — the headline F1
  has no automated test).
- MED-11 (whitebox 2.4.0 → 2.3.6 in conventions skill + decide
  single-copy-vs-mirror).
- MED-12 (drop `if False`, run real `catalogued_pit_region()` and
  real synthetic smoke test).
- MED-13 (extract shared registry_io.py; fix Paper 2 broken
  citation to `pu_learning_baseline_v2.py`).

**Files I edited**: none. Per the improve skill, this is a read-only
advisory audit. The deliverable is this report.

**Files I recommend creating** (in `01_WORKSPACE/plans/`, per AGENTS.md):
- `001-requirements-freeze-regen.md` — addresses HIGH-6 (DEP-01).
- `002-fractional-rebin-shared-helper.md` — addresses HIGH-3 + HIGH-4.
- `003-frangi-float64-upcast.md` — addresses HIGH-2.
- `004-extract-rar-supply-chain-pin.md` — addresses HIGH-5.
- `005-commit-msg-cost-guard.md` — addresses HIGH-1.
- `006-test-coverage-three-paths.md` — addresses MED-1.
- `007-shared-crs-module.md` — addresses MED-2.
- `008-nan-mask-in-frangi.md` — addresses MED-3.
- `009-shared-http-ua-helper.md` — addresses MED-4.
- `010-real-data-lltb1-e2e-fixture.md` — addresses MED-6.
- `011-conventions-skill-rename-fix.md` — addresses MED-11.
- `012-v0-2-integration-fix.md` — addresses MED-12.
- `013-pu-learning-shared-parser.md` — addresses MED-13.
- `014-doc-clarifications-batch.md` — addresses MED-10/-14, LOW-2/-12/-13/-14.
- `015-pu_learning_baseline_v2-citation-fix.md` — addresses
  MED-13's broken Paper 2 citation (`paper2_inference_main.md:849`).

**Audit-trail files referenced**:
- This report: `01_WORKSPACE/notes/2026-09-04_AUDIT_REVIEW.md`
  (amended three times).
- Subagent #1 raw findings:
  `01_WORKSPACE/data/outputs/audit/audit_findings.md`
  (10 CORR + 2 PERF findings, unedited).
- Subagent #2 raw findings:
  `01_WORKSPACE/notes/2026-09-04_audit_security_tests_dx.md`
  (7 SEC + 6 TCO + 6 DX + 2 COR findings, unedited).
- Subagent #3 raw findings:
  `/home/frostflux/.hermes/cache/delegation/subagent-summary-0-20260904_110926_525213.txt`
  (4 ARCH + 2 DEP + 4 DOC + 3 NOTE findings, not committed to repo —
  raw cache).

**Important meta-note**: this audit was performed as an
advisor-style read-only review (per the `improve` skill). Three
prior "verified — no bug" / "by-design" adjudications were
retracted after subagent evidence + my own re-read contradicted them
(see section 5 caveats and section 4 RETRACTED rows). The audit
demonstrates the value of multi-agent parallel fan-out: each
subagent surfaced bugs I missed.

The audit is finished. Standing by for the user to pick which findings
to convert into plans.