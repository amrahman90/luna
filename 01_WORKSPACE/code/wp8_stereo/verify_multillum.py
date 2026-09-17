"""LUNARVOID WP8 stereo / Step 19.1b — independent post-hoc verification
of the Phase C multi-illumination EDR fetch.

The original multillum_fetch.py run completed (all 28 logged OK), but its
skip-existing logic only checks >1 MiB + non-HTML, which can bless
TRUNCATED files (observed live: PRCLRMPIT01/M1450672896LE was 79 MB on
disk while logged OK at 264 MB mid-run).  This script verifies every CSV
row against the authoritative remote Content-Length:

  per file:  HEAD (curl -sIL, 2 s politeness) -> remote length
             local exists, size == remote length, size > 10 MB,
             first 16 bytes not <!DOCTYPE/<html
             sha256 recomputed and compared to the CSV value

  on mismatch: one repair attempt (curl -L --retry 3 -C -; fresh start
             if local is HTML-headed or oversized), then re-verify;
             still bad -> recorded as FAILED in the summary + log.

Finally rewrites the selection CSV in place (same rows, same column
order) with verified size_bytes + sha256, and appends per-file
VERIFY_* rows to ~/lunarvoid/data/edr/multillum/fetch_log.csv.

Usage:
    verify_multillum.py            # verify + repair + enrich CSV
    verify_multillum.py --noverify-sha   # skip sha recompute (not default)

Output: 01_WORKSPACE/data/wp8_stereo/multillum_verify_2026-09-14.json
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from multillum_fetch import (  # noqa: E402
    UA, EDR_ROOT, FETCH_LOG, SELECTION_CSV, LICENCE_ATTR,
    _sha256_of_file, _first_bytes_html, _disk_free_gb, log_row,
)

SUMMARY_JSON = SELECTION_CSV.parent / "multillum_verify_2026-09-14.json"
RATE_S = 2.0            # politeness: 1 request / 2 s (dispatch mandate)
MIN_BYTES = 10 * 1024 * 1024   # dispatch: size must be > 10 MB
DISK_FLOOR_GB = 45.0
_last = [0.0]


def _polite() -> None:
    dt = time.time() - _last[0]
    if dt < RATE_S:
        time.sleep(RATE_S - dt)
    _last[0] = time.time()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def remote_length(url: str) -> int | None:
    """Content-Length of the FINAL redirect target (HEAD; range-GET
    fallback if the server rejects HEAD)."""
    _polite()
    proc = subprocess.run(
        ["curl", "-sIL", "-A", UA, "--connect-timeout", "30", url],
        capture_output=True, text=True, timeout=120)
    lengths = [int(m) for m in
               re.findall(r"(?i)^content-length:\s*(\d+)\s*$",
                          proc.stdout, re.M)]
    if proc.returncode == 0 and lengths:
        return lengths[-1]
    # fallback: 1-byte range GET, parse Content-Range total
    _polite()
    proc = subprocess.run(
        ["curl", "-sL", "-r", "0-0", "-A", UA, "--connect-timeout", "30",
         "-o", "/dev/null", "-D", "-", url],
        capture_output=True, text=True, timeout=120)
    m = re.search(r"(?i)^content-range:\s*bytes\s+0-0/(\d+)\s*$",
                  proc.stdout, re.M)
    if m:
        return int(m.group(1))
    lengths = [int(x) for x in
               re.findall(r"(?i)^content-length:\s*(\d+)\s*$",
                          proc.stdout, re.M)]
    return lengths[-1] if lengths else None


def check_local(path: Path, rlen: int | None) -> tuple[bool, str]:
    """(ok, reason) against dispatch criteria + Content-Length."""
    if not path.exists():
        return False, "missing"
    size = path.stat().st_size
    if _first_bytes_html(path):
        return False, f"html_head size={size}"
    if size <= MIN_BYTES:
        return False, f"tiny size={size}"
    if rlen is not None and size != rlen:
        return False, f"size_mismatch local={size} remote={rlen}"
    if rlen is None:
        return False, "no_remote_length"
    return True, ""


def repair(url: str, dst: Path, rlen: int | None) -> tuple[bool, str]:
    """One repair download. -C - resumes truncated partials; delete
    first when the local copy would poison a resume (HTML head or
    larger-than-remote)."""
    if dst.exists():
        bad_head = _first_bytes_html(dst)
        oversize = rlen is not None and dst.stat().st_size > rlen
        if bad_head or oversize:
            dst.unlink()
    if _disk_free_gb() < DISK_FLOOR_GB:
        return False, f"disk_floor free={_disk_free_gb():.1f}GB"
    _polite()
    proc = subprocess.run(
        ["curl", "-L", "--retry", "3", "-C", "-", "-sS", "--fail",
         "--connect-timeout", "30", "-A", UA, "-o", str(dst), url],
        capture_output=True, text=True, timeout=3600)
    ok = proc.returncode == 0 and dst.exists()
    return ok, (f"rc={proc.returncode}" if not ok else "rc=0")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-sha", action="store_true", default=True)
    args = ap.parse_args()

    with open(SELECTION_CSV, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    assert header[:2] == ["site", "product_id"], header
    i_size, i_sha = header.index("size_bytes"), header.index("sha256")
    i_path, i_url = header.index("local_path"), header.index("pds_url")

    results, n_fail = [], 0
    total_bytes = 0
    for row in rows:
        site, pid = row[0], row[1]
        dst, url = Path(row[i_path]), row[i_url]
        rlen = remote_length(url)
        ok, why = check_local(dst, rlen)
        note, status = why, "VERIFY_OK"
        if not ok:
            print(f"[repair] {site}/{pid}: {why}", flush=True)
            dok, dmsg = repair(url, dst, rlen)
            rlen2 = remote_length(url)     # fresh HEAD after repair
            ok2, why2 = check_local(dst, rlen2 if rlen2 else rlen)
            if not (dok and ok2):
                status = "VERIFY_FAIL"
                note = f"{why}; repair {dmsg}; {why2}"
                n_fail += 1
            else:
                status = "VERIFY_FIX"
                note = f"{why}; repaired {dmsg}"
        # authoritative sha (recompute; hardlinked dupes hash identically)
        sha = _sha256_of_file(dst) if dst.exists() else ""
        prev_sha = row[i_sha]
        if sha and sha != prev_sha:
            note += f"; csv_sha_updated(was={prev_sha[:12]})"
        row[i_size] = str(dst.stat().st_size) if dst.exists() else ""
        row[i_sha] = sha
        total_bytes += dst.stat().st_size if dst.exists() else 0
        log_row({"site": site, "product_id": pid, "url": url,
                 "status": status, "size_bytes": row[i_size],
                 "sha256": sha, "note": note})
        results.append({"site": site, "product_id": pid, "status": status,
                        "size_bytes": row[i_size], "sha256": sha,
                        "remote_length": rlen, "detail": note})
        print(f"[{status}] {site}/{pid} size={row[i_size]} "
              f"remote={rlen} sha={sha[:12]}", flush=True)

    # rewrite CSV in place, identical layout, enriched
    with open(SELECTION_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

    per_site: dict[str, dict[str, int]] = {}
    for r in results:
        d = per_site.setdefault(r["site"], {"ok": 0, "total": 0})
        d["total"] += 1
        d["ok"] += r["status"] != "VERIFY_FAIL"
    summary = {
        "generated_utc": _now_iso(),
        "n_rows": len(results),
        "n_ok": sum(1 for r in results if r["status"] != "VERIFY_FAIL"),
        "n_fixed": sum(1 for r in results if r["status"] == "VERIFY_FIX"),
        "n_failed": n_fail,
        "total_bytes_apparent": total_bytes,
        "per_site": per_site,
        "disk_free_gb_after": round(_disk_free_gb(), 1),
        "licence": LICENCE_ATTR,
        "results": results,
    }
    with open(SUMMARY_JSON, "w") as f:
        json.dump(summary, f, indent=1)
    print(f"\n[summary] ok={summary['n_ok']}/{len(results)} "
          f"fixed={summary['n_fixed']} failed={n_fail}; "
          f"free={summary['disk_free_gb_after']} GB", flush=True)
    print(f"[json] {SUMMARY_JSON}", flush=True)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
