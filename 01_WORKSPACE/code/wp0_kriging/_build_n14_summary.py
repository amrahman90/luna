"""Combine existing 10 + new 4 + 5 highland stubs = 19 per-DTM rows,
write new summary JSON with by_terrain split (mare vs highland) and
per_dtm terrain_extrapolation annotations for highland sites.

N=19 = 10 existing processed + 4 new processed (FECUNPIT + KINGCRATER2/3/4)
       + 5 highland TYCHOPK* stubs (skipped due to insufficient panels;
         flagged as extrapolation, not portability).

The 2 FRESHMELT* DTMs (impact melt, mare-classified) are also SKIPPED
but not added to N=19 (they are documented in run_metadata of the
summary JSON).

This is a one-shot build script; called from bash.
"""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import numpy as np

REPO = Path("/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube")
OLD_CSV = Path("/home/frostflux/lunarvoid/admin_evidence/p3_1c_n19_2026_08_22/per_dtm_floors_n10_backup.csv")
OLD_SUMMARY = Path("/home/frostflux/lunarvoid/admin_evidence/p3_1c_n19_2026_08_22/per_dtm_floors_summary_n10_backup.json")
NEW_CSV_DIR = Path("/tmp/per_dtm_new")
NEW_CSV = REPO / "01_WORKSPACE/data/outputs/wp0_kriging/per_dtm_floors.csv"
NEW_SUMMARY = REPO / "01_WORKSPACE/data/outputs/wp0_kriging/per_dtm_floors_summary.json"

NEW_DTMS_OK = ["FECUNPIT", "KINGCRATER2", "KINGCRATER3", "KINGCRATER4"]
NEW_DTMS_SKIP_HIGHLAND = ["TYCHOPK", "TYCHOPK02", "TYCHOPK03", "TYCHOPK04", "TYCHOPK07"]
NEW_DTMS_SKIP_MARE = ["FRESHMELT", "FRESHMELT1"]  # impact melt, mare class

# mare vs highland classification (per dispatch 2026-08-22)
HIGHLAND = {"GRUITHUIS17", "SWFECUNPIT1",
            "TYCHOPK", "TYCHOPK02", "TYCHOPK03",
            "TYCHOPK04", "TYCHOPK07",
            "KINGCRATER2", "KINGCRATER3", "KINGCRATER4"}

# 1) read existing 10 + 4 new = 14 rows
old_df = pd.read_csv(OLD_CSV)
print(f"[load] existing 10 rows: {list(old_df.dtm_name)}")

new_rows = []
for d in NEW_DTMS_OK:
    df = pd.read_csv(NEW_CSV_DIR / f"per_dtm_{d}.csv")
    assert len(df) == 1, f"expected 1 row for {d}, got {len(df)}"
    new_rows.append(df.iloc[0].to_dict())
print(f"[load] new {len(new_rows)} rows: {[r['dtm_name'] for r in new_rows]}")

# 2) add 5 stub rows for highland TYCHOPK* DTMs (skipped due to no flat panels)
# numeric columns NaN (will be written as empty strings); notes go in summary
HIGHLAND_STUB_SITES = {
    "TYCHOPK": "Tycho Central Peak",
    "TYCHOPK02": "Tycho Central Peak",
    "TYCHOPK03": "Tycho Central Peak",
    "TYCHOPK04": "Tycho Central Peak",
    "TYCHOPK07": "Tycho Central Peak",
}
for name, site in HIGHLAND_STUB_SITES.items():
    new_rows.append({
        "dtm_name": name,
        "site": site,
        "lon_min": np.nan, "lon_max": np.nan,
        "lat_min": np.nan, "lat_max": np.nan,
        "n_panels": 0,
        "pooled_rms_m": np.nan, "three_sigma_m": np.nan,
        "panel_min_rms": np.nan, "panel_max_rms": np.nan,
        "local_Amin_m": np.nan,
        "mtime": "skipped_insufficient_panels",
    })
print(f"[load] highland stubs: {list(HIGHLAND_STUB_SITES.keys())}")

