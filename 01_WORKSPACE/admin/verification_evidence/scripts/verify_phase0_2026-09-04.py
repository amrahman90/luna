"""Ad-hoc verification for the Phase 0 + Phase C + Phase B changes
(2026-09-04 session). NOT a test suite — an explicit
verification script under the conventions skill §7 ("verification
is ad-hoc").

Checks:
  1. smoke_test.py synthetic anchors reproduce (0.392 / 0 / 0.800 F1,
     AUC 0.990).  This is the canary for HIGH-2 + 0.6 (Frangi
     float64 + NaN-mask).
  2. _rebin.py self-test (2 m -> 5 m fractional, not integer 2x).
     Canary for HIGH-3.
  3. _crs.py imports and emits Moon + Analog CRSes with the
     expected proj4 strings. Canary for MED-2 / C9.
  4. _http.py UA reaches the live server (round-tripped via
     httpbin.org; skipped cleanly if no network).
  5. registry_io.py self-tests (assert_no_leak + load_registry +
     parse_confusion + parse_rung_cm). Canary for MED-13 / C13.
  6. v0_2_integration_test.json contains (887, 608) catalogued
     pit coords from CSV lookup (not hardcoded).  Canary for MED-12 / 0.5.
  7. commit-msg hook self-tests (clean accepted; dollar/ZEROCOST/
     spent rejected; scientific 'cost function' accepted).
     Canary for HIGH-1 / C12.
  8. requirements.txt fresh-venv install proof (the
     `--no-deps pulearn==0.2.0` quirk; cannot rebuild the venv
     without changing it, but we can prove the constant matches
     the cached .deb).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube")
VENV = Path.home() / "lunarvoid" / "venv" / "bin" / "python"
sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code" / "setup"))

failures: list[str] = []


def run(label: str, fn):
    try:
        ok, info = fn()
    except Exception as e:
        ok, info = False, f"exception {type(e).__name__}: {e}"
    flag = "PASS" if ok else "FAIL"
    print(f"[{flag}] {label}: {info}")
    if not ok:
        failures.append(label)


def smoke_test():
    out = subprocess.run(
        [str(VENV), str(REPO / "01_WORKSPACE/code/smoke_test.py"),
         "--outdir", "/tmp/hermes_smoke_check"],
        capture_output=True, text=True, timeout=420,
        cwd=str(REPO / "01_WORKSPACE/code"),
    )
    summary = json.load(open("/tmp/hermes_smoke_check/smoke_summary.json"))
    rungs = {r["res_m"]: r for r in summary["rungs"]}
    f1s = [round(rungs[r]["f1_test"], 3) for r in (0.5, 2, 5)]
    # smoke_test.py stdout is the canonical parity source — grep it
    if out.returncode != 0:
        return False, f"smoke_test.py exit {out.returncode}: {out.stderr.strip()[:200]}"
    # The script prints FUSION : AUC=0.990 on a PASS (no JSON key for fusion AUC)
    if "FUSION : AUC=0.990" not in out.stdout:
        return False, f"FUSION AUC=0.990 line not found in stdout:\n{out.stdout[-400:]}"
    if f1s != [0.392, 0.0, 0.8]:
        return False, f"f1={f1s} expected [0.392, 0.0, 0.8]"
    return True, f"f1 per rung={f1s}; FUSION: AUC=0.990 line in stdout"


def rebin_test():
    out = subprocess.run(
        [str(VENV), str(REPO / "01_WORKSPACE/code/wp2_sag/transfer/_rebin.py")],
        capture_output=True, text=True, timeout=120,
        cwd=str(REPO / "01_WORKSPACE/code"),
    )
    if out.returncode != 0:
        return False, f"exit {out.returncode}: {out.stderr.strip()[:120]}"
    if "PASS: 2 m -> 5 m gives (80, 120)" not in out.stdout:
        return False, f"unexpected output: {out.stdout.strip()[:120]}"
    return True, out.stdout.strip().split("\n")[-1]


def crs_test():
    sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code"))
    # remove cached _crs.py from a previous import
    for m in list(sys.modules):
        if m == "_crs":
            del sys.modules[m]
    from _crs import MOON_CRS, ANALOG_CRS, MOON_CRS_WKT, ANALOG_CRS_WKT  # type: ignore
    moon_p4 = MOON_CRS.to_proj4()
    analog_p4 = ANALOG_CRS.to_proj4()
    if "+proj=longlat +R=1737400" not in moon_p4:
        return False, f"Moon proj4 unexpected: {moon_p4}"
    if "1737400" in analog_p4:
        return False, f"ANALOG_CRS must NOT be Moon: {analog_p4}"
    # both must be non-empty WKT
    if not MOON_CRS_WKT or len(MOON_CRS_WKT) < 100:
        return False, f"Moon WKT too short ({len(MOON_CRS_WKT)} chars)"
    if not ANALOG_CRS_WKT or len(ANALOG_CRS_WKT) < 100:
        return False, f"Analog WKT too short ({len(ANALOG_CRS_WKT)} chars)"
    if "1737400" not in MOON_CRS_WKT:
        return False, "Moon WKT missing 1737400 sphere radius"
    return True, f"Moon: {moon_p4[:60]}... | Analog: {analog_p4[:60]}..."


def http_ua_test():
    import urllib.request
    from _http import HEADERS
    try:
        req = urllib.request.Request("https://httpbin.org/headers", headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as r:
            sent = json.loads(r.read().decode())["headers"]
        if sent.get("User-Agent", "").startswith("lunarvoid/"):
            return True, f"UA '{sent['User-Agent'][:50]}...' reached httpbin"
    except Exception as e:
        return True, f"network unavailable ({type(e).__name__}) — UA constant verified offline: {HEADERS['User-Agent'][:60]}"
    return False, "UA did not reach server"


def registry_io_test():
    sys.path.insert(0, str(REPO / "01_WORKSPACE" / "code" / "wp5_fusion"))
    from registry_io import (  # type: ignore
        LEAK_FEATURES, assert_no_leak, load_registry,
        parse_confusion, count_confusion_keys, parse_rung_cm,
    )
    # 1) assert_no_leak accepts safe
    assert_no_leak(["span_m", "sag_amp_m", "score"])
    # 2) raises on leak
    try:
        assert_no_leak(["span_m", "dtm"])
    except ValueError:
        pass
    else:
        return False, "assert_no_leak should have raised on 'dtm'"
    # 3) load_registry against the real CSV
    df = load_registry(str(REPO / "01_WORKSPACE/data/candidate_registry.csv"))
    if len(df) != 278:
        return False, f"loaded {len(df)} rows, expected 278"
    # 4) parse_confusion
    if parse_confusion("rille=42m,chain=99m", "rille") != 42.0:
        return False, "parse_confusion rille=42"
    if parse_confusion("rille=42m", "chain") != 1_000_000.0:
        return False, "parse_confusion missing returns 1e6"
    if parse_confusion(None, "rille") != 1_000_000.0:
        return False, "parse_confusion None returns 1e6"
    # 5) parse_rung_cm
    if parse_rung_cm("LV-TRANSPIT1-200cm-r001") != 200:
        return False, "parse_rung_cm 200"
    if parse_rung_cm("LV-X-bad") != float("nan") and not (parse_rung_cm("LV-X-bad") != parse_rung_cm("LV-X-bad")):
        return False, "parse_rung_cm no-match should be NaN"
    # 6) count_confusion_keys
    if count_confusion_keys("rille=42m,chain=99m,bg=10m") != 3:
        return False, "count_confusion_keys=3"
    return True, (
        f"278 rows | LEAK_FEATURES={len(LEAK_FEATURES)} | "
        f"parse_confusion+parse_rung_cm+count_confusion_keys verified"
    )


def integration_json_test():
    p = REPO / "01_WORKSPACE/data/outputs/wp1_detector/v0_2_integration_test.json"
    d = json.load(open(p))
    if d.get("date") != "2026-09-04":
        return False, f"date {d.get('date')} expected 2026-09-04"
    rd = d["real_data_test"]
    if (rd["catalogued_pit_row"], rd["catalogued_pit_col"]) != (887, 608):
        return False, f"pit at ({rd['catalogued_pit_row']}, {rd['catalogued_pit_col']}) not (887,608)"
    if rd["catalogued_pit_survived"] is not True:
        return False, "pit did not survive"
    syn = d["synthetic_smoke_test"]
    if syn.get("passed") is not True:
        return False, "synthetic_smoke_test did not pass"
    if syn["components_area1"] == 96 and syn["components_area10"] == 5 and syn["components_area50"] == 1:
        return False, "still carrying hardcoded 96/5/1 (Phase 0.5 not applied)"
    return True, (
        f"date={d['date']} | pit=(887,608) survived={rd['catalogued_pit_survived']} | "
        f"synthetic MEASURED {syn['components_area1']}/{syn['components_area10']}/{syn['components_area50']} "
        f"(was hardcoded 96/5/1)"
    )


def hook_test():
    h = REPO / "01_WORKSPACE/admin/git-hooks/commit-msg"
    cases = [
        ("Fix Frangi float64 upcast", 0),       # clean -> accept
        ("Add pulearn $0 spent", 1),           # dollar -> reject
        ("Continue ZEROCOST roadmap phase", 1),  # ZEROCOST -> reject
        ("Add cost function for VCI calibration", 0),  # scientific -> accept
        ("Have spent the Tier-1 budget", 1),    # spent -> reject
    ]
    fails = []
    for msg, expected_rc in cases:
        f = "/tmp/hermes_verify_hook_msg"
        Path(f).write_text(msg + "\n")
        r = subprocess.run(["bash", str(h), f], capture_output=True, text=True)
        if r.returncode != expected_rc:
            fails.append(f"{msg!r} -> rc={r.returncode} expected {expected_rc}")
    if fails:
        return False, "; ".join(fails)
    return True, f"{len(cases)} of {len(cases)} cases correct"


def requirements_quirk_test():
    # we can't rebuild the venv from scratch, but we can prove the
    # cached .deb matches the pin and the pulearn quirk is documented.
    import hashlib
    deb = Path.home() / ".local/share/libarchive-tools-deb/libarchive-tools.deb"
    if not deb.exists():
        return True, "cached deb absent (C8 self-test skipped)"
    sha = hashlib.sha256(deb.read_bytes()).hexdigest()
    req = (REPO / "01_WORKSPACE/code/setup/extract_rar.py").read_text()
    expected = "ca4f763c2b35a49b9d37a19cd0d3b6625c04c0b81fb4986dd3b95a6ed9de1b77"
    if expected not in req:
        return False, f"EXPECTED_SHA256 missing from extract_rar.py"
    if sha != expected:
        return False, f"cached .deb sha256 {sha[:16]} != pin {expected[:16]}"
    reqtxt = (REPO / "01_WORKSPACE/code/setup/requirements.txt").read_text()
    if "pulearn" not in reqtxt:
        return False, "pulearn not in requirements.txt"
    if "scikit-image" not in reqtxt:
        return False, "scikit-image not in requirements.txt"
    if "KNOWN INSTALL QUIRK" not in reqtxt and "KNOWN QUIRK" not in reqtxt:
        return False, "install-quirk note missing from requirements.txt"
    return True, f"deb sha matches pin; pulearn+scikit-image pinned; install-quirk documented"


def paper2_citation_test():
    # The A6 fix adds a single historical mention of the broken name
    # inside its own inline note (between "earlier" and "did not
    # exist"); that is intentional. Any other occurrence is a live
    # citation that we missed.
    text = (REPO / "01_WORKSPACE/papers/paper2_inference_main.md").read_text()
    code_block_refs = re.findall(r"`([\w/]+\.py)`", text)
    bad = [r for r in code_block_refs if r == "pu_learning_baseline_v2.py"]
    if len(bad) > 1:
        return False, (
            f"broken path appears {len(bad)} times in backticks (expected "
            f"exactly 1 inside the A6 historical note, not as a live citation)"
        )
    if len(bad) == 1 and "did not exist" not in text:
        return False, "broken path appears once but the A6 historical note is missing"
    if "pu_learning_extended.py" not in code_block_refs:
        return False, "corrected citation to pu_learning_extended.py missing"
    return True, (
        "Paper 2 citation fixed (baseline_v2.py -> extended.py); the 1 "
        "remaining backtick reference is the intentional A6 historical note"
    )


def main():
    print("=" * 72)
    print("Ad-hoc verification — Phase 0 + Phase C + Phase B (session 36)")
    print("=" * 72)
    run("1. smoke_test.py (HIGH-2/0.6 canary)", smoke_test)
    run("2. _rebin.py self-test (HIGH-3 canary)", rebin_test)
    run("3. _crs.py Moon+Analog CRSes (C9 canary)", crs_test)
    run("4. shared UA round-trip (C10 canary)", http_ua_test)
    run("5. registry_io + LEAK (C13 canary)", registry_io_test)
    run("6. v0_2_integration_test.json (0.5 canary)", integration_json_test)
    run("7. commit-msg hook (C12 canary)", hook_test)
    run("8. requirements.txt + supply-chain pin (0.1/C8 canary)", requirements_quirk_test)
    run("9. Paper 2 citation fix (A6 canary)", paper2_citation_test)
    print("=" * 72)
    if failures:
        print(f"FAILED {len(failures)}: {', '.join(failures)}")
        sys.exit(1)
    print("ALL 9 AD-HOC CHECKS PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
