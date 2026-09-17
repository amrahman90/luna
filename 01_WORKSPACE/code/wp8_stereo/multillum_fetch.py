"""LUNARVOID WP8 stereo / Step 19.1 — fetch NAC EDR images across
illumination geometries for the 7 above-floor candidate sites
(multi-evidence stacking prep).

Sites (atlas names approx per dispatch; resolved 2026-09-14 from the
Wagner & Robinson 2021 pit atlas shapefile at
~/lunarvoid/data/index_layers/pit_atlas/LUNAR_PIT_LOCATIONS_180.SHP,
except FECUNPIT which is a DTM frame, not a catalogued pit — its
centre is the mean of the ACTIVE FECUNPIT registry candidates):

    TRANQPIT1    Mare Tranquillitatis Pit        ( 33.2220,   8.3355)
    FECUNPIT     alt. Fecunditatis frame         ( 48.7515,  -0.2853)
    FECNDITATS2  Central Mare Fecunditatis Pit   ( 48.6595,  -0.9182)
    INGENIIPIT   Mare Ingenii Pit                (166.0559, -35.9494)
    MARIUSPIT01  Marius Hills Pit                (-56.7701,  14.0917)
    PRCLRMPIT01  North Procellarum 1 Pit         (-45.6398,  35.4097)
    SWFECUNPIT1  Southwest Mare Fecunditatis Pit ( 42.7595,  -6.7521)

Bbox = centre +- 0.15 deg.  (lon, lat) planetocentric, -180..180.

Discovery mechanism (verified live 2026-09-14):
  * LROC Image Search is a Rails POST form at
    https://data.lroc.im-ldi.com/lroc/search  (GET returns the empty
    form + CSRF token + session cookies).
  * GOTCHA (cost an hour): a POST with only the filter fields returns
    HTTP 500.  The app requires the COMPLETE browser field set — in
    particular `filter[slew_abs]=0` (hidden input) and the six empty
    `filter[doy_*]` selects.  `_form_fields()` replicates the browser
    byte-for-byte.
  * Pagination: append `page=<n>` to the POST body (GET ?page= loses
    the filter — it is NOT session-persisted).
  * Result rows: /lroc/view_lroc/LRO-L-LROC-2-EDR-V1.0/<ID>; NAC IDs
    match ^M\\d{10}(LE|RE)$ (10 digits, not 9).  WAC are CE/CW/MG.
  * Product pages: metadata table rows are MALFORMED HTML
    (`<td>Key</th><td>value</td>`) — parse with
    `<td>(key)</th>\\s*<td>(value)</td>`.  Incidence/Emission/Phase
    angles, Resolution (m/px), Start time, and the direct PDS byte
    link `//pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/...IMG`
    (302 -> pds.mcp.nasa.gov, binary/octet-stream) all live there.

Selection (illumination diversity): 4 incidence buckets per site
[20-40], [40-60], [60-80], [80-100]; up to 4 NAC images per site, one
per populated bucket, chosen nearest the bucket midpoint (30/50/70/90)
to maximise inter-pick spread; NAC-L preferred, NAC-R only if no L.
resolution <= 3 m/px enforced server-side by the filter.

Download: curl -L --retry 3 -C - to
~/lunarvoid/data/edr/multillum/<SITE>/<PRODUCT_ID>.IMG (+ tiny .LBL
best-effort, detached PDS3 label needed to read the IMG later).
First-bytes check rejects HTML error pages (<!DOCTYPE).  sha256 every
completed file.  Disk guard: skip downloads if free < 45 GB.

Licence: LROC NAC EDR, NASA/ASU, PDS public domain.

Usage (per project fetcher convention, dry-run is the DEFAULT):
    multillum_fetch.py                     # discovery+selection, no downloads
    multillum_fetch.py --fetch             # actually download
    multillum_fetch.py --site TRANQPIT1 --fetch
    multillum_fetch.py --refresh-cache     # ignore caches, re-discover
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DATA = REPO / "01_WORKSPACE" / "data"

# Raw EDR images live ONLY under ~/lunarvoid/data/ (conventions §1).
EDR_ROOT = Path.home() / "lunarvoid" / "data" / "edr" / "multillum"
FETCH_LOG = EDR_ROOT / "fetch_log.csv"
DISCOVERY_CACHE = EDR_ROOT / "discovery_cache.json"
METADATA_CACHE = EDR_ROOT / "metadata_cache.json"

# Repo-side selection CSV (dispatch deliverable 2).
SELECTION_CSV = DATA / "wp8_stereo" / "multillum_selection_2026-09-14.csv"

SEARCH_URL = "https://data.lroc.im-ldi.com/lroc/search"
VIEW_URL = "https://data.lroc.im-ldi.com/lroc/view_lroc/LRO-L-LROC-2-EDR-V1.0/{pid}"

UA = ("Mozilla/5.0 (X11; Linux x86_64) LUNARVOID-research/1.0 "
      "(lunar lava tube study; contact via LROC PDS)")

LICENCE_ATTR = "LROC NAC EDR, NASA/ASU, PDS public domain"

# site -> (lon, lat, provenance)
SITES: dict[str, tuple[float, float, str]] = {
    "TRANQPIT1": (33.2220, 8.3355, "atlas:Mare Tranquillitatis Pit"),
    "FECUNPIT": (48.7515, -0.2853, "registry ACTIVE candidates mean (alt DTM frame)"),
    "FECNDITATS2": (48.6595, -0.9182, "atlas:Central Mare Fecunditatis Pit"),
    "INGENIIPIT": (166.0559, -35.9494, "atlas:Mare Ingenii Pit"),
    "MARIUSPIT01": (-56.7701, 14.0917, "atlas:Marius Hills Pit"),
    "PRCLRMPIT01": (-45.6398, 35.4097, "atlas:North Procellarum 1 Pit"),
    "SWFECUNPIT1": (42.7595, -6.7521, "atlas:Southwest Mare Fecunditatis Pit"),
}

# Download priority if disk forces triage (dispatch order).
PRIORITY = ["TRANQPIT1", "FECUNPIT", "FECNDITATS2", "INGENIIPIT",
            "MARIUSPIT01", "PRCLRMPIT01", "SWFECUNPIT1"]

BBOX_DEG = 0.15
BUCKETS = [(20.0, 40.0), (40.0, 60.0), (60.0, 80.0), (80.0, 100.0)]
RES_MAX = 3.0
PER_PAGE = 100
MAX_PAGES = 3          # per bucket POST; 3*100 candidates is plenty
PROBE_PER_BUCKET = 5   # product pages fetched per bucket (early-exit near midpoint)
EARLY_EXIT_DEG = 5.0   # stop probing when |inc - midpoint| < this

RATE_LIMIT_SECONDS = 2.0
DISK_FLOOR_GB = 45.0

NAC_ID_RE = re.compile(r"^M\d{9,10}(LE|RE)$")
ROW_ID_RE = re.compile(
    r"/lroc/view_lroc/LRO-L-LROC-2-EDR-V1\.0/(M\d{9,10}[A-Z]{2})")
EDR_LINK_RE = re.compile(
    r"//pds\.lroc\.im-ldi\.com/data/LRO-L-LROC-2-EDR-V1\.0/[^\"'\s]+?\.IMG")
# Malformed product-page table: <td>Key</th> <td>value</td>
META_RE = re.compile(r"<td>\s*([^<>]+?)\s*</th>\s*<td[^>]*>(.*?)</td>", re.S)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _tagstrip(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


class PoliteRate:
    """Enforce >= rate seconds between consecutive HTTP requests."""

    def __init__(self, rate: float):
        self.rate = rate
        self._last = 0.0

    def wait(self) -> None:
        dt = time.time() - self._last
        if dt < self.rate:
            time.sleep(self.rate - dt)
        self._last = time.time()


class LrocSession:
    """CSRF + cookie session against the LROC Rails search."""

    def __init__(self, rate: float, timeout: int = 120):
        self.jar = Path("/tmp/opencode/lroc_multillum_cookies.txt")
        self.jar.parent.mkdir(parents=True, exist_ok=True)
        self.rate = PoliteRate(rate)
        self.timeout = timeout
        self.token: str | None = None

    # -- plumbing ----------------------------------------------------
    def _curl(self, args: list[str]) -> tuple[int, str]:
        cmd = ["curl", "-s", "-A", UA, "-w", "%{http_code}", *args]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=self.timeout)
        except subprocess.TimeoutExpired:
            return 0, ""          # caller treats 0 as transient failure
        body = proc.stdout[:-3] if len(proc.stdout) >= 3 else ""
        try:
            code = int(proc.stdout[-3:])
        except ValueError:
            code = 0
        return code, body

    def ensure_token(self, force: bool = False) -> None:
        if self.token and not force:
            return
        self.rate.wait()
        code, body = self._curl(["-c", str(self.jar), SEARCH_URL])
        if code != 200:
            raise RuntimeError(f"token GET failed: HTTP {code}")
        m = re.search(r'name="authenticity_token" value="([^"]+)"', body)
        if not m:
            raise RuntimeError("no authenticity_token in search form")
        self.token = m.group(1)

    def search(self, fields: dict[str, str]) -> tuple[int, str]:
        """POST the full browser field set. Retries transient failures
        (timeout/0, 429, 5xx) with backoff; refreshes CSRF on 422."""
        code, body = 0, ""
        for attempt in range(1, 4):
            self.ensure_token(force=(attempt > 1))
            args = ["-b", str(self.jar), "-X", "POST", SEARCH_URL,
                    "-H", f"Origin: https://data.lroc.im-ldi.com",
                    "-H", f"Referer: {SEARCH_URL}"]
            for k, v in fields.items():
                v = self.token if k == "authenticity_token" else v
                args += ["--data-urlencode", f"{k}={v}"]
            self.rate.wait()
            code, body = self._curl(args)
            if code == 422:            # stale CSRF -> retry with fresh token
                continue
            if code == 0 or code == 429 or code >= 500:
                time.sleep(min(2 ** attempt * 2, 16))
                continue
            return code, body
        return code, body

    def get_page(self, url: str) -> tuple[int, str]:
        self.rate.wait()
        return self._curl(["-b", str(self.jar), url])


def _form_fields(w: float, e: float, s: float, n: float,
                 inc_lo: str, inc_hi: str, page: int) -> dict[str, str]:
    """COMPLETE browser field set — the 500 gotcha lives here.
    Do not prune fields: slew_abs=0 + empty doy selects are required."""
    return {
        "utf8": "\u2713",
        "authenticity_token": "__TOKEN__",  # replaced by session.search()
        "filter[product_id]": "",
        "filter[west]": f"{w:.4f}", "filter[east]": f"{e:.4f}",
        "filter[south]": f"{s:.4f}", "filter[north]": f"{n:.4f}",
        "filter[incidence_min]": inc_lo, "filter[incidence_max]": inc_hi,
        "filter[emission_min]": "", "filter[emission_max]": "",
        "filter[slew_min]": "", "filter[slew_max]": "",
        "filter[slew_abs]": "0",
        "filter[resolution_min]": "", "filter[resolution_max]": f"{RES_MAX:g}",
        "filter[exposure_min]": "", "filter[exposure_max]": "",
        "filter[sunsublon_min]": "", "filter[sunsublon_max]": "",
        "filter[sunsublat_min]": "", "filter[sunsublat_max]": "",
        "filter[orbit_min]": "", "filter[orbit_max]": "",
        "filter[doy_min][year]": "", "filter[doy_min][month]": "",
        "filter[doy_min][day]": "",
        "filter[doy_max][year]": "", "filter[doy_max][month]": "",
        "filter[doy_max][day]": "",
        "filter[product_type][]": "EDR",
        "show_thumbs": "",
        "per_page": str(PER_PAGE),
        "commit": "Search",
        "page": str(page),
    }


def bbox_for(lon: float, lat: float) -> tuple[float, float, float, float]:
    w, e = lon - BBOX_DEG, lon + BBOX_DEG
    if e > 180.0:                       # dateline wrap (defensive; none of
        w, e = w - 360.0, e - 360.0     # our 7 sites needs it)
    if w < -180.0:
        w, e = w + 360.0, e + 360.0
    return w, e, lat - BBOX_DEG, lat + BBOX_DEG


def parse_rows(html: str) -> list[dict]:
    """Result rows -> [{pid, time, type}] preserving server order."""
    out, seen = [], set()
    for m in re.finditer(
            r"<td><a href=\"/lroc/view_lroc/LRO-L-LROC-2-EDR-V1\.0/"
            r"(M\d{9,10}[A-Z]{2})\">[^<]*</a></td>\s*<td>([^<]*)</td>\s*"
            r"<td>([^<]*)</td>", html):
        pid, t, typ = m.group(1), m.group(2).strip(), m.group(3).strip()
        if pid not in seen:
            seen.add(pid)
            out.append({"pid": pid, "time": t, "type": typ})
    return out


def discover_bucket(sess: LrocSession, w: float, e: float, s: float,
                     n: float, lo: str, hi: str) -> list[dict]:
    rows: list[dict] = []
    for page in range(1, MAX_PAGES + 1):
        fields = _form_fields(w, e, s, n, lo, hi, page)
        code, body = sess.search(fields)
        if code != 200:
            print(f"    [warn] search POST HTTP {code} (page {page})", flush=True)
            break
        page_rows = parse_rows(body)
        rows.extend(page_rows)
        if len(page_rows) < PER_PAGE:
            break
    # keep only NAC L/R EDR
    return [r for r in rows if NAC_ID_RE.match(r["pid"])]


def parse_product_page(html: str, pid: str) -> dict | None:
    meta: dict[str, str] = {}
    for m in META_RE.finditer(html):
        meta[_tagstrip(m.group(1)).lower()] = _tagstrip(m.group(2))
    links = EDR_LINK_RE.findall(html)
    edr_url = ("https:" + sorted(links)[0]) if links else ""
    if not edr_url:
        return None
    def _f(k):
        try:
            return float(meta.get(k, "nan"))
        except ValueError:
            return float("nan")
    return {
        "pid": pid,
        "incidence_deg": _f("incidence angle"),
        "emission_deg": _f("emission angle"),
        "phase_deg": _f("phase angle"),
        "resolution_m": _f("resolution"),
        "acquisition_time": meta.get("start time", ""),
        "edr_url": edr_url,
        "lbl_url": edr_url[:-4] + ".LBL",
    }


def probe_products(sess: LrocSession, pids: list[str],
                   cache: dict) -> list[dict]:
    """Fetch product pages for pids (cache-aware), return metadata list."""
    metas = []
    for pid in pids:
        if pid in cache and cache[pid].get("edr_url"):
            metas.append(cache[pid])
            continue
        code, body = sess.get_page(VIEW_URL.format(pid=pid))
        if code != 200:
            print(f"    [warn] product page {pid} HTTP {code}", flush=True)
            continue
        parsed = parse_product_page(body, pid)
        if parsed:
            cache[pid] = parsed
            metas.append(parsed)
    return metas


def select_per_bucket(cands: list[dict], lo: float, hi: float) -> dict | None:
    """Pick NAC-L nearest bucket midpoint; NAC-R only if no L available."""
    mid = (lo + hi) / 2.0

    def key(m):
        inc = m["incidence_deg"]
        return (abs(inc - mid) if inc == inc else 1e9,
                0 if m["pid"].endswith("LE") else 1)

    lefts = [m for m in cands if m["pid"].endswith("LE")]
    pool = lefts or cands
    if not pool:
        return None
    return sorted(pool, key=key)[0]


def _load_json(p: Path) -> dict:
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return {}


def _save_json(p: Path, d: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(d, f, indent=1, sort_keys=True)


def _disk_free_gb() -> float:
    return shutil.disk_usage("/").free / 1024 ** 3


def _sha256_of_file(path: Path, buf: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(buf)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _first_bytes_html(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            head = f.read(16).lstrip().lower()
        return head.startswith(b"<!doctype") or head.startswith(b"<html")
    except OSError:
        return True


def curl_download(url: str, dst: Path, timeout: int = 3600) -> tuple[bool, str]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["curl", "-L", "--retry", "3", "-C", "-", "-sS", "--fail",
           "--connect-timeout", "30", "-A", UA, "-o", str(dst), url]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, "curl timeout"
    if proc.returncode == 0 and dst.exists() and dst.stat().st_size > 0:
        return True, f"rc=0 size={dst.stat().st_size}"
    return False, f"rc={proc.returncode} {proc.stderr.strip()[:160]}"


def log_row(row: dict) -> None:
    FETCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not FETCH_LOG.exists()
    with open(FETCH_LOG, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp_utc", "site", "product_id", "url",
                        "status", "size_bytes", "sha256", "licence", "note"])
        w.writerow([row.get("timestamp_utc", _now_iso()),
                    row.get("site", ""), row.get("product_id", ""),
                    row.get("url", ""), row.get("status", ""),
                    row.get("size_bytes", ""), row.get("sha256", ""),
                    LICENCE_ATTR, row.get("note", "")])


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fetch", action="store_true",
                    help="actually download (default: dry-run, discovery only)")
    ap.add_argument("--dry-run", action="store_true", default=True,
                    help="(default) never download")
    ap.add_argument("--site", choices=sorted(SITES), action="append",
                    help="restrict to site(s); repeatable")
    ap.add_argument("--refresh-cache", action="store_true",
                    help="ignore + overwrite discovery/metadata caches")
    ap.add_argument("--rate-limit", type=float, default=RATE_LIMIT_SECONDS)
    ap.add_argument("--max-per-site", type=int, default=4)
    args = ap.parse_args()
    # --dry-run is the DEFAULT (project fetcher convention); only an
    # explicit --fetch performs downloads.
    fetch = bool(args.fetch)

    sites = args.site or PRIORITY
    sess = LrocSession(args.rate_limit)

    disco = {} if args.refresh_cache else _load_json(DISCOVERY_CACHE)
    meta = {} if args.refresh_cache else _load_json(METADATA_CACHE)

    EDR_ROOT.mkdir(parents=True, exist_ok=True)

    # ---------- Phase 1: discovery + selection --------------------------
    selection: list[dict] = []
    bucket_report: list[str] = []
    for site in sites:
        lon, lat, prov = SITES[site]
        w, e, s, n = bbox_for(lon, lat)
        print(f"[site] {site} centre=({lon:.4f},{lat:.4f}) "
              f"bbox W{w:.4f} E{e:.4f} S{s:.4f} N{n:.4f} [{prov}]", flush=True)
        sd = disco.setdefault(site, {})
        picks: dict[str, dict] = {}
        for lo, hi in BUCKETS:
            bkey = f"{lo:g}-{hi:g}"
            if bkey not in sd:
                sd[bkey] = discover_bucket(sess, w, e, s, n, str(lo), str(hi))
            rows = sd[bkey]
            n_le = sum(1 for r in rows if r["pid"].endswith("LE"))
            if not rows:
                bucket_report.append(f"{site} [{bkey}]: EMPTY")
                print(f"  bucket {bkey}: EMPTY", flush=True)
                continue
            # probe a few product pages, prefer LE, early-exit near midpoint
            cand_pids = ([r["pid"] for r in rows if r["pid"].endswith("LE")]
                         or [r["pid"] for r in rows])[:PROBE_PER_BUCKET]
            metas = probe_products(sess, cand_pids, meta)
            pick = None
            mid = (lo + hi) / 2
            for m in metas:  # server order; early-exit if near midpoint
                if abs(m["incidence_deg"] - mid) < EARLY_EXIT_DEG:
                    pick = m
                    break
            if pick is None and metas:
                pick = select_per_bucket(metas, lo, hi)
            if pick is None:
                bucket_report.append(f"{site} [{bkey}]: {len(rows)} NAC rows, "
                                     f"0 probed OK")
                continue
            picks[bkey] = pick
            bucket_report.append(
                f"{site} [{bkey}]: {len(rows)} NAC ({n_le} L) -> {pick['pid']} "
                f"inc={pick['incidence_deg']:.2f}")
            print(f"  bucket {bkey}: {len(rows)} NAC ({n_le} L) -> "
                  f"{pick['pid']} inc={pick['incidence_deg']:.2f}", flush=True)
        for bkey, m in list(picks.items())[: args.max_per_site]:
            selection.append({"site": site, "bucket": bkey, **m})
        # persist incrementally so a killed run can resume cleanly
        _save_json(DISCOVERY_CACHE, disco)
        _save_json(METADATA_CACHE, meta)

    _save_json(DISCOVERY_CACHE, disco)
    _save_json(METADATA_CACHE, meta)

    # ---------- Phase 2: write selection CSV ----------------------------
    SELECTION_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(SELECTION_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["site", "product_id", "incidence_deg", "emission_deg",
                    "resolution_m", "acquisition_time", "size_bytes",
                    "sha256", "local_path", "pds_url"])
        for r in selection:
            local = EDR_ROOT / r["site"] / f"{r['pid']}.IMG"
            w.writerow([r["site"], r["pid"],
                        f"{r['incidence_deg']:.2f}", f"{r['emission_deg']:.2f}",
                        f"{r['resolution_m']:.4f}", r["acquisition_time"],
                        r.get("size_bytes", ""), r.get("sha256", ""),
                        local, r["edr_url"]])
    print(f"\n[selection] {len(selection)} images -> {SELECTION_CSV}", flush=True)

    # spread check (aim >=20 deg between picks per site)
    per_site: dict[str, list[float]] = {}
    for r in selection:
        per_site.setdefault(r["site"], []).append(r["incidence_deg"])
    for site, incs in per_site.items():
        incs = sorted(incs)
        gaps = [round(b - a, 1) for a, b in zip(incs, incs[1:])]
        small = [g for g in gaps if g < 20]
        if small:
            print(f"[note] {site} inter-pick gaps {gaps} (target >=20)",
                  flush=True)

    if not fetch:
        print("[dry-run] no downloads performed; rerun with --fetch", flush=True)
        return 0

    # ---------- Phase 3: download ---------------------------------------
    order = {s: i for i, s in enumerate(PRIORITY)}
    selection.sort(key=lambda r: order.get(r["site"], 99))
    total_bytes = 0
    n_ok = n_skip = n_fail = 0
    fetched: dict[str, Path] = {}   # pid -> first local copy (bbox overlap
    for r in selection:             # dedupes shared FECUN/FECNDITATS2 picks)
        site, pid, url = r["site"], r["pid"], r["edr_url"]
        dst = EDR_ROOT / site / f"{pid}.IMG"
        if pid in fetched and not dst.exists():
            # same product selected by two sites: hardlink, do not re-pull
            dst.parent.mkdir(parents=True, exist_ok=True)
            try:
                dst.hardlink_to(fetched[pid])
                src = fetched[pid]
                src2 = src.with_suffix(".LBL")
                if src2.exists():
                    dst.with_suffix(".LBL").hardlink_to(src2)
                sha = _sha256_of_file(dst)
                size = dst.stat().st_size
                r["size_bytes"], r["sha256"] = size, sha
                total_bytes += size
                n_ok += 1
                log_row({"site": site, "product_id": pid, "url": url,
                         "status": "OK_LINK", "size_bytes": size,
                         "sha256": sha, "note": f"hardlink to {src}"})
                print(f"[ok-link] {site}/{pid} -> {src}", flush=True)
                continue
            except OSError:
                pass  # fall through to a normal fetch
        if dst.exists() and dst.stat().st_size > 1 << 20 \
                and not _first_bytes_html(dst):
            sha = _sha256_of_file(dst)
            log_row({"site": site, "product_id": pid, "url": url,
                     "status": "SKIP_EXISTS",
                     "size_bytes": dst.stat().st_size, "sha256": sha})
            n_skip += 1
            total_bytes += dst.stat().st_size
            r["size_bytes"] = dst.stat().st_size
            r["sha256"] = sha
            fetched[pid] = dst
            print(f"[skip] {site}/{pid} exists ({dst.stat().st_size} B)",
                  flush=True)
            continue
        free = _disk_free_gb()
        if free < DISK_FLOOR_GB:
            log_row({"site": site, "product_id": pid, "url": url,
                     "status": "SKIP_DISK",
                     "note": f"free={free:.1f}GB < {DISK_FLOOR_GB}GB floor"})
            n_fail += 1
            print(f"[disk] STOP {site}/{pid}: free {free:.1f} GB < "
                  f"{DISK_FLOOR_GB} GB floor", flush=True)
            continue
        ok, msg = curl_download(url, dst)
        if not ok or _first_bytes_html(dst):
            status = "FAIL_HTML" if ok else "FAIL"
            log_row({"site": site, "product_id": pid, "url": url,
                     "status": status, "note": msg})
            n_fail += 1
            print(f"[{status.lower()}] {site}/{pid} {msg}", flush=True)
            continue
        size = dst.stat().st_size
        sha = _sha256_of_file(dst)
        total_bytes += size
        n_ok += 1
        fetched[pid] = dst
        # detached PDS3 label (tiny, best-effort)
        lbl_ok, _ = curl_download(r["lbl_url"], dst.with_suffix(".LBL"))
        log_row({"site": site, "product_id": pid, "url": url, "status": "OK",
                 "size_bytes": size, "sha256": sha,
                 "note": f"lbl={'ok' if lbl_ok else 'miss'}"})
        print(f"[ok] {site}/{pid} {size} B sha={sha[:12]} "
              f"(lbl {'ok' if lbl_ok else 'MISS'})", flush=True)
        # fill size/sha back into the selection CSV row
        r["size_bytes"], r["sha256"] = size, sha

    # rewrite CSV with size/sha filled in
    with open(SELECTION_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["site", "product_id", "incidence_deg", "emission_deg",
                    "resolution_m", "acquisition_time", "size_bytes",
                    "sha256", "local_path", "pds_url"])
        for r in selection:
            local = EDR_ROOT / r["site"] / f"{r['pid']}.IMG"
            w.writerow([r["site"], r["pid"],
                        f"{r['incidence_deg']:.2f}", f"{r['emission_deg']:.2f}",
                        f"{r['resolution_m']:.4f}", r["acquisition_time"],
                        r.get("size_bytes", ""), r.get("sha256", ""),
                        local, r["edr_url"]])

    print(f"\n[done] ok={n_ok} skip={n_skip} fail={n_fail} "
          f"bytes={total_bytes/1024**3:.2f} GiB; "
          f"disk free now {_disk_free_gb():.1f} GB", flush=True)
    print(f"[log] {FETCH_LOG}", flush=True)
    print(f"[csv] {SELECTION_CSV}", flush=True)
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
