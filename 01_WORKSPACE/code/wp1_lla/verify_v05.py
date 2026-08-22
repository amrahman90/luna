"""LLTB-1 v0.5 verification — Task 13.4 sensor stage + composed table +
skeptic METHODS corrections (2026-08-22). Re-checks headline numbers
from the STORED artifacts (no pipeline re-run except the synthetic
smoke test). Writes the evidence record to
admin/verification_evidence/2026-08-22_v05_verification.json
(same schema as the v02-v04 records)."""
import json, re, subprocess, sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
W = REPO / "01_WORKSPACE"
VENV = Path("/home/frostflux/lunarvoid/venv/bin/python")
SENSOR = W / "data/outputs/wp1_ladder/sensor"
HAPKE = W / "data/outputs/wp1_ladder/hapke"
EVIDENCE = W / "admin/verification_evidence/2026-08-22_v05_verification.json"

results = {"release": "LLTB-1 v0.5", "date": "2026-08-22", "checks": []}
def check(name, ok, detail=""):
    results["checks"].append({"name": name, "ok": bool(ok), "detail": str(detail)[:300]})
    print(f"  {'OK ' if ok else 'FAIL'}  {name}: {detail}")

# 1. summary artifact exists and identifies the release
S = json.loads((SENSOR / "sensor_summary.json").read_text())
check("sensor_summary.json exists, task 13.4 + release v0.5",
      S.get("task", "").startswith("13.4") and S.get("release") == "LLTB-1 v0.5",
      f"release={S.get('release')}")

# 2. composed table complete + finite
ct = S["composed_table_f1_test_slope"]
need = {"0.5", "1", "2", "5"}
keys = ["baseline", "noiseonly_i65", "sensor_snr50", "sensor_snr100",
        "sensor_snr200", "hapke_mean", "hapkesensor_snr100_mean"]
ok = need <= set(ct) and all(np.isfinite(ct[r][k]) for r in need for k in keys)
check("composed table: 4 rungs x {baseline,noise,sensor50/100/200,hapke,hapke+sensor} finite",
      ok, "all present" if ok else "incomplete")

# 3. composed table reproducible from the committed CSV (determinism)
df = pd.read_csv(SENSOR / "sensor_f1_comparison.csv")
h = df[df.arm.str.match(r"^i\d+_az\d+$")]
hs = df[df.arm.str.startswith("hs_") & (~df.arm.str.contains("i65az90"))]
errs = []
for r, rk in [(0.5, "0.5"), (1.0, "1"), (2.0, "2"), (5.0, "5")]:
    errs += [abs(ct[rk]["hapke_mean"] - h[h.res_m == r].f1_test_slope.mean()),
             abs(ct[rk]["hapkesensor_snr100_mean"] - hs[hs.res_m == r].f1_test_slope.mean()),
             abs(ct[rk]["baseline"] - df[(df.arm == "baseline") & (df.res_m == r)].f1_test_slope.iloc[0])]
check("composed table recomputes from sensor_f1_comparison.csv (max err < 1e-9)",
      max(errs) < 1e-9, f"max err={max(errs):.2e}")

# 4. 13.3 replication exact (within CSV float round-off)
cons = S["consistency_vs_133_csv"]
check("baseline/noiseonly/Hapke arms reproduce 13.3 CSV exactly (< 1e-9)",
      cons.get("max_abs_diff_f1_test_slope", 1.0) < 1e-9 and cons.get("arms_checked", 0) >= 56,
      f"max|dF1|={cons.get('max_abs_diff_f1_test_slope')} over {cons.get('arms_checked')} rows")

# 5. headline numbers (quoted in release note / METHODS)
q = [abs(ct["0.5"][k] - v) < 5e-4 for k, v in
     [("baseline", 0.349), ("noiseonly_i65", 0.300), ("sensor_snr100", 0.309),
      ("hapke_mean", 0.096), ("hapkesensor_snr100_mean", 0.096)]]
q += [abs(ct["2"]["sensor_snr100"] - 0.122) < 5e-4,
      abs(ct["2"]["hapkesensor_snr100_mean"] - 0.109) < 5e-4]
check("headline numbers match quoted 0.349/0.300/0.309/0.096/0.096 (0.5 m) "
      "and sensor-2m regression 0.122, composed 0.109", all(q))

