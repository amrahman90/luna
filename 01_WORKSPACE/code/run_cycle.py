#!/usr/bin/env python3
"""run_cycle.py — one-command chain for the CURRENT lunar inference cycle.

Task C6 (Next-Level Plan v2), per ADR D6 "scripts-not-package" (ADJ-1):
thin SUBPROCESS orchestration only — this module imports NONE of the
chained scripts. Every step is an exact venv-python invocation of an
existing script, re-runnable by hand from the printed command line.

The chain, as it exists today (verified against
data/outputs/wp2_sag/transfer/METHODS.md + each script's argparse):

  site_check   (internal) resolve + fail-fast the DTM for <SITE>
               (krigcorr preferred, raw fallback — same rule as
               score_raster_gen.dtm_source).
  floors       wp0_kriging/per_dtm_floors.py
               AUTO-SKIP when <SITE> already has a row in
               data/outputs/wp0_kriging/per_dtm_floors.csv (the value
               is frozen). When the row is missing the script is run
               UNFILTERED (full batch): its `--dtm` filter REWRITES the
               canonical CSV with only the filtered rows — a site-scoped
               run would TRUNCATE it (known gotcha, do not "fix" here).
  score        wp2_sag/transfer/score_raster_gen.py --dtms <SITE>
               AUTO-SKIP when <SITE> already has >=1 cached score
               raster in EITHER root transfer_apply.py discovers
               (~/lunarvoid/data/outputs/wp2_sag/score_rasters/<SITE>/
               or the legacy 01_WORKSPACE/data/outputs/wp2_sag/<sub>/
               cache). Re-generating for a legacy-cached site (e.g.
               TRANQPIT1, MTP 5 m) would SHADOW the frozen raster the
               registry rows reproduce from — Cycles 1-2 practice is
               generation for new sites only.
  transfer     wp2_sag/transfer/transfer_apply.py (UNFILTERED)
               Frozen I15 calibration -> candidate rows + registry
               append (idempotent, dedup by candidate_id) +
               transfer_summary.json. Run unfiltered because a
               site-scoped `--dtms` run REWRITES the canonical
               transfer_summary.json to a single-site scope banner
               (audit LOW-15 clobber gotcha); the registry/summary
               layer is global-by-design, append-only.
  accounting   wp2_sag/transfer/unique_accounting.py
               Registry-wide FP re-accounting (row-based regression +
               unique-feature B1 groups). Reads the canonical registry
               + transfer_summary; exits 2 on reconciliation failure.

REGISTRY DISCIPLINE: registry updates beyond transfer_apply.py's
idempotent append (skeptic annotations, tier-B/A promotion, repairs)
are MANUAL by design (append-only discipline) and are NOT chained.
If the cycle ends at outputs + zero new registry rows on a re-run,
that is correct behaviour.

FROZEN-EVIDENCE GUARD (C6-retry): the chained scripts write canonical
repo paths BY DESIGN — transfer_apply.py regenerates
transfer_summary.json (fresh runtime_s => new bytes every run) and
rewrites candidate_registry.csv when new rows append;
unique_accounting.py rewrites unique_accounting_<date>.json (it
embeds transfer_summary's md5). run_cycle treats those files, the
frozen calibration_transqpit1.json, and wp5_fusion/*.json as FROZEN
evidence: before the first step they are snapshotted to
<out-root>/run_cycle_guard/<SITE>_<ts>/ and sha256'd; after EVERY
step they are re-hashed and ANY change is restored byte-identical
from the snapshot, with a prominent warning naming the offending
step and an incident recorded in the run JSON
(frozen_writes_blocked: [{file, step, action: restored}]). The run's
own results live ONLY in the run JSON; genuinely-intended registry
appends stay recoverable from the snapshot dir for manual review.

--cc-filter is accepted for CLI compatibility with the detector
family, but NO lunar-chain step consumes it today (task C3 wired
--cc-filter into the ANALOG sag_detect.py only). on/auto print a
warning and are recorded in the run log; nothing is passed on.

Usage:
  ~/lunarvoid/venv/bin/python 01_WORKSPACE/code/run_cycle.py TRANQPIT1 \
      [--dtm-path PATH] [--cc-filter off|on|auto]
      [--out-root ~/lunarvoid/data/outputs] [--dry-run]
      [--skip-steps floors,score,transfer,accounting]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CODE_DIR = Path(__file__).resolve().parent
RAW = Path.home() / "lunarvoid" / "data"

VENV_DEFAULT = Path.home() / "lunarvoid" / "venv" / "bin" / "python"
FLOORS_CSV = REPO / "01_WORKSPACE" / "data" / "outputs" / "wp0_kriging" / "per_dtm_floors.csv"
LEGACY_SCORE_ROOT = REPO / "01_WORKSPACE" / "data" / "outputs" / "wp2_sag"
RUN_LOG_DIR = REPO / "01_WORKSPACE" / "data" / "outputs" / "run_cycle"

STEPS = ("floors", "score", "transfer", "accounting")


# --------------------------------------------------------------------------
# helpers (read-only filesystem checks — no chain-internal imports)
# --------------------------------------------------------------------------

def resolve_venv_python() -> Path:
    """Venv python: $LUNARVOID_VENV_PYTHON override, else the Tier-0 venv.

    Never falls back to sys.executable implicitly — the sandbox python
    lacks numpy/rasterio (conventions §7), so a silent fallback would
    produce a confusing ImportError mid-chain instead of a clear message.
    """
    env = os.environ.get("LUNARVOID_VENV_PYTHON")
    py = Path(env).expanduser() if env else VENV_DEFAULT
    if not py.is_file():
        sys.exit(
            f"[run_cycle] venv python not found: {py}\n"
            f"             set LUNARVOID_VENV_PYTHON or create the Tier-0 venv."
        )
    return py


def dtm_source(dtm_name: str) -> Path | None:
    """DTM path (krigcorr preferred, raw fallback) — mirrors
    score_raster_gen.dtm_source() WITHOUT importing it."""
    krig = RAW / "outputs" / dtm_name / f"NAC_DTM_{dtm_name}_krigcorr.tif"
    if krig.exists():
        return krig
    raw = RAW / "dtms" / dtm_name / f"NAC_DTM_{dtm_name}.TIF"
    return raw if raw.exists() else None


def floors_row_present(site: str) -> bool:
    """True if <site> has a dtm_name row in per_dtm_floors.csv."""
    if not FLOORS_CSV.exists():
        return False
    with open(FLOORS_CSV, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("dtm_name") == site:
                return True
    return False


def cached_score_rasters(site: str, score_out_root: Path) -> list[str]:
    """Score rasters for <site> in EITHER root transfer_apply discovers.

    New root : <score_out_root>/<SITE>/score_<rung>m.tif
    Legacy   : 01_WORKSPACE/data/outputs/wp2_sag/<sub>/<SITE>_<rung>m_score.tif
    """
    hits: list[str] = []
    new_dir = score_out_root / site
    if new_dir.is_dir():
        hits += sorted(str(p) for p in new_dir.glob("score_*m.tif"))
    if LEGACY_SCORE_ROOT.is_dir():
        for sub in sorted(LEGACY_SCORE_ROOT.iterdir()):
            if sub.is_dir():
                hits += sorted(str(p) for p in sub.glob(f"{site}_*m_score.tif"))
    return hits


def child_env() -> dict[str, str]:
    """Env for chained scripts: PYTHONPATH=01_WORKSPACE/code prepended.

    The scripts self-insert most of their sys.path entries (D6 pattern),
    but bare-module imports (`from _rebin import ...`, `from wp0_kriging
    import noise_floor`) still rely on code/ and the script's own dir
    being importable — the documented CWD-luck constraint (ADR D6).
    We make that explicit: cwd=code/ + PYTHONPATH=code/ for every child.
    """
    env = dict(os.environ)
    parts = [str(CODE_DIR)]
    for p in env.get("PYTHONPATH", "").split(os.pathsep):
        if p and p not in parts:
            parts.append(p)
    env["PYTHONPATH"] = os.pathsep.join(parts)
    return env


# --------------------------------------------------------------------------
# frozen-evidence guard (C6-retry)
# --------------------------------------------------------------------------

# Canonical repo artifacts the chain can touch and that run_cycle
# treats as FROZEN evidence: a cycle must leave them byte-identical.
FROZEN_EXACT: tuple[Path, ...] = (
    REPO / "01_WORKSPACE" / "data" / "candidate_registry.csv",
    REPO / "01_WORKSPACE" / "data" / "outputs" / "wp2_sag" / "transfer"
         / "transfer_summary.json",
    REPO / "01_WORKSPACE" / "data" / "outputs" / "wp2_sag" / "transfer"
         / "calibration_transqpit1.json",
)
# Globbed families: every existing match is frozen, and files APPEARING
# under these globs mid-run (e.g. a rolled unique_accounting_<date>.json)
# are treated as canonical writes too (restored = deleted).
FROZEN_GLOBS: tuple[tuple[Path, str], ...] = (
    (REPO / "01_WORKSPACE" / "data" / "outputs" / "wp2_sag",
     "unique_accounting_*.json"),
    (REPO / "01_WORKSPACE" / "data" / "outputs" / "wp5_fusion", "*.json"),
)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def frozen_targets() -> list[dict]:
    """Resolve the frozen set NOW (fresh each check, so new glob matches
    that appear mid-run are caught): [{key: repo-relative, path}]."""
    targets = [{"key": str(p.relative_to(REPO)), "path": p}
               for p in FROZEN_EXACT]
    for parent, pat in FROZEN_GLOBS:
        targets += [{"key": str(p.relative_to(REPO)), "path": p}
                    for p in sorted(parent.glob(pat))]
    return targets


class FrozenArtifactGuard:
    """Snapshot + sha256 the frozen evidence; restore on ANY change.

    Why (C6-retry incident, 2026-09-10): a real run let
    transfer_apply.py and unique_accounting.py overwrite two frozen
    evidence files at their canonical paths — transfer_summary.json is
    regenerated with a fresh runtime_s (new bytes every run) and the
    accounting JSON embeds transfer_summary's md5. run_cycle now
    restores them byte-identical from a pre-run snapshot and records
    every blocked write in the run JSON (frozen_writes_blocked).
    """

    def __init__(self, site: str, out_root: Path) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.snapshot_dir = (Path(out_root).expanduser()
                             / "run_cycle_guard" / f"{site}_{ts}")
        self.targets: dict[str, Path] = {}
        self.baseline: dict[str, str | None] = {}  # key -> sha | None(missing)
        self.records: list[dict] = []               # per-file run-JSON rows
        self.incidents: list[dict] = []             # frozen_writes_blocked

    # -- setup -----------------------------------------------------------

    def snapshot(self) -> None:
        for t in frozen_targets():
            key, path = t["key"], t["path"]
            self.targets[key] = path
            self.baseline[key] = None
            if path.exists():
                dest = self.snapshot_dir / key
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dest)
                self.baseline[key] = sha256_file(path)
            self.records.append({"file": key,
                                 "sha256_before": self.baseline[key],
                                 "sha256_after": None,
                                 "written_by_step": None,
                                 "restored": False})
        n = sum(1 for v in self.baseline.values() if v is not None)
        print(f"[frozen-guard] snapshotted {n} frozen artifact(s) "
              f"(+{len(self.baseline) - n} absent) -> {self.snapshot_dir}",
              flush=True)

    # -- checking ---------------------------------------------------------

    def check(self, step: str) -> None:
        """Re-hash the frozen set after `step`; restore any change.

        Fresh glob resolution also catches files CREATED under a frozen
        glob during the run (restored = deleted; that too is a canonical
        write).
        """
        current = {t["key"]: t["path"] for t in frozen_targets()}
        # 1) tracked targets whose bytes changed (or were deleted)
        for key, base in self.baseline.items():
            path = self.targets[key]
            after = sha256_file(path) if path.exists() else None
            rec = next(r for r in self.records if r["file"] == key)
            rec["sha256_after"] = after
            if after != base:
                rec["written_by_step"] = step
                rec["restored"] = True
                self._restore(key, path, base, step)
        # 2) new files matching a frozen glob that were not in baseline
        for key, path in current.items():
            if key not in self.baseline:
                self.baseline[key] = None
                self.targets[key] = path
                self.records.append({"file": key, "sha256_before": None,
                                     "sha256_after": sha256_file(path),
                                     "written_by_step": step,
                                     "restored": True})
                self._restore(key, path, None, step)

    def _restore(self, key: str, path: Path, base: str | None,
                 step: str) -> None:
        if base is None:  # did not exist before the run -> remove it again
            action, how = "restored", "deleted (file was created during the run)"
        else:
            action, how = "restored", "restored byte-identical from snapshot"
        try:
            if base is None:
                path.unlink(missing_ok=True)
            else:
                shutil.copy2(self.snapshot_dir / key, path)
            self.incidents.append({"file": key, "step": step, "action": action})
            msg = (f"\n[run_cycle] *** FROZEN-EVIDENCE WRITE BLOCKED ***\n"
                   f"    step '{step}' wrote a canonical frozen artifact:\n"
                   f"      {key}\n"
                   f"    {how}:\n      {self.snapshot_dir / key}\n"
                   f"    incident recorded in run JSON (frozen_writes_blocked).\n")
            print(msg, flush=True)
            print(msg, file=sys.stderr, flush=True)
        except Exception as e:  # never mask the cycle result
            self.incidents.append({"file": key, "step": step,
                                   "action": f"restore-failed: {e}"})
            print(f"[run_cycle] *** FROZEN-GUARD RESTORE FAILED *** "
                  f"{key} ({e}) — reconcile manually against "
                  f"{self.snapshot_dir / key}", file=sys.stderr, flush=True)

    # -- reporting ----------------------------------------------------------

    def log_fields(self) -> dict:
        ok = True
        for key, base in self.baseline.items():
            path = self.targets[key]
            now = sha256_file(path) if path.exists() else None
            if now != base:
                ok = False
        return {
            "frozen_guard": {
                "snapshot_dir": str(self.snapshot_dir),
                "files": self.records,
                "all_byte_identical_after_run": ok,
            },
            "frozen_writes_blocked": self.incidents,
        }


# --------------------------------------------------------------------------
# plan construction
# --------------------------------------------------------------------------

def build_plan(site: str, args: argparse.Namespace) -> list[dict]:
    """One entry per step: {name, action: run|skip-user|skip-auto,
    cmd (list) | reason (str), script (path)}."""
    py = str(args.venv_python)
    score_out_root = Path(args.out_root).expanduser() / "wp2_sag" / "score_rasters"
    plan: list[dict] = []

    # --- site_check (internal, cannot be skipped) ---
    if args.dtm_path:
        given = Path(args.dtm_path).expanduser()
        if not given.is_file():
            sys.exit(f"[run_cycle] --dtm-path does not exist: {given}")
        resolved = dtm_source(site)
        note = ""
        if resolved is not None and given.resolve() != resolved.resolve():
            note = (f"\n[run_cycle] NOTE: chained scripts resolve the DTM by "
                    f"site-name convention and will use:\n             {resolved}\n"
                    f"             --dtm-path is validated + logged only "
                    f"(no chained script accepts an explicit DTM path).")
        print(f"[site_check] {site}: DTM at {given}{note}")
    else:
        resolved = dtm_source(site)
        if resolved is None:
            sys.exit(
                f"[run_cycle] no DTM for site '{site}' under\n"
                f"             {RAW / 'outputs' / site}/ (krigcorr) or\n"
                f"             {RAW / 'dtms' / site}/ (raw NAC DTM).\n"
                f"             Pass --dtm-path or check the site name."
            )
        print(f"[site_check] {site}: DTM at {resolved}")

    # --- floors ---
    if "floors" in args.skip_steps:
        plan.append({"name": "floors", "action": "skip-user",
                     "reason": "skipped via --skip-steps",
                     "script": CODE_DIR / "wp0_kriging" / "per_dtm_floors.py"})
    elif floors_row_present(site):
        plan.append({"name": "floors", "action": "skip-auto",
                     "reason": (f"{site} already has a row in {FLOORS_CSV.name} "
                                f"(frozen P3.1a value); a --dtm-filtered re-run "
                                f"would TRUNCATE the canonical CSV"),
                     "script": CODE_DIR / "wp0_kriging" / "per_dtm_floors.py"})
    else:
        plan.append({"name": "floors", "action": "run",
                     "cmd": [py, str(CODE_DIR / "wp0_kriging" / "per_dtm_floors.py")],
                     "script": CODE_DIR / "wp0_kriging" / "per_dtm_floors.py"})

    # --- score ---
    gen = CODE_DIR / "wp2_sag" / "transfer" / "score_raster_gen.py"
    cached = cached_score_rasters(site, score_out_root)
    if "score" in args.skip_steps:
        plan.append({"name": "score", "action": "skip-user",
                     "reason": "skipped via --skip-steps", "script": gen})
    elif cached:
        plan.append({"name": "score", "action": "skip-auto",
                     "reason": (f"{len(cached)} cached score raster(s) already "
                                f"discovered by transfer_apply "
                                f"({', '.join(Path(c).name for c in cached[:4])}"
                                f"{' …' if len(cached) > 4 else ''}); regenerating "
                                f"would shadow the frozen cache the registry "
                                f"rows reproduce from"),
                     "script": gen})
    else:
        plan.append({"name": "score", "action": "run",
                     "cmd": [py, str(gen), "--dtms", site,
                             "--rungs", "2", "4", "5",
                             "--outdir", str(score_out_root)],
                     "script": gen})

    # --- transfer (always unfiltered — see module docstring) ---
    plan.append({"name": "transfer",
                 "action": "skip-user" if "transfer" in args.skip_steps else "run",
                 "cmd": [py, str(CODE_DIR / "wp2_sag" / "transfer" / "transfer_apply.py")],
                 "reason": "skipped via --skip-steps",
                 "script": CODE_DIR / "wp2_sag" / "transfer" / "transfer_apply.py"})

    # --- accounting ---
    plan.append({"name": "accounting",
                 "action": "skip-user" if "accounting" in args.skip_steps else "run",
                 "cmd": [py, str(CODE_DIR / "wp2_sag" / "transfer" / "unique_accounting.py")],
                 "reason": "skipped via --skip-steps",
                 "script": CODE_DIR / "wp2_sag" / "transfer" / "unique_accounting.py"})

    return plan


# --------------------------------------------------------------------------
# execution
# --------------------------------------------------------------------------

def fmt_elapsed(s: float) -> str:
    return f"{s / 60.0:.0f}m{s % 60.0:04.1f}s" if s >= 60 else f"{s:.1f}s"


def run_plan(plan: list[dict], args: argparse.Namespace) -> int:
    env = child_env()
    guard = FrozenArtifactGuard(args.site, Path(args.out_root))
    guard.snapshot()
    log: dict = {
        "site": args.site, "utc": datetime.now(timezone.utc).isoformat(),
        "dry_run": bool(args.dry_run), "cc_filter": args.cc_filter,
        "skip_steps": sorted(args.skip_steps), "steps": [],
    }
    if args.cc_filter != "off":
        print(f"[run_cycle] WARNING: --cc-filter {args.cc_filter} has NO consumer "
              f"in the lunar chain today (C3 wired it into the ANALOG "
              f"sag_detect.py only); recorded in the run log, not passed on.",
              flush=True)

    for i, step in enumerate(plan, 1):
        if step["action"] == "run":
            cmd_str = shlex.join(step["cmd"])
            print(f"\n=== [{i}/{len(plan)}] {step['name']}: START ===",
                  flush=True)
            print(f"$ {cmd_str}", flush=True)
            t0 = time.time()
            proc = subprocess.run(step["cmd"], cwd=str(CODE_DIR), env=env)
            guard.check(step["name"])  # attribute canonical writes to this step
            dt = time.time() - t0
            log["steps"].append({"name": step["name"], "action": "run",
                                 "command": cmd_str,
                                 "returncode": proc.returncode,
                                 "elapsed_s": round(dt, 1)})
            if proc.returncode != 0:
                print(f"\n[run_cycle] FAILED at step '{step['name']}' "
                      f"(exit {proc.returncode}) after {fmt_elapsed(dt)}.",
                      file=sys.stderr)
                print(f"[run_cycle] Re-run it manually with:\n"
                      f"  (cd {CODE_DIR} && {cmd_str})",
                      file=sys.stderr)
                guard.check("post-run")
                log.update(guard.log_fields())
                write_log(log)
                return proc.returncode
            print(f"=== [{i}/{len(plan)}] {step['name']}: OK "
                  f"({fmt_elapsed(dt)}) ===", flush=True)
        else:
            why = ("--skip-steps" if step["action"] == "skip-user" else "auto")
            print(f"\n=== [{i}/{len(plan)}] {step['name']}: SKIP ({why}) ===\n"
                  f"    {step['reason']}", flush=True)
            log["steps"].append({"name": step["name"], "action": step["action"],
                                 "reason": step["reason"]})

    guard.check("post-run")  # final re-hash: nothing may differ from baseline
    log.update(guard.log_fields())
    print(f"\n[run_cycle] cycle complete for {args.site}: "
          f"{sum(1 for s in log['steps'] if s['action'] == 'run')} run / "
          f"{sum(1 for s in log['steps'] if s['action'] != 'run')} skipped.",
          flush=True)
    if log["frozen_writes_blocked"]:
        print(f"[run_cycle] frozen-evidence guard blocked "
              f"{len(log['frozen_writes_blocked'])} canonical write(s): "
              f"{', '.join(sorted({i['file'] for i in log['frozen_writes_blocked']}))} "
              f"— all restored byte-identical (see frozen_writes_blocked in the run log).",
              flush=True)
    else:
        print("[run_cycle] frozen-evidence guard: no canonical writes; "
              "all frozen artifacts byte-identical.", flush=True)
    print("[run_cycle] registry annotations/promotions stay MANUAL by design; "
          "new rows (if any) were appended by transfer_apply.py only.",
          flush=True)
    write_log(log)
    return 0


def write_log(log: dict) -> None:
    if log.get("dry_run"):
        return  # no run log for --dry-run (run_plan is not called then;
                # guard kept for defensive use)
    try:
        RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        p = RUN_LOG_DIR / f"{log['site']}_{ts}.json"
        p.write_text(json.dumps(log, indent=2) + "\n")
        try:
            shown = str(p.relative_to(REPO))
        except ValueError:  # log dir redirected outside the repo
            shown = str(p)
        print(f"[run_cycle] run log -> {shown}", flush=True)
    except Exception as e:  # logging must never mask the cycle result
        print(f"[run_cycle] run-log write failed (non-fatal): {e}", flush=True)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="run_cycle.py",
        description=(
            "One-command chain of the CURRENT lunar inference cycle for one "
            "DTM site (task C6, ADR D6 scripts-not-package: thin subprocess "
            "orchestration, no imports of the chained scripts).\n\n"
            "Steps: site_check (internal) -> floors (per_dtm_floors.py, "
            "auto-skip when frozen) -> score (score_raster_gen.py, auto-skip "
            "when cached) -> transfer (transfer_apply.py, UNFILTERED) -> "
            "accounting (unique_accounting.py).\n\n"
            "REGISTRY DISCIPLINE: transfer_apply.py appends new registry rows "
            "idempotently (dedup by candidate_id). Skeptic annotations, "
            "tier-B/A promotions and repairs are MANUAL by design and are "
            "NOT chained. A re-run that appends zero rows is correct.\n\n"
            "GOTCHAS (do NOT 'fix' these in the chained scripts):\n"
            "  - per_dtm_floors.py --dtm FILTER TRUNCATES the canonical "
            "per_dtm_floors.csv, so run_cycle only ever runs it unfiltered;\n"
            "  - transfer_apply.py --dtms SITE would clobber the canonical "
            "transfer_summary.json scope banner, so the transfer step runs "
            "unfiltered (registry/summary layer is global, append-only);\n"
            "  - transfer_apply.py + unique_accounting.py REWRITE canonical "
            "frozen evidence (transfer_summary.json with a fresh runtime_s, "
            "unique_accounting_<date>.json embedding its md5, the registry "
            "on append) — the C6-retry guard snapshots those files (plus "
            "calibration_transqpit1.json and wp5_fusion/*.json) to "
            "<out-root>/run_cycle_guard/ before step 1 and restores them "
            "byte-identical after ANY step that touches them, recording "
            "incidents in the run JSON (frozen_writes_blocked);\n"
            "  - --cc-filter has NO lunar consumer today (C3 wired it into "
            "the analog sag_detect.py only); on/auto warn + log, pass-on "
            "nothing.\n\n"
            "Outputs: score rasters under "
            "~/lunarvoid/data/outputs/wp2_sag/score_rasters/ (via --out-root); "
            "per_dtm_floors.csv, transfer_summary.json, registry appends and "
            "the accounting JSON go to their fixed canonical repo paths by "
            "the chained scripts' own design."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("site",
                    help="DTM site name, e.g. TRANQPIT1 (directory under "
                         "~/lunarvoid/data/dtms/<SITE>/ holding "
                         "NAC_DTM_<SITE>.TIF)")
    ap.add_argument("--dtm-path", default=None, metavar="PATH",
                    help="explicit DTM GeoTIFF (validated + recorded; the "
                         "chained scripts still resolve the source by "
                         "site-name convention)")
    ap.add_argument("--cc-filter", choices=["off", "on", "auto"], default="off",
                    help="CC post-filter mode (default off). NO lunar-chain "
                         "step consumes it today — see GOTCHAS above.")
    ap.add_argument("--out-root", default=str(RAW / "outputs"), metavar="PATH",
                    help="root for derived score rasters "
                         "(default %(default)s); only the score step is "
                         "affected — the other steps write to fixed "
                         "canonical paths")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the exact subprocess command graph without "
                         "executing anything")
    ap.add_argument("--skip-steps", default="", metavar="step1,step2",
                    help=f"comma-separated steps to skip "
                         f"({', '.join(STEPS)})")
    args = ap.parse_args(argv)

    skip = {s.strip().lower() for s in args.skip_steps.split(",") if s.strip()}
    unknown = skip - set(STEPS)
    if unknown:
        ap.error(f"unknown --skip-steps {sorted(unknown)}; valid: {STEPS}")
    args.skip_steps = skip
    args.site = args.site.strip()
    args.venv_python = resolve_venv_python()

    plan = build_plan(args.site, args)

    if args.dry_run:
        print(f"[dry-run] cycle for {args.site} "
              f"(nothing will be executed):", flush=True)
        for i, step in enumerate(plan, 1):
            if step["action"] == "run":
                print(f"  [{i}/{len(plan)}] {step['name']:10s} RUN     "
                      f"$ {shlex.join(step['cmd'])}")
            else:
                print(f"  [{i}/{len(plan)}] {step['name']:10s} "
                      f"SKIP-{step['action'].removeprefix('skip-'):4s} "
                      f"({step['reason']})")
        return 0

    return run_plan(plan, args)


if __name__ == "__main__":
    sys.exit(main())
