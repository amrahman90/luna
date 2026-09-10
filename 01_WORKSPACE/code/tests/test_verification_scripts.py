"""C4: the ad-hoc verifier scripts ported as parametrized pytest cases.

Ports (and RE-EXECUTES — not just re-reads stored PASS JSON):

  v02  admin/verification_evidence/scripts/verify_v02_f32dir_and_filter.py
  v03  admin/verification_evidence/scripts/verify_v03_slope_mask.py
  v04  admin/verification_evidence/scripts/verify_v04_tune_slope.py
  p0   admin/verification_evidence/scripts/verify_phase0_2026-09-04.py
  v05  code/wp1_lla/verify_v05.py   (stored-artifact recomputation by design)

Each check is a small function re-running the original verifier's logic
against the CURRENT code and artifacts. Checks that need rasters which
exist only on this machine (~/lunarvoid/data) skip with an explicit
reason when the file is absent — so CI (repo-only checkout) stays green
while the local run re-executes everything re-executable.

Heavy subprocess re-runs (smoke_test.py, sag_detect.py CLI) are cached
per session by the conftest fixtures, so several checks share one run.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from conftest import CODE_DIR, DATA_ROOT, REPO_ROOT, WS_DIR

# Mirror the original verifiers' import layout (they put the module dirs
# on sys.path; conftest already put 01_WORKSPACE/code there for _crs etc.)
for _p in ("wp1_detector", "wp1_lla", "setup", "wp5_fusion"):
    _p = CODE_DIR / _p
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

FIEG_NPZ = DATA_ROOT / "lltb1/Fieg/Fieg_0.5m.npz"
KINGS_NPZ = DATA_ROOT / "lltb1/Kingsbowl/lltb1/Kingsbowl_0.5m.npz"
SENSOR_DIR = WS_DIR / "data/outputs/wp1_ladder/sensor"
HAPKE_DIR = WS_DIR / "data/outputs/wp1_ladder/hapke"

# ---------------------------------------------------------------- registry --

CHECKS: dict[str, object] = {}


def check(vid: str):
    """Register a ported verifier check under '<vid>-<fn name>'."""
    def deco(fn):
        CHECKS[f"{vid}-{fn.__name__}"] = fn
        return fn
    return deco


def _require(*paths: Path, why: str):
    """Skip (with reason) when a local-only artifact is absent."""
    for p in paths:
        if not p.exists():
            pytest.skip(f"{why}: {p} absent (LUNARVOID_DATA={DATA_ROOT})")


def _sag():
    import sag_detect  # deferred: heavy imports (whitebox, rasterio, ...)
    return sag_detect


Ctx = SimpleNamespace  # ctx: repo, code, ws, data, help, smoke, sag, venv_run

# ------------------------------------------------------------------- v02 ----

@check("v02")
def filter_helper_exists(ctx):
    return hasattr(_sag(), "filter_small_components"), "filter_small_components"


@check("v02")
def filter_min_size1_noop(ctx):
    m = np.zeros((10, 10), dtype=bool); m[3:6, 3:6] = True
    out = _sag().filter_small_components(m, min_size=1)
    return np.array_equal(out, m), f"identity={np.array_equal(out, m)}"


@check("v02")
def filter_drops_small_components(ctx):
    m2 = np.zeros((20, 20), dtype=bool)
    m2[0, 0] = True             # 1-cell component -> removed
    m2[10:15, 10:15] = True     # 25-cell component -> kept
    m2[5:7, 5:7] = True         # 4-cell component -> removed at min=5
    out2 = _sag().filter_small_components(m2, min_size=5)
    ok = (not out2[0, 0] and out2[5:7, 5:7].sum() == 0
          and out2[10:15, 10:15].sum() == 25)
    return ok, f"1cell={out2[0, 0]}, 4cell={out2[5:7, 5:7].sum()}, 25cell={out2[10:15, 10:15].sum()}"


@check("v02")
def filter_nan_safe(ctx):
    m3 = np.zeros((10, 10), dtype=bool)
    m3[0, 0] = True; m3[5, 5] = np.nan; m3[8, 8] = True
    out3 = _sag().filter_small_components(m3, min_size=5)
    ok = (not out3[5, 5] and not out3[0, 0] and not out3[8, 8])
    return ok, f"NaN/1-cell cells all False={ok}"


@check("v02")
def cli_min_component_flag(ctx):
    return "--min-component" in ctx.help, "--min-component in --help"


@check("v02")
def e2e_fieg_rung5_mincomp10(ctx):
    """Re-run sag_detect on the Fieg npz (v0.2 check f, re-executed)."""
    _require(FIEG_NPZ, why="Fieg analog npz is local-only")
    res = ctx.sag(FIEG_NPZ, [5], min_component=10)
    if res["rc"] != 0:
        return False, f"rc={res['rc']}: {res['stderr'][-200:]}"
    r0 = res["summary"]["rungs"][0]
    ok = ("f1_test" in r0 and "f1_test_raw" in r0
          and r0.get("min_component") == 10)
    return ok, f"keys ok={ok}, min_component={r0.get('min_component')}"


@check("v02")
def e2e_pred_raster_written(ctx):
    _require(FIEG_NPZ, why="Fieg analog npz is local-only")
    res = ctx.sag(FIEG_NPZ, [5], min_component=10)
    pred = res["outdir"] / "pred_5m.tif"
    ok = pred.exists() and pred.stat().st_size > 100
    return ok, f"{pred.name}: {pred.stat().st_size if pred.exists() else 0} bytes"


@check("v02")
def run_lltb1_suffix_strip_logic(ctx):
    site = "IndianTunnel_cave_10x"
    candidates = [site]
    for suffix in ("_10x", "_1x", "_full", "_topo", "_Mesh"):
        if site.endswith(suffix):
            candidates.append(site[: -len(suffix)])
            break
    ok = candidates == ["IndianTunnel_cave_10x", "IndianTunnel_cave"]
    return ok, f"candidate_sites={candidates}"


@check("v02")
def run_lltb1_autodiscovery(ctx):
    """Empty --f32-dir auto-discovery against the canonical analog layout."""
    analog = DATA_ROOT / "analog/IndianTunnel_cave"
    _require(analog, why="analog IndianTunnel_cave f32 dir is local-only")
    roots = [analog, *[p for p in analog.iterdir() if p.is_dir()]]
    f32s = []
    for root in roots:
        f32s = sorted(root.glob("*.f32"))
        if f32s:
            break
    return len(f32s) > 0, f"auto-discovered {len(f32s)} .f32 under {analog.name}/"


@check("v02")
def run_lltb1_imports_cleanly(ctx):
    r = ctx.venv_run(
        ["-c", "import sys; sys.path.insert(0, "
               f"{str(CODE_DIR / 'wp1_lla')!r}); import run_lltb1"])
    return r.returncode == 0, (r.stdout or r.stderr[-200:])


@check("v02")
def extract_rar_mirror_fallback_in_source(ctx):
    src = (CODE_DIR / "setup/extract_rar.py").read_text()
    ok = (src.count("archive.ubuntu.com") >= 2
          or src.count("snapshot.ubuntu.com") >= 1)
    return ok, (f"ubuntu.com={src.count('ubuntu.com')}, "
                f"snapshot={src.count('snapshot.ubuntu.com')}")


@check("v02")
def extract_rar_bsdtar_local(ctx):
    """conventions §8.1 local bsdtar install; CI does not have it."""
    bsdtar = Path.home() / ".local/bin/bsdtar"
    _require(bsdtar, why="local bsdtar (libarchive-tools .deb) is machine-specific")
    sys.path.insert(0, str(CODE_DIR / "setup"))
    import extract_rar  # noqa: E402
    got = extract_rar.get_bsdtar()
    return bool(got), f"get_bsdtar()={got}"


# ------------------------------------------------------------------- v03 ----

@check("v03")
def slope_mask_helper_exists(ctx):
    return hasattr(_sag(), "slope_mask"), "slope_mask"


@check("v03")
def slope_mask_disabled_returns_all_true(ctx):
    y, x = np.mgrid[0:50, 0:50]
    dtm = (x * 0.05 + y * 0.05).astype(np.float64)
    mask = _sag().slope_mask(dtm, pixel_m=1.0, min_slope_deg=0.0)
    return bool(mask.all()), f"True cells={mask.sum()}/{mask.size}"


@check("v03")
def slope_mask_steep_surface_mostly_true(ctx):
    y, x = np.mgrid[0:50, 0:50]
    dtm_steep = (x * 0.5 + y * 0.5).astype(np.float64)  # ~25 deg
    mask = _sag().slope_mask(dtm_steep, pixel_m=1.0, min_slope_deg=10.0)
    return mask.sum() > mask.size * 0.8, f"True={mask.sum()}/{mask.size}"


@check("v03")
def slope_mask_flat_surface_mostly_false(ctx):
    dtm_flat = np.zeros((50, 50), dtype=np.float64)
    mask = _sag().slope_mask(dtm_flat, pixel_m=1.0, min_slope_deg=10.0)
    return mask.sum() < mask.size * 0.05, f"True={mask.sum()}/{mask.size}"


@check("v03")
def slope_mask_nan_safe(ctx):
    dtm_nan = np.full((20, 20), 5.0, dtype=np.float64)
    dtm_nan[5:10, 5:10] = np.nan
    mask = _sag().slope_mask(dtm_nan, pixel_m=1.0, min_slope_deg=10.0)
    return not mask[5:10, 5:10].any(), "NaN cells all False"


@check("v03")
def cli_slope_mask_flag(ctx):
    return "--slope-mask-degrees" in ctx.help, "--slope-mask-degrees in --help"


@check("v03")
def e2e_fieg_fixed_slope10(ctx):
    """Re-run sag_detect on Fieg at 0.5+5 m with the fixed 10-deg mask."""
    _require(FIEG_NPZ, why="Fieg analog npz is local-only")
    res = ctx.sag(FIEG_NPZ, [0.5, 5], "--slope-mask-degrees", "10",
                  min_component=5)
    if res["rc"] != 0:
        return False, f"rc={res['rc']}: {res['stderr'][-200:]}"
    r0 = res["summary"]["rungs"][0]
    ok = ("f1_test_slope" in r0 and "slope_mask_degrees" in r0
          and r0["slope_mask_degrees"] == 10.0
          and r0["f1_test_slope"] >= r0["f1_test"] - 1e-9)
    return ok, (f"f1={r0.get('f1_test'):.4f}, +slope={r0.get('f1_test_slope'):.4f}, "
                f"deg={r0.get('slope_mask_degrees')}")


@check("v03")
def e2e_slope_ok_audit_raster(ctx):
    _require(FIEG_NPZ, why="Fieg analog npz is local-only")
    res = ctx.sag(FIEG_NPZ, [0.5, 5], "--slope-mask-degrees", "10",
                  min_component=5)
    tif = res["outdir"] / "slope_ok_0.5m.tif"
    ok = tif.exists() and tif.stat().st_size > 100
    return ok, f"{tif.name}: {tif.stat().st_size if tif.exists() else 0} bytes"


@check("v03")
def kingsbowl_slope_lift_10x(ctx):
    """v0.3 worst-case lift: slope>=10 lifts Kingsbowl F1 by >=10x."""
    _require(KINGS_NPZ, why="Kingsbowl analog npz is local-only")
    res = ctx.sag(KINGS_NPZ, [5], "--slope-mask-degrees", "10",
                  min_component=5)
    if res["summary"] is None:
        return False, f"rc={res['rc']}: {res['stderr'][-200:]}"
    rk = res["summary"]["rungs"][0]
    raw, slope = rk["f1_test_raw"], rk["f1_test_slope"]
    return slope >= raw * 10 + 1e-9, f"raw={raw:.4f}, +slope={slope:.4f} ({slope / max(raw, 1e-9):.1f}x)"


# ------------------------------------------------------------------- v04 ----

@check("v04")
def tune_helpers_exist(ctx):
    s = _sag()
    return (hasattr(s, "slope_deg_map") and hasattr(s, "tune_slope_threshold")), \
        "slope_deg_map + tune_slope_threshold"


@check("v04")
def slope_deg_map_ramp(ctx):
    dtm = np.array([[i * 0.1 for i in range(20)] for _ in range(20)])
    slope = _sag().slope_deg_map(dtm, pixel_m=1.0)
    med = float(np.nanmedian(slope))
    return slope.shape == dtm.shape and 4.0 < med < 12.0, f"median={med:.2f} deg"


@check("v04")
def tune_slope_threshold_toy(ctx):
    pred = np.zeros((5, 5), bool); truth = np.zeros((5, 5), bool)
    pred[0, 0] = True; pred[4, 4] = True; truth[0, 0] = True
    best_deg, best_f1 = _sag().tune_slope_threshold(
        np.full((5, 5), 100.0), pred, truth, np.ones((5, 5), bool))
    return best_deg > 0 and best_f1 >= 0, f"best_deg={best_deg}, best_f1={best_f1}"


@check("v04")
def cli_tune_slope_flag(ctx):
    return "--tune-slope" in ctx.help, "--tune-slope in --help"


@check("v04")
def e2e_fieg_tune_slope(ctx):
    """--tune-slope on Fieg 0.5 m: tuned flag set and F1 lift > 0.05."""
    _require(FIEG_NPZ, why="Fieg analog npz is local-only")
    res = ctx.sag(FIEG_NPZ, [0.5], "--tune-slope", min_component=5)
    if res["rc"] != 0:
        return False, f"rc={res['rc']}: {res['stderr'][-200:]}"
    r0 = res["summary"]["rungs"][0]
    ok = (r0.get("slope_mask_tuned") is True
          and r0["f1_test_slope"] > 0.05)
    return ok, (f"tuned={r0.get('slope_mask_tuned')}, deg={r0.get('slope_mask_degrees')}, "
                f"f1+slope={r0['f1_test_slope']:.4f} (target >0.05)")


# ------------------------------------------------------------------- p0 -----
# verify_phase0_2026-09-04.py (session 36): 9 ad-hoc checks.

@check("p0")
def smoke_anchors(ctx):
    sm = ctx.smoke
    if sm["rc"] != 0:
        return False, f"smoke exit {sm['rc']}"
    f1s = [round(r["f1_test"], 3) for r in sm["summary"]["rungs"]]
    ok = f1s == [0.392, 0.0, 0.8] and "FUSION : AUC=0.990" in sm["stdout"]
    return ok, f"f1={f1s}, FUSION AUC line={'present' if 'FUSION : AUC=0.990' in sm['stdout'] else 'MISSING'}"


@check("p0")
def rebin_selftest(ctx):
    r = ctx.venv_run([CODE_DIR / "wp2_sag/transfer/_rebin.py"], timeout=300)
    ok = r.returncode == 0 and "PASS: 2 m -> 5 m gives (80, 120)" in r.stdout
    return ok, (r.stdout.strip().splitlines()[-1] if r.stdout.strip()
                else f"rc={r.returncode}: {r.stderr[-120:]}")


@check("p0")
def crs_moon_and_analog(ctx):
    for m in list(sys.modules):
        if m == "_crs":
            del sys.modules[m]
    from _crs import MOON_CRS, ANALOG_CRS, MOON_CRS_WKT, ANALOG_CRS_WKT
    moon_p4, analog_p4 = MOON_CRS.to_proj4(), ANALOG_CRS.to_proj4()
    ok = ("+proj=longlat +R=1737400" in moon_p4
          and "1737400" not in analog_p4
          and len(MOON_CRS_WKT) >= 100 and len(ANALOG_CRS_WKT) >= 100
          and "1737400" in MOON_CRS_WKT)
    return ok, f"moon={moon_p4[:50]}... | analog={analog_p4[:40]}..."


@check("p0")
def http_ua_offline_safe(ctx):
    """Original degrades to PASS when network is unavailable (as here:
    the autouse socket fixture keeps the suite offline)."""
    import urllib.request
    from _http import HEADERS
    try:
        req = urllib.request.Request("https://httpbin.org/headers", headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as r:
            sent = json.loads(r.read().decode())["headers"]
        return sent.get("User-Agent", "").startswith("lunarvoid/"), \
            f"live UA round-trip ok: {sent['User-Agent'][:40]}"
    except Exception as e:  # offline -> constant-only verification
        return HEADERS["User-Agent"].startswith("lunarvoid/"), \
            f"network unavailable ({type(e).__name__}); UA constant verified offline"


@check("p0")
def registry_io_selftests(ctx):
    from registry_io import (LEAK_FEATURES, assert_no_leak, load_registry,
                             parse_confusion, count_confusion_keys, parse_rung_cm)
    assert_no_leak(["span_m", "sag_amp_m", "score"])
    try:
        assert_no_leak(["span_m", "dtm"])
        return False, "assert_no_leak should have raised on 'dtm'"
    except ValueError:
        pass
    df = load_registry(str(WS_DIR / "data/candidate_registry.csv"))
    if len(df) != 278:
        return False, f"loaded {len(df)} rows, expected 278"
    ok = (parse_confusion("rille=42m,chain=99m", "rille") == 42.0
          and parse_confusion("rille=42m", "chain") == 1_000_000.0
          and parse_confusion(None, "rille") == 1_000_000.0
          and parse_rung_cm("LV-TRANSPIT1-200cm-r001") == 200
          and count_confusion_keys("rille=42m,chain=99m,bg=10m") == 3)
    return ok, f"278 rows | LEAK_FEATURES={len(LEAK_FEATURES)} | parsers verified"


@check("p0")
def integration_json_from_csv_lookup(ctx):
    d = json.loads((WS_DIR / "data/outputs/wp1_detector/v0_2_integration_test.json").read_text())
    rd, syn = d["real_data_test"], d["synthetic_smoke_test"]
    ok = (d.get("date") == "2026-09-04"
          and (rd["catalogued_pit_row"], rd["catalogued_pit_col"]) == (887, 608)
          and rd["catalogued_pit_survived"] is True
          and syn.get("passed") is True
          and not (syn["components_area1"] == 96 and syn["components_area10"] == 5
                   and syn["components_area50"] == 1))
    return ok, (f"date={d.get('date')}, pit=(887,608), "
                f"syn {syn['components_area1']}/{syn['components_area10']}/{syn['components_area50']}")


@check("p0")
def commit_msg_hook(ctx):
    hook = WS_DIR / "admin/git-hooks/commit-msg"
    _require(hook, why="commit-msg hook missing from repo checkout")
    cases = [("Fix Frangi float64 upcast", 0),
             ("Add pulearn $0 spent", 1),
             ("Continue ZEROCOST roadmap phase", 1),
             ("Add cost function for VCI calibration", 0),
             ("Have spent the Tier-1 budget", 1)]
    fails = []
    with tempfile.NamedTemporaryFile("w", suffix=".msg", delete=False) as f:
        msgfile = f.name
    for msg, expected_rc in cases:
        Path(msgfile).write_text(msg + "\n")
        r = subprocess.run(["bash", str(hook), msgfile],
                           capture_output=True, text=True, timeout=30)
        if r.returncode != expected_rc:
            fails.append(f"{msg!r}->rc={r.returncode}!={expected_rc}")
    return not fails, "; ".join(fails) or f"{len(cases)}/{len(cases)} cases correct"


@check("p0")
def requirements_pulearn_quirk(ctx):
    reqtxt = (CODE_DIR / "setup/requirements.txt").read_text()
    # DRIFT NOTE (ported 2026-09-10): the original phase0 check required
    # the literal marker "KNOWN INSTALL QUIRK"; requirements.txt was
    # regenerated 2026-09-06 and the marker is now "KNOWN QUIRK" (same
    # note, shortened). Accept both so the port tests the documented
    # intent (quirk note present) rather than 2026-09-04 wording.
    quirk_marked = ("KNOWN INSTALL QUIRK" in reqtxt) or ("KNOWN QUIRK" in reqtxt)
    ok = "pulearn" in reqtxt and "scikit-image" in reqtxt and quirk_marked
    detail = "pulearn+scikit-image pinned, quirk documented"
    if not quirk_marked:
        detail = "install-quirk note MISSING from requirements.txt"
    deb = Path.home() / ".local/share/libarchive-tools-deb/libarchive-tools.deb"
    if deb.exists():
        sha = hashlib.sha256(deb.read_bytes()).hexdigest()
        expected = "ca4f763c2b35a49b9d37a19cd0d3b6625c04c0b81fb4986dd3b95a6ed9de1b77"
        src = (CODE_DIR / "setup/extract_rar.py").read_text()
        ok = ok and expected in src and sha == expected
        detail += f"; cached .deb sha256 matches pin ({sha[:16]}...)"
    else:
        detail += "; cached .deb absent -> sha leg skipped (CI)"
    return ok, detail


@check("p0")
def paper2_citation_fixed(ctx):
    text = (WS_DIR / "papers/paper2_inference_main.md").read_text()
    refs = re.findall(r"`([\w/]+\.py)`", text)
    bad = [r for r in refs if r == "pu_learning_baseline_v2.py"]
    ok = (len(bad) <= 1
          and (len(bad) != 1 or "did not exist" in text)
          and "pu_learning_extended.py" in refs)
    return ok, f"baseline_v2 backticks={len(bad)} (1 = A6 historical note), extended cited={'pu_learning_extended.py' in refs}"


# ------------------------------------------------------------------- v05 ----
# code/wp1_lla/verify_v05.py — stored-artifact recomputation checks (the
# original v05 verifier deliberately re-derives numbers from committed
# CSV/JSON rather than re-running the pipeline).

def _sensor_summary(ctx):
    p = SENSOR_DIR / "sensor_summary.json"
    _require(p, why="v05 sensor summary artifact missing from checkout")
    return json.loads(p.read_text())


@check("v05")
def sensor_summary_identifies_release(ctx):
    S = _sensor_summary(ctx)
    ok = S.get("task", "").startswith("13.4") and S.get("release") == "LLTB-1 v0.5"
    return ok, f"release={S.get('release')}, task={S.get('task')}"


@check("v05")
def composed_table_complete_finite(ctx):
    ct = _sensor_summary(ctx)["composed_table_f1_test_slope"]
    keys = ["baseline", "noiseonly_i65", "sensor_snr50", "sensor_snr100",
            "sensor_snr200", "hapke_mean", "hapkesensor_snr100_mean"]
    ok = {"0.5", "1", "2", "5"} <= set(ct) and all(
        np.isfinite(ct[r][k]) for r in ("0.5", "1", "2", "5") for k in keys)
    return ok, "4 rungs x 7 arms finite" if ok else "incomplete"


@check("v05")
def composed_table_recomputes_from_csv(ctx):
    import pandas as pd
    _require(SENSOR_DIR / "sensor_f1_comparison.csv",
             why="sensor_f1_comparison.csv missing from checkout")
    ct = _sensor_summary(ctx)["composed_table_f1_test_slope"]
    df = pd.read_csv(SENSOR_DIR / "sensor_f1_comparison.csv")
    h = df[df.arm.str.match(r"^i\d+_az\d+$")]
    hs = df[df.arm.str.startswith("hs_") & (~df.arm.str.contains("i65az90"))]
    errs = []
    for r, rk in [(0.5, "0.5"), (1.0, "1"), (2.0, "2"), (5.0, "5")]:
        errs += [abs(ct[rk]["hapke_mean"] - h[h.res_m == r].f1_test_slope.mean()),
                 abs(ct[rk]["hapkesensor_snr100_mean"] - hs[hs.res_m == r].f1_test_slope.mean()),
                 abs(ct[rk]["baseline"] - df[(df.arm == "baseline") & (df.res_m == r)].f1_test_slope.iloc[0])]
    return max(errs) < 1e-9, f"max err={max(errs):.2e}"


@check("v05")
def consistency_vs_13_3_csv(ctx):
    cons = _sensor_summary(ctx)["consistency_vs_133_csv"]
    ok = (cons.get("max_abs_diff_f1_test_slope", 1.0) < 1e-9
          and cons.get("arms_checked", 0) >= 56)
    return ok, f"max|dF1|={cons.get('max_abs_diff_f1_test_slope')} over {cons.get('arms_checked')} rows"


@check("v05")
def headline_numbers_match(ctx):
    ct = _sensor_summary(ctx)["composed_table_f1_test_slope"]
    q = [abs(ct["0.5"][k] - v) < 5e-4 for k, v in
         [("baseline", 0.349), ("noiseonly_i65", 0.300), ("sensor_snr100", 0.309),
          ("hapke_mean", 0.096), ("hapkesensor_snr100_mean", 0.096)]]
    q += [abs(ct["2"]["sensor_snr100"] - 0.122) < 5e-4,
          abs(ct["2"]["hapkesensor_snr100_mean"] - 0.109) < 5e-4]
    return all(q), "0.349/0.300/0.309/0.096/0.096 @0.5m; 0.122/0.109 @2m"


@check("v05")
def shadow_voiding_correction(ctx):
    S = _sensor_summary(ctx)
    am = S["shadow_voiding_correction"]["azimuth_means"]
    pg = S["shadow_voiding_correction"]["per_geometry"]
    means_ok = all(abs(am[f"i{i}"]["allvoid"] - m) < 0.005
                   for i, m in [(45, 0.615), (65, 0.753), (85, 0.918)])
    vals = {i: [v["void_cells_shadowed_frac_allvoid"] for v in pg.values()
                if v["incidence_deg"] == i] for i in (45, 65, 85)}
    ranges_ok = all(round(min(vals[i]) * 100) >= lo and round(max(vals[i]) * 100) <= hi
                    for i, (lo, hi) in [(45, (52, 68)), (65, (67, 80)), (85, (85, 95))])
    return means_ok and ranges_ok, \
        f"means={[round(am[f'i{i}']['allvoid'], 3) for i in (45, 65, 85)]}"


@check("v05")
def hapke_methods_corrections(ctx):
    _require(HAPKE_DIR / "METHODS.md", why="hapke METHODS.md missing from checkout")
    mt = (HAPKE_DIR / "METHODS.md").read_text()
    ok = ("62 %" in mt and "75 %" in mt and "92 %" in mt and "single azimuths" in mt
          and "0.051-0.122" in mt
          and "except i=85°, where label voiding is genuine information loss" in mt
          and "UNTESTED by this experiment" in mt)
    return ok, "62/75/92 %, favorable-azimuth note, 0.051-0.122, i=85 note, caveat"


@check("v05")
def hapke_summary_logs_correction(ctx):
    _require(HAPKE_DIR / "hapke_summary.json", why="hapke_summary.json missing from checkout")
    c22 = json.loads((HAPKE_DIR / "hapke_summary.json").read_text()).get("correction_2026-08-22", {})
    ok = ("azimuth_means_allvoid" in c22 and "per_geometry" in c22
          and all(k in c22["azimuth_means_allvoid"] for k in ("i45", "i65", "i85")))
    return ok, f"correction_2026-08-22 block keys={sorted(c22)[:4]}"


@check("v05")
def perturbed_raster_and_preview_exist(ctx):
    rast = DATA_ROOT / "outputs/wp1_ladder/sensor/sensor_snr100/rung_0.5m.tif"
    png = SENSOR_DIR / "sensor_degradation_preview.png"
    _require(rast, png, why="v05 preview/raster artifacts missing")
    from PIL import Image
    im = Image.open(png)
    ok = im.size[0] >= 800 and im.size[1] >= 500
    return ok, f"raster exists, png={im.size}"


@check("v05")
def release_note_quotes_table(ctx):
    rn = WS_DIR / "notes/2026-08-22_LLTB1_v0.5_release_note.md"
    _require(rn, why="v0.5 release note missing from checkout")
    t = rn.read_text()
    return "0.349" in t and "0.122" in t, "quotes 0.349 and 0.122"


@check("v05")
def smoke_known_good_unchanged(ctx):
    sm = ctx.smoke
    f1s = [float(v) for v in re.findall(r"F1_test=([\d.]+)", sm["stdout"])]
    auc = float((re.findall(r"FUSION : AUC=([\d.]+)", sm["stdout"]) or ["0"])[0])
    ok = (sm["rc"] == 0 and len(f1s) >= 3
          and abs(f1s[0] - 0.392) < 0.005 and abs(f1s[1]) < 0.005
          and abs(f1s[2] - 0.800) < 0.005 and abs(auc - 0.990) < 0.002)
    return ok, f"F1={f1s[:3]}, AUC={auc}"


# --------------------------------------------------------------- driver ----

@pytest.fixture(scope="session")
def verification_ctx(sag_help, smoke_run, sag_run, venv_run,
                     repo_root, code_dir, data_root) -> Ctx:
    return Ctx(repo=repo_root, code=code_dir, ws=WS_DIR, data=data_root,
               help=sag_help, smoke=smoke_run, sag=sag_run, venv_run=venv_run)


@pytest.mark.parametrize("cid", sorted(CHECKS))
def test_verifier_check(cid, verification_ctx):
    """Re-run one ported verifier check and assert its PASS condition."""
    fn = CHECKS[cid]
    ok, detail = fn(verification_ctx)
    assert ok, f"[{cid}] FAIL: {detail}"
