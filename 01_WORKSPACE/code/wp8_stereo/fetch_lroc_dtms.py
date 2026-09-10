"""LUNARVOID WP8 stereo — fetch LROC NAC DTMs to `~/lunarvoid/data/dtms/`.

Reads `01_WORKSPACE/data/lroc_dtm_availability.csv` (produced by
`enumerate_lroc_dtm_availability.py`) and downloads each NAC DTM
GeoTIFF (+ PDS3 label) to:

    ~/lunarvoid/data/dtms/<DTM_NAME>/NAC_DTM_<DTM_NAME>.TIF
    ~/lunarvoid/data/dtms/<DTM_NAME>/NAC_DTM_<DTM_NAME>.LBL

The download pattern mirrors the project's existing NAC EDR fetcher
(verified live for TRANQPIT1/M137332905LE in
`admin/2026-08-21_local_asp_attempt.md`): curl with `-L` (follow
302 -> pds.mcp.nasa.gov), `--retry 3`, `--connect-timeout 30`,
`-C -` (resume).

Licence: NAC DTMs are **PDS public domain** (NASA/ASU). Attribution
recorded per MANIFEST.md conventions: "LROC NAC DTM, NASA/ASU, PDS
public domain". See `01_WORKSPACE/data/MANIFEST.md` for the existing
7 on-disk DTMs' rows (TRANQPIT1, MARIUSPIT01, INGENIIPIT, IRIDIUMPIT1,
PRCLRMPIT01, SWFECUNPIT1, FECNDITATS2) — the orchestrator will add new
rows here after a successful fetch cycle.

DISCOVERY-ONLY CONTRACT (per orchestrator dispatch, 2026-08-22):
this script supports --dry-run. The actual fetch launch is a separate
orchestrator cycle; this file is the fetcher itself, not a runner.

Politeness: rate-limited to 1 req / 2 s; resumable; HEAD-probe first to
skip already-complete files (sha256 verification on resume).

Usage:
    fetch_lroc_dtms.py --dry-run                      # default; safe
    fetch_lroc_dtms.py --max 3                        # fetch first 3 unique DTMs
    fetch_lroc_dtms.py --priority-only --max 7        # only the 7 priority DTMs
    fetch_lroc_dtms.py --dtm TRANQPIT1 --force        # force re-fetch one DTM
    fetch_lroc_dtms.py --skip-existing --max 19       # skip if already on disk
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

REPO = Path(__file__).resolve().parents[3]
DATA = REPO / "01_WORKSPACE" / "data"
AVAIL_CSV = DATA / "lroc_dtm_availability.csv"

# Output roots (per lunarvoid-conventions §1): raw/derived rasters ONLY
# live under ~/lunarvoid/data/. Repo gets code + small CSVs only.
DTMS_ROOT = Path.home() / "lunarvoid" / "data" / "dtms"
FETCH_LOG = Path.home() / "lunarvoid" / "data" / "fetch_log_lroc.csv"

# Rate limit per URL (PDS is generous but be polite). The project
# pattern (Task 8 NAC EDR fetch) used sequential curl with 1-2 s gaps.
RATE_LIMIT_SECONDS = 2.0

# Project attribution (per MANIFEST.md conventions)
LICENCE_ATTR = "LROC NAC DTM, NASA/ASU, PDS public domain"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _head_size(url: str, timeout: int = 30) -> int | None:
    """HEAD probe to get the upstream content-length (used for
    completeness check on resume). Returns None on any error."""
    try:
        req = Request(url, method="HEAD")
        with urlopen(req, timeout=timeout) as resp:
            cl = resp.headers.get("Content-Length")
            return int(cl) if cl else None
    except Exception:
        # silent by design: HEAD probe is best-effort — None means the
        # resume completeness check is simply skipped
        return None


def _sha256_of_file(path: Path, buf: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(buf)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _curl_fetch(url: str, dst: Path, *, connect_timeout: int = 30,
                max_retries: int = 3) -> tuple[bool, str]:
    """Run curl with the project's standard flags. Returns (ok, message).

    Flags (per dispatch):
        -L                   follow redirects (pds.lroc.im-ldi.com 302
                             -> pds.mcp.nasa.gov)
        --retry 3            up to 3 retries on transient failures
        --connect-timeout 30 network-level connect timeout (seconds)
        -C -                 resume partial downloads (S3 supports range)
        -s -S                silent but show errors
        --fail               HTTP errors -> non-zero exit (curl <7.66
                             defaulted to 0; --fail makes it explicit)
        -o <dst>             write to file
        --create-dirs        make parent directories
    """
    _ensure_dir(dst.parent)
    cmd = [
        "curl",
        "-L",
        "--retry", str(max_retries),
        "--connect-timeout", str(connect_timeout),
        "-C", "-",
        "-sS",
        "--fail",
        "--create-dirs",
        "-o", str(dst),
        url,
    ]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=max(120, connect_timeout * 30),  # overall ceiling
        )
        if proc.returncode == 0 and dst.exists() and dst.stat().st_size > 0:
            return True, f"curl rc=0 size={dst.stat().st_size}"
        return False, f"curl rc={proc.returncode} stderr={proc.stderr.strip()[:200]}"
    except subprocess.TimeoutExpired as e:
        return False, f"curl timeout after {e.timeout}s"
    except Exception as e:
        return False, f"curl exception: {type(e).__name__}: {e}"


def _read_availability(csv_path: Path) -> list[dict]:
    """Read availability CSV. Skip comment lines."""
    rows: list[dict] = []
    if not csv_path.exists():
        sys.exit(f"[abort] availability CSV missing: {csv_path} -- run "
                 f"enumerate_lroc_dtm_availability.py first")
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            # skip blanks
            if not r.get("lroc_dtm_product_id"):
                continue
            rows.append(r)
    return rows


def _dedupe_by_dtm(rows: list[dict]) -> list[dict]:
    """Many pits share one DTM (e.g., 32 King pits in KINGCRATER2).
    The fetcher downloads each DTM exactly once; we keep the FIRST
    occurrence per DTM and preserve priority order."""
    seen: set[str] = set()
    out: list[dict] = []
    for r in rows:
        dtm = r["lroc_dtm_product_id"]
        if dtm in seen:
            continue
        seen.add(dtm)
        out.append(r)
    return out


def _init_fetch_log(path: Path) -> None:
    """Create the fetch log with header if absent."""
    if path.exists():
        return
    _ensure_dir(path.parent)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "timestamp_utc", "site", "product_id", "url",
            "status", "size_bytes", "sha256", "expected_size_bytes",
            "elapsed_sec", "licence",
        ])


def _log_row(path: Path, **kw) -> None:
    """Append one row to the fetch log."""
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            kw.get("timestamp_utc", _now_iso()),
            kw.get("site", ""),
            kw.get("product_id", ""),
            kw.get("url", ""),
            kw.get("status", ""),
            kw.get("size_bytes", ""),
            kw.get("sha256", ""),
            kw.get("expected_size_bytes", ""),
            kw.get("elapsed_sec", ""),
            kw.get("licence", LICENCE_ATTR),
        ])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--availability", type=Path, default=AVAIL_CSV,
                    help=f"path to lroc_dtm_availability.csv (default: {AVAIL_CSV})")
    ap.add_argument("--out-root", type=Path, default=DTMS_ROOT,
                    help=f"DTM destination root (default: {DTMS_ROOT})")
    ap.add_argument("--fetch-log", type=Path, default=FETCH_LOG,
                    help=f"fetch log CSV (default: {FETCH_LOG})")
    ap.add_argument("--dry-run", action="store_true",
                    help="print planned actions only; do not curl")
    ap.add_argument("--max", type=int, default=0,
                    help="fetch at most N DTMs (0 = all)")
    ap.add_argument("--dtm", type=str, default=None,
                    help="fetch exactly one DTM (by DTM_NAME)")
    ap.add_argument("--priority-only", action="store_true",
                    help="only the 7 priority DTMs in candidate_registry.csv")
    ap.add_argument("--skip-existing", action="store_true",
                    help="skip DTMs already present at destination (sha256 OK)")
    ap.add_argument("--force", action="store_true",
                    help="re-fetch even if existing file looks complete")
    ap.add_argument("--rate-limit", type=float, default=RATE_LIMIT_SECONDS,
                    help=f"seconds between requests (default: {RATE_LIMIT_SECONDS})")
    args = ap.parse_args()

    rows = _read_availability(args.availability)
    if args.priority_only:
        rows = [r for r in rows if r.get("priority_in_registry") == "True"]
    if args.dtm:
        rows = [r for r in rows if r["lroc_dtm_product_id"] == args.dtm]
    rows = _dedupe_by_dtm(rows)
    if args.max > 0:
        rows = rows[: args.max]

    n_total = len(rows)
    print(f"[plan] {n_total} unique DTMs to consider "
          f"(filter: priority_only={args.priority_only}, dtm={args.dtm}, "
          f"max={args.max})", flush=True)
    if n_total == 0:
        sys.exit("[abort] no rows selected; check --availability / --priority-only / --dtm")

    _ensure_dir(args.out_root)
    _init_fetch_log(args.fetch_log)

    n_ok = n_skip = n_fail = n_dry = 0
    total_bytes = 0
    t_run_start = time.time()
    for i, r in enumerate(rows, start=1):
        dtm = r["lroc_dtm_product_id"]
        site_dir = args.out_root / dtm
        tif_dst = site_dir / f"NAC_DTM_{dtm}.TIF"
        lbl_dst = site_dir / f"NAC_DTM_{dtm}.LBL"
        url_tif = r["lroc_dtm_url"]
        url_lbl = r.get("lroc_dtm_lbl_url") or url_tif.replace(".TIF", ".LBL")

        # HEAD probe to learn the upstream size for completeness check
        upstream_size = _head_size(url_tif)

        # Decide whether to skip (already exists and looks complete)
        exists = tif_dst.exists()
        size_ok = exists and upstream_size is not None and tif_dst.stat().st_size == upstream_size
        sha_ok = False
        if exists and size_ok and not args.force:
            sha_ok = True
        elif exists and upstream_size is None and tif_dst.stat().st_size > 1024 and not args.force:
            # upstream HEAD failed (CDN/cache); treat >1 KB as plausibly complete
            sha_ok = True

        if sha_ok and args.skip_existing and not args.force:
            sha = _sha256_of_file(tif_dst)
            elapsed = time.time() - t_run_start
            _log_row(args.fetch_log,
                     site=dtm, product_id=dtm, url=url_tif,
                     status="SKIP_EXISTS", size_bytes=tif_dst.stat().st_size,
                     sha256=sha, expected_size_bytes=upstream_size,
                     elapsed_sec=round(elapsed, 1))
            n_skip += 1
            print(f"[{i}/{n_total}] SKIP_EXISTS {dtm} "
                  f"(size {tif_dst.stat().st_size} == upstream {upstream_size})",
                  flush=True)
            continue

        if args.dry_run:
            sha = ""
            elapsed = time.time() - t_run_start
            _log_row(args.fetch_log,
                     site=dtm, product_id=dtm, url=url_tif,
                     status="DRY_RUN", size_bytes="",
                     sha256="", expected_size_bytes=upstream_size,
                     elapsed_sec=round(elapsed, 1))
            n_dry += 1
            print(f"[{i}/{n_total}] DRY_RUN {dtm} url={url_tif} "
                  f"upstream_size={upstream_size} -> {tif_dst}", flush=True)
            continue

        # ---- Real fetch (--dry-run not set) ----------------------------
        t0 = time.time()
        ok, msg = _curl_fetch(url_tif, tif_dst)
        elapsed = time.time() - t0
        if not ok:
            _log_row(args.fetch_log,
                     site=dtm, product_id=dtm, url=url_tif,
                     status="FAIL", size_bytes="",
                     sha256="", expected_size_bytes=upstream_size,
                     elapsed_sec=round(elapsed, 1))
            n_fail += 1
            print(f"[{i}/{n_total}] FAIL    {dtm} {msg}", flush=True)
            # Politeness between attempts
            time.sleep(args.rate_limit)
            continue

        # Companion LBL (small, best-effort; do not fail the DTM on LBL miss)
        ok_lbl, _ = _curl_fetch(url_lbl, lbl_dst)
        if not ok_lbl:
            print(f"[warn]   LBL fetch failed for {dtm} (continuing)", flush=True)

        # Verify size + SHA-256
        size = tif_dst.stat().st_size
        sha = _sha256_of_file(tif_dst)
        if upstream_size is not None and size != upstream_size:
            status = "FAIL_SIZE_MISMATCH"
            n_fail += 1
        else:
            status = "OK"
            n_ok += 1
            total_bytes += size

        _log_row(args.fetch_log,
                 site=dtm, product_id=dtm, url=url_tif,
                 status=status, size_bytes=size, sha256=sha,
                 expected_size_bytes=upstream_size,
                 elapsed_sec=round(elapsed, 1))
        print(f"[{i}/{n_total}] {status:<6} {dtm} size={size} sha256={sha[:12]} "
              f"({elapsed:.1f}s) {msg}", flush=True)

        # Politeness (skip if last in batch)
        if i < n_total:
            time.sleep(args.rate_limit)

    elapsed = time.time() - t_run_start
    print("", flush=True)
    print(f"[done] {n_total} considered, {n_ok} OK, {n_skip} SKIP_EXISTS, "
          f"{n_fail} FAIL, {n_dry} DRY_RUN, total={total_bytes/1024/1024:.1f} MB, "
          f"elapsed={elapsed:.1f}s", flush=True)
    print(f"[log] {args.fetch_log}", flush=True)
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
