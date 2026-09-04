# LUNARVOID — Security / Test-Coverage / DX-Tooling Audit

- **Auditor:** subagent (hermes improve skill)
- **Scope:** `01_WORKSPACE/code/` + root + `01_WORKSPACE/admin/orchestrator/` + `01_WORKSPACE/admin/verification_evidence/`
- **Date:** 2026-09-04
- **Mode:** read-only, no execution, no modifications

---

## Finding Format Reference

Each finding below uses the project's required format:

```
### [CAT-NN] Short imperative title
- **Evidence**: `path/file.py:NN` — one-sentence description.
- **Impact**: ...
- **Effort**: S/M/L
- **Risk**: LOW/MED/HIGH + one line.
- **Confidence**: HIGH/MED/LOW
- **Fix sketch**: ...
```

Categories: SEC = security, TCO = test coverage, DX = DX/tooling, COR = correctness (incidental).

---

## Security findings

The project has very low external attack surface: no web endpoint, no
auth, no user-supplied data crossing trust boundaries. PDS / Wayback /
Zenodo / Brown endpoints are all public and carry no credentials.
Findings below are calibrated to this reality — only real issues are
listed.

### [SEC-01] No User-Agent header on PDS / Wayback / Ubuntu downloads
- **Evidence**: `01_WORKSPACE/code/setup/extract_rar.py:61` (urllib.urlretrieve), `01_WORKSPACE/code/wp4_diviner/parallel_range_download.py:21-22` (urllib Request), `01_WORKSPACE/code/wp8_stereo/retry_nac_edr_fetch.py:144-145,170` (urllib Request), `01_WORKSPACE/code/wp8_stereo/fetch_lroc_dtms.py:49` (curl via subprocess, no `-A`). AGENTS.md §"Plan status" specifies "polite UA, ≤3 retries" but no module sets one.
- **Impact**: (a) Some upstream operators (PDS CDN, Wayback) have rate-limited or 403-blocked default-Python UAs in the past; this both reduces reliability and looks like a bot. (b) The repo's own most recent commit (`245f7e7`, "UA-bypass hypothesis FALSIFIED") documents Mozilla-UA still 403 — meaning PDS WAF behavior was investigated but the project still does NOT consistently apply a UA across all fetchers, leaving the failure mode variable. (c) No operator can contact the researcher on a 4xx.
- **Effort**: S (one helper `UA = "lunarvoid/0.1 (+contact: <email>)"` imported by every fetcher).
- **Risk**: LOW — additive header, no behavior change in happy path.
- **Confidence**: MED (the `245f7e7` commit shows the team already considered this; not setting UA is a known omission).
- **Fix sketch**: add `01_WORKSPACE/code/setup/http.py` exposing `UA`, `HEADERS`, `urlopen_retry()`; have every fetcher import it. Centralizes politeness for the project.

### [SEC-02] HTTP (not HTTPS) for first-mirror `archive.ubuntu.com` download
- **Evidence**: `01_WORKSPACE/code/setup/extract_rar.py:23-25` — `DEB_URL = "http://archive.ubuntu.com/ubuntu/pool/.../"` (plain HTTP). The other three mirrors in the same list at lines 48-56 are also HTTP (`http://archive.ubuntu.com/...`, `https://launchpad.net/...`, `https://snapshot.ubuntu.com/...`). The HTTPS mirrors are tried later in the loop, so on success against the first mirror the file is fetched in the clear.
- **Impact**: A network-path attacker between the user and `archive.ubuntu.com` could swap the `.deb` for a tampered binary; the script then `ar x`s + `tar -xf`s + `shutil.copy2` + `chmod 0755`s it into `~/.local/bin/bsdtar`, which is subsequently run on user RAR archives (which originate from `data.lroc.im-ldi.com` / `pds.mcp.nasa.gov` / `launchpad.net` / etc.). Effectively a TOFU supply-chain risk for a single binary that touches every RAR5 extraction on the machine. Self-archived .deb content is also NOT sha256-verified (compare `extract_rar.py:46-72` to `parallel_range_download.py:101-110` which DOES sha256).
- **Effort**: S.
- **Risk**: MED (user-impersonation possible; targeted at a single research machine). Low likelihood because the attacker must be on-path.
- **Confidence**: HIGH.
- **Fix sketch**: (a) reorder the mirror list so HTTPS URLs come first; (b) compute sha256 of the downloaded `.deb` against a pinned value before extraction (the Ubuntu pool URL embeds a versioned filename, so the sha256 is stable; pin it). Mention the verification step in the docstring.

