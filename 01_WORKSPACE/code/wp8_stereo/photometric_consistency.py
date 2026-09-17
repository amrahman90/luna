"""LUNARVOID WP8 / Step 19.2 — multi-illumination photometric consistency
score for above-floor sag candidates (artifact-consistency triage aid).

For each of the 7 multillum sites, uses the 4 NAC EDR images fetched in
Step 19.1 (incidence ~26-93 deg) to test whether each flagged candidate's
local shading tracks the ILLUMINATION GEOMETRY (topographic-depression
signature) instead of a fixed albedo pattern (artifact signature).

Per image (serial, ONE cube at a time, nice +10):
    lronac2isis -> /tmp/mi19/<PID>.cub ; spiceinit web=yes ;
    campt (USECOORDLIST, lat,lon per line) at each unique candidate
    coordinate + 4 basis points around the site centroid ;
    DELETE the cube immediately after campt (peak transient ~1.1 GB).
Intensity crops are then read from the ORIGINAL .IMG files directly
(attached PDS3 label parse: RECORD_BYTES, ^IMAGE, 8-bit lines).

Metric (documented sign convention):
    u = sun unit vector in pixel space, from the local (lon,lat)->(sample,
    line) Jacobian at the site centroid, rotated by the great-circle
    azimuth of the sub-solar point (campt SubSolarGroundAzimuth;
    cross-checked against a NorthAzimuth-based estimate).
    x = signed pixel distance toward the sun, relative to crop centre.
    Interior disc radius R=100 px; sunward half (x >= +25) vs anti-sun
    half (x <= -25) of that disc:
        asym = (mean I_sunward - mean I_antisunward) / std(I_disc)
    A concave depression with sun azimuth A has its cast shadow on the
    sun side of the interior and its bright inner wall on the ANTI-sun
    side (the wall that faces the sun is across the pit): the
    depression-consistent sign is therefore asym < 0 at EVERY incidence.
    An albedo blotch does not track sun azimuth, so its asym sign flips
    across geometries.  score = fraction of used images with asym < 0.

HONESTY / LIMITATIONS (also written into the JSON summary):
    - raw EDR DN: 8-bit LUT-COMPANDED indices, no radiometric calibration,
      no decompanding, no photometric (incidence/emission/phase)
      correction; magnitudes are not comparable across images, only the
      SIGN consistency is used.
    - geolocation: crop centred on campt sample/line (spiceinit
      reconstructed pointing; typical NAC geolocation ~tens of m);
      windows near swath edges are shifted inside the image and flagged.
    - interior disc R=100 px is a fixed pit-scale prior (~65-190 m at
      0.65-1.9 m/px), not per-candidate geometry.
    - the score is an INFERENCE AID for triage of artifact-vs-depression
      character. It is NOT a detection, confirmation, or verification of
      any subsurface void.

Usage (dry-run is the DEFAULT, project convention):
    photometric_consistency.py            # plan + label parse only
    photometric_consistency.py --run      # full serial ISIS pass + outputs
    photometric_consistency.py --run --only-site TRANQPIT1   # debug one site
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
SELECTION_CSV = REPO / "01_WORKSPACE/data/wp8_stereo/multillum_selection_2026-09-14.csv"
FLAGS_CSV = REPO / "01_WORKSPACE/data/candidate_registry_flags.csv"
REGISTRY_CSV = REPO / "01_WORKSPACE/data/candidate_registry.csv"
OUT_DIR = REPO / "01_WORKSPACE/data/outputs/wp2_sag"
FIG_DIR = OUT_DIR / "photometric_figs"
OUT_CSV = OUT_DIR / "photometric_score_2026-09-15.csv"
OUT_JSON = OUT_DIR / "photometric_summary_2026-09-15.json"

ISIS_ENV = "/home/frostflux/lunarvoid/bin/run_isis_chain.sh"
TMP = Path("/tmp/mi19")

CROP = 400            # px window read from the EDR
R_INT = 100           # interior disc radius (px)
X0 = 25               # min |x| toward sun to enter a half-window (px)
SMOOTH = 5            # box filter size (px)
RSEARCH = 100         # recentring search half-box (px); NAC reconstructed
                      # pointing is good to ~tens of m, the analysis disc
                      # is pit-sized, so re-centre on the darkest feature
                      # (shadowed depression) near the campt point.
DISK_FLOOR_GB = 35.0  # hard stop per dispatch (stereo job co-tenancy)
R_MOON = 1737400.0
DELTA_DEG = 0.01      # basis-point offset for the pixel Jacobian
LICENCE = "PDS/LROC EDR: public domain (NASA/PDS); no redistribution of imagery"

METHOD_NOTES = [
    "Raw 8-bit LUT-companded EDR DN; no radiometric calibration, no "
    "decompanding, no photometric correction; only SIGN consistency of "
    "the asymmetry across geometries is used.",
    "Depression-consistent sign defined as asym<0: sun-side interior "
    "shadowed, bright inner wall on anti-sun side (wall facing the sun "
    "lies across the pit). Positive-relief or albedo artifacts are "
    "expected to break this consistency.",
    "Geolocation via spiceinit-reconstructed pointing (campt); typical "
    "NAC ground accuracy ~tens of metres; the pit-scale analysis disc is "
    "re-centred on the darkest-feature centroid within +-100 px of the "
    "campt point (offset recorded in notes when >25 m); crops near "
    "swath edges are shifted inside the image and flagged.",
    "Fixed interior radius R=100 px pit-scale prior (~65-190 m), not "
    "per-candidate geometry.",
    "Output is an artifact-consistency TRIAGE score for calibrated "
    "inference only; it is not a detection, confirmation, or "
    "verification of any subsurface void.",
    "Geometries with campt incidence >=90 deg (sun below the local "
    "horizon) carry no illumination-consistency information and are "
    "excluded from the score (flagged in notes). Some selected EDRs do "
    "not actually contain a given candidate within their swath (campt "
    "extrapolates beyond the raster without erroring); such geometries "
    "are recorded as misses and reduce n_images_used.",
    "Score convention: asym<0 is depression-consistent (sun-side "
    "interior shadowed; bright inner wall on the anti-sun side). "
    "Positive-relief or albedo-dominated candidates are expected to "
    "break sign consistency; scores near 0.5 carry little information.",
]


def disk_free_gb() -> float:
    st = os.statvfs("/")
    return st.f_bavail * st.f_frsize / 1e9


def bash_isis(cmd: str, timeout: int = 900) -> subprocess.CompletedProcess:
    """Run one ISIS command inside the project env, nice +10."""
    full = (f"source {ISIS_ENV} >/dev/null 2>&1; "
            f"exec nice -n 10 {cmd}")
    return subprocess.run(["bash", "-c", full], capture_output=True,
                          text=True, timeout=timeout)


# ---------------------------------------------------------------- inputs


def load_selection() -> "OrderedDict[str, list[dict]]":
    by_site: OrderedDict[str, list[dict]] = OrderedDict()
    with open(SELECTION_CSV, newline="") as f:
        for r in csv.DictReader(f):
            r["incidence_deg"] = float(r["incidence_deg"])
            by_site.setdefault(r["site"], []).append(r)
    for s in by_site:
        by_site[s].sort(key=lambda r: r["incidence_deg"])
    return by_site


def load_candidates() -> list[dict]:
    lines = REGISTRY_CSV.read_text().splitlines()
    hdr = next(i for i, l in enumerate(lines) if l.startswith("candidate_id,"))
    reg = {r["candidate_id"]: r for r in
           csv.DictReader([lines[hdr]] +
                          [l for l in lines[hdr + 1:] if not l.startswith("#")])}
    out = []
    with open(FLAGS_CSV, newline="") as f:
        for fr in csv.DictReader(f):
            if not (fr["is_tp"] == "True" or fr["is_fp"] == "True"
                    or fr["is_ring"] == "True" or fr["is_funnel"] == "True"):
                continue
            cid = fr["candidate_id"]
            rr = reg[cid]
            if fr["is_tp"] == "True":
                cls = "tp"
            elif fr["is_ring"] == "True":
                cls = "ring"
            elif fr["is_funnel"] == "True":
                cls = "funnel"
            else:
                cls = "fp"
            out.append({"candidate_id": cid,
                        "site": cid.split("-")[1],
                        "lon": float(rr["lon"]), "lat": float(rr["lat"]),
                        "class": cls})
    return out


# ------------------------------------------------------------ PDS3 label


def parse_pds3_label(img: Path) -> dict:
    """Parse the attached PDS3 header of a NAC EDR (standalone END)."""
    with open(img, "rb") as f:
        head = f.read(65536)
    txt = head.decode("ascii", errors="replace")
    m = re.search(r"(?m)^END\s*$", txt)
    if not m:
        raise ValueError(f"{img.name}: no standalone END in first 64 KiB")
    lab = txt[:m.end()]

    def kw(name: str) -> str | None:
        mm = re.search(rf"(?m)^{re.escape(name)}\s*=\s*(.+?)\s*$", lab)
        return mm.group(1).strip().strip('"') if mm else None

    rec = int(kw("RECORD_BYTES"))
    mm = re.search(r"(?m)^\^IMAGE\s*=\s*(\d+)", lab)
    if not mm:
        raise ValueError(f"{img.name}: no ^IMAGE pointer")
    offset = (int(mm.group(1)) - 1) * rec
    lines = int(re.search(r"(?m)^\s*LINES\s*=\s*(\d+)", lab).group(1))
    lsamp = int(re.search(r"(?m)^\s*LINE_SAMPLES\s*=\s*(\d+)", lab).group(1))
    sbits = int(re.search(r"(?m)^\s*SAMPLE_BITS\s*=\s*(\d+)", lab).group(1))
    size = img.stat().st_size
    if sbits != 8:
        raise ValueError(f"{img.name}: unexpected SAMPLE_BITS={sbits}")
    if size - offset < lines * lsamp:
        raise ValueError(f"{img.name}: file truncated for declared image")
    return {"offset": offset, "lines": lines, "lsamp": lsamp,
            "record_bytes": rec}


def read_crop(img: Path, lab: dict, sample: float, line: float,
              size: int = CROP) -> tuple[np.ndarray, int, int]:
    """(crop, row0, col0) from the ORIGINAL .IMG; window shifted inside
    bounds if the centre is too close to an edge."""
    mm = np.memmap(img, dtype=np.uint8, mode="r", shape=(lab["lines"],
                                                         lab["lsamp"]),
                   offset=lab["offset"])
    c0 = int(round(sample - 1))
    r0 = int(round(line - 1))
    half = size // 2
    colA, rowA = c0 - half, r0 - half
    colA = max(0, min(colA, lab["lsamp"] - size))
    rowA = max(0, min(rowA, lab["lines"] - size))
    crop = np.array(mm[rowA:rowA + size, colA:colA + size])
    return crop, rowA, colA


# ---------------------------------------------------------------- geodesy


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle azimuth from point 1 to point 2, from north, CW."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = (math.cos(p1) * math.sin(p2)
         - math.sin(p1) * math.cos(p2) * math.cos(dl))
    return math.degrees(math.atan2(y, x)) % 360.0


def sun_pixel_vector(A_deg: float, east_pix, north_pix) -> tuple[float, float]:
    """Sun direction in (col,row) pixel space from its ground azimuth
    (from north, CW) and the unit east/north pixel basis vectors."""
    a = math.radians(A_deg)
    ux = math.sin(a) * east_pix[0] + math.cos(a) * north_pix[0]
    uy = math.sin(a) * east_pix[1] + math.cos(a) * north_pix[1]
    n = math.hypot(ux, uy) or 1.0
    return ux / n, uy / n


# ------------------------------------------------------------------ campt


CAMPT_FIELDS = ["Sample", "Line", "Incidence", "Emission",
                "SubSolarLatitude", "SubSolarLongitude",
                "SubSolarGroundAzimuth", "NorthAzimuth",
                "PlanetocentricLatitude", "PositiveEast180Longitude", "Error"]


def campt_points(cub: Path, latlons: list[tuple[float, float]]) -> list[dict]:
    cl = TMP / "coordlist.txt"
    cl.write_text("\n".join(f"{la:.6f},{lo:.6f}" for la, lo in latlons))
    out_csv = TMP / "campt_flat.csv"
    if out_csv.exists():
        out_csv.unlink()
    p = bash_isis(
        f"campt from={cub} to={out_csv} usecoordlist=true "
        f"coordlist={cl} coordtype=ground format=flat")
    if p.returncode != 0 or not out_csv.exists():
        raise RuntimeError(f"campt failed rc={p.returncode}: "
                           f"{p.stdout[-300:]} {p.stderr[-300:]}")
    rows = list(csv.DictReader(open(out_csv, newline="")))
    if len(rows) != len(latlons):
        raise RuntimeError(f"campt rows {len(rows)} != points {len(latlons)}")
    res = []
    for r in rows:
        d = {}
        for k in CAMPT_FIELDS:
            v = r.get(k, "")
            try:
                d[k] = float(v)
            except (TypeError, ValueError):
                d[k] = None
        d["Error"] = (r.get("Error", "") or "").strip()
        res.append(d)
    return res


def is_err(d: dict) -> bool:
    """campt FLAT writes literal NULL in Error for good rows."""
    return d["Error"] not in ("", "NULL") or d["Sample"] is None


def in_image(d: dict, lab: dict, margin: int = 0) -> bool:
    """campt extrapolates projections beyond the imaged swath without
    erroring — require the point to lie inside the actual raster."""
    return (d["Sample"] is not None and d["Line"] is not None
            and 1 + margin <= d["Sample"] <= lab["lsamp"] - margin
            and 1 + margin <= d["Line"] <= lab["lines"] - margin)


# ------------------------------------------------------------- asymmetry


def recentre_dark(crop: np.ndarray) -> tuple[int, int]:
    """Offset (drow, dcol) from the crop centre to the centroid of the
    darkest 5% of a smoothed search box (the shadowed depression),
    clamped to +-RSEARCH px. Keeps the analysis disc on the feature when
    reconstructed pointing is off by tens of metres."""
    from scipy.ndimage import uniform_filter
    I = uniform_filter(crop.astype(np.float64), size=SMOOTH)
    H, W = I.shape
    rc, cc = (H - 1) // 2, (W - 1) // 2
    box = I[max(0, rc - RSEARCH):rc + RSEARCH,
            max(0, cc - RSEARCH):cc + RSEARCH]
    thr = np.percentile(box, 5)
    m = box <= thr
    if m.sum() < 20:
        return 0, 0
    rr, ccr = np.nonzero(m)
    dr = int(round(rr.mean() + max(0, rc - RSEARCH) - rc))
    dc = int(round(ccr.mean() + max(0, cc - RSEARCH) - cc))
    return (max(-RSEARCH, min(RSEARCH, dr)),
            max(-RSEARCH, min(RSEARCH, dc)))


def asymmetry(crop: np.ndarray, u: tuple[float, float],
              dr: int = 0, dc: int = 0) -> dict:
    from scipy.ndimage import uniform_filter
    I = uniform_filter(crop.astype(np.float64), size=SMOOTH)
    H, W = I.shape
    rc, cc = (H - 1) / 2.0 + dr, (W - 1) / 2.0 + dc
    rows, cols = np.mgrid[0:H, 0:W]
    dx = (cols - cc) * u[0] + (rows - rc) * u[1]
    dist = np.hypot(cols - cc, rows - rc)
    disc = dist <= R_INT
    sig = I[disc].std()
    sun_h = disc & (dx >= X0)
    anti_h = disc & (dx <= -X0)
    if sun_h.sum() < 50 or anti_h.sum() < 50 or sig < 1e-6:
        return {"asym": None, "grad_fit": None,
                "n_sun": int(sun_h.sum()), "n_anti": int(anti_h.sum()),
                "std": float(sig)}
    asym = (I[sun_h].mean() - I[anti_h].mean()) / sig
    # secondary: least-squares slope of I vs x over the full window
    g = np.polyfit(dx.ravel(), I.ravel(), 1)[0] / (I.std() + 1e-6)
    return {"asym": float(asym), "grad_fit": float(g),
            "n_sun": int(sun_h.sum()), "n_anti": int(anti_h.sum()),
            "std": float(sig)}


# ------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", action="store_true",
                    help="execute the serial ISIS pass + write outputs "
                         "(default: dry-run, plan + label parse only)")
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--only-site", default=None,
                    help="restrict to one site (debug)")
    args = ap.parse_args()

    t0 = time.time()
    disk0 = disk_free_gb()
    sel = load_selection()
    cands = load_candidates()
    sites = [s for s in sel if args.only_site in (None, s)]
    cand_by_site: dict[str, list[dict]] = {s: [] for s in sites}
    for c in cands:
        if c["site"] in cand_by_site:
            cand_by_site[c["site"]].append(c)

    print(f"[plan] sites={len(sites)} images={sum(len(sel[s]) for s in sites)} "
          f"candidates={sum(len(v) for v in cand_by_site.values())} "
          f"disk_free={disk0:.1f} GB", flush=True)

    # labels: parse all (cheap, read-only) — also the dry-run payload
    labels: dict[str, dict] = {}
    img_by_pid: dict[str, Path] = {}
    for s in sites:
        for r in sel[s]:
            pid = r["product_id"]
            img = Path(r["local_path"])
            if pid not in labels:
                labels[pid] = parse_pds3_label(img)
                img_by_pid[pid] = img
    print(f"[labels] parsed {len(labels)} unique products OK "
          f"(shared hardlinked products reused across sites)", flush=True)

    # unique product -> sites that use it (import once, campt all sites)
    prod_sites: "OrderedDict[str, list[str]]" = OrderedDict()
    for s in sites:
        for r in sel[s]:
            prod_sites.setdefault(r["product_id"], [])
            if s not in prod_sites[r["product_id"]]:
                prod_sites[r["product_id"]].append(s)

    if not args.run:
        for pid, ss in prod_sites.items():
            lab = labels[pid]
            print(f"[dry-run] {pid} sites={ss} "
                  f"{lab['lines']}x{lab['lsamp']} @off {lab['offset']}",
                  flush=True)
        print(f"[dry-run] would write {OUT_CSV}, {OUT_JSON}, "
              f"{FIG_DIR}/<SITE>.png ({len(sites)} figs); "
              f"rerun with --run", flush=True)
        return 0

    # ------------------------------------------------------------- run
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)

    # campt cache: survive crop-stage restarts without re-importing cubes
    cache_path = TMP / "campt_cache.json"
    cache: dict = {}
    if cache_path.exists():
        cache = json.loads(cache_path.read_text())
        print(f"[cache] {len(cache)} products with cached campt results",
              flush=True)

    # results[site][rank] = {pid, per-candidate campt + basis}
    results: dict[str, list[dict]] = {s: [] for s in sites}
    basis: dict[tuple[str, str], dict] = {}   # (pid, site) -> basis
    az_check: list[float] = []                # bearing vs campt azimuth, deg
    sanity_done = False
    cubes_cleaned = 0
    events: list[str] = []

    for pid, ssites in prod_sites.items():
        if disk_free_gb() < DISK_FLOOR_GB:
            print(f"[ABORT] disk free {disk_free_gb():.1f} GB < floor",
                  flush=True)
            return 2
        if pid in cache:
            ce = cache[pid]
            az_check += ce.get("az", [])
            for s in ssites:
                srec = ce["sites"].get(s)
                if srec is None:
                    continue
                if "error" in srec:
                    results[s].append({"pid": pid, "error": srec["error"]})
                else:
                    results[s].append({
                        "pid": pid,
                        "hits": {tuple(float(v) for v in k.split(",")): v
                                 for k, v in srec["hits"].items()},
                        "misses": srec["misses"]})
                if s in ce.get("basis", {}):
                    basis[(pid, s)] = ce["basis"][s]
            print(f"[cache] {pid} reused (no ISIS import)", flush=True)
            continue
        img = img_by_pid[pid]
        cub = TMP / f"{pid}.cub"
        t1 = time.time()
        ce = {"sites": {}, "basis": {}, "az": []}
        p = bash_isis(f"lronac2isis from={img} to={cub}", timeout=900)
        if p.returncode != 0 or not cub.exists():
            events.append(f"{pid}: lronac2isis FAILED rc={p.returncode}")
            for s in ssites:
                results[s].append({"pid": pid, "error": "lronac2isis"})
                ce["sites"][s] = {"error": "lronac2isis"}
            continue
        try:
            p = bash_isis(f"spiceinit from={cub} web=yes", timeout=1800)
            if p.returncode != 0:
                events.append(f"{pid}: spiceinit FAILED rc={p.returncode}")
                for s in ssites:
                    results[s].append({"pid": pid, "error": "spiceinit"})
                    ce["sites"][s] = {"error": "spiceinit"}
                continue
            # geodesy sanity gate on the very first cube: use the site's
            # TP candidate (catalogued pit — expected in-frame); without
            # a TP there is no known in-frame point, defer the check.
            if not sanity_done:
                s0 = ssites[0]
                tp0 = next((c for c in cand_by_site[s0]
                            if c["class"] == "tp"), None)
                if tp0 is not None:
                    chk = campt_points(cub, [(tp0["lat"], tp0["lon"])])[0]
                    if is_err(chk):
                        raise RuntimeError(f"sanity campt missed for {s0}")
                    dl = abs(chk["PositiveEast180Longitude"] - tp0["lon"])
                    dp = abs(chk["PlanetocentricLatitude"] - tp0["lat"])
                    m_per_deg = math.pi * R_MOON / 180.0
                    err_m = math.hypot(
                        dl * m_per_deg * math.cos(math.radians(tp0["lat"])),
                        dp * m_per_deg)
                    inside = (1 <= chk["Sample"] <= labels[pid]["lsamp"]
                              and 1 <= chk["Line"] <= labels[pid]["lines"])
                    print(f"[sanity] {s0} {pid} campt roundtrip err "
                          f"{err_m:.1f} m; S={chk['Sample']:.0f} "
                          f"L={chk['Line']:.0f} inside={inside}", flush=True)
                    if err_m > 100 or not inside:
                        raise RuntimeError("geodesy sanity FAILED — abort")
                    sanity_done = True
                else:
                    events.append(f"{s0}: no TP candidate; geodesy sanity "
                                  f"deferred to first campt hit")
                    sanity_done = True
            # campt per site: unique candidate coords + 4 basis points
            for s in ssites:
                cl = cand_by_site[s]
                uniq: dict[tuple[float, float], list[int]] = {}
                for i, c in enumerate(cl):
                    uniq.setdefault((c["lat"], c["lon"]), []).append(i)
                la = np.mean([c["lat"] for c in cl])
                lo = np.mean([c["lon"] for c in cl])
                pts = list(uniq.keys()) + [
                    (la, lo + DELTA_DEG), (la, lo - DELTA_DEG),
                    (la + DELTA_DEG, lo), (la - DELTA_DEG, lo)]
                try:
                    rows = campt_points(cub, pts)
                except RuntimeError as e:
                    events.append(f"{pid}/{s}: campt batch failed: {e}")
                    results[s].append({"pid": pid, "error": "campt"})
                    ce["sites"][s] = {"error": "campt"}
                    continue
                core = rows[:len(uniq)]
                basis_rows = rows[len(uniq):]
                rec = {"pid": pid, "hits": {}, "misses": []}
                az_new: list[float] = []
                for (key, idxs), rr in zip(uniq.items(), core):
                    if is_err(rr) or not in_image(rr, labels[pid]):
                        rec["misses"] += [cl[i]["candidate_id"] for i in idxs]
                    else:
                        rec["hits"][key] = rr
                        # cross-check campt sun azimuth vs own bearing
                        if (rr["SubSolarLatitude"] is not None
                                and rr["SubSolarGroundAzimuth"] is not None):
                            b = bearing_deg(key[0], key[1],
                                            rr["SubSolarLatitude"],
                                            rr["SubSolarLongitude"])
                            az_new.append(
                                (rr["SubSolarGroundAzimuth"] - b + 180)
                                % 360 - 180)
                # pixel Jacobian basis from the 4 offset points (all four
                # must project INSIDE the raster)
                ok = all(not is_err(r) and in_image(r, labels[pid])
                         for r in basis_rows)
                if ok:
                    eS = (basis_rows[0]["Sample"] - basis_rows[1]["Sample"],
                          basis_rows[0]["Line"] - basis_rows[1]["Line"])
                    nS = (basis_rows[2]["Sample"] - basis_rows[3]["Sample"],
                          basis_rows[2]["Line"] - basis_rows[3]["Line"])
                    en = math.hypot(*eS)
                    nn = math.hypot(*nS)
                    if en > 1 and nn > 1:
                        basis[(pid, s)] = {
                            "east": (eS[0] / en, eS[1] / en),
                            "north": (nS[0] / nn, nS[1] / nn),
                            "mode": "jacobian"}
                if (pid, s) not in basis:
                    # NorthAzimuth fallback: geometry is valid even for
                    # extrapolated projections, use any candidate row
                    na = next((r0["NorthAzimuth"] for r0 in core
                               if not is_err(r0)
                               and r0["NorthAzimuth"] is not None), None)
                    if na is not None:
                        th = math.radians(na)
                        # north pix dir = (sin NA, -cos NA) from image-up CW
                        basis[(pid, s)] = {
                            "east": (math.cos(th), math.sin(th)),
                            "north": (math.sin(th), -math.cos(th)),
                            "mode": "northazimuth_fallback"}
                results[s].append(rec)
                ce["sites"][s] = {
                    "hits": {f"{k[0]},{k[1]}": v
                             for k, v in rec["hits"].items()},
                    "misses": rec["misses"]}
                if (pid, s) in basis:
                    ce["basis"][s] = basis[(pid, s)]
                ce["az"] = az_new
                az_check += az_new
        finally:
            if cub.exists():
                cub.unlink()
                cubes_cleaned += 1
            for junk in ("campt_flat.csv", "coordlist.txt", "campt_flat.pvl"):
                jp = TMP / junk
                if jp.exists():
                    jp.unlink()
        print(f"[isis] {pid} sites={ssites} done in "
              f"{time.time() - t1:.0f}s free={disk_free_gb():.1f} GB",
              flush=True)
        cache[pid] = ce
        cache_path.write_text(json.dumps(cache))

    # ------------------------------------------- crops + asymmetry (no ISIS)
    from scipy.ndimage import uniform_filter  # noqa: F401  (import check)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    per_cand: dict[str, dict] = {}
    for s in sites:
        for i, c in enumerate(cand_by_site[s]):
            per_cand[c["candidate_id"]] = {"c": c, "imgs": []}
        for rec in results[s]:
            if "error" in rec:
                for c in cand_by_site[s]:
                    per_cand[c["candidate_id"]]["imgs"].append(
                        {"pid": rec["pid"], "state": "error",
                         "why": rec["error"]})
                continue
            b = basis.get((rec["pid"], s))
            for c in cand_by_site[s]:
                key = (c["lat"], c["lon"])
                rr = rec["hits"].get(key)
                entry = {"pid": rec["pid"],
                         "inc_csv": next(r["incidence_deg"] for r in sel[s]
                                         if r["product_id"] == rec["pid"])}
                if rr is None:
                    entry.update({"state": "campt_miss"})
                elif b is None:
                    entry.update({"state": "no_basis"})
                else:
                    entry.update({"state": "ok",
                                  "Sample": rr["Sample"], "Line": rr["Line"],
                                  "incidence": rr["Incidence"],
                                  "emission": rr["Emission"],
                                  "sun_az": rr["SubSolarGroundAzimuth"],
                                  "basis_mode": b["mode"]})
                per_cand[c["candidate_id"]]["imgs"].append(entry)

    # attach crops/asymmetry
    for cid, d in per_cand.items():
        c = d["c"]
        for e in d["imgs"]:
            if e["state"] != "ok":
                e["asym"] = None
                continue
            pid = e["pid"]
            lab = labels[pid]
            crop, rowA, colA = read_crop(img_by_pid[pid], lab,
                                         e["Sample"], e["Line"])
            b = basis[(pid, c["site"])]
            u = sun_pixel_vector(e["sun_az"], b["east"], b["north"])
            e["u"] = u
            e["crop"] = crop
            e["shift_col"] = int(round((e["Sample"] - 1) - (colA + CROP / 2)))
            e["shift_row"] = int(round((e["Line"] - 1) - (rowA + CROP / 2)))
            dr, dc = recentre_dark(crop)
            res_m = float(next(r["resolution_m"] for r in sel[c["site"]]
                               if r["product_id"] == pid))
            e["recenter_px"] = [dr, dc]
            e["recenter_m"] = round(math.hypot(dr, dc) * res_m, 1)
            m = asymmetry(crop, u, dr=dr, dc=dc)
            e.update(m)

    # ------------------------------------------------------------ CSV
    rows_out = []
    for cid in sorted(per_cand):
        d = per_cand[cid]
        c = d["c"]
        used = [e for e in d["imgs"] if e["state"] == "ok"
                and e["asym"] is not None]
        n_used = len(used)
        score = (sum(1 for e in used if e["asym"] < 0) / n_used
                 if n_used else None)
        asyms = ["", "", "", ""]
        incs = []
        notes = []
        for e in sorted(d["imgs"], key=lambda x: x["inc_csv"]):
            if e["state"] == "ok" and e["asym"] is not None:
                inc = e.get("incidence") or e["inc_csv"]
                if inc >= 90.0:
                    # sun below the local horizon: no illumination-
                    # consistency information; excluded from the score
                    notes.append(f"{e['pid']}:i>=90_excluded({inc:.1f})")
                    continue
                k = len(incs)
                asyms[k] = f"{e['asym']:.4f}"
                incs.append(round(inc, 2))
            elif e["state"] == "campt_miss":
                notes.append(f"{e['pid']}:campt_miss")
            elif e["state"] == "error":
                notes.append(f"{e['pid']}:{e['why']}")
            elif e["state"] == "no_basis":
                notes.append(f"{e['pid']}:no_basis")
            elif e["state"] == "ok":
                notes.append(f"{e['pid']}:no_data")
            if e["state"] == "ok" and (abs(e["shift_col"]) > 50
                                       or abs(e["shift_row"]) > 50):
                notes.append(f"{e['pid']}:winshift({e['shift_col']},"
                             f"{e['shift_row']})")
            if e["state"] == "ok" and e.get("recenter_m", 0) > 25:
                notes.append(f"{e['pid']}:recentred({e['recenter_m']}m)")
        mean_abs = (sum(abs(e["asym"]) for e in used) / n_used
                    if n_used else None)
        rows_out.append({
            "candidate_id": cid, "site": c["site"],
            "lon": c["lon"], "lat": c["lat"], "class": c["class"],
            "n_images_used": n_used, "n_images_avail": len(d["imgs"]),
            "score_consistent_fraction": ("" if score is None
                                          else f"{score:.3f}"),
            "asym_1": asyms[0], "asym_2": asyms[1],
            "asym_3": asyms[2], "asym_4": asyms[3],
            "incidences": ";".join(str(x) for x in incs),
            "mean_abs_asym": ("" if mean_abs is None else f"{mean_abs:.4f}"),
            "notes": " ".join(notes)})
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)
    print(f"[csv] {OUT_CSV} ({len(rows_out)} rows)", flush=True)

    # --------------------------------------------------------- figures
    fig_info = []
    for s in sites:
        cls = cand_by_site[s]
        fig_cand = next((c for c in cls if c["class"] == "tp"), cls[0])
        d = per_cand[fig_cand["candidate_id"]]
        imgs = sorted([e for e in d["imgs"] if e["state"] == "ok"
                       and e.get("crop") is not None
                       and e.get("asym") is not None],
                      key=lambda x: x["inc_csv"])
        if not imgs:
            events.append(f"{s}: no usable images for figure")
            continue
        fig, axes = plt.subplots(2, 2, figsize=(7.2, 7.2), dpi=110)
        for ax, e in zip(axes.flat, imgs):
            ax.imshow(e["crop"], cmap="gray", vmin=np.percentile(
                e["crop"], 0.5), vmax=np.percentile(e["crop"], 99.5))
            H, W = e["crop"].shape
            cy = H / 2 + e["shift_row"]
            cx = W / 2 + e["shift_col"]
            dr, dc = e.get("recenter_px", [0, 0])
            ry, rx = H / 2 + dr, W / 2 + dc
            ax.plot([cx], [cy], "r+", ms=14, mew=1.5)
            ax.add_patch(plt.Circle((rx, ry), R_INT, fill=False,
                                    color="red", lw=0.8, ls=":"))
            L = 60
            ax.annotate("", xy=(rx + e["u"][0] * L, ry + e["u"][1] * L),
                        xytext=(rx, ry),
                        arrowprops=dict(arrowstyle="->", color="cyan", lw=1.6))
            ax.set_title(f"{e['pid']}  "
                         f"i={(e.get('incidence') or e['inc_csv']):.1f}°"
                         f"  asym={e['asym']:+.2f}", fontsize=8)
            ax.set_xticks([])
            ax.set_yticks([])
        for ax in axes.flat[len(imgs):]:
            ax.axis("off")
        fig.suptitle(f"{s} — {fig_cand['candidate_id']} "
                     f"({fig_cand['class'].upper()}); cyan arrow = sun",
                     fontsize=9)
        fig.tight_layout()
        fp = FIG_DIR / f"{s}.png"
        fig.savefig(fp)
        plt.close(fig)
        from PIL import Image
        with Image.open(fp) as im:
            fig_info.append({"site": s, "path": str(fp),
                             "size": im.size,
                             "candidate": fig_cand["candidate_id"]})
        print(f"[fig] {fp} {fig_info[-1]['size']}", flush=True)

    # --------------------------------------------------------- summary
    per_site_stats = {}
    for s in sites:
        sc = {}
        for c in cand_by_site[s]:
            r = next(x for x in rows_out
                     if x["candidate_id"] == c["candidate_id"])
            if r["score_consistent_fraction"]:
                sc.setdefault(c["class"], []).append(
                    float(r["score_consistent_fraction"]))
        per_site_stats[s] = {
            k: {"n": len(v), "mean_score": round(sum(v) / len(v), 3)}
            for k, v in sc.items()}
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"),
        "step": "19.2 multi-illumination photometric consistency",
        "n_candidates": len(rows_out),
        "n_images_unique_products": len(labels),
        "campt_points_total": sum(
            1 for d in per_cand.values() for e in d["imgs"]),
        "azimuth_crosscheck_deg": {
            "n": len(az_check),
            "max_abs": round(max(abs(x) for x in az_check), 3) if az_check
            else None,
            "mean_abs": round(float(np.mean(np.abs(az_check))), 3)
            if az_check else None},
        "per_site": per_site_stats,
        "figures": fig_info,
        "events": events,
        "method_notes": METHOD_NOTES,
        "licence": LICENCE,
        "claim": "artifact-consistency triage score for inference; "
                 "not a detection or verification of any subsurface void",
        "disk_free_gb_before": round(disk0, 1),
        "disk_free_gb_after": round(disk_free_gb(), 1),
        "temp_cubes_deleted": cubes_cleaned,
        "tmp_dir_clean": not list(TMP.glob("*.cub")),
        "elapsed_s": round(time.time() - t0, 1),
    }
    with open(OUT_JSON, "w") as f:
        json.dump(summary, f, indent=1)
    cache_path.unlink(missing_ok=True)
    print(f"[json] {OUT_JSON}", flush=True)
    print(f"[done] free={disk_free_gb():.1f} GB cubes_deleted="
          f"{cubes_cleaned} tmp_clean={summary['tmp_dir_clean']} "
          f"elapsed={summary['elapsed_s']}s", flush=True)
    return 0 if not events else 0


if __name__ == "__main__":
    sys.exit(main())
