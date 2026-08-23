"""P3.1c Cycle 1 close — merge the new GRUITHUIS17/GRUITHMARE2/MARIUSCONE
per-DTM entries into the existing comprehensive transfer_summary.json.

Inputs:
  - /tmp/transfer_summary_old.json   : the git-HEAD version (21 DTMs, 257 cands, 9 FP, 14840.27 km^2)
  - 01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json  : the new partial 3-DTM run (we re-ran here)
  - The actual numbers we just measured from the 3-DTM run (stored in scripts/transfer_summary_partial.json)

Output:
  - 01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json  : merged
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from scipy.stats import chi2

OLD = json.load(open('/tmp/transfer_summary_old.json'))
# Also pull the 3 new per-DTM entries from the partial run we just did
PARTIAL = json.load(open('01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json'))

# The 3 new DTMs
NEW_DTMS = ['GRUITHUIS17', 'GRUITHMARE2', 'MARIUSCONE']


def poisson_fp_ci(n_fp, area_km2):
    """FP/10^4 km^2 point + 95% Poisson CI."""
    if area_km2 <= 0:
        return (float("nan"), float("nan"), float("nan"))
    if n_fp == 0:
        upper_count = chi2.ppf(0.95, 2) / 2.0
        return (0.0, 0.0, upper_count / area_km2 * 1e4)
    lo_count = chi2.ppf(0.025, 2 * n_fp) / 2.0
    hi_count = chi2.ppf(0.975, 2 * n_fp + 2) / 2.0
    return (n_fp / area_km2 * 1e4,
            lo_count / area_km2 * 1e4,
            hi_count / area_km2 * 1e4)


# ---- Take the new per-DTM entries from the partial run ----
new_per_dtm = {d: PARTIAL['per_dtm'][d] for d in NEW_DTMS}

# ---- Merge into the OLD summary ----
merged = json.loads(json.dumps(OLD))  # deep copy

# Replace the 3 stub per-dtm entries with the real ones
for d in NEW_DTMS:
    merged['per_dtm'][d] = new_per_dtm[d]

# ---- Recompute the aggregate from the merged per-dtm ----
total_cands = sum(d.get('n_candidates', 0) for d in merged['per_dtm'].values())
total_above = sum(d.get('n_above_local_floor', 0) for d in merged['per_dtm'].values())
total_below = sum(d.get('n_below_local_floor', 0) for d in merged['per_dtm'].values())
total_tierB = sum(d.get('n_tier_B', 0) for d in merged['per_dtm'].values())
total_fp = sum(d.get('n_fp', 0) for d in merged['per_dtm'].values())
total_tp = sum(d.get('n_tp', 0) for d in merged['per_dtm'].values())
total_area = sum(d.get('area_km2', 0.0) for d in merged['per_dtm'].values())
agg_pt, agg_lo, agg_hi = poisson_fp_ci(total_fp, total_area)

# Count DTMs with real (non-stub) per-dtm entries:
# "n_dtms_with_score_raster" — DTMs that contributed real peaks (area>0 or n_candidates>0)
score_dtm_set = sorted([
    k for k, v in merged['per_dtm'].items()
    if v.get('area_km2', 0.0) > 0.0 or v.get('n_candidates', 0) > 0
    or v.get('rungs') and any(r is not None for r in v.get('rungs', []))
])
n_score_raster = len(score_dtm_set)
skipped = sorted([k for k in merged['per_dtm'].keys() if k not in score_dtm_set])
n_skipped = len(skipped)
n_dtm_rung_pairs = sum(
    sum(1 for r in v.get('rungs', []) if r is not None) for v in merged['per_dtm'].values()
)

# Update aggregate block
merged['aggregate']['n_dtms_with_score_raster'] = n_score_raster
merged['aggregate']['n_dtms_skipped_no_raster'] = n_skipped
merged['aggregate']['dtms_skipped'] = skipped
merged['aggregate']['n_dtm_rung_pairs'] = n_dtm_rung_pairs
merged['aggregate']['n_candidates'] = total_cands
merged['aggregate']['n_above_local_floor'] = total_above
merged['aggregate']['n_below_local_floor'] = total_below
merged['aggregate']['n_tier_B'] = total_tierB
merged['aggregate']['n_fp'] = total_fp
merged['aggregate']['n_tp'] = total_tp
merged['aggregate']['total_area_km2'] = total_area
merged['aggregate']['fp_per_1e4km2'] = agg_pt
merged['aggregate']['fp_per_1e4km2_ci95_lo'] = agg_lo
merged['aggregate']['fp_per_1e4km2_ci95_hi'] = agg_hi
merged['aggregate']['fp_per_1e4km2_n_above_floor'] = total_above

# Update scope_banner
merged['scope_banner'] = (
    f"N=21/649 (21 good-tier DTMs on disk of 649 in scope; "
    f"{n_score_raster} have cached v0.1 score rasters; "
    f"{n_skipped} are skipped for missing score raster: {skipped})"
)

# Update the date stamp
from datetime import date
merged['generated'] = date.today().isoformat()

# Annotate the "aggregate" fields with cycle notes
merged['cycle_notes'] = {
    "cycle1_close_2026-08-23": [
        "Added 3 newly-Frangi-scored NAC DTMs: GRUITHUIS17, GRUITHMARE2, MARIUSCONE",
        "Added 18 below-local-floor candidates to registry (10 GRUITHMARE2 + 6 GRUITHUIS17 + 2 MARIUSCONE)",
        "All 18 new candidates are below-local-floor (sag_amp < local_Amin at peak; local_Amin exists at all 3 sites — NOT terrain-extrapolation)",
        "0 new FPs (above-floor count: 0; FPs require above-floor)",
        "Skeptic fall-back annotation (Cycle 1 second-opinion rule) applied to GRUITHMARE2 and MARIUSCONE new rows; GRUITHUIS17 NOT annotated (frangi@score=0.0424 ≥ 0.02 threshold)",
        "n_fp delta: 0 (was 9, still 9); area delta: +6205.89 km^2 (was 14840.27, now 21046.16)",
    ],
    "frangi_at_score_check": {
        "GRUITHUIS17": {"frangi_at_score_max": 0.0424, "depth_at_score_max_m": 8.1,
                        "annotate": False, "reason": "frangi@score >= 0.02; pit passes vesselness threshold"},
        "GRUITHMARE2": {"frangi_at_score_max": 0.0150, "depth_at_score_max_m": 604.3,
                        "annotate": True, "reason": "frangi@score < 0.02 AND depth@score >= 100 m — deep-pit low-vesselness"},
        "MARIUSCONE":  {"frangi_at_score_max": 0.0107, "depth_at_score_max_m": 619.3,
                        "annotate": True, "reason": "frangi@score < 0.02 AND depth@score >= 100 m — deep-pit low-vesselness"},
    },
}

# ---- Recompute per_rung from the merged per_dtm ----
# We need to rebuild per_rung from each per_dtm's rungs + the pair_results
# But the per_dtm entries only have aggregated stats. The pair_results in the partial
# has the per-rung breakdown for the 3 new sites. Let's load it.
# Simpler: compute per_rung from pair_results in OLD + NEW

# Load old pair_results
old_pair_results = OLD.get('pair_results', [])
new_pair_results = PARTIAL.get('pair_results', [])
# Filter new_pair_results to the 3 NEW_DTMS (exclude stubs from skipped)
new_pair_real = [r for r in new_pair_results if r.get('dtm') in NEW_DTMS and r.get('rung_m') is not None]

# Combine
combined_pair_results = old_pair_results + new_pair_real

per_rung = {}
for r in combined_pair_results:
    if r.get('rung_m') is None or 'n_candidates' not in r:
        continue
    key = r['rung_m']
    d = per_rung.setdefault(key, {
        'n_candidates': 0, 'n_above_local_floor': 0,
        'n_tier_B': 0, 'n_fp': 0, 'n_tp': 0, 'area_km2': 0.0,
    })
    d['n_candidates'] += r.get('n_candidates', 0)
    d['n_above_local_floor'] += r.get('n_above_local_floor', 0)
    d['n_tier_B'] += r.get('n_tier_B', 0)
    d['n_fp'] += r.get('n_fp', 0)
    d['n_tp'] += r.get('n_tp', 0)
    d['area_km2'] += r.get('area_km2', 0.0)
for rung, d in per_rung.items():
    pt, lo, hi = poisson_fp_ci(d['n_fp'], d['area_km2'])
    d['fp_per_1e4km2'] = pt
    d['fp_per_1e4km2_ci95_lo'] = lo
    d['fp_per_1e4km2_ci95_hi'] = hi
    d['ci_method'] = 'Poisson-exact (Garwood) 95% CI'

merged['per_rung'] = {f"{k:g}": v for k, v in sorted(per_rung.items())}
merged['pair_results'] = combined_pair_results
merged['registry_rows_added'] = OLD.get('registry_rows_added', 0) + 18  # 18 new rows this cycle

# Write out
out_path = Path('01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json')
with open(out_path, 'w') as f:
    json.dump(merged, f, indent=2)

print(f"[out] merged {out_path}")
print(f"[agg] n_fp={total_fp}, total_area_km2={total_area:.4f}")
print(f"[agg] fp_per_1e4km2={agg_pt:.4f} [95% CI {agg_lo:.4f}, {agg_hi:.4f}]")
print(f"[per] n_candidates={total_cands}, above={total_above}, below={total_below}, tier_B={total_tierB}, tier_A=0")
print(f"[per] DTMs with score raster: {n_score_raster}; skipped: {n_skipped} {skipped}")
print(f"[per] registry rows added this cycle: 18 (total: 257 + 18 = 275)")
print()
print("=== Per-DTM new entries ===")
for d in NEW_DTMS:
    v = merged['per_dtm'][d]
    print(f"{d}: n_cands={v['n_candidates']}, above={v['n_above_local_floor']}, FP={v['n_fp']}, "
          f"area={v['area_km2']:.2f} km^2, top_score={v['top_score']:.4f}")
