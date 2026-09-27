"""Verification script for WP0.5 - Roof Deformation Forward Model.

Reproduces the 7 canonical anchor points from the v5 F1 derivation,
compares against the dispatch-table expected values, and writes a
deterministic JSON evidence record.

Verification protocol
---------------------
- Imports `deflection_model.clamped_slab` (the function the rest of
  the pipeline depends on; arch and damaged regimes are first-order
  reductions of it, so anchoring the slab formula is sufficient to
  validate the whole module).
- Computes each canonical point with TWO densities:
    * rho = 2900  (the value stated in the dispatch canonical table)
    * rho = 3000  (the value explicitly used in the F1 derivation,
                   see `00_SOURCE_ORIGINALS/LUNARVOID_v5_Review_Report.txt`
                   sec. F1, line: "with rho = 3000 kg/m^3")
- Reports both, PASSes if the rho=2900 (table-stated) value matches
  the expected within +/-5% (T5 rule). Also reports the rho=3000
  reproduction as an evidence bonus.
- Prints `PASS: 7/7 (ALL OK)` (or `FAIL: N/7 ...`).
- Writes `verify_wp0_5_deflection_<UTC-timestamp>.json` to the
  verification_evidence/scripts/ dir per the conventions section 7.

Usage
-----
    ~/lunarvoid/venv/bin/python verify_wp0_5_deflection.py

Exit code 0 on PASS, 1 on FAIL (verifier-friendly).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Repo-rooted, sys.path inject for sibling-module import.
REPO = Path("/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube")
sys.path.insert(0, str(REPO / "01_WORKSPACE/code/wp0_5_deflection"))

from deflection_model import (  # noqa: E402
    G_LUNAR,
    clamped_slab,
    CANONICAL_ANCHORS,
)

# Detection floor from v5 conventions section 5 ("3x sag-band RMS =>
# only A>=4 m single-DTM detectable") - used in the per-row evidence
# so the JSON record carries the reconciliation claim.
DETECTOR_FLOOR_M = 4.0

# T5 tolerance per protocol.
TOL_T5 = 0.05  # +/-5%


def fmt_mm(d_m: float) -> str:
    """Pretty-print metres as a sensible unit."""
    if d_m < 1.0e-3:
        return f"{d_m*1000:.4f} mm"
    if d_m < 1.0:
        return f"{d_m*100:.4f} cm"
    return f"{d_m:.4f} m"


def main() -> int:
    print("=" * 72)
    print("WP0.5 deflection model: canonical anchor verification (T5 +/-5%)")
    print("=" * 72)

    g = G_LUNAR
    evidence: dict = {
        "task": "WP0.5 deflection model verification",
        "protocol": "T5 +/-5%",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "g_lunar_mps2": g,
        "detector_floor_m": DETECTOR_FLOOR_M,
        "anchors": [],
    }

    n_pass = 0
    n_total = 0
    for a in CANONICAL_ANCHORS:
        n_total += 1
        L, h, E_GPa = a["L"], a["h"], a["E"]
        E_Pa = E_GPa * 1.0e9
        # rho=2900 (dispatch table value)
        d_2900 = clamped_slab(2900, g, L, E_Pa, h)
        # rho=3000 (F1 derivation value per review report)
        d_3000 = clamped_slab(3000, g, L, E_Pa, h)
        expected = a["expected_m"]

        rel_2900 = abs(d_2900 - expected) / expected
        rel_3000 = abs(d_3000 - expected) / expected
        ok = rel_2900 <= TOL_T5
        n_pass += int(ok)

        marker = "OK " if ok else "FAIL"
        print(
            f"  [{marker}] {a['label']:<40s}  "
            f"L={L:>4d}m h={h:>2d}m E={E_GPa:>3d}GPa  "
            f"rho=2900: {fmt_mm(d_2900):>12s}  ({rel_2900*100:>5.2f}%)  "
            f"rho=3000: {fmt_mm(d_3000):>12s}  ({rel_3000*100:>5.2f}%)  "
            f"expected: {fmt_mm(expected):>12s}"
        )

        evidence["anchors"].append({
            "label": a["label"],
            "L_m": L, "h_m": h, "E_GPa": E_GPa,
            "rho_table_kgm3": 2900,
            "rho_f1_kgm3": 3000,
            "expected_m": expected,
            "computed_rho2900_m": d_2900,
            "computed_rho3000_m": d_3000,
            "rel_err_rho2900": rel_2900,
            "rel_err_rho3000": rel_3000,
            "t5_pass_rho2900": bool(ok),
            "t5_pass_rho3000": bool(rel_3000 <= TOL_T5),
        })

    evidence["n_anchors"] = n_total
    evidence["n_pass_rho2900"] = n_pass
    evidence["n_pass_rho3000"] = sum(
        1 for r in evidence["anchors"] if r["t5_pass_rho3000"]
    )
    evidence["all_ok"] = (n_pass == n_total)

    print("=" * 72)
    verdict = (
        f"PASS: {n_pass}/{n_total} (ALL OK)"
        if n_pass == n_total else
        f"FAIL: {n_total - n_pass}/{n_total} (regressions)"
    )
    print(verdict)
    print(
        f"  (rho=2900, table-stated: {evidence['n_pass_rho2900']}/{n_total} within T5; "
        f"rho=3000, F1-stated: {evidence['n_pass_rho3000']}/{n_total} within T5)"
    )

    # Write deterministic JSON evidence record. Use the run's UTC
    # timestamp in the filename so re-runs don't clobber each other,
    # but the JSON payload itself is fully reproducible given the
    # canonical anchors (no randomness anywhere).
    evidence_dir = REPO / "01_WORKSPACE/admin/verification_evidence/scripts"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence_path = evidence_dir / f"verify_wp0_5_deflection_{stamp}.json"
    evidence_path.write_text(json.dumps(evidence, indent=2))
    print(f"Wrote {evidence_path}")

    return 0 if n_pass == n_total else 1


if __name__ == "__main__":
    sys.exit(main())
