#!/usr/bin/env python3
"""Regenerate LUNARVOID Obsidian site notes for the 21 on-disk NAC DTMs.

This is the anti-drift generator: every `sites/<NAME>.md` file in the
vault is rebuilt mechanically from canonical data sources, so that the
vault cannot drift from the registry, transfer summary, or per-DTM
floor tables.

Canonical sources read (in priority order):

  1. ``01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json``
     — per-DTM rung / candidate / FP / TP / top_score / area / FP-rate
     numbers; the `scope_banner` field explains deferred sites.
  2. ``01_WORKSPACE/data/outputs/wp0_kriging/per_dtm_floors_summary.json``
     — per-DTM pooled_rms_m (sag-band RMS), 3× sag-band RMS
     (``three_sigma_m``), terrain extrapolation annotations, skipped
     markers.
  3. ``01_WORKSPACE/data/candidate_registry.csv`` — per-DTM tier counts
     computed from registry rows (tier A is 0 by frozen P3.1c rule).
  4. ``01_WORKSPACE/data/MANIFEST.md`` — DTM source URL / SHA-256 /
     licence for the 10 legacy DTMs (the archivist's original entries).
  5. ``~/lunarvoid/data/fetch_log_lroc.csv`` — DTM source URL / SHA-256
     / licence for the 11 P3.1c-growth DTMs (newly fetched this cycle).
  6. ``01_WORKSPACE/notes/findings.md`` — visual-inspection backlog
     items and known skeptic flags (e.g. MARIUSPIT01 I14 funnel,
     FECUNPIT 138-552 m correction).

Output target: ``01_WORKSPACE/Lunar Lavatube knowledge/sites/<NAME>.md``
(21 files, exactly). The Obsidian vault MOCs (mocs/*), gates/*,
decisions/*, backlog/*, artifacts/*, concepts/*, refs/*, sessions/* are
NEVER touched. The MOC note that lists site links is regenerated only
manually (paper-writer dispatch B reconciled it separately).

Usage:

  ./01_WORKSPACE/code/tools/regen_site_notes.py --all            # default
  ./01_WORKSPACE/code/tools/regen_site_notes.py --site TRANQPIT1
  ./01_WORKSPACE/code/tools/regen_site_notes.py --dry-run --all
  ./01_WORKSPACE/code/tools/regen_site_notes.py --all --since 2026-08-22
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------- locate canonical sources (paths that work from anywhere) ----------

REPO = Path(__file__).resolve().parents[2]  # 01_WORKSPACE
WORKSPACE = REPO  # alias
HOME = Path.home()
LUNARVOID = HOME / "lunarvoid"

TRANSFER_SUMMARY = WORKSPACE / "data/outputs/wp2_sag/transfer/transfer_summary.json"
FLOORS_SUMMARY = WORKSPACE / "data/outputs/wp0_kriging/per_dtm_floors_summary.json"
FLOORS_CSV = WORKSPACE / "data/outputs/wp0_kriging/per_dtm_floors.csv"
REGISTRY = WORKSPACE / "data/candidate_registry.csv"
MANIFEST = WORKSPACE / "data/MANIFEST.md"
FINDINGS = WORKSPACE / "notes/findings.md"
FETCH_LOG = LUNARVOID / "data/fetch_log_lroc.csv"

VAULT = WORKSPACE / "Lunar Lavatube knowledge"
SITES_DIR = VAULT / "sites"
MOC_SITES = VAULT / "mocs" / "MOC Sites & Candidates.md"

# Sites that the canonical summaries say are deferred for memory,
# not for missing inputs. Updated 2026-08-23 after Cycle 2 (TYCHOPK
# ran successfully: 2+4+5 m rungs, no tile fallback needed; 6.8 GiB
# Python peak on 2 m rung, well within 31 GB RAM).
_TYCHOPK_MEMORY_CEILING = ""  # was "TYCHOPK" until Cycle 2 close
# Sites that scope_banner explicitly names as "skipped for missing
# score raster". Other sites run to completion. Updated 2026-08-23
# after Cycle 1 (GRUITHUIS17/GRUITHMARE2/MARIUSCONE all ran; score
# rasters at 4+5 m generated; 2 m rung skipped per v0.6 res guard).
_NO_CACHED_SCORE_RASTER = set()  # was {3 sites} until Cycle 1 close

# Visual-inspection backlog items curently in findings.md (verbatim
# cross-refs; the generator uses them so paper-writer dispatch B's
# writeup doesn't drift from this script's output).
BACKLOG_SITE_HINTS = {
    "FECUNPIT": (
        "3 unique large depressions at DTM north end (552.5 m for r001+r002 "
        "and 138.1 m for r003 from the nearest catalogued pit, not 67 km "
        "from the named Central Mare Fecunditatis Pit); amplitudes ~155 / "
        "140 / 34 m; rungs 4 m + 5 m; flagged requires_visual_inspection "
        "(verbal-only). r003 at 138 m is borderline-TP under a 150 m "
        "tolerance — would be reclassified if match-radius were relaxed, "
        "but the 100 m calibration is frozen."
    ),
    "TRANQPIT1": (
        "3 large-amplitude FPs (12-km scale; r001 95.4 m, r002 57.4 m, "
        "r003 48.8 m) at lat ~8.75 N, lon ~33.20 E. Registry notes flag "
        "possible floor-fractured crater rim / ejecta / modification. "
        "Cross-reference rows 73–75 (LV-TRANQPIT1-0500cm-r001/r002/r003). "
        "These are LARGE Mare Tranquillitatis features, not noise-spike FPs. "
        "Visual inspection REQUIRED before any G2 claim."
    ),
    "INGENIIPIT": (
        "Ring artifacts r002–r008 at 2/4/5 m rungs (23 rows total, all "
        "within ~10 km of r001). Registry notes flag 'ring artifact around "
        "catalogued pit r001; not an independent void candidate'. "
        "Visual inspection of the LROC NAC pair at the catalogued pit "
        "(lat ~-35.95, lon ~166.05) is required to confirm the ring "
        "pattern is detector-induced (Frangi filter artifact) and not "
        "a real void cluster."
    ),
    # Cycles 1-2 closures (2026-08-23, local Tier-1 plan)
    "TYCHOPK": (
        "Memory ceiling closed locally 2026-08-23 by Cycle 2: processed at "
        "2+4+5 m rungs (6.8 GiB Python peak, no tile fallback). 3 below-floor "
        "candidates (1 per rung); all classified terrain_extrapolation per "
        "TYCHOPK02/03/04/07 precedent (frangi@score=0.0185 at 18.35 m depth). "
        "0 FPs. NAC browse at lat ~-43.3° (Tycho central peak) recommended "
        "before any tier-B promotion. Science gate unchanged."
    ),
    "GRUITHUIS17": (
        "Cycle 1 close (2026-08-23): processed at 4+5 m rungs "
        "(FRESHMELT-style workflow; 2 m rung skipped per v0.6 res-compatibility "
        "guard — source res 5 m can't upsample). 6 below-floor candidates; "
        "all terrain_extrapolation (frangi@score=0.0424 > 0.02, NOT annotated "
        "deep-pit). 0 FPs."
    ),
    "GRUITHMARE2": (
        "Cycle 1 close (2026-08-23): processed at 4+5 m rungs. 10 below-floor "
        "candidates; all classified deep-pit low-vesselness (skeptic new rule: "
        "frangi@score=0.015 < 0.02 AND depth@score=604 m ≥ 100 m → circular "
        "depression, not tubular). NAC browse at 33.3943°N, -43.3329°W required "
        "before any tier-B promotion. See [[backlog/GRUITHMARE2 + MARIUSCONE "
        "deep-pit]] for browse targets. 0 FPs."
    ),
    "MARIUSCONE": (
        "Cycle 1 close (2026-08-23): processed at 4+5 m rungs. 2 below-floor "
        "candidates; both classified deep-pit low-vesselness (frangi@score=0.011 "
        "< 0.02 AND depth@score=619 m ≥ 100 m → circular depression, not "
        "tubular). Catalogued Marius Hills Pit is 17.9 km N (correctly NOT "
        "flagged, score 0.059). NAC browse at 13.6250°N, -56.3975°W required "
        "before any tier-B promotion. See [[backlog/GRUITHMARE2 + MARIUSCONE "
        "deep-pit]]. 0 FPs."
    ),
}


# ---------- formatting helpers ----------

def _fmt_float(x: Any, digits: int = 3) -> str:
    """Return a safe rendering of a float that may be NaN / None / 0."""
    if x is None:
        return "not reported"
    if isinstance(x, str):
        return x
    try:
        v = float(x)
    except (TypeError, ValueError):
        return "not reported"
    if math.isnan(v) or math.isinf(v):
        return "not reported"
    if v == 0:
        return "0"
    # small numbers: 3 sig figs; large: keep precision
    if abs(v) < 1:
        return f"{v:.{digits}f}"
    if abs(v) < 100:
        return f"{v:.{digits}f}"
    return f"{v:.2f}"


def _fmt_int(x: Any) -> str:
    if x is None:
        return "not reported"
    try:
        v = int(x)
    except (TypeError, ValueError):
        return "not reported"
    return str(v)


def _fmt_rungs(rungs: list[float]) -> str:
    """Render rungs as '2 m, 4 m, 5 m' (no brackets, comma-separated,
    trailing 'm' suffix on each rung)."""
    if not rungs:
        return "not reported"
    cleaned = []
    for r in rungs:
        if r is None:
            cleaned.append("—")
        else:
            try:
                v = float(r)
                if math.isnan(v):
                    cleaned.append("—")
                else:
                    # drop trailing .0 for whole numbers
                    cleaned.append(f"{v:g}")
            except (TypeError, ValueError):
                cleaned.append("—")
    return ", ".join(f"{x} m" for x in cleaned)


def _fmt_top_score(x: Any) -> str:
    """top_score may be 0.0..inf; render 0 as '0' and non-finite as not reported."""
    if x is None:
        return "not reported"
    try:
        v = float(x)
    except (TypeError, ValueError):
        return "not reported"
    if math.isnan(v):
        return "not reported"
    if math.isinf(v):
        return "∞"
    return f"{v:.3f}"


def _fmt_ci(x: Any) -> str:
    if x is None:
        return "not reported"
    try:
        v = float(x)
    except (TypeError, ValueError):
        return "not reported"
    if math.isnan(v):
        return "not reported"
    return f"{v:.2f}"


# ---------- data loaders ----------

def _load_transfer() -> dict:
    with TRANSFER_SUMMARY.open() as f:
        return json.load(f)


def _load_floors() -> dict:
    with FLOORS_SUMMARY.open() as f:
        return json.load(f)


def _load_registry_rows() -> list[dict]:
    """Read registry CSV; ignore comment lines starting with '#'."""
    rows = []
    with REGISTRY.open() as f:
        for ln in f:
            if not ln.strip() or ln.lstrip().startswith("#"):
                continue
            break  # first non-comment line is the header
    # Use csv.DictReader from the start
    with REGISTRY.open() as f:
        rdr = csv.reader(f)
        header = None
        for row in rdr:
            if not row or all(not c for c in row):
                continue
            if header is None:
                # Skip comments
                if row[0].startswith("#"):
                    continue
                header = row
                continue
            rows.append({h: v for h, v in zip(header, row)})
    return rows


def _registry_per_dtm(rows: list[dict]) -> dict[str, dict[str, int]]:
    """Aggregate registry rows by DTM (col 'dtm'); yield tier counts
    + strongest candidate span/amplitude for the site header."""
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        dtm = r.get("dtm", "").strip()
        if not dtm:
            continue
        bucket = out.setdefault(
            dtm, {"tier_A": 0, "tier_B": 0, "tier_C": 0,
                  "top_amp_m": 0.0, "top_score": 0.0}
        )
        tier = (r.get("tier") or "").strip()
        if tier == "A":
            bucket["tier_A"] += 1
        elif tier == "B":
            bucket["tier_B"] += 1
        else:
            bucket["tier_C"] += 1
        try:
            amp = float(r.get("sag_amp_m") or 0.0)
            if amp > bucket["top_amp_m"]:
                bucket["top_amp_m"] = amp
        except ValueError:
            pass
        try:
            score = float(r.get("score") or 0.0)
            if score > bucket["top_score"]:
                bucket["top_score"] = score
        except ValueError:
            pass
    return out


def _parse_legacy_manifest_urls() -> dict[str, dict[str, str]]:
    """Pull DTM-level rows out of MANIFEST.md (legacy pipe table).

    Two formats exist in the file:

      Format A (legacy): "| NAC DTM <NAME> (...) | downloaded | `<url>` |
      `<local>` | `<sha256>` | PDS public domain |". Two variants per DTM
      (.TIF and .LBL); we want only the .TIF row.

      Format B (P3.1c additions): "|`LROC_NAC_DTM_<NAME>`| ... | `<url>`
      | `~/lunarvoid/data/fetch_log_lroc.csv` | 2026-08-22 | <bytes> |
      `<sha256>` | NASA/ASU LROC, PDS public domain | `~/lunarvoid/data/...` |".

    Returns: {DTM_NAME: {url, sha256, licence}}.
    """
    out: dict[str, dict[str, str]] = {}
    if not MANIFEST.exists():
        return out
    text = MANIFEST.read_text(encoding="utf-8")

    # Generic row pattern: NAC DTM <NAME> ... URL ... SHA256 on the same line.
    # We capture: name, url, sha256. The URL ends at the next backtick or
    # pipe; the sha256 is 64 hex chars.
    pattern = re.compile(
        r"NAC DTM\s+([A-Z0-9_]+)[^\n]*?https?://([^\s|`]+)[^\n]*?([a-f0-9]{64})"
    )
    for m in pattern.finditer(text):
        name = m.group(1)
        url = "https://" + m.group(2).rstrip("`").rstrip()
        sha = m.group(3)
        # Skip .LBL (label) rows — only keep the .TIF for the DTM table.
        if not url.endswith(".TIF") and ".TIF" not in url.split("`")[0]:
            # Still keep if the line says it's the GeoTIFF (legacy first row).
            pass
        # Only count the URL ending in .TIF to dedupe .LBL rows.
        if not url.upper().endswith(".TIF"):
            continue
        if name in out:
            # Already populated; keep first (deterministic).
            continue
        out[name] = {
            "url": url,
            "sha256": sha,
            "licence": "PDS public domain",
        }
    return out


def _parse_fetch_log() -> dict[str, dict[str, str]]:
    """Read the 11 P3.1c-growth DTMs from the fetch log CSV.

    Only first OK row per site is used (deterministic; the OK row is
    where we have a verified sha256 / size; DRY_RUN rows are skipped).
    """
    out: dict[str, dict[str, str]] = {}
    if not FETCH_LOG.exists():
        return out
    with FETCH_LOG.open() as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            if row.get("status") != "OK":
                continue
            site = (row.get("site") or row.get("product_id") or "").strip()
            if not site:
                continue
            # only first OK row per site (fetch log is chronological)
            out.setdefault(
                site,
                {
                    "url": (row.get("url") or "").strip(),
                    "sha256": (row.get("sha256") or "").strip(),
                    "licence": (row.get("licence") or "").strip(),
                    "size_bytes": (row.get("size_bytes") or "").strip(),
                },
            )
    return out


# ---------- site status decision ----------

def _decide_status(site: str, transfer_row: dict, floor_row: dict) -> str:
    """Return one of: ran | deferred | no-cached-raster |
    terrain-extrapolation | deferred memory ceiling.

    Order of precedence:
      * TYCHOPK (1.44 GiB) -> deferred memory ceiling.
      * No cached score raster -> no-cached-raster.
      * Terrain extrapolation (highland / impact-melt) flag -> terrain-extrapolation
        AND that fact is also surfaced in Notes; the Status field
        reflects what was reported in transfer_summary.
      * rungs have at least one valid value -> ran.
    """
    if site == _TYCHOPK_MEMORY_CEILING:
        return "deferred memory ceiling"

    if site in _NO_CACHED_SCORE_RASTER:
        return "no-cached-raster"

    # transfer_row rungs == [null] when no rungs ran
    rungs = transfer_row.get("rungs") or []
    rungs_real = [r for r in rungs if r is not None]
    if not rungs_real:
        return "no-cached-raster"

    # highland/impact-melt sites run for inspection but are flagged
    if floor_row.get("terrain_extrapolation"):
        return "terrain-extrapolation"

    return "ran"


# ---------- per-site data extraction ----------

def _site_data(
    site: str,
    transfer: dict,
    floors: dict,
    registry_per_dtm: dict[str, dict[str, int]],
    manifest_urls: dict[str, dict[str, str]],
    fetch_urls: dict[str, dict[str, str]],
) -> dict[str, Any]:
    """Collect everything we know about `site` into one dict."""
    pd = transfer["per_dtm"].get(site) or {}
    fl = floors.get("per_dtm", {}).get(site) or {}
    reg = registry_per_dtm.get(site) or {}

    # Tier counts: authoritative = transfer summary's n_tier_B; tier A is
    # frozen to 0 (P3.1c rule); tier C = max(n_above_local_floor - n_tier_B, 0)
    # for above-floor candidates (the below-floor ones are excluded, since
    # they're either impact-melt/highland extrapolation or aliasing noise).
    n_above = pd.get("n_above_local_floor") or 0
    n_tier_b = pd.get("n_tier_B") or 0
    n_tier_a = 0  # P3.1c: tier A never assigned
    n_tier_c = max(int(n_above) - int(n_tier_b), 0)

    # DTM source URL / sha — prefer fetch_log (newer, has fresh DTMs),
    # fall back to MANIFEST (legacy).
    src = fetch_urls.get(site) or manifest_urls.get(site) or {}

    return {
        "site": site,
        "rungs": pd.get("rungs", []),
        "n_candidates": pd.get("n_candidates", 0),
        "n_above_local_floor": n_above,
        "n_below_local_floor": pd.get("n_below_local_floor"),
        "n_tier_a": n_tier_a,
        "n_tier_b": n_tier_b,
        "n_tier_c": n_tier_c,
        "n_fp": pd.get("n_fp", 0),
        "n_tp": pd.get("n_tp", 0),
        "fp_per_1e4km2": pd.get("fp_per_1e4km2"),
        "fp_lo": pd.get("fp_per_1e4km2_ci95_lo"),
        "fp_hi": pd.get("fp_per_1e4km2_ci95_hi"),
        "ci_method": pd.get("ci_method"),
        "top_score": pd.get("top_score"),
        "pooled_rms": fl.get("pooled_rms_m"),
        "three_sigma": fl.get("three_sigma_m") or pd.get("local_3sigma_m"),
        "terrain_extrapolation": fl.get("terrain_extrapolation"),
        "n_panels": fl.get("n_panels"),
        "dtm_url": src.get("url", ""),
        "dtm_sha256": src.get("sha256", ""),
        "dtm_licence": src.get("licence", ""),
        "transfer_notes": pd.get("notes"),
    }


# ---------- narrative rules ----------

def _narrative(site: str, data: dict, status: str) -> str:
    """2-4 sentences: what the site is, why interesting, what the detector found.

    Uses literal substrings from the spec edge-case list:
      * highland site -> 'terrain_extrapolation' annotation in Notes
      * TYCHOPK 1.44 GiB -> 'deferred memory ceiling' (already in Status)
      * site with 0 candidates -> 'no candidates'
      * MARIUSPIT01 tier-B I14 downgrades -> flag in Notes
    """
    if site == _TYCHOPK_MEMORY_CEILING:
        return (
            "Tycho Central Peak at 1.44 GiB float32 exceeds the on-disk memory "
            "budget for the Frangi filter (would peak >6 GiB after float64 "
            "promotion + scratch), so this DTM is deferred to the post-G2 "
            "Tier-1 phase. No transfer-summary candidates were generated. "
            "The 4 smaller Tycho DTMs (TYCHOPK02/03/04/07) DID run and are "
            "tagged terrain-extrapolation (highland; the frozen TRANQPIT1 "
            "recipe is mare-only)."
        )

    if status == "no-cached-raster":
        # Used for GRUITHMARE2, GRUITHUIS17, MARIUSCONE — all named in
        # transfer summary's scope_banner.
        site_pretty = site
        return (
            f"{site_pretty} is one of three 2026-08-22 DTMs (with "
            "GRUITHMARE2 / GRUITHUIS17 / MARIUSCONE) named in "
            "transfer_summary.json scope_banner as 'skipped for missing "
            "score raster'. The v0.1 Frangi score raster was not generated "
            "(out-of-scope for P3.1c); no candidates or FP rates are "
            "available. The pooled sag-band RMS comes from per_dtm_floors."
        )

    if data["n_candidates"] == 0:
        # All below-floor impact-melt/highland sites land here.
        if data.get("terrain_extrapolation"):
            return (
                f"{site} ran under the frozen TRANQPIT1 recipe (slope=45°, "
                "frac=0.20, neigh=5, sigmas 30–300 m) on a {data['n_panels']}-panel "
                "kriging-correction set; all candidates are below the 3× local "
                "noise floor (signal too low to confirm). The result is "
                "annotated **terrain-extrapolation** — TRANQPIT1 calibration "
                "is mare-only and these numbers should not be cited as "
                "highland lava-tube detections."
            )
        return (
            f"{site} ran under the frozen TRANQPIT1 recipe but produced zero "
            "candidates (rungs reported as null). No FP-rate or top-score is "
            "available. The pooled sag-band RMS comes from per_dtm_floors."
        )

    # Below we have at least one candidate. Build a 2-4 sentence narrative.
    n_fp = data["n_fp"] or 0
    n_tp = data["n_tp"] or 0
    top = data["top_score"]
    notes_extra = []

    if site == "FECUNPIT":
        return (
            f"Fecunditatis Pit: {data['n_candidates']} candidate(s) at rungs "
            f"{data['rungs']}; {n_fp} FPs / {n_tp} TPs. 3 unique large "
            "depressions (amplitudes 155 / 140 / 34 m) sit at the DTM north "
            "end; the cluster centre is 552.5 m from the NEAREST catalogued "
            "pit (not 67 km from the named Central Mare Fecunditatis Pit). "
            "r003 at 138.1 m is borderline-TP under a 150 m tolerance but "
            "labelled FP per the 100 m frozen calibration; visual "
            "inspection of the nearby pit's NAC frame is the relevant "
            "check (skeptic 2026-08-23 correction)."
        )

    if site == "TRANQPIT1":
        return (
            "Mare Tranquillitatis Pit — the frozen-calibration site "
            "(only positive in the Z2 ladder, see "
            "`code/wp2_sag/transfer/calibration_transqpit1.json`). At "
            "rung 5 m the detector ran to completion; the 3 FPs "
            "(r001/r002/r003) are LARGE 12-km-scale features (amplitudes "
            "95 / 57 / 49 m), NOT noise — likely floor-fractured crater "
            "rim / ejecta / modification. Visual inspection of LROC NAC "
            "at lat ~8.75 N, lon ~33.20 E required before any G2 claim."
        )

    if site == "MARIUSPIT01":
        i14 = (
            " Registry tier-B promotion on r001/r002/r002@8m was overturned "
            "by the I14 funnel-risk critic (pit-incised-into-rille failure "
            "mode — rille intersection is the confound, not independent "
            "confirmation). Registry tier for those rows is downstream of "
            "this note: per the Z2 transfer summary n_tier_B=3 is reported "
            "but the skeptic recommends tier C. **Site is I14 funnel-risk "
            "flagged.**"
        )
        rungs_str = _fmt_rungs(data["rungs"])
        return (
            f"Marius Hills Pit: {data['n_candidates']} candidate(s) at rungs "
            f"{rungs_str}; {n_fp} FPs / {n_tp} TPs."
            f"{i14}"
        )

    if site == "INGENIIPIT":
        return (
            f"Mare Ingenii Pit: {data['n_candidates']} candidate(s) at rungs "
            f"{data['rungs']}; {n_fp} FPs / {n_tp} TPs (r001 only). "
            "r002–r008 are ring artifacts around r001 (Frangi filter "
            "bias), not independent void candidates — registry rows for "
            "those already carry the 'ring artifact' annotation. Visual "
            "inspection of the LROC NAC pair at lat ~-35.95, "
            "lon ~166.05 required to confirm the ring pattern is "
            "detector-induced."
        )

    # Generic site — give concise narrative.
    site_label = site
    rung_str = ", ".join(
        f"{int(r)}" if r == int(r) else f"{r:g}"
        for r in data["rungs"] if r is not None
    ) or "—"
    return (
        f"{site_label}: {data['n_candidates']} candidate(s) at rung(s) "
        f"{rung_str} m; {n_fp} FPs / {n_tp} TPs; top score "
        f"{_fmt_top_score(top)}. "
        f"Pooled sag-band RMS {_fmt_float(data['pooled_rms'])} m; "
        f"3× convention {_fmt_float(data['three_sigma'])} m."
    )


# ---------- markdown emission ----------

def _tags_for(site: str, data: dict) -> list[str]:
    """Tags line for the header.

    Terrain tag consults the per_dtm_floors `terrain_extrapolation`
    field, which is the canonical ground-truth supplied by WP0 kriging
    (e.g. SWFECUNPIT1 is highland per scope_caveats even though its
    name does not contain TYCHO / KING / FRESHMELT). Falls back to a
    name-based heuristic when the floors data is silent.
    """
    fl_extrap = (data.get("terrain_extrapolation") or "").lower()
    if fl_extrap.startswith("highland"):
        terrain = "highland"
    elif fl_extrap.startswith("impact"):
        terrain = "impact-melt"
    elif "TYCHO" in site or "KINGCRATER" in site:
        terrain = "highland"
    elif "FRESHMELT" in site:
        terrain = "impact-melt"
    else:
        terrain = "mare"

    # Catalogued-pit vs random-mare
    catalogued = (data.get("n_tp", 0) or 0) > 0
    site_tag = "catalogued-pit" if catalogued else "random-mare"

    # Gate label: based on rung content + status
    if data["n_candidates"] == 0 or "deferred" in (data.get("status") or ""):
        gate = "g0prime"
    else:
        # All sites with >= 1 candidate pass at least G1 (single-method
        # sag) and contribute to the G2 N=21 aggregate. Use g1 if
        # n_below == n_candidates (pure below-floor) -> extrapolation
        # only, no fresh tier C; otherwise g2.
        n_below = data.get("n_below_local_floor")
        if n_below is not None and n_below > 0 and (
            data.get("n_above_local_floor") or 0
        ) == 0:
            gate = "g1"
        else:
            gate = "g2"

    return [f"#site", f"#{terrain}", f"#{site_tag}", f"#{gate}"]


def _wikilinks(site: str) -> str:
    """Return the canonical Obsidian wikilink footer."""
    return (
        "Wikilinks: `[[mocs/MOC Sites & Candidates]]`, "
        "`[[mocs/MOC Data & Code]]`, "
        "`[[mocs/MOC Gates & Decisions]]`, "
        "`[[gates/G2]]`."
    )


def _visual_inspection_block(site: str) -> str:
    hint = BACKLOG_SITE_HINTS.get(site)
    if hint:
        return hint
    return "None"


def _render_site_md(
    site: str,
    data: dict,
    status: str,
    timestamp: str,
) -> str:
    """Build the markdown body for a single site."""
    tags = " ".join(_tags_for(site, data))
    site_label = site
    # Terrain row: consult the same source as the tag (#mare / #highland
    # / #impact-melt) so the table matches the header tag.
    fl_extrap = (data.get("terrain_extrapolation") or "").lower()
    if fl_extrap.startswith("highland"):
        terrain = "highland"
    elif fl_extrap.startswith("impact"):
        terrain = "impact-melt"
    elif "TYCHO" in site or "KINGCRATER" in site:
        terrain = "highland"
    elif "FRESHMELT" in site:
        terrain = "impact-melt"
    else:
        terrain = "mare"

    # FP-rate formatting: if numeric, render "[lo, hi] (method)"
    fp = data.get("fp_per_1e4km2")
    fp_lo = data.get("fp_lo")
    fp_hi = data.get("fp_hi")
    method = data.get("ci_method") or ""
    if fp is not None and not (
        isinstance(fp, float) and math.isnan(fp)
    ):
        fp_block = f"{_fmt_float(fp)} [{_fmt_ci(fp_lo)}, {_fmt_ci(fp_hi)}] ({method})"
    else:
        fp_block = "not reported"

    # DTM source URL/SHA: always show URL if known; fall back to local
    # path (per MANIFEST convention) if not.
    url = data.get("dtm_url") or ""
    if not url:
        url = f"~/lunarvoid/data/dtms/{site}/NAC_DTM_{site}.TIF"
    # Show licence on a separate line below the URL is too verbose
    # for the table — keep just the URL here.

    n_below = data.get("n_below_local_floor")
    n_below_str = _fmt_int(n_below) if n_below is not None else "not reported"

    # narrative
    narrative = _narrative(site, data, status)
    terrain_tag = ""
    # Only add the terrain-extrapolation annotation line when the
    # _narrative caller did not already include it (it embeds the
    # annotation for site=='TYCHOPK' AND for the n_candidates==0
    # impact-melt/highland branch). For sites that ran with terrain-
    # extrapolation (KINGCRATER*, TYCHOPK02/03/04/07, FRESHMELT* etc.)
    # the _narrative call returns a generic line, so we tack the
    # annotation on separately.
    if (
        data.get("terrain_extrapolation")
        and "terrain-extrapolation" not in narrative.lower()
    ):
        terrain_tag = (
            f" Terrain extrapolation flagged: {data['terrain_extrapolation']}."
        )
    notes_block = narrative + terrain_tag

    # Suffix warnings:
    extra_notes = []
    if site == "MARIUSPIT01" and (data.get("n_tier_b") or 0) > 0:
        extra_notes.append(
            "**Skeptic I14 funnel flag**: tier-B rows "
            f"({data.get('n_tier_b')}) promoted by the 'rille intersection "
            "within 100 m' rule were DOWNGRADED to tier C by skeptic review "
            "(2026-08-22). Citing this site as a rille-confirmed void "
            "requires independent confirmation."
        )
    if (data.get("dtm_sha256") or "") and len(data.get("dtm_sha256") or "") == 64:
        extra_notes.append(
            f"SHA-256: `{data['dtm_sha256']}`"
        )

    if extra_notes:
        notes_block += "\n\n" + "\n\n".join(extra_notes)

    backlog = _visual_inspection_block(site)

    md = [
        f"# {site_label}",
        "",
        f"> Tags: {tags}",
        f"> Generated by regen_site_notes.py on {timestamp}; "
        "do not hand-edit data tables (links and narrative OK).",
        "",
        "| Property | Value |",
        "|---|---|",
        f"| Terrain | {terrain} |",
        f"| DTM source | <{url}> |",
        f"| Pooled sag-band RMS | {_fmt_float(data.get('pooled_rms'))} m |",
        f"| 3× sag-band RMS | {_fmt_float(data.get('three_sigma'))} m |",
        f"| Rungs scored | {_fmt_rungs(data.get('rungs') or [])} |",
        f"| Candidates | {_fmt_int(data.get('n_candidates'))} |",
        f"| Above local floor | {_fmt_int(data.get('n_above_local_floor'))} |",
        f"| Below local floor | {n_below_str} |",
        f"| Tier A / B / C | {_fmt_int(data.get('n_tier_a'))} / "
        f"{_fmt_int(data.get('n_tier_b'))} / "
        f"{_fmt_int(data.get('n_tier_c'))} |",
        f"| FPs | {_fmt_int(data.get('n_fp'))} |",
        f"| TPs | {_fmt_int(data.get('n_tp'))} |",
        f"| FP per 10⁴ km² | {fp_block} |",
        f"| Top score | {_fmt_top_score(data.get('top_score'))} |",
        f"| Status | {status} |",
        "",
        "## Notes",
        "",
        notes_block,
        "",
        "## Visual-inspection backlog items",
        "",
        backlog,
        "",
        _wikilinks(site),
        "",
    ]
    return "\n".join(md)


# ---------- mtime-aware --since filter ----------

def _latest_source_mtime(site: str) -> float | None:
    """Return the most recent mtime of any source file that contains
    data for `site`. Used for the --since filter."""
    files = [
        TRANSFER_SUMMARY,
        FLOORS_SUMMARY,
        FLOORS_CSV,
        REGISTRY,
        MANIFEST,
        FINDINGS,
        FETCH_LOG,
    ]
    # In addition, scrape findings.md for the site name (case-insensitive
    # substring match) — but for performance skip text scanning here.
    mtimes = []
    for f in files:
        if f.exists():
            try:
                mtimes.append(f.stat().st_mtime)
            except OSError:
                continue
    if not mtimes:
        return None
    return max(mtimes)


def _parse_since(s: str) -> float:
    """Parse YYYY-MM-DD to a midnight UTC timestamp."""
    dt = datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return dt.timestamp()


# ---------- main ----------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument(
        "--site", help="Regenerate this single site only (matches a "
                       "DTM/key in transfer_summary.json)"
    )
    ap.add_argument(
        "--all", action="store_true",
        help="Regenerate all 21 sites (default behaviour)",
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be written without writing any file",
    )
    ap.add_argument(
        "--since", default=None,
        help="Only regenerate sites whose source data was modified "
             "after this YYYY-MM-DD date (uses file mtime of the "
             "canonical sources)",
    )
    args = ap.parse_args(argv)

    if not args.site and not args.all:
        # default behaviour per spec: --all is the default
        args.all = True

    # Load once, share across sites.
    transfer = _load_transfer()
    floors = _load_floors()
    registry_rows = _load_registry_rows()
    registry_per_dtm = _registry_per_dtm(registry_rows)
    manifest_urls = _parse_legacy_manifest_urls()
    fetch_urls = _parse_fetch_log()

    all_sites = sorted(transfer["per_dtm"].keys())
    if args.site:
        if args.site not in transfer["per_dtm"]:
            sys.stderr.write(
                f"ERROR: --site {args.site!r} not in "
                f"{TRANSFER_SUMMARY.relative_to(WORKSPACE)}\n"
                f"       known sites: {', '.join(all_sites)}\n"
            )
            return 2
        sites = [args.site]
    else:
        sites = all_sites

    # --since filter
    since_ts = None
    if args.since:
        try:
            since_ts = _parse_since(args.since)
        except ValueError:
            sys.stderr.write(
                f"ERROR: --since {args.since!r} is not YYYY-MM-DD\n"
            )
            return 2

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    written = 0
    skipped_since = 0
    for site in sites:
        data = _site_data(
            site,
            transfer=transfer,
            floors=floors,
            registry_per_dtm=registry_per_dtm,
            manifest_urls=manifest_urls,
            fetch_urls=fetch_urls,
        )
        floor_row = floors.get("per_dtm", {}).get(site, {})
        status = _decide_status(site, transfer["per_dtm"].get(site, {}), floor_row)
        data["status"] = status

        if since_ts is not None:
            latest = _latest_source_mtime(site)
            if latest is None or latest <= since_ts:
                skipped_since += 1
                continue

        md = _render_site_md(site, data, status, timestamp)
        out_path = SITES_DIR / f"{site}.md"

        if args.dry_run:
            print(f"would write: {out_path}")
            continue

        SITES_DIR.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        written += 1

    if args.dry_run:
        print(f"\n[dry-run] would write {len(sites) - skipped_since} site(s)")
    else:
        print(f"\n[ok] wrote {written} site note(s) under {SITES_DIR}")
        if skipped_since:
            print(f"     skipped {skipped_since} (older than --since)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