### [SEC-03] No SHA-256 integrity check on the .deb extraction (supply-chain TOFU)
- **Evidence**: `01_WORKSPACE/code/setup/extract_rar.py:46-95` — downloads a `.deb` and unconditionally runs `ar x` + `tar -xf`. There is no hash check, no signature check, no size check. Compare to `01_WORKSPACE/code/wp8_stereo/fetch_lroc_dtms.py:324-336` and `01_WORKSPACE/code/wp4_diviner/parallel_range_download.py:101-110` which both sha256 their downloads.
- **Impact**: Pairs with [SEC-02] — if the .deb is tampered (or corrupted by mirror), the project installs an attacker-controlled `bsdtar` into `~/.local/bin` on PATH. This binary then runs on every extracted analog archive. The detection surface is zero: a silently-bad bsdtar could fail open (return garbage) or fail closed (refuse to extract), and the rest of the pipeline would either compute on bad input or block visibly — neither triggers an integrity alarm.
- **Effort**: S (sha256 constant + 4-line check).
- **Risk**: MED (matches [SEC-02]).
- **Confidence**: HIGH.
- **Fix sketch**: pin a known `EXPECTED_SHA256 = "<64 hex>"` for the chosen .deb filename; compute and compare before `ar x`; on mismatch `raise RuntimeError` and refuse to install.

### [SEC-04] Wayback CDX response parsed without length / schema checks
- **Evidence**: `01_WORKSPACE/code/wp8_stereo/retry_nac_edr_fetch.py:170-185` — `data = json.loads(resp.read().decode("utf-8"))`, then `data[1:]`, then sort on `r[1]`. The CDX API returns a JSON array of arrays whose header (first row) is documented at line 176 but NOT validated against the actual response. If Wayback returns an empty list, an error envelope, or a renamed schema, the script silently picks `r[0][2]` as the snapshot URL.
- **Impact**: A misformatted CDX response (or one without the expected `original` column) could send `_download` to a URL derived from a wrong-position field — possibly another Wayback field, possibly an unrelated mimetype. The Wayback response is the input to a 400-MB write to disk; a wrong URL could be an attacker-controlled endpoint (CDX has returned redirect-style captures).
- **Effort**: S.
- **Risk**: LOW (Wayback is publicly audited; PDS data is non-secret).
- **Confidence**: MED.
- **Fix sketch**: assert `len(data) >= 2 and data[0] == EXPECTED_HEADER`; if not, `return None`. Also clamp the `if_/` snapshot URL: it must start with `https://web.archive.org/web/`.

### [SEC-05] `verify_v02_f32dir_and_filter.py` deletes a user-supplied symlink without confirmation
- **Evidence**: `01_WORKSPACE/admin/verification_evidence/scripts/verify_v02_f32dir_and_filter.py:167-170` — `if sym.is_symlink() or sym.exists(): sym.unlink()`. The `sym` path is hard-coded (`cave_f32_dir / "IndianTunnel_full_10x.f32"`), so the blast radius is bounded — but it is an ad-hoc delete of a user file with no confirm, and the verification script is run as the user. The script also (line 131) creates `/tmp/v02_verify_empty_f32` and (line 78) `/tmp/v02_verify_sag/` — both outside `01_WORKSPACE/`, but `/tmp` is acceptable per project conventions.
- **Impact**: Low — pinned to one well-known filename. But the pattern (silently deleting a file because a verifier decided the symlink was stale) is the kind of footgun that bites when someone edits the hard-coded path. A future typo could target a different file.
- **Effort**: S.
- **Risk**: LOW (research-machine only, hard-coded target).
- **Confidence**: HIGH.
- **Fix sketch**: rename the existing file rather than delete it (`.bak`); print the rename; let the user decide if the new copy is wrong.

### [SEC-06] `--out` / `--outdir` / `--f32-dir` CLI args accepted without sandboxing
- **Evidence**: `01_WORKSPACE/code/setup/extract_rar.py:121-126` (writes to `args.out`), `01_WORKSPACE/code/wp4_diviner/parallel_range_download.py:51-58` (writes to `args.output`), `01_WORKSPACE/code/wp8_stereo/fetch_lroc_dtms.py:210-211` (writes to `args.out_root`), `01_WORKSPACE/code/wp1_lla/run_lltb1.py:39-46` (reads `.f32-dir` and writes `--outdir`). All use `Path(args.X).mkdir(parents=True, exist_ok=True)` with no path-validation.
- **Impact**: In a local-only research pipeline there is no untrusted caller, so the absence of a sandbox is **by design and not a finding**. The argument is included only because the audit asks for it — the team has documented single-author-local posture in AGENTS.md, and the orchestrator (`01_WORKSPACE/admin/orchestrator/pipeline.py`) is the only caller, which constructs paths from `tasks.yaml` the operator authors.
- **Effort**: N/A.
- **Risk**: LOW.
- **Confidence**: HIGH (no finding — recorded so the omission is intentional).
- **Fix sketch**: None required. If the project ever gains a public-facing entry point (web hook, CI), revisit.

