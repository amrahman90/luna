"""cc_filter_eval_v0_6.py — C3 evaluation battery for the --cc-filter wiring.

LLTB-1 v0.6 candidate (task C3). Runs the production sag_detect.py CLI on
all 7 analog sites in two arms:

  - OFF  (--cc-filter off): the legacy inline scalar --min-component 5
    path = v0.5 parity. Asserted equal to the v0.4/v0.5 site-table F1s
    (release note 2026-08-21 §5; the v0.5 note froze that table) within
    2e-3 (pins are 4-dp rounded).
  - AUTO (--cc-filter auto): the standalone connected_component_filter
    engine with the per-rung AREA_MIN table (V0.2_PLAN.md §4.1).

Settings per the conventions §8 v0.4 site table: best rung per site,
--tune-slope everywhere EXCEPT IndianTunnel_cave_1x which uses the FIXED
--slope-mask-degrees 10 (tune-slope regresses there).

Decision rule (applied and reported, decides the CLI default):
  default ON only if per-site F1 is non-regressing
  (>= v0.5 - 0.005) at EVERY site AND improves F1 at >= 3 sites;
  otherwise default OFF.

Output: 01_WORKSPACE/data/outputs/wp1_detector/cc_filter_evaluation_v0_6.json
(provenance: git sha, seed 42, per-site settings, both arms, deltas,
AREA_MIN table, decision-rule branch).

Usage:
  ~/lunarvoid/venv/bin/python 01_WORKSPACE/code/wp1_detector/cc_filter_eval_v0_6.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

# v1 C1 refactor (session 56): the per-site npz dir is now derived from
# io_common.LLTB1_DATA ("~/lunarvoid/data") + "lltb1" instead of the
# hard-coded /home/frostflux/lunarvoid/data/lltb1 literal. The hard-coded
# literal was the same string the previous version of this script
# carried; swapping to the resolver preserves the on-disk path exactly
# (no data writes, no SHA-256 drift).
_HERE = Path(__file__).resolve().parent
_CODE = _HERE.parent
if str(_CODE) not in sys.path:
    sys.path.insert(0, str(_CODE))
from io_common import LLTB1_DATA, LLTB1_VENV_PY  # noqa: E402

REPO = Path("/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube")
VENV = LLTB1_VENV_PY  # io_common.LLTB1_VENV_PY (~/lunarvoid/venv/bin/python)
SAG = REPO / "01_WORKSPACE/code/wp1_detector/sag_detect.py"
OUT_JSON = (REPO / "01_WORKSPACE/data/outputs/wp1_detector/"
            "cc_filter_evaluation_v0_6.json")
TMP = Path("/tmp/opencode/cc_eval_v0_6")

# (site, npz, rung_m, tune_slope, v0.4/v0.5 pin F1_test_slope)
# Pins: notes/2026-08-21_LLTB1_v0.4_release_note.md §5 (4-dp rounded);
# cave_1x pin = the fixed-10° value from the same note's caveat section
# (conventions §8: "use fixed --slope-mask-degrees 10 (F1 0.068)").
DATA = LLTB1_DATA / "lltb1"
SITES = [
    ("IndianTunnel_NorthSurface",
     DATA / "IndianTunnel_NorthSurface/lltb1/IndianTunnel_NorthSurface_0.5m.npz",
     1.0, True, 0.3618),
    ("IndianTunnel_Collapse3",
     DATA / "IndianTunnel_Collapse3/IndianTunnel_Collapse3_0.5m.npz",
     0.5, True, 0.1875),
    ("Fieg_A",
     DATA / "Fieg/Fieg_0.5m.npz",
     0.5, True, 0.1365),
    ("Sheepridge",
     DATA / "Sheepridge/Sheepridge_0p5m.npz",
     5.0, True, 0.0909),
    ("IndianTunnel_cave_10x",
     DATA / "IndianTunnel_cave_10x/IndianTunnel_cave_10x_0p5m.npz",
     5.0, True, 0.085),
    ("Kingsbowl",
     DATA / "Kingsbowl/lltb1/Kingsbowl_0.5m.npz",
     5.0, True, 0.043),
    ("IndianTunnel_cave_1x",
     DATA / "IndianTunnel_cave_1x/IndianTunnel_cave_1x_0p5m.npz",
     5.0, False, 0.068),  # FIXED slope 10 (default), NO tune-slope
]

PIN_TOL = 2e-3          # pins are 4-dp rounded
NONREG_TOL = 0.005      # decision rule: F1_auto >= F1_off - 0.005
IMPROVE_MIN_SITES = 3   # decision rule: >= 3 sites with F1_auto > F1_off


def run_arm(site: str, npz: Path, rung: float, tune: bool, mode: str) -> dict:
    outdir = TMP / f"{site}_{mode}"
    outdir.mkdir(parents=True, exist_ok=True)
    cmd = [str(VENV), str(SAG), "--npz", str(npz), "--outdir", str(outdir),
           "--rungs", str(rung), "--min-component", "5",
           "--cc-filter", mode]
    if tune:
        cmd.append("--tune-slope")
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600,
                       cwd=str(REPO),
                       env={"PYTHONPATH": str(REPO / "01_WORKSPACE/code"),
                            "MPLBACKEND": "Agg", "PATH": "/usr/bin:/bin"})
    if r.returncode != 0:
        raise RuntimeError(f"{site}/{mode} rc={r.returncode}: {r.stderr[-600:]}")
    summary = json.loads((outdir / "sag_summary.json").read_text())
    r0 = summary["rungs"][0]
    return {"rung": r0, "wall_s": round(time.time() - t0, 1),
            "cmd": cmd, "outdir": str(outdir)}


def main() -> dict:
    TMP.mkdir(parents=True, exist_ok=True)
    git_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
        text=True).stdout.strip()
    git_dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO, capture_output=True,
        text=True).stdout.strip() != ""

    rows, failures = [], []
    for site, npz, rung, tune, pin in SITES:
        print(f"=== {site} @ {rung} m ({'tune' if tune else 'fixed10'}) ===",
              flush=True)
        off = run_arm(site, npz, rung, tune, "off")
        on = run_arm(site, npz, rung, tune, "auto")
        o, a = off["rung"], on["rung"]

        parity_ok = abs(o["f1_test_slope"] - pin) <= PIN_TOL
        if not parity_ok:
            failures.append(
                f"{site}: OFF-arm F1 {o['f1_test_slope']:.4f} != v0.4/v0.5 "
                f"pin {pin:.4f} (tol {PIN_TOL})")
        row = {
            "site": site, "rung_m": rung, "tune_slope": tune,
            "npz": str(npz),
            "slope_mask_degrees_off": o["slope_mask_degrees"],
            "slope_mask_degrees_auto": a["slope_mask_degrees"],
            "v05_pin_f1": pin,
            "off": {
                "f1": o["f1_test_slope"], "precision": o["precision_test_slope"],
                "recall": o["recall_test_slope"], "threshold": o["threshold"],
                "cc_components_dropped_ratio": o["cc_components_dropped_ratio"],
                "cc_area_min_effective": o["cc_area_min_effective"],
                "parity_ok": parity_ok,
            },
            "auto": {
                "f1": a["f1_test_slope"], "precision": a["precision_test_slope"],
                "recall": a["recall_test_slope"], "threshold": a["threshold"],
                "cc_components_dropped_ratio": a["cc_components_dropped_ratio"],
                "cc_area_min_effective": a["cc_area_min_effective"],
            },
            "delta": {
                "f1": a["f1_test_slope"] - o["f1_test_slope"],
                "precision": a["precision_test_slope"] - o["precision_test_slope"],
                "recall": a["recall_test_slope"] - o["recall_test_slope"],
            },
        }
        rows.append(row)
        print(f"  off : F1={o['f1_test_slope']:.4f} P={o['precision_test_slope']:.4f} "
              f"R={o['recall_test_slope']:.4f} (pin {pin:.4f}, "
              f"{'OK' if parity_ok else 'MISMATCH'})")
        print(f"  auto: F1={a['f1_test_slope']:.4f} P={a['precision_test_slope']:.4f} "
              f"R={a['recall_test_slope']:.4f} "
              f"(area_min={a['cc_area_min_effective']}, "
              f"drop_ratio={a['cc_components_dropped_ratio']:.3f})")

    # decision rule
    nonreg = [r for r in rows if r["auto"]["f1"] >= r["off"]["f1"] - NONREG_TOL]
    improved = [r for r in rows if r["auto"]["f1"] > r["off"]["f1"]]
    default_on = (len(nonreg) == len(rows)) and (len(improved) >= IMPROVE_MIN_SITES)
    branch = ("ON: non-regressing at ALL "
              f"{len(nonreg)}/{len(rows)} sites AND improved at "
              f"{len(improved)}/{len(rows)} (>= {IMPROVE_MIN_SITES})"
              if default_on else
              f"OFF: non-regressing at {len(nonreg)}/{len(rows)} sites, "
              f"improved at {len(improved)}/{len(rows)} "
              f"(needs ALL + >= {IMPROVE_MIN_SITES})")

    result = {
        "task": "C3 — cc-filter wiring evaluation (LLTB-1 v0.6 candidate)",
        "date": str(date.today()),
        "provenance": {
            "git_sha": git_sha, "git_tree_dirty": git_dirty,
            "seed": 42, "split": "50/50 cal/test (v5 I9)",
            "detector": "01_WORKSPACE/code/wp1_detector/sag_detect.py",
            "engine": "01_WORKSPACE/code/wp1_detector/connected_component_filter.py",
            "frozen_evidence": "Paper 1/2 JSONs derive from LLTB-1 v0.5 "
                               "(--cc-filter off); untouched by this change",
        },
        "arms": {
            "off": "--cc-filter off (legacy scalar min-component 5; v0.5 parity)",
            "auto": "--cc-filter auto (per-rung AREA_MIN table)",
        },
        "area_min_table": {"0.5": 50, "1": 20, "2": 8, "5": 3, "8": 2, "10": 2},
        "area_min_rationale": "V0.2_PLAN.md §4.1 table (authoritative); "
                              "(GSD ratio)^2 scale-awareness documented in "
                              "connected_component_filter.AREA_MIN_PER_RUNG",
        "parity": {
            "reference": "notes/2026-08-21_LLTB1_v0.4_release_note.md §5 "
                         "(site table frozen through v0.5)",
            "tolerance": PIN_TOL,
            "all_ok": not failures, "failures": failures,
        },
        "decision_rule": {
            "rule": f"default ON only if F1_auto >= F1_off - {NONREG_TOL} at "
                    f"EVERY site AND F1_auto > F1_off at >= {IMPROVE_MIN_SITES} "
                    f"sites; else OFF",
            "n_nonregressing": len(nonreg), "n_improved": len(improved),
            "n_sites": len(rows), "default_on": default_on, "branch": branch,
        },
        "sites": rows,
        "commands": {r["site"]: {"off": None, "auto": None} for r in rows},
    }
    for r, (site, npz, rung, tune, pin) in zip(rows, SITES):
        base = [str(VENV), str(SAG), "--npz", str(npz), "--outdir", "<outdir>",
                "--rungs", str(rung), "--min-component", "5"]
        result["commands"][site] = {
            "off": base + ["--cc-filter", "off"] + (["--tune-slope"] if tune else []),
            "auto": base + ["--cc-filter", "auto"] + (["--tune-slope"] if tune else []),
        }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2))
    print(f"\nDecision rule branch: {branch}")
    print(f"Default --cc-filter = {'auto' if default_on else 'off'}")
    print(f"Output -> {OUT_JSON}")
    if failures:
        print("PARITY FAILURES:", *failures, sep="\n  ")
    return result


if __name__ == "__main__":
    main()