# 6. shadow-voiding correction (skeptic): azimuth means + per-az ranges
am = S["shadow_voiding_correction"]["azimuth_means"]
pg = S["shadow_voiding_correction"]["per_geometry"]
means_ok = all(abs(am[f"i{i}"]["allvoid"] - m) < 0.005 for i, m in [(45, 0.615), (65, 0.753), (85, 0.918)])
vals = {i: [v["void_cells_shadowed_frac_allvoid"] for k, v in pg.items() if v["incidence_deg"] == i]
        for i in (45, 65, 85)}
ranges_ok = all(round(min(vals[i]) * 100) >= lo and round(max(vals[i]) * 100) <= hi
                for i, (lo, hi) in [(45, (52, 68)), (65, (67, 80)), (85, (85, 95))])
check("voiding azimuth-means 0.615/0.753/0.918; ranges 52-68/67-80/85-95 %",
      means_ok and ranges_ok,
      f"means={[round(am[f'i{i}']['allvoid'],3) for i in (45,65,85)]}; "
      f"ranges={[f'{min(v):.2f}-{max(v):.2f}' for v in vals.values()]}")

# 7. Hapke METHODS.md corrections present
mt = (HAPKE / "METHODS.md").read_text()
ok = ("62 %" in mt and "75 %" in mt and "92 %" in mt and "single azimuths" in mt
      and "0.051-0.122" in mt
      and "except i=85°, where label voiding is genuine information loss" in mt
      and "UNTESTED by this experiment" in mt)
check("hapke METHODS.md: corrected 62/75/92 %, favorable-azimuth note, "
      "per-geometry range 0.051-0.122, i=85 genuine-loss attribution, "
      "analog-scope caveat", ok)

# 8. hapke_summary.json logs both series
hs_json = json.loads((HAPKE / "hapke_summary.json").read_text())
c22 = hs_json.get("correction_2026-08-22", {})
ok = ("azimuth_means_allvoid" in c22 and "per_geometry" in c22 and
      all(k in c22["azimuth_means_allvoid"] for k in ("i45", "i65", "i85")))
check("hapke_summary.json correction_2026-08-22 block logs both series", ok)

# 9. raster + preview artifacts exist
rast = Path.home() / "lunarvoid/data/outputs/wp1_ladder/sensor/sensor_snr100/rung_0.5m.tif"
png = SENSOR / "sensor_degradation_preview.png"
from PIL import Image
im = Image.open(png)
check("perturbed rung raster + preview PNG exist (>=800x500 px)",
      rast.exists() and png.exists() and im.size[0] >= 800 and im.size[1] >= 500,
      f"raster={rast.exists()}, png={im.size}")

# 10. release note exists with composed table
rn = (W / "notes/2026-08-22_LLTB1_v0.5_release_note.md")
ok = rn.exists() and "0.349" in rn.read_text() and "0.122" in rn.read_text()
check("release note exists and quotes composed-table numbers", ok)

# 11. smoke test known-good (synthetic; unchanged by this task)
r = subprocess.run([str(VENV), str(W / "code/smoke_test.py")],
                   capture_output=True, text=True, timeout=600)
out = r.stdout + r.stderr
f1s = [float(x) for x in re.findall(r"F1_test=([\d.]+)", out)]
auc = float((re.findall(r"FUSION : AUC=([\d.]+)", out) or ["0"])[0])
check("smoke test known-good: per-rung F1 0.392/0.000/0.800, fusion AUC 0.990",
      r.returncode == 0 and len(f1s) >= 3 and
      abs(f1s[0] - 0.392) < 0.005 and abs(f1s[1]) < 0.005 and
      abs(f1s[2] - 0.800) < 0.005 and abs(auc - 0.990) < 0.002,
      f"F1={f1s[:3]}, AUC={auc}")

# Summary
results["n_checks"] = len(results["checks"])
results["n_ok"] = sum(1 for c in results["checks"] if c["ok"])
results["n_fail"] = results["n_checks"] - results["n_ok"]
results["all_ok"] = results["n_fail"] == 0
EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.write_text(json.dumps(results, indent=2))
print(f"\nWrote {EVIDENCE}")
print(f"PASS: {results['n_ok']}/{results['n_checks']}  "
      f"({'ALL OK' if results['all_ok'] else 'SOME FAILED'})")
sys.exit(0 if results["all_ok"] else 1)