### [SEC-07] Verification scripts under `admin/verification_evidence/scripts/` are world-readable on a single-user machine (informational)
- **Evidence**: `ls -la 01_WORKSPACE/admin/verification_evidence/scripts/` shows two files with `mode -rw-------` (verify_v02_f32dir_and_filter.py, verify_v03_slope_mask.py) and one with `-rw-rw-r--` (verify_v04_tune_slope.py). Disk permission flip from a prior session.
- **Impact**: Operationally zero (single-user research machine). The two stricter ones presumably were made private because they reference `~/lunarvoid/data/lltb1/IndianTunnel_cave/f32/` paths — purely defensive hygiene, not a real secret.
- **Effort**: S (`chmod 644` all three).
- **Risk**: LOW.
- **Confidence**: HIGH.
- **Fix sketch**: uniform `chmod 644` across all three; document a project convention in AGENTS.md or a CONVENTIONS.md.

---

## Test-coverage findings

This project intentionally has no `tests/` directory. Verification is
done via (a) `smoke_test.py` (synthetic, runs in CI-less local) and
(b) per-edit ad-hoc scripts under
`admin/verification_evidence/scripts/` that produce versioned JSON
records. The convention is documented in
`01_WORKSPACE/admin/verification_evidence/README.md` ("Why ad-hoc and
not a test suite"). Findings below describe the *structural coverage*
gaps that this convention leaves open.

### [TCO-01] `smoke_test.py` fusion stage contains dead `if False else` code
- **Evidence**: `01_WORKSPACE/code/smoke_test.py:184-185` — `depth_f = np.maximum(sink_fill_planchon(wbt, sag_dir / f"dtm_{r:g}m.tif", sag_dir / f"filled_{rung:g}m.tif") if False else Zr, 0)  # placeholder`. The `if False else Zr` evaluates to `Zr` (the raw rebinned DEM, not the sink-filled surface), then line 189 discards `depth_f` and recomputes it from the on-disk `_filled.tif`. The recompute is correct; the placeholder is dead code that obscures intent.
- **Impact**: A future maintainer who removes the "redundant" recompute on lines 188-189 will silently ship `depth = Zr` (the unbinned raw DTM) as the depth signal — this would still PASS the smoke test (the synthetic cloud has a deep enough void to register positive depth in both paths) but would break the LLTB-1 paper-1 results because the depth = fill - raw contract is fundamental.
- **Effort**: S (delete lines 184-185).
- **Risk**: LOW (the recompute immediately downstream makes the bad path unreachable; risk is purely "future regression").
- **Confidence**: HIGH.
- **Fix sketch**: delete the `depth_f = ... if False else Zr ... # placeholder` line; collapse to one derivation block.

### [TCO-02] No coverage of the LLTB-1 detector pipeline on REAL data
- **Evidence**: `01_WORKSPACE/code/smoke_test.py:1-2` documents itself as "synthetic... NOT a real result." The synthetic cloud has one circular void and no noise comparable to a NAC DTM. The only REAL-data verifications are: (a) `01_WORKSPACE/code/wp1_lla/verify_v05.py` (which only checks JSON-artifact shape and re-runs the smoke test, lines 111-121), (b) `verify_v02_f32dir_and_filter.py` (which only checks the `filter_small_components` function on synthetic masks, lines 36-66), (c) `verify_v03_slope_mask.py` and `verify_v04_tune_slope.py` (per the README matrix at `01_WORKSPACE/admin/verification_evidence/README.md:73-93` — slope-mask lift against one real site).
- **Impact**: A regression in any module on the LLTB-1 path (`convert_f32 → degrade → VCI → sag_detect → fusion`) that still produces a syntactically valid JSON summary would ship undetected. The smoke test would not catch it because the synthetic cloud lacks the gradient / texture / noise that triggers the bug. Real data verifications cover the slope-mask stage only. **The `$0.349` headline F1 quoted in the paper has no automated regression test.**
- **Effort**: M (add a single "end-to-end on Fieg_A" check that compares a fresh `sag_summary.json` against a frozen expected JSON committed at `01_WORKSPACE/admin/frozen_expected/fieg_v01.json` — same pattern as `verify_v05.py` lines 39-50 which already does this for `sensor_f1_comparison.csv`).
- **Risk**: LOW (read-only diff; no real-data mutation).
- **Confidence**: HIGH.
- **Fix sketch**: write `01_WORKSPACE/admin/verification_evidence/scripts/verify_lltb1_e2e.py` that runs `sag_detect.py` against the on-disk `~/lunarvoid/data/lltb1/Fieg/Fieg_0.5m.npz` with seed 42 and asserts `ladder_summary.json` + `sag_summary.json` byte-match against a frozen fixture (within float epsilon). Wire as a manual entry in the verification matrix.

### [TCO-03] Registry aggregation in `wp2_sag/transfer/` has no integrity check
- **Evidence**: `01_WORKSPACE/code/wp2_sag/transfer/transfer_apply.py` (890 lines, 9 deliverable scripts under that dir), `01_WORKSPACE/code/wp2_sag/transfer/apply_skeptic_annotation.py:75-89` does its own `subprocess.run(['grep', ...])` post-hoc verification, `01_WORKSPACE/code/wp2_sag/transfer/merge_cycle1.py` and `noise_floors_batch.py` exist but no smoke test or verify script exercises them. The "transfer_summary.json" is the canonical output and is NOT referenced by any `verify_*.py` file.
- **Impact**: The candidate-registry is the project's central artifact (paper-1 results, paper-2 baseline). The schema-mutation pipeline (skeptic annotation, transfer apply, merge cycle, noise floor batch) can silently drop rows, reorder them, or change tier assignments. No test catches it.
- **Effort**: M.
- **Risk**: LOW (single-author pipeline; manual review catches it).
- **Confidence**: MED (by-design per the project's "verification is ad-hoc" convention, but the registry is the highest-value artifact — the per-edit verification model is mismatched to its risk profile).
- **Fix sketch**: add a verify script that loads `01_WORKSPACE/data/candidate_registry.csv` (or the analogous summary) and asserts (a) row count, (b) every row's `candidate_id` is unique, (c) the 7 priority DTMs each appear at least once, (d) `tier` values are restricted to {A, B, C}. Pin in JSON.

### [TCO-04] PU-learning skeleton has a self-test that mathematically cannot fail (trivially `f1_test == 0`)
- **Evidence**: `01_WORKSPACE/code/wp5_fusion/pu_learning_baseline.py:421-451` — the synthetic self-test asserts `assert isinstance(f1, float)` (line 449). The f1 is computed at line 448 as `f1_score(np.zeros_like(y_pred), y_pred, zero_division=0)`, where the y_true is all zeros — the test then asserts the API works, not that the algorithm is correct. The docstring at line 423 even states "F1 will be 0 because y_test is all-zero" — so the "self-test" only proves the code doesn't crash.
- **Impact**: A future regression that flips `predict_proba` ordering (so positives get LOW scores instead of HIGH) would still pass the self-test (because F1 with all-zero y_true is always 0 regardless of predictions). The real-data adapter `pu_learning_on_registry.py` is the only thing that touches real data, and it has no self-test at all.
- **Effort**: S.
- **Risk**: LOW (skeleton; explicitly marked SKELETON in docstring line 75).
- **Confidence**: HIGH.
- **Fix sketch**: replace the synthetic self-test with one where y_test contains at least 1 positive (held out from `X_p`); then assert `roc_auc > 0.7` (the docstring already promises this on line 419).

### [TCO-05] No characterization test for the I2 kriging correction
- **Evidence**: `01_WORKSPACE/code/wp0_kriging/kriging_correction.py` is 531 lines and is the I2 deliverable. It is invoked by `wp2_sag/sag_search_run.py` and is the keystone of the "we correct DTM systematic error against LOLA" claim in paper 1. There is no `verify_kriging*.py` under `admin/verification_evidence/scripts/`, and no entry in the README's verification matrix (`01_WORKSPACE/admin/verification_evidence/README.md:50-56`).
- **Impact**: A regression in the spherical-variogram auto-fit / fallback path (`kriging_correction.py:280-301`) would silently degrade the bias/RMSE numbers quoted in the paper. The empirical-fit fallback at line 293 has subtle semantics (`empirical-numpy-fit` vs `pykrige-autofit`) that no test asserts.
- **Effort**: M.
- **Risk**: MED (this is the headline correction; downstream headline numbers depend on it).
- **Confidence**: MED.
- **Fix sketch**: extract a small synthetic "checkerboard DTM + synthetic LOLA" fixture (~50 shots on a 5x5 km grid), run `kriging_correction.run()` with `--max-train 30 --holdout 0.2`, assert the bias-reduction direction is monotone.

### [TCO-06] `lunarvoid-conventions` paths are duplicated across many modules
- **Evidence**: `RAW = Path.home() / "lunarvoid" / "data"` appears in 8+ files (`wp8_stereo/fetch_lroc_dtms.py:57`, `wp8_stereo/retry_nac_edr_fetch.py:79-80`, `wp0_kriging/kriging_correction.py` via `R_MOON` constant, `wp2_sag/sag_search.py:47`, `wp2_sag/sag_search_run.py`, etc.). The convention is mentioned as `lunarvoid-conventions §1` in 10+ docstrings but there is no `01_WORKSPACE/code/setup/paths.py` exporting `RAW`, `DTMS_ROOT`, `WP1_DATA`, etc.
- **Impact**: Not a test coverage gap per se — but a refactor hazard. If the convention changes (e.g., the user moves `lunarvoid/` to a different parent), every site that defines `RAW` independently must be edited; a missed edit will produce silent "directory not found" failures that don't trip any verification script. Verification scripts use absolute paths (`verify_v02_f32dir_and_filter.py:10-11`, `verify_v05.py:15`) precisely to dodge this fragility.
- **Effort**: S (one `paths.py` file + 8 import swaps).
- **Risk**: LOW (refactor hygiene, not a runtime bug).
- **Confidence**: HIGH.
- **Fix sketch**: write `01_WORKSPACE/code/setup/paths.py` with `RAW`, `EDR_ROOT`, `VENV_PY`, `DTMS_ROOT`, `WP1_OUT`, etc. Have every module that currently does `Path.home() / "lunarvoid" / ...` import from there.

---

## DX & tooling findings

### [DX-01] `requirements.txt` is checked in but the venv is `uv`-managed and there's no `pyproject.toml` / `uv.lock`
- **Evidence**: `01_WORKSPACE/code/setup/requirements.txt` (33 pinned packages including `numpy==2.5.2`, `whitebox==2.3.6`). `opencode.json:11` uses `uvx` for MCP servers (`uvx arxiv-mcp-server`, `uvx zotero-mcp`). No `pyproject.toml`, no `uv.lock`, no `Pipfile`, no `setup.cfg` anywhere in the repo (`search_files` returns zero hits for `pyproject|\.flake8|mypy|ruff|pylint`).
- **Impact**: The venv the project actually uses is `~/lunarvoid/venv/`, but its dependency state is not reproducible from the repo — `pip install -r requirements.txt` will pin to the same versions but won't reflect the venv's actual extras (e.g. `pulearn` per `pu_learning_baseline.py:303-306`, which the script itself acknowledges is "NOT yet installed"). The AGENTS.md framing is single-author local; this isn't blocking, but it means any second agent (or a fresh CI box) must reconstruct the venv by trial-and-error.
- **Effort**: M (one `pyproject.toml` with `[project]` + `[tool.uv]` + `uv.lock` via `uv lock`; delete `requirements.txt` or mark it informational).
- **Risk**: LOW (no behavior change; the venv continues to work).
- **Confidence**: HIGH.
- **Fix sketch**: run `uv init --bare` in `01_WORKSPACE/code/`, move the 33 pins into `[project] dependencies`, run `uv lock`, commit `uv.lock`. Add `[tool.ruff]` with project rule "E501 line length 100" and `[tool.ruff.lint] select = ["E", "F", "W", "I"]` — purely advisory, no fix-on-save wiring. This is the smallest investment that gives the project a reproducible install + a lint baseline.

### [DX-02] No formatter / linter / typechecker configured
- **Evidence**: `find … -name "Makefile" -o -name ".flake8" -o -name "ruff.toml" -o -name "mypy.ini" -o -name ".pre-commit-config.yaml"` returns zero matches. No `pyproject.toml` with `[tool.ruff]`, `[tool.black]`, `[tool.mypy]`, `[tool.pyright]`.
- **Impact**: Code style varies across modules (4-space vs 2-space indentation, docstring conventions, single vs double quotes). A future maintainer or second agent will produce churn to converge on one style. The lack of a typechecker means the `np.column_stack([...])` / `np.clip` / `curve_fit` shape mismatches across modules are caught only at runtime. AGENTS.md is explicit that no CI is required (single-author local), so the absence is by-design — but a project-local pre-commit is cheap and orthogonal to CI.
- **Effort**: M (one `pyproject.toml` + a `Makefile` with `make lint`, `make typecheck`, `make smoke` targets).
- **Risk**: LOW (lint is advisory; ruff's default rule set is conservative).
- **Confidence**: HIGH.
- **Fix sketch**: add `[tool.ruff] line-length = 100`, `[tool.ruff.lint] select = ["E", "F", "W", "I"]`, plus a `.pre-commit-config.yaml` with `ruff check --fix` and `ruff format`. Optional: add `[tool.mypy] strict = false` and run on the `wp5_fusion/` modules first (most ML-style code, most likely to surface type errors).

### [DX-03] No `Makefile` / `tasks.yaml` exposed runner for the verification matrix
- **Evidence**: The README's "How to use this" section (`01_WORKSPACE/admin/verification_evidence/README.md:23-31`) gives raw `~/lunarvoid/venv/bin/python …/scripts/verify_vXX_*.py` invocations as the manual entry point. `01_WORKSPACE/admin/orchestrator/pipeline.py` runs `tasks.yaml` entries via `opencode run` — but `tasks.yaml` is not committed (the script at `pipeline.py:55` reads `TASKS_FILE.read_text()` from the same dir; if absent the script crashes immediately). The verify scripts each duplicate the VENV path (`verify_v02_f32dir_and_filter.py:11`, `verify_v05.py:15`).
- **Impact**: Onboarding friction: any new agent must discover the VENV path by reading the docstring or by reading `verify_v05.py:15`. The VENV is hard-coded `/home/frostflux/lunarvoid/venv/bin/python` in two verify scripts — a relocation of the venv breaks both with no warning.
- **Effort**: S.
- **Risk**: LOW.
- **Confidence**: HIGH.
- **Fix sketch**: add `01_WORKSPACE/Makefile` with targets `verify-v02`, `verify-v03`, `verify-v04`, `verify-v05`, `verify-e2e` (TCO-02's new one), and a top-level `make verify-all`. Have each target locate the venv via `python -c "import sys; print(sys.executable)"` if available, falling back to the hard-coded path.

### [DX-04] `verify_session_edits.py` referenced in the audit prompt does not exist
- **Evidence**: A search for `verify_session_edits` across the entire repo returns zero hits. The actual pattern is `/tmp/hermes_verify_lunarvoid*.py` one-off scripts (referenced in `2026-08-20_v01_v02_smoke_test_verification.json:5-6`); the canonical surviving scripts are `01_WORKSPACE/admin/verification_evidence/scripts/verify_v0[2-4]_*.py` + `01_WORKSPACE/code/wp1_lla/verify_v05.py`.
- **Impact**: The audit prompt assumed a verifier named `verify_session_edits.py` exists; it doesn't. Documentation drift between the project's self-description (which uses "verify_vXX" naming) and any downstream prompt that references "verify_session_edits" is real.
- **Effort**: S (or N/A if the prompt's reference is itself stale).
- **Risk**: LOW.
- **Confidence**: HIGH.
- **Fix sketch**: nothing to fix in the repo; just note in the audit summary that this expected file is absent. (This is a finding about the prompt, not the code.)

### [DX-05] `smoke_test.py`'s documented numbers (F1 0.39/0/0.80, AUC 0.990) have no programmatic gate
- **Evidence**: `01_WORKSPACE/admin/verification_evidence/2026-08-22_v05_verification.json:56-59` records these as a passing check, and `01_WORKSPACE/code/wp1_lla/verify_v05.py:112-121` re-runs the smoke test and asserts the numbers within tolerance (`abs(f1s[0] - 0.392) < 0.005 etc.`). This is well-implemented. However, `smoke_test.py` itself (the document under audit) only PRINTS the numbers — it does not assert them. So if someone runs `python smoke_test.py` outside the verify harness, a regression that produces F1 0.10 silently passes.
- **Impact**: The smoke test is treated as a verification artifact but is a passive instrument — its claims depend on a human watching stdout. The `verify_v05.py` wrapper fixes this but is a one-off for v0.5 only; there's no equivalent gate for v0.1–v0.4 changes.
- **Effort**: S.
- **Risk**: LOW.
- **Confidence**: HIGH.
- **Fix sketch**: at the bottom of `smoke_test.py:222`, add `assert all(abs(actual - expected) < tol for ...)` blocks keyed off the same numbers `verify_v05.py` already encodes. Single source of truth.

### [DX-06] `__pycache__/` directories exist on disk alongside tracked Python
- **Evidence**: `find … -name "__pycache__"` shows 8+ `__pycache__/` subdirs under `01_WORKSPACE/code/` (e.g. `wp1_detector/__pycache__/vci.cpython-312.pyc`). `git ls-files | grep __pycache__` returns zero — so they are NOT tracked in git, and `.gitignore:3` correctly excludes them. This is a hygiene entry only.
- **Impact**: On disk only. No repo effect.
- **Effort**: S (`find . -name __pycache__ -exec rm -rf {} +`).
- **Risk**: LOW.
- **Confidence**: HIGH.
- **Fix sketch**: nothing — the `.gitignore` is correct; just `git clean -fdx` on disk.

---

## Correctness findings (incidental, surfaced during the audit)

### [COR-01] `pu_learning_baseline.py` ROC-AUC computes against all-zero y_true, producing `nan` then guarding it back to nan
- **Evidence**: `01_WORKSPACE/code/wp5_fusion/pu_learning_baseline.py:391` — `roc_auc_test = float(roc_auc_score(np.zeros_like(y_score), y_score)) if len(set(np.zeros_like(y_score))) > 1 else float("nan")`. This is a no-op trap: `np.zeros_like` always produces a single class (0), so `len(set(...)) > 1` is always False, so the metric is always `nan`. The branch is dead.
- **Impact**: The `roc_auc_test` field in the metrics JSON is *always* `nan` by construction. Any downstream consumer that reads this metric to compare to other classifiers is comparing nan to nan.
- **Effort**: S.
- **Risk**: LOW (the docstring at line 376-381 acknowledges the issue and marks the held-out-P evaluation as TODO).
- **Confidence**: HIGH.
- **Fix sketch**: either (a) implement the held-out-P evaluation the docstring promises (split 5 of 14 P into test, report `roc_auc_score(y_test_holdout, y_score_holdout)`), or (b) drop the metric and replace with the U-test-set ranking quality at top-K (e.g. precision@10).

### [COR-02] `transfer_apply.py` reads a registry row that may not have the `confusion` column
- **Evidence**: `01_WORKSPACE/code/wp2_sag/transfer/transfer_apply.py` (read at lines 100-220). The module is documented to consume the candidate registry; `pu_learning_on_registry.py:215-272` independently documents that "the registry schema lacks" several expected columns. If `transfer_apply.py` ever invokes the same schema probe without the column-report fall-back that `pu_learning_on_registry.py` does, a KeyError would terminate a multi-hour run.
- **Impact**: A future schema drift between `transfer_apply.py` (which writes the registry) and the consumer of `confusion` would surface as a late-stage crash, after `compute_dtm_one` etc. have produced rasters. Mitigation cost: high (re-run the pipeline). Detection cost today: low (no test for schema compatibility).
- **Effort**: M (one shared `registry_columns.py` helper).
- **Risk**: MED (one bug per column-missing per pipeline).
- **Confidence**: MED (the schema mismatch is already documented; the question is when the next one happens).
- **Fix sketch**: extract a `01_WORKSPACE/code/wp2_sag/registry_helpers.py` with `required_columns(registry_csv: Path) -> tuple[str, ...]` and have every registry-reading module call it once at startup.

---

## Top findings by leverage

Ordered by impact ÷ effort, discounted by confidence and fix-risk. Tiebreakers per the playbook.

1. **[SEC-02] HTTP-only mirror for `.deb` download** — 4-line reorder + a sha256 pin; closes a real supply-chain TOFU on a binary that runs on every RAR5 extraction. Effort S, Risk MED, Confidence HIGH.
2. **[SEC-03] No SHA-256 integrity check on the .deb** — direct consequence of (1); one constant + 4 lines; fixes a real silent-tamper vector. Effort S, Risk MED, Confidence HIGH.
3. **[TCO-02] No real-data E2E regression on the LLTB-1 pipeline** — the headline numbers in paper 1 have no automated regression test. Add a frozen-fixture verify script (mirrors `verify_v05.py` lines 39-50 which already does it for the composed table). Effort M, Risk LOW, Confidence HIGH.
4. **[SEC-01] No User-Agent on PDS / Wayback / Ubuntu fetches** — one shared header helper; AGENTS.md already specifies politeness but no module honors it. Effort S, Risk LOW, Confidence MED.
5. **[DX-01] No `pyproject.toml` / `uv.lock` despite `uv`-managed venv** — closes the install-reproducibility gap and gets a lint baseline for free. Effort M, Risk LOW, Confidence HIGH.
6. **[TCO-05] No characterization test for `kriging_correction.py`** — the keystone of paper 1's correction claim. Small synthetic fixture + bias-reduction assertion. Effort M, Risk MED, Confidence MED.
7. **[SEC-04] Wayback CDX response not schema-checked** — small defensive check; pairs with [SEC-01]. Effort S, Risk LOW, Confidence MED.
8. **[TCO-06] `RAW = Path.home() / "lunarvoid" / "data"` duplicated across modules** — refactor hygiene; extract `01_WORKSPACE/code/setup/paths.py`. Effort S, Risk LOW, Confidence HIGH.

---

## Files audited (read-only)

Root:
- `AGENTS.md`, `opencode.json`, `.gitignore`

`01_WORKSPACE/admin/`:
- `orchestrator/pipeline.py`
- `verification_evidence/README.md`
- `verification_evidence/scripts/verify_v02_f32dir_and_filter.py`
- `verification_evidence/scripts/verify_v03_slope_mask.py`
- `verification_evidence/scripts/verify_v04_tune_slope.py`
- `verification_evidence/2026-08-20_v01_v02_smoke_test_verification.json`
- `verification_evidence/2026-08-21_v02_regression_verification.json`
- `verification_evidence/2026-08-21_v03_lift_verification.json`
- `verification_evidence/2026-08-21_v04_tune_slope_verification.json`
- `verification_evidence/2026-08-22_v05_verification.json`

`01_WORKSPACE/code/`:
- `setup/extract_rar.py`, `setup/requirements.txt`
- `smoke_test.py`
- `wp0_kriging/kriging_correction.py` (lines 1–531, full)
- `wp0_primitive/depression_depth.py`, `wp0_primitive/sweep_pits.py` (listed, not deep-read)
- `wp1_lla/convert_f32.py` (lines 1–100), `wp1_lla/run_lltb1.py` (full), `wp1_lla/verify_v05.py` (full)
- `wp1_detector/sag_detect.py` (lines 1–40 + structure)
- `wp2_sag/sag_search.py` (lines 1–50), `wp2_sag/sag_search_run.py` (lines 1–120)
- `wp2_sag/transfer/transfer_apply.py` (lines 1–220)
- `wp2_sag/transfer/calibrate_transqpit1.py` (lines 1–100)
- `wp2_sag/transfer/apply_skeptic_annotation.py` (lines 60–89)
- `wp2_sag/transfer/apply_skeptic_annotation_tychopk.py` (grep signature)
- `wp4_diviner/parallel_range_download.py` (full)
- `wp4_diviner/sample_diviner_at_candidates.py` (lines 1–105)
- `wp5_fusion/pu_learning_baseline.py` (full)
- `wp5_fusion/pu_learning_on_registry.py` (lines 1–280)
- `wp5_fusion/pu_learning_extended.py` (grep signature)
- `wp8_stereo/fetch_lroc_dtms.py` (full)
- `wp8_stereo/retry_nac_edr_fetch.py` (full)
- `wp8_stereo/enumerate_lroc_dtm_availability.py` (lines 1–100)

Also: `git log --oneline -15`, `git ls-files | wc -l`, full search across `01_WORKSPACE/` for credential patterns (`api_key`, `Bearer`, `sk-`, `token=`, `password=`, `secret=`, `.env`) — zero matches.

---

## Files NOT audited and why

- **`00_SOURCE_ORIGINALS/`** — READ-ONLY by project rule (`AGENTS.md` rule 1); read-only by audit rule.
- **`01_WORKSPACE/learning/`** — explicitly local-only (`learning/` is in `.gitignore:77`); intentionally not in scope.
- **`01_WORKSPACE/Lunar Lavatube knowledge/`** — explicitly local-only (`.gitignore:73`); intentionally not in scope.
- **`01_WORKSPACE/papers/`** — paper drafts / figures / submission material; non-code, out of scope for a code audit.
- **`01_WORKSPACE/data/outputs/`** — generated rasters + summaries (and the large `_tif` derivatives are gitignored at `.gitignore:32-67`); the JSON summaries inside were sampled (`sensor_summary.json`, `hapke_summary.json` via `verify_v05.py`).
- **`01_WORKSPACE/data/index_layers/`, `01_WORKSPACE/data/wp8_stereo/`, `01_WORKSPACE/data/outputs/`** — JSON manifests / CSVs only, sampled not exhaustively read.
- **`~/lunarvoid/data/`** — outside the repo, raw data per AGENTS.md.
- **`01_WORKSPACE/admin/hetzner_rental_k/`** — infrastructure kit (terraform + bootstrap); a security review of its own, out of scope for "the LLTB-1 pipeline audit." Noted as deferred.
- **Visual inspection HTML cheatsheets under `01_WORKSPACE/learning/reference/*.html`** — knowledge-base artifacts, non-code.
- **`00_SOURCE_ORIGINALS/LUNARVOID_Master_Plan_v5_Full_Synthesis.txt`** — READ-ONLY per project rule; the project-conventions skill already ingests it for scope decisions; not needed for an audit whose findings are code-anchored.
- **`01_WORKSPACE/plans/`** — roadmap drafts; non-code.
- **`01_WORKSPACE/notes/`** (besides this audit) — user-authored notes; non-code.
- **MCP server config in `opencode.json`** — third-party (`uvx arxiv-mcp-server`, `uvx zotero-mcp`); not project code.
- **`01_WORKSPACE/admin/orchestrator/tasks.yaml`** — not committed (would crash `pipeline.py:55` if missing); verified absent by audit.
