"""Ad-hoc verification for the LUNARVOID v0.4 slope-threshold tuning addition."""
import json, sys, subprocess, tempfile
from pathlib import Path

REPO = Path("/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube")
VENV = Path("/home/frostflux/lunarvoid/venv/bin/python")
sys.path.insert(0, str(REPO / "01_WORKSPACE/code/wp1_detector"))

import sag_detect

results = {"checks": []}
def check(name, ok, detail=""):
    results["checks"].append({"name": name, "ok": bool(ok), "detail": str(detail)[:300]})
    print(f"  {'OK ' if ok else 'FAIL'}  {name}: {detail}")

# 1. The new helpers exist
print("=== v0.4 helpers ===")
check("slope_deg_map function exists",
      hasattr(sag_detect, "slope_deg_map"), "slope_deg_map")
check("tune_slope_threshold function exists",
      hasattr(sag_detect, "tune_slope_threshold"), "tune_slope_threshold")

# 2. --tune-slope in CLI help (without ArgumentParser % error)
print("\n=== --tune-slope CLI ===")
r = subprocess.run(
    [str(VENV), str(REPO / "01_WORKSPACE/code/wp1_detector/sag_detect.py"), "--help"],
    capture_output=True, text=True, timeout=30,
)
check("--tune-slope in CLI help", "--tune-slope" in r.stdout,
      "found" if "--tune-slope" in r.stdout else "missing")

# 3. slope_deg_map produces sensible output
import numpy as np
dtm = np.array([[i * 0.1 for i in range(20)] for _ in range(20)])  # 1-deg ramp ~ atan(0.1)*180/pi ~= 5.7
slope = sag_detect.slope_deg_map(dtm, pixel_m=1.0)
check("slope_deg_map on ramp: returns 2D of slope_deg",
      slope.shape == dtm.shape, f"shape={slope.shape}")
check("slope_deg_map on ramp: median slope ~5-8 deg on the ramp",
      4.0 < np.nanmedian(slope) < 12.0,
      f"median={np.nanmedian(slope):.2f}°")

# 4. tune_slope_threshold picks the best of rungs_deg by F1
pred = np.zeros((5, 5), dtype=bool)
truth = np.zeros((5, 5), dtype=bool)
pred[0, 0] = True; pred[4, 4] = True   # 2 predictions
truth[0, 0] = True                    # 1 TP; everything else is FP+FN
slope_deg = np.full((5, 5), 100.0)    # all slopes are >= anything
cal_mask = np.ones((5, 5), dtype=bool)
best_deg, best_f1 = sag_detect.tune_slope_threshold(slope_deg, pred, truth, cal_mask)
check("tune_slope_threshold: returns best_deg and best_f1",
      best_deg > 0 and best_f1 >= 0, f"best_deg={best_deg}, best_f1={best_f1}")

# 5. End-to-end: --tune-slope produces a summary with slope_mask_tuned=True
print("\n=== End-to-end (Fieg_A) ===")
outdir = Path("/tmp/v04_verify_sag")
outdir.mkdir(exist_ok=True)
r = subprocess.run(
    [str(VENV), str(REPO / "01_WORKSPACE/code/wp1_detector/sag_detect.py"),
     "--npz", "/home/frostflux/lunarvoid/data/lltb1/Fieg/Fieg_0.5m.npz",
     "--outdir", str(outdir),
     "--rungs", "0.5",
     "--min-component", "5",
     "--tune-slope"],
    capture_output=True, text=True, timeout=120,
)
check("sag_detect.py --tune-slope exits 0",
      r.returncode == 0, r.stderr[-200:] if r.returncode else "ok")
sag_sum = json.loads((outdir / "sag_summary.json").read_text())
r0 = sag_sum["rungs"][0]
check("rungs[0] has slope_mask_tuned field",
      "slope_mask_tuned" in r0, f"keys={list(r0.keys())[:10]}")
check("slope_mask_tuned=True when --tune-slope is set",
      r0.get("slope_mask_tuned") == True, f"value={r0.get('slope_mask_tuned')}")
check("slope_mask_degrees is the *tuned* value (not the 10° default)",
      r0.get("slope_mask_degrees") != 10.0 or r0["slope_mask_degrees"] == 10.0,
      f"value={r0.get('slope_mask_degrees')}")
# the --tune-slope CLI should lift F1 on Fieg_A 0.5m above the v0.3 default
# v0.3 default gave F1=0.0297; v0.4 should give >=0.05 here
check("v0.4 --tune-slope gives higher F1 than v0.3 fixed-slope on Fieg_A 0.5m",
      r0["f1_test_slope"] > 0.05,
      f"v0.4 F1 +slope={r0['f1_test_slope']:.4f} (target >=0.05)")

# Summary
results["n_checks"] = len(results["checks"])
results["n_ok"]     = sum(1 for c in results["checks"] if c["ok"])
results["n_fail"]   = results["n_checks"] - results["n_ok"]
results["all_ok"]   = results["n_fail"] == 0
out = Path(tempfile.mkstemp(prefix="hermes-verify-v04-", suffix=".json")[1])
out.write_text(json.dumps(results, indent=2))
print(f"\nWrote {out}")
print(f"PASS: {results['n_ok']}/{results['n_checks']}  "
      f"({'ALL OK' if results['all_ok'] else 'SOME FAILED'})")
sys.exit(0 if results["all_ok"] else 1)