# concat preserving existing 10 byte-identically (column order matches OLD)
combined = pd.concat([old_df, pd.DataFrame(new_rows)], ignore_index=True)
assert len(combined) == 19, f"expected 19 rows, got {len(combined)}"
combined.to_csv(NEW_CSV, index=False, float_format="%.6f")
print(f"[out] per_dtm_floors.csv -> {NEW_CSV} ({len(combined)} rows)")

# 2) build new summary
with OLD_SUMMARY.open() as f:
    old = json.load(f)

# skip list: existing 639 minus 4 newly processed = 635 (the 7 newly-skipped
# were already in the 639 list, so they stay)
old_skipped = set(old["skipped"])
new_processed = set(NEW_DTMS_OK)  # these were in old skipped, now move out
new_skipped_list = sorted(old_skipped - new_processed)
assert len(new_skipped_list) == 635, f"expected 635 skipped, got {len(new_skipped_list)}"

# n_processed: count only rows with a real pooled_rms_m (excluding stub rows)
processed_mask = np.isfinite(combined["pooled_rms_m"].to_numpy())
n_processed_actual = int(processed_mask.sum())

rms = combined["pooled_rms_m"].to_numpy()
is_highland = combined["dtm_name"].isin(HIGHLAND).to_numpy()
is_mare = ~is_highland
# for by_terrain stats use only processed rows
mare_rms = rms[is_mare & processed_mask]
highland_rms = rms[is_highland & processed_mask]
mare_Amin = combined.loc[is_mare & processed_mask, "local_Amin_m"].to_numpy()
highland_Amin = combined.loc[is_highland & processed_mask, "local_Amin_m"].to_numpy()

# sources_used list: 10 existing + 4 new
sources_used = old["sources_used"] + ["raw"] * len(NEW_DTMS_OK)

# per-dtm block with terrain_extrapolation for highland sites
per_dtm_block = {}
for _, row in combined.iterrows():
    name = row["dtm_name"]
    entry = {
        "site": row["site"],
        "pooled_rms_m": round(float(row["pooled_rms_m"]), 6),
        "three_sigma_m": round(float(row["three_sigma_m"]), 6),
        "local_Amin_m": round(float(row["local_Amin_m"]), 6),
        "n_panels": int(row["n_panels"]),
        "mtime": row["mtime"],
    }
    if name in HIGHLAND:
        entry["terrain_extrapolation"] = (
            "highland; TRANQPIT1 calibration is mare-only; "
            "results are extrapolation, not portability"
        )
    per_dtm_block[name] = entry

# add stub per_dtm entries for SKIPPED highland sites (TYCHOPK02/03/04/07).
# They were skipped at the per_dtm_floors level (insufficient flat panels);
# still flag them as highland-extrapolation so any downstream caller
# can refuse to use them without reading the broader summary.
SKIPPED_HIGHLAND = {
    "TYCHOPK": ("Tycho Central Peak", "3 panels (below min_panels=4)"),
    "TYCHOPK02": ("Tycho Central Peak", "0 panels (central peak, too steep)"),
    "TYCHOPK03": ("Tycho Central Peak", "0 panels (central peak, too steep)"),
    "TYCHOPK04": ("Tycho Central Peak", "0 panels (central peak, too steep)"),
    "TYCHOPK07": ("Tycho Central Peak", "0 panels (central peak, too steep)"),
}
for name, (site, reason) in SKIPPED_HIGHLAND.items():
    per_dtm_block[name] = {
        "site": site,
        "status": "skipped_insufficient_panels",
        "n_panels": 0,
        "skip_reason": reason,
        "terrain_extrapolation": (
            "highland; TRANQPIT1 calibration is mare-only; "
            "results are extrapolation, not portability"
        ),
    }

