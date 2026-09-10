#!/usr/bin/env python
"""A2a — unique-feature FP re-accounting over the repaired (B1) registry.

Row-based headline (frozen, Paper 1) to regress against before any unique
computation:
    FP 9 -> 3.74018820451733 [1.7102522128891549, 7.100042260610549]
    per 10^4 km^2 over 24,062.96 km^2 (21 DTMs)
Row decomposition of the 45 above-floor rows: 9 FP + 14 TP + 21 ring + 1 funnel.

Classification rules (identical evidence to Paper 1; see transfer_apply.py):
  * above-floor  : registry row whose notes do NOT carry below-local-floor
  * ring         : notes carry "ring artifact" (excluded from TP matching,
                   exactly as the skeptic annotation did)
  * TP row       : per (DTM, rung) pair, each catalogued pit
                   (outputs/wp0_scope_map/relevant_pits_x_dtms.csv) is matched
                   by its NEAREST above-floor non-ring row within 100 m;
                   that row is the TP (re-detection). One TP row per matched
                   pit per pair — this reproduces transfer_summary pair n_tp.
  * FP row       : above-floor, non-ring, > 100 m from every catalogued pit
                   of its DTM (reproduces transfer_summary pair n_fp).
  * funnel row   : above-floor, non-ring, within 100 m of a pit but not the
                   nearest (unassigned), carrying the I14 funnel annotation
                   (MARIUSPIT01). Any other unassigned near-pit row is a
                   reconciliation FAILURE (none exist in this registry).

Uniqueness (B1 key): group = ACTIVE primary + rows whose notes carry
`superseded_by=<primary_id>`. A group's class = class of its PRIMARY.
Sensitivity: rounded lon/lat keys (2/3/4 dp) and haversine single-linkage
clustering within DTM at 30/60/100 m on R=1737400; group class = class of
the group representative (finest rung, then highest score, then lowest id).

CI: Poisson-exact Garwood 95% — lower = 0.5*chi2.ppf(0.025, 2n),
upper = 0.5*chi2.ppf(0.975, 2n+2); n=0 -> [0, 0.5*chi2.ppf(0.95, 2)].
NEVER Wilson. Deterministic; no network; seeds fixed (no RNG used).

Output: 01_WORKSPACE/data/outputs/wp2_sag/unique_accounting_2026-09-07.json
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

from scipy.stats import chi2

REPO = Path(__file__).resolve().parents[4]
REGISTRY = REPO / "01_WORKSPACE/data/candidate_registry.csv"
PIT_CATALOG = REPO / "01_WORKSPACE/data/outputs/wp0_scope_map/relevant_pits_x_dtms.csv"
SUMMARY = REPO / "01_WORKSPACE/data/outputs/wp2_sag/transfer/transfer_summary.json"
OUT = REPO / "01_WORKSPACE/data/outputs/wp2_sag/unique_accounting_2026-09-07.json"

MOON_R = 1737400.0
PIT_MATCH_RADIUS_M = 100.0  # Z2 / Paper-1 convention
SEED = 42  # declared for convention; no stochastic step exists in this script

# Frozen regression targets (Paper 1 row-based headline)
EXPECT = {
    "n_fp": 9,
    "n_tp": 14,
    "n_ring": 21,
    "n_funnel": 1,
    "n_above": 45,
    "rate": 3.74018820451733,
    "ci_lo": 1.7102522128891549,
    "ci_hi": 7.100042260610549,
    "area_km2": 24062.96022518323,
}


def haversine_m(lon1, lat1, lon2, lat2):
    la1, la2 = math.radians(lat1), math.radians(lat2)
    dlat = la2 - la1
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dlon / 2) ** 2
    return MOON_R * 2 * math.asin(math.sqrt(a))


def garwood(n, area_km2):
    """Poisson-exact (Garwood) 95% CI on n events over area, per 10^4 km^2."""
    if area_km2 <= 0:
        return float("nan"), float("nan"), float("nan")
    if n == 0:
        return 0.0, 0.0, (0.5 * chi2.ppf(0.95, 2)) / area_km2 * 1e4
    lo = (0.5 * chi2.ppf(0.025, 2 * n)) / area_km2 * 1e4
    hi = (0.5 * chi2.ppf(0.975, 2 * n + 2)) / area_km2 * 1e4
    return n / area_km2 * 1e4, lo, hi


def md5(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def load_registry():
    """csv-module-only load; skip comment lines by FIRST FIELD starting '#'.

    Handles the quoted '# notes ...' schema line (its parsed first field
    starts with '#') exactly like every other comment line.
    """
    rows = []
    with open(REGISTRY, newline="") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            fields = next(csv.reader([line]))
            if fields[0].lstrip().startswith("#"):
                continue
            rows.append(fields)
    header, data = rows[0], rows[1:]
    idx = {h: i for i, h in enumerate(header)}
    recs = []
    for r in data:
        m = re.search(r"-(\d+)cm-r(\d+)$", r[idx["candidate_id"]])
        sup = re.search(r"superseded_by=(\S+)", r[idx["notes"]])
        recs.append({
            "id": r[idx["candidate_id"]],
            "lon": float(r[idx["lon"]]),
            "lat": float(r[idx["lat"]]),
            "dtm": r[idx["dtm"]],
            "rung_cm": int(m.group(1)),
            "rank": int(m.group(2)),
            "score": float(r[idx["score"]]),
            "status": r[idx["status"]],
            "above": "below-local-floor" not in r[idx["notes"]],
            "ring": "ring artifact" in r[idx["notes"]],
            "funnel_annot": "I14 funnel risk" in r[idx["notes"]],
            "superseded_by": sup.group(1) if sup else None,
        })
    return recs


def load_pits():
    pits = defaultdict(list)
    with open(PIT_CATALOG, newline="") as f:
        for row in csv.DictReader(l for l in f if not l.lstrip().startswith("#")):
            pits[row["DTM_NAME"]].append(
                {"name": row["Name"], "lat": float(row["Latitude"]),
                 "lon": float(row["Longitude"])})
    return pits


def classify(recs, pits):
    """Assign row classes FP / TP / RING / FUNNEL; return per-pair counters."""
    pairs = defaultdict(lambda: {"n_fp": 0, "n_tp": 0})
    for rec in recs:
        if not rec["above"]:
            rec["cls"] = "BELOW"
        elif rec["ring"]:
            rec["cls"] = "RING"
    eligible = [r for r in recs if r["above"] and not r["ring"]]
    by_pair = defaultdict(list)
    for r in eligible:
        by_pair[(r["dtm"], r["rung_cm"])].append(r)

    anomalies = []
    for (dtm, rung), rows in sorted(by_pair.items()):
        pair = pairs[(dtm, rung)]
        dtm_pits = pits.get(dtm, [])
        # distance of each row to each pit
        d = {(r["id"], i): haversine_m(r["lon"], r["lat"], p["lon"], p["lat"])
             for r in rows for i, p in enumerate(dtm_pits)}
        # FP: > radius from every pit (row count, as in transfer_apply)
        for r in rows:
            if all(d[(r["id"], i)] > PIT_MATCH_RADIUS_M for i in range(len(dtm_pits))):
                r["cls"] = "FP"
                pair["n_fp"] += 1
        # TP: per pit (catalog order), nearest unassigned within-radius row
        assigned = set()
        for i, p in enumerate(dtm_pits):
            cands = sorted(
                ((d[(r["id"], i)], -r["score"], r["id"], r) for r in rows
                 if d[(r["id"], i)] <= PIT_MATCH_RADIUS_M and r["id"] not in assigned),
                key=lambda t: t[:3])
            if cands:
                _, _, _, row = cands[0]
                row["cls"] = "TP"
                assigned.add(row["id"])
                pair["n_tp"] += 1
        # leftovers: within radius of some pit but unassigned
        for r in rows:
            if r["id"] in assigned or r.get("cls") == "FP":
                continue
            if any(d[(r["id"], i)] <= PIT_MATCH_RADIUS_M for i in range(len(dtm_pits))):
                if r["funnel_annot"]:
                    r["cls"] = "FUNNEL"
                else:
                    r["cls"] = "UNASSIGNED-NEAR-PIT"
                    anomalies.append(r["id"])
            else:
                r["cls"] = "UNCLASSIFIED"
                anomalies.append(r["id"])
    return pairs, anomalies


def reconcile(recs, pairs, summary):
    """Hard stop if computed row accounting != transfer_summary + frozen headline."""
    fails = []
    # pair-level FP/TP vs summary pair_results
    for pr in summary.get("pair_results", []):
        key = (pr.get("dtm"), int(pr["rung_m"]) * 100 if pr.get("rung_m") else None)
        if key[1] is None:
            continue
        got = pairs.get(key)
        if got and (got["n_fp"] != pr.get("n_fp", 0) or got["n_tp"] != pr.get("n_tp", 0)):
            fails.append(f"pair {key}: computed fp/tp {got['n_fp']}/{got['n_tp']} "
                         f"!= summary {pr.get('n_fp', 0)}/{pr.get('n_tp', 0)}")
    agg = summary["aggregate"]
    n_fp = sum(r["cls"] == "FP" for r in recs)
    n_tp = sum(r["cls"] == "TP" for r in recs)
    n_ring = sum(r["cls"] == "RING" for r in recs)
    n_funnel = sum(r["cls"] == "FUNNEL" for r in recs)
    n_above = sum(r["above"] for r in recs)
    for name, got, want in [("n_fp", n_fp, agg["n_fp"]), ("n_tp", n_tp, agg["n_tp"]),
                            ("n_above", n_above, agg["n_above_local_floor"])]:
        if got != want:
            fails.append(f"aggregate {name}: computed {got} != summary {want}")
    for name, got in [("n_fp", n_fp), ("n_tp", n_tp), ("n_ring", n_ring),
                      ("n_funnel", n_funnel), ("n_above", n_above)]:
        if got != EXPECT[name]:
            fails.append(f"frozen {name}: computed {got} != {EXPECT[name]}")
    rate, lo, hi = garwood(n_fp, agg["total_area_km2"])
    for name, got, want in [("rate", rate, EXPECT["rate"]), ("ci_lo", lo, EXPECT["ci_lo"]),
                            ("ci_hi", hi, EXPECT["ci_hi"])]:
        if not math.isclose(got, want, rel_tol=1e-9):
            fails.append(f"frozen {name}: computed {got!r} != {want!r}")
    return fails, {"n_fp": n_fp, "n_tp": n_tp, "n_ring": n_ring,
                   "n_funnel": n_funnel, "n_above": n_above,
                   "rate": rate, "ci_lo": lo, "ci_hi": hi}


def link_groups(recs):
    """B1 groups: ACTIVE primary + direct superseded children. Integrity-checked."""
    fails = []
    by_id = {r["id"]: r for r in recs}
    children = defaultdict(list)
    for r in recs:
        if r["superseded_by"]:
            tgt = by_id.get(r["superseded_by"])
            if tgt is None:
                fails.append(f"dangling superseded_by: {r['id']} -> {r['superseded_by']}")
                continue
            if tgt["status"] != "ACTIVE":
                fails.append(f"superseded_by target not ACTIVE: {r['id']} -> {tgt['id']}")
            if r["status"] != "SUPERSEDED":
                fails.append(f"non-SUPERSEDED row carries superseded_by: {r['id']}")
            children[tgt["id"]].append(r["id"])
    for r in recs:
        if r["status"] == "SUPERSEDED" and not r["superseded_by"]:
            fails.append(f"SUPERSEDED without superseded_by: {r['id']}")
    groups = []
    for p in recs:
        if p["status"] != "ACTIVE":
            continue
        members = [p] + [by_id[c] for c in sorted(children[p["id"]])]
        groups.append({"primary": p, "members": members, "cls": p["cls"]})
    return groups, fails


def key_groups(above, keyfn):
    """Group above-floor rows by (dtm, key(lon,lat)); class = representative's.

    Representative = finest rung, then highest score, then lowest id
    (the same preference the B1 repair used to pick primaries).
    """
    buckets = defaultdict(list)
    for r in above:
        buckets[(r["dtm"],) + keyfn(r)].append(r)
    groups = []
    for k, rows in sorted(buckets.items(), key=lambda kv: str(kv[0])):
        rep = min(rows, key=lambda r: (r["rung_cm"], -r["score"], r["id"]))
        groups.append({"key": list(k[1:]), "representative": rep["id"],
                       "cls": rep["cls"], "members": [r["id"] for r in sorted(
                           rows, key=lambda r: r["id"])]})
    return groups


def cluster_groups(above, radius_m):
    """Single-linkage union-find within DTM at haversine radius."""
    parent = {r["id"]: r["id"] for r in above}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    by_dtm = defaultdict(list)
    for r in above:
        by_dtm[r["dtm"]].append(r)
    for dtm, rows in by_dtm.items():
        for i, a in enumerate(rows):
            for b in rows[i + 1:]:
                if haversine_m(a["lon"], a["lat"], b["lon"], b["lat"]) <= radius_m:
                    parent[find(a["id"])] = find(b["id"])
    clusters = defaultdict(list)
    for r in above:
        clusters[find(r["id"])].append(r)
    by_id = {r["id"]: r for r in above}
    groups = []
    for root, rows in sorted(clusters.items()):
        rep = min(rows, key=lambda r: (r["rung_cm"], -r["score"], r["id"]))
        groups.append({"radius_m": radius_m, "representative": rep["id"],
                       "cls": rep["cls"], "members": [r["id"] for r in
                                                      sorted(rows, key=lambda r: r["id"])]})
    return groups


def uniq_counts(groups):
    c = defaultdict(int)
    for g in groups:
        c[g["cls"]] += 1
    return {"total": len(groups), "fp": c["FP"], "tp": c["TP"],
            "ring": c["RING"], "funnel": c["FUNNEL"]}


def main():
    recs = load_registry()
    pits = load_pits()
    summary = json.load(open(SUMMARY))
    area = summary["aggregate"]["total_area_km2"]

    pairs, anomalies = classify(recs, pits)
    fails, rowbased = reconcile(recs, pairs, summary)
    if anomalies:
        fails.append(f"classification anomalies: {anomalies}")

    groups, gfails = link_groups(recs)
    fails += gfails
    above = [r for r in recs if r["above"]]
    by_id = {r["id"]: r for r in recs}
    above_groups = [g for g in groups if g["primary"]["above"]]
    # every above-floor ACTIVE must be the finest-rung member of its group
    for g in above_groups:
        rep = min(g["members"], key=lambda r: (r["rung_cm"], -r["score"], r["id"]))
        if rep["id"] != g["primary"]["id"]:
            fails.append(f"group {g['primary']['id']}: primary is not finest-rung rep ({rep['id']})")

    if fails:
        print("RECONCILIATION FAILURE — refusing to compute uniques:", file=sys.stderr)
        for f in fails:
            print("  FAIL:", f, file=sys.stderr)
        sys.exit(2)

    # ---- unique-feature accounting (B1 link key) ----
    u = uniq_counts(above_groups)
    u_rate, u_lo, u_hi = garwood(u["fp"], area)
    unique_block = {
        "grouping_key": "B1 link key (primary + superseded_by children; class = primary's class)",
        "n_unique_above_floor": u["total"],
        "n_unique_fp": u["fp"], "n_unique_tp": u["tp"],
        "n_unique_ring": u["ring"], "n_unique_funnel": u["funnel"],
        "fp_per_1e4km2": u_rate, "ci95_lo": u_lo, "ci95_hi": u_hi,
        "ci_method": "Poisson-exact (Garwood) 95% CI",
        "area_km2": area,
    }

    # ---- key sensitivity ----
    sens = []
    for dp, scale in [(2, 300.0), (3, 30.0), (4, 3.0)]:
        g = key_groups(above, lambda r, dp=dp: (round(r["lon"], dp), round(r["lat"], dp)))
        c = uniq_counts(g)
        r_, lo, hi = garwood(c["fp"], area)
        sens.append({"key": f"round lon/lat to {dp} dp (~{scale:.0f} m grid)",
                     "n_groups": c["total"], "n_fp": c["fp"], "n_tp": c["tp"],
                     "n_ring": c["ring"], "n_funnel": c["funnel"],
                     "fp_per_1e4km2": r_, "ci95_lo": lo, "ci95_hi": hi})
    for rad in (30.0, 60.0, 100.0):
        g = cluster_groups(above, rad)
        c = uniq_counts(g)
        r_, lo, hi = garwood(c["fp"], area)
        sens.append({"key": f"haversine single-linkage {rad:.0f} m (within DTM, R=1737400)",
                     "n_groups": c["total"], "n_fp": c["fp"], "n_tp": c["tp"],
                     "n_ring": c["ring"], "n_funnel": c["funnel"],
                     "fp_per_1e4km2": r_, "ci95_lo": lo, "ci95_hi": hi})

    # ---- boundary straddlers ----
    straddlers = []
    seen = set()
    by_dtm = defaultdict(list)
    for r in above:
        by_dtm[r["dtm"]].append(r)
    group_of = {}
    for g in above_groups:
        for m in g["members"]:
            group_of[m["id"]] = g["primary"]["id"]
    k3 = {}
    for g in key_groups(above, lambda r: (round(r["lon"], 3), round(r["lat"], 3))):
        for m in g["members"]:
            k3[m] = tuple(g["key"])
    k4 = {}
    for g in key_groups(above, lambda r: (round(r["lon"], 4), round(r["lat"], 4))):
        for m in g["members"]:
            k4[m] = tuple(g["key"])
    k2 = {}
    for g in key_groups(above, lambda r: (round(r["lon"], 2), round(r["lat"], 2))):
        for m in g["members"]:
            k2[m] = tuple(g["key"])
    for dtm, rows in sorted(by_dtm.items()):
        for i, a in enumerate(rows):
            for b in rows[i + 1:]:
                d = haversine_m(a["lon"], a["lat"], b["lon"], b["lat"])
                flags = []
                if group_of.get(a["id"]) and group_of.get(b["id"]):
                    if group_of[a["id"]] == group_of[b["id"]] and d > 30.0:
                        flags.append(f"B1-linked but {d:.1f} m apart (>30 m B1 scale)")
                    if group_of[a["id"]] != group_of[b["id"]] and d <= 30.0:
                        flags.append(f"B1-distinct but {d:.1f} m apart (<=30 m B1 scale)")
                if k3[a["id"]] == k3[b["id"]] and k4[a["id"]] != k4[b["id"]]:
                    flags.append("same 3-dp cell, split at 4 dp")
                if k2[a["id"]] == k2[b["id"]] and k3[a["id"]] != k3[b["id"]]:
                    flags.append("same 2-dp cell, split at 3 dp")
                if flags:
                    pk = tuple(sorted((a["id"], b["id"])))
                    if pk in seen:
                        continue
                    seen.add(pk)
                    straddlers.append({
                        "row_a": a["id"], "row_b": b["id"], "dtm": dtm,
                        "sep_m": round(d, 2),
                        "classes": f"{a['cls']}/{b['cls']}",
                        "same_b1_group": group_of.get(a["id"]) == group_of.get(b["id"]),
                        "flags": flags})

    # ---- FP group detail (B1 key) ----
    fp_groups = []
    for g in above_groups:
        if g["cls"] != "FP":
            continue
        p = g["primary"]
        fp_groups.append({
            "primary": p["id"], "dtm": p["dtm"], "class": "FP",
            "n_members": len(g["members"]),
            "members": [{
                "id": m["id"], "rung_cm": m["rung_cm"], "status": m["status"],
                "lon": m["lon"], "lat": m["lat"], "score": m["score"],
                "dist_to_primary_m": round(
                    haversine_m(m["lon"], m["lat"], p["lon"], p["lat"]), 2),
            } for m in sorted(g["members"], key=lambda r: r["id"])]})

    out = {
        "task": "A2a unique-feature FP re-accounting",
        "deterministic": True, "seed_declared": SEED, "network": "none",
        "inputs": {
            "registry": str(REGISTRY.relative_to(REPO)), "registry_md5": md5(REGISTRY),
            "registry_rows": len(recs),
            "registry_status_counts": {
                s: sum(r["status"] == s for r in recs) for s in ("ACTIVE", "SUPERSEDED")},
            "pit_catalog": str(PIT_CATALOG.relative_to(REPO)),
            "pit_catalog_md5": md5(PIT_CATALOG),
            "transfer_summary": str(SUMMARY.relative_to(REPO)),
            "transfer_summary_md5": md5(SUMMARY),
        },
        "classification_rules": {
            "above_floor": "notes lack below-local-floor",
            "ring": 'notes contain "ring artifact" (excluded from TP matching)',
            "tp": "per (DTM, rung): nearest above-floor non-ring row within "
                  f"{PIT_MATCH_RADIUS_M:.0f} m of a catalogued pit (one TP row per pit per pair)",
            "fp": f"above-floor, non-ring, >{PIT_MATCH_RADIUS_M:.0f} m from every pit of its DTM",
            "funnel": "above-floor, non-ring, within radius but unassigned, I14-annotated",
            "ci": "Poisson-exact Garwood 95%; NEVER Wilson",
        },
        "row_based": {
            "n_above": rowbased["n_above"], "n_fp": rowbased["n_fp"],
            "n_tp": rowbased["n_tp"], "n_ring": rowbased["n_ring"],
            "n_funnel": rowbased["n_funnel"],
            "fp_per_1e4km2": rowbased["rate"],
            "ci95_lo": rowbased["ci_lo"], "ci95_hi": rowbased["ci_hi"],
            "area_km2": area,
            "regression_vs_paper1": {
                "n_fp_9": "PASS", "n_tp_14": "PASS", "n_ring_21": "PASS",
                "n_funnel_1": "PASS", "rate_3.74018820451733": "PASS",
                "ci_1.7102522128891549_7.100042260610549": "PASS"},
        },
        "unique_b1_key": unique_block,
        "sensitivity": sens,
        "boundary_straddlers": straddlers,
        "fp_group_detail": fp_groups,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, sort_keys=False)
        f.write("\n")

    print(f"[ok] {len(recs)} rows | above {rowbased['n_above']} "
          f"(FP {rowbased['n_fp']} TP {rowbased['n_tp']} "
          f"ring {rowbased['n_ring']} funnel {rowbased['n_funnel']})")
    print(f"[ok] row-based FP {rowbased['rate']:.4f} "
          f"[{rowbased['ci_lo']:.4f}, {rowbased['ci_hi']:.4f}] per 1e4 km^2 (regressed)")
    print(f"[ok] unique (B1): {u['total']} groups -> FP {u['fp']}, TP {u['tp']}, "
          f"ring {u['ring']}, funnel {u['funnel']}; "
          f"FP {u_rate:.4f} [{u_lo:.4f}, {u_hi:.4f}] per 1e4 km^2")
    for s in sens:
        print(f"[sens] {s['key']:48s} n_groups={s['n_groups']:3d} "
              f"FP={s['n_fp']} TP={s['n_tp']} ring={s['n_ring']} funnel={s['n_funnel']}")
    print(f"[ok] {len(straddlers)} boundary-straddler pair(s); "
          f"{len(fp_groups)} FP group detail blocks")
    print(f"[out] {OUT}")


if __name__ == "__main__":
    main()
