"""retry_nac_edr_fetch.py — NAC EDR retry fetcher with multi-endpoint fallback.

PDS NAC_EDR endpoints have been intermittently 404 since ~2026-08-23
(proxy/CDN migration). This script implements a 4-stage retry strategy
that tries each known endpoint in sequence and falls back to the
Wayback CDX API if all four fail.

Endpoints (in order):
  1. `https://pds.lroc.im-ldi.com/data/`  (legacy direct)
  2. `https://pds.mcp.nasa.gov/data/lroc/` (CDR + EDR redirect target;
     current canonical since the 2024 PDS migration)
  3. `https://wms.lroc.im-ldi.com/`       (WMS — usually non-functional
     but the request still resolves; useful as a probe)
  4. Wayback CDX: `https://web.archive.org/cdx/search/cdx?url=...`
     returns a JSON list of archived snapshots; pick the most recent.

Algorithm contract:
  Input  : CSV queue at `01_WORKSPACE/data/wp8_stereo/nac_edr_retry_queue.csv`
           with columns (product_id, dtm, expected_size_bytes, notes).
  Output : per-row retry log at
           `01_WORKSPACE/data/wp8_stereo/nac_edr_retry_log.csv` with
           columns (timestamp_utc, product_id, dtm, endpoint, status,
           size_bytes, sha256, elapsed_sec, http_status, notes).
  Skip   : already-fetched products are skipped by querying the existing
           `~/lunarvoid/data/fetch_log_lroc.csv` for SKIP_EXISTS rows.

Status codes emitted:
  - SKIP_EXISTS         : on-disk product; skip
  - OK_<endpoint>       : downloaded successfully from <endpoint>
  - HTTP_<code>_<endpoint> : got a HTTP code != 200 from <endpoint>
  - URL_NOT_FOUND       : all 3 PDS endpoints returned 404
  - WAYBACK_FOUND       : found in Wayback (snapshot URL logged)
  - WAYBACK_NOT_FOUND   : not in Wayback
  - ERROR               : exception (timeout, DNS, etc.)

USAGE:
    ~/lunarvoid/venv/bin/python code/wp8_stereo/retry_nac_edr_fetch.py
    ~/lunarvoid/venv/bin/python code/wp8_stereo/retry_nac_edr_fetch.py --max 3
    ~/lunarflux/lunarvoid/venv/bin/python code/wp8_stereo/retry_nac_edr_fetch.py --product M137332905LE

Cost: $0. Network only. Politeness: 1-2 s gap between retries per URL.

CLAIM DISCIPLINE: This script only FETCHES files. It does NOT extract,
process, or claim anything about their contents. The fetched files
land in `~/lunarvoid/data/edr/<dtm>/<product_id>.IMG`; the geo-coder
picks them up from there in the stereo pipeline.

KNOWN STATE (2026-08-24): PDS endpoints are returning 404. The script
will log URL_NOT_FOUND on every row at this point in time; that is the
EXPECTED behaviour and the retry log is the audit trail.

Dependencies:
  - requests (or urllib3; we use urllib3 here for minimal deps)
  - python >= 3.10
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths (project conventions)
# ---------------------------------------------------------------------------
QUEUE_CSV = Path("01_WORKSPACE/data/wp8_stereo/nac_edr_retry_queue.csv")
LOG_CSV = Path("01_WORKSPACE/data/wp8_stereo/nac_edr_retry_log.csv")
FETCH_LOG = Path.home() / "lunarvoid/data/fetch_log_lroc.csv"
EDR_DEST_ROOT = Path.home() / "lunarvoid" / "data" / "edr"
# C10: standardise on the shared UA across all fetchers (SEC-01 fix)
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "code" / "setup"))
from _http import HEADERS  # noqa: E402

# Endpoint templates. Each is a (name, url_template) tuple. The template
# uses {product_id} as the substitution.
ENDPOINTS = [
    ("legacy",   "https://pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_2001/DATA/SDP/NAC_IMG/{product_id}.IMG"),
    ("mcp",      "https://pds.mcp.nasa.gov/data/lroc/LRO-L-LROC-2-EDR-V1.0/LROLRC_2001/DATA/SDP/NAC_IMG/{product_id}.IMG"),
    ("wms",      "https://wms.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_2001/DATA/SDP/NAC_IMG/{product_id}.IMG"),
]

# Wayback CDX endpoint (template uses {url} substitution)
WAYBACK_CDX = "https://web.archive.org/cdx/search/cdx?url={url}&output=json&limit=1&from=20240101"

# Rate limit per URL (seconds). PDS is generous but be polite.
RATE_LIMIT_SECONDS = 1.5
TIMEOUT_SECONDS = 30
MAX_RETRIES_PER_URL = 2

# Project attribution per MANIFEST.md conventions
LICENCE_ATTR = "LROC NAC EDR, NASA/ASU, PDS public domain"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_of_file(path: Path, chunk: int = 1 << 20) -> str:
    """Compute SHA-256 of a file. Streams in 1 MiB chunks to handle
    large NAC IMG files (~400 MB each)."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            buf = f.read(chunk)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def _head_request(url: str, timeout: float = TIMEOUT_SECONDS) -> tuple[int, Optional[int]]:
    """HEAD-equivalent GET probe. Returns (http_status, content_length_or_None).

    Uses urllib with method="HEAD" if the server accepts it; otherwise
    a tiny range GET. urllib does not support method="HEAD" natively
    but Request does.
    """
    req = urllib.request.Request(url, method="HEAD", headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            cl = resp.headers.get("Content-Length")
            return resp.status, int(cl) if cl else None
    except urllib.error.HTTPError as e:
        return e.code, None
    except (urllib.error.URLError, socket.timeout, ConnectionError) as e:
        logger.debug("HEAD %s failed: %s", url, e)
        return -1, None


def _download(url: str, dest: Path, timeout: float = TIMEOUT_SECONDS) -> tuple[int, int]:
    """Download url -> dest. Returns (http_status, bytes_written)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp, dest.open("wb") as f:
            written = 0
            while True:
                buf = resp.read(1 << 20)
                if not buf:
                    break
                f.write(buf)
                written += len(buf)
            return resp.status, written
    except urllib.error.HTTPError as e:
        return e.code, 0
    except (urllib.error.URLError, socket.timeout, ConnectionError) as e:
        logger.debug("GET %s failed: %s", url, e)
        return -1, 0

def _wayback_lookup(product_id: str) -> Optional[str]:
    """Look up the product in the Wayback CDX API. Returns the most
    recent snapshot URL or None.
    """
    candidate = ENDPOINTS[0][1].format(product_id=product_id)
    cdx = WAYBACK_CDX.format(url=candidate)
    try:
        req = urllib.request.Request(cdx, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        # CDX returns a JSON array of arrays: first row is the header.
        if not data or len(data) < 2:
            return None
        # Find the row with the most recent timestamp.
        # Header: ["urlkey", "timestamp", "original", "mimetype", ...]
        rows = data[1:]
        if not rows:
            return None
        rows.sort(key=lambda r: r[1], reverse=True)
        ts, original = rows[0][1], rows[0][2]
        return f"https://web.archive.org/web/{ts}if_/{original}"
    except (urllib.error.URLError, socket.timeout, ConnectionError, json.JSONDecodeError) as e:
        logger.debug("Wayback CDX failed for %s: %s", product_id, e)
        return None


def _already_fetched(product_id: str) -> Optional[str]:
    """Check fetch_log_lroc.csv for an OK / SKIP_EXISTS row for this product_id.
    Returns the sha256 if found, else None.
    """
    if not FETCH_LOG.exists():
        return None
    import csv
    with FETCH_LOG.open() as f:
        for row in csv.DictReader(f):
            if row.get("product_id") == product_id and row.get("status") in ("OK", "SKIP_EXISTS"):
                return row.get("sha256")
    return None


def _already_on_disk(product_id: str, dtm: str) -> bool:
    """Check whether the IMG is already on disk under
    ~/lunarvoid/data/edr/<dtm>/<product_id>.IMG.
    """
    dest = EDR_DEST_ROOT / dtm / f"{product_id}.IMG"
    return dest.exists() and dest.stat().st_size > 0


# ---------------------------------------------------------------------------
# Main retry logic
# ---------------------------------------------------------------------------
def retry_one(product_id: str, dtm: str, expected_size_bytes: int) -> dict:
    """Try all 4 endpoints in sequence for a single product.

    Returns a result dict with keys: product_id, dtm, endpoint, status,
    size_bytes, sha256, elapsed_sec, http_status, notes. Used by the
    caller to append to the retry log.
    """
    t0 = time.monotonic()

    # Stage 0: skip if already on disk OR in fetch_log.
    if _already_on_disk(product_id, dtm):
        return {
            "timestamp_utc": _now_iso(), "product_id": product_id, "dtm": dtm,
            "endpoint": "on-disk", "status": "SKIP_EXISTS",
            "size_bytes": (EDR_DEST_ROOT / dtm / f"{product_id}.IMG").stat().st_size,
            "sha256": _sha256_of_file(EDR_DEST_ROOT / dtm / f"{product_id}.IMG"),
            "elapsed_sec": round(time.monotonic() - t0, 2),
            "http_status": 200, "notes": "already on disk; skipping",
        }
    prev_sha = _already_fetched(product_id)
    if prev_sha:
        return {
            "timestamp_utc": _now_iso(), "product_id": product_id, "dtm": dtm,
            "endpoint": "fetch-log", "status": "SKIP_EXISTS",
            "size_bytes": 0, "sha256": prev_sha,
            "elapsed_sec": round(time.monotonic() - t0, 2),
            "http_status": 200, "notes": "in fetch_log; skipping",
        }

    # Stages 1-3: PDS endpoints.
    for ep_name, ep_template in ENDPOINTS:
        url = ep_template.format(product_id=product_id)
        # Probe with HEAD first to save bandwidth.
        status, cl = _head_request(url)
        logger.info("HEAD %s -> %s (Content-Length=%s)", url, status, cl)
        if status == 200:
            # Real download.
            dest = EDR_DEST_ROOT / dtm / f"{product_id}.IMG"
            d_status, written = _download(url, dest)
            if d_status == 200 and written > 0:
                sha = _sha256_of_file(dest)
                return {
                    "timestamp_utc": _now_iso(), "product_id": product_id, "dtm": dtm,
                    "endpoint": ep_name, "status": f"OK_{ep_name}",
                    "size_bytes": written, "sha256": sha,
                    "elapsed_sec": round(time.monotonic() - t0, 2),
                    "http_status": 200, "notes": "downloaded",
                }
        # C15-4: only sleep on a non-200 (skipping a successful endpoint
        # back to the next endpoint is wasteful; on the happy path this
        # halves the per-row sleep budget).
        if status != 200:
            time.sleep(RATE_LIMIT_SECONDS)

    # Stage 4: Wayback fallback.
    wayback_url = _wayback_lookup(product_id)
    if wayback_url is not None:
        dest = EDR_DEST_ROOT / dtm / f"{product_id}.IMG"
        w_status, w_written = _download(wayback_url, dest)
        if w_status == 200 and w_written > 0:
            sha = _sha256_of_file(dest)
            return {
                "timestamp_utc": _now_iso(), "product_id": product_id, "dtm": dtm,
                "endpoint": "wayback", "status": "WAYBACK_FOUND",
                "size_bytes": w_written, "sha256": sha,
                "elapsed_sec": round(time.monotonic() - t0, 2),
                "http_status": 200,
                "notes": f"wayback snapshot: {wayback_url}",
            }

    # All stages failed.
    return {
        "timestamp_utc": _now_iso(), "product_id": product_id, "dtm": dtm,
        "endpoint": "none", "status": "URL_NOT_FOUND",
        "size_bytes": 0, "sha256": "",
        "elapsed_sec": round(time.monotonic() - t0, 2),
        "http_status": 404,
        "notes": "all 3 PDS endpoints returned non-200; wayback empty",
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--queue", default=str(QUEUE_CSV), help="Path to retry queue CSV")
    parser.add_argument("--log", default=str(LOG_CSV), help="Path to retry log CSV")
    parser.add_argument("--max", type=int, default=0, help="Max rows to retry (0 = all)")
    parser.add_argument("--product", default=None, help="Retry only this product_id")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    queue_path = Path(args.queue)
    log_path = Path(args.log)
    if not queue_path.exists():
        logger.error("Queue CSV not found: %s", queue_path)
        return 2

    rows = []
    with queue_path.open() as f:
        for r in csv.DictReader(f):
            rows.append(r)
    logger.info("Loaded %d rows from %s", len(rows), queue_path)

    if args.product:
        rows = [r for r in rows if r["product_id"] == args.product]
        if not rows:
            logger.error("product_id %s not in queue", args.product)
            return 2
    if args.max > 0:
        rows = rows[:args.max]

    # Ensure log directory exists.
    log_path.parent.mkdir(parents=True, exist_ok=True)
    # Open log in append mode; create with header if absent.
    write_header = not log_path.exists()
    with log_path.open("a", newline="") as f:
        fieldnames = [
            "timestamp_utc", "product_id", "dtm", "endpoint", "status",
            "size_bytes", "sha256", "elapsed_sec", "http_status", "notes",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            w.writeheader()

        for r in rows:
            product_id = r["product_id"]
            dtm = r["dtm"]
            expected_size = int(r.get("expected_size_bytes", 0))
            logger.info("Retrying %s (%s, expected=%d B)", product_id, dtm, expected_size)
            result = retry_one(product_id, dtm, expected_size)
            w.writerow(result)
            f.flush()
            logger.info("  -> status=%s, http=%s, size=%d B",
                        result["status"], result["http_status"], result["size_bytes"])

    logger.info("Retry log written to %s", log_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())