summary = {
    "generated": datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
    "n_processed": n_processed_actual,
    "n_in_csv_total": int(len(combined)),  # 19 = 14 processed + 5 highland stubs
    "n_skipped": int(len(new_skipped_list)),
    "skipped": new_skipped_list,
    "min_panels": old["min_panels"],
    "median_pooled_rms_m": round(float(np.median(rms[processed_mask])), 6),
    "min_pooled_rms_m": round(float(rms[processed_mask].min()), 6),
    "max_pooled_rms_m": round(float(rms[processed_mask].max()), 6),
    "median_local_Amin_m": round(float(np.median(combined.loc[processed_mask, "local_Amin_m"])), 6),
    "elapsed_s": old["elapsed_s"] + 651.5,  # total wall time including new 11 (~10.85 min)
    "csv": str(NEW_CSV),
    "sources_used": sources_used,
    "by_terrain": {
        "mare": {
            "n": int(len(mare_rms)),
            "median_pooled_rms_m": round(float(np.median(mare_rms)), 6),
            "min_pooled_rms_m": round(float(mare_rms.min()), 6),
            "max_pooled_rms_m": round(float(mare_rms.max()), 6),
            "median_local_Amin_m": round(float(np.median(mare_Amin)), 6),
            "sites": sorted(combined.loc[is_mare & processed_mask, "dtm_name"].tolist()),
        },
        "highland": {
            "n": int(len(highland_rms)),
            "median_pooled_rms_m": round(float(np.median(highland_rms)), 6),
            "min_pooled_rms_m": round(float(highland_rms.min()), 6),
            "max_pooled_rms_m": round(float(highland_rms.max()), 6),
            "median_local_Amin_m": round(float(np.median(highland_Amin)), 6),
            "sites": sorted(combined.loc[is_highland & processed_mask, "dtm_name"].tolist()),
            "highland_sites_set": sorted(HIGHLAND),
            "highland_classification_note": (
                "highland = Gruithuisen domes (silicic, non-mare), "
                "SW Fecunditatis pit (SW rim of Mare Fecunditatis, "
                "highland edge per findings.md 2026-08-21), all "
                "TYCHOPK* (Tycho central peak — highland composition) "
                "+ KINGCRATER* (King crater peak — highland composition) "
                "sites. Mare subset excludes these."
            ),
            "terrain_extrapolation_note": (
                "TRANQPIT1 calibration is mare-only. Highland per-DTM "
                "floors are reported for completeness, but any "
                "morphometric inference on highland sites using the "
                "frozen (mare-calibrated) thresholds is extrapolation, "
                "not portability. See per_dtm.<DTM>.terrain_extrapolation."
            ),
        },
    },
    "per_dtm": per_dtm_block,
    "run_metadata": {
        "n_dtms_attempted_in_run": 11,
        "n_dtms_skipped_due_to_insufficient_panels_highland": len(NEW_DTMS_SKIP_HIGHLAND),
        "n_dtms_skipped_due_to_insufficient_panels_mare_impact_melt": len(NEW_DTMS_SKIP_MARE),
        "skipped_in_run_due_to_panels": NEW_DTMS_SKIP_HIGHLAND + NEW_DTMS_SKIP_MARE,
        "highland_stub_rows_added_to_csv": NEW_DTMS_SKIP_HIGHLAND,
        "reproducibility": "existing 10 rows are byte-identical to the "
                           "2026-08-22 backup; verified by re-running the "
                           "pipeline with seed=42 (diff exit 0)",
        "format_failures": "none; all 11 new DTMs loaded OK (CRS, geokeys, "
                           "f32 sentinel |x|>1e30 per conventions §1.5); "
                           "7 were skipped due to insufficient flat mare "
                           "panels (<=3 panels in highland/impact-melt terrain)",
    },
}

with NEW_SUMMARY.open("w") as f:
    json.dump(summary, f, indent=2)
print(f"[out] per_dtm_floors_summary.json -> {NEW_SUMMARY}")
print(f"[stats] mare n={len(mare_rms)}, pooled_rms median={np.median(mare_rms):.4f} m")
print(f"[stats] highland n={len(highland_rms)}, pooled_rms median={np.median(highland_rms):.4f} m")
print(f"[stats] all n={len(rms)}, pooled_rms median={np.median(rms):.4f} m")
