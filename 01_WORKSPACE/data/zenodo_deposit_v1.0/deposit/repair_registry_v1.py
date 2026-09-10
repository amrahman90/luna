#!/usr/bin/env python3
"""repair_registry_v1.py — LUNARVOID Next-Level Plan v2, Phase B1.

Repair of 01_WORKSPACE/data/candidate_registry.csv:

  1. Robust parse: any line whose first field starts with '#' is a comment
     (kept verbatim, never a data row — Hermes LOW-11). Rows with >15
     fields (unquoted commas in the free-text notes column) are repaired
     by joining the overflow tail back into the notes field. Notes text
     is NEVER reworded — only quoting is fixed.
  2. Emits a properly quoted CSV (csv.writer, QUOTE_MINIMAL), exactly the
     frozen 15-column schema, every row exactly 15 fields. Rows are never
     deleted; row order is preserved.
  3. methods="C" schema violations fixed to the schema-conformant value
     used by same-DTM sibling rows (most common if siblings vary).
  4. Cross-rung dedupe: group by (dtm, lon, lat) rounded to 3 decimals
     (~30 m at the lunar equator = atlas positional accuracy; v5 I15
     match radius >= 30 m). PRIMARY = finest rung (smallest rung value
     parsed from candidate_id '-<N>cm-r###'; tie-break: earliest
     candidate_id, then file order). Others: status ACTIVE -> SUPERSEDED
     and notes gain '; superseded_by=<primary_id>' (semicolon-append
     matches existing note style). Tier values unchanged.
  5. Repair report JSON with md5s, counts, per-DTM breakdown, quarantine
     flags (rows that could not be auto-repaired confidently).

Deterministic and idempotent: re-running on the repaired file produces a
byte-identical registry (superseded rows stay superseded; the
superseded_by marker is never appended twice). stdlib only (csv/json/
hashlib/re/argparse/collections). No seed needed (no randomness).

Usage:
  python repair_registry_v1.py \
      [--registry 01_WORKSPACE/data/candidate_registry.csv] \
      [--backup   01_WORKSPACE/data/candidate_registry_backup_2026-09-06.csv] \
      [--report   01_WORKSPACE/data/outputs/wp2_sag/registry_repair_2026-09-06.json]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import tempfile
from collections import Counter, OrderedDict

SCHEMA = [
    "candidate_id", "lon", "lat", "dtm", "span_m", "sag_amp_m", "score",
    "confusion", "methods", "tier", "status", "first_found", "updated",
    "evidence", "notes",
]
NCOLS = len(SCHEMA)  # 15 — frozen
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RUNG_RE = re.compile(r"-(\d+)cm-r\d+$")
COORD_DP = 3  # rounding for dedupe key (~30 m at lunar equator)
SUPERSEDED_MARKER = "superseded_by="
VALID_TIERS = {"A", "B", "C"}
VALID_STATUS = {"ACTIVE", "DOWNGRADED", "SUPERSEDED"}


def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_row(fields: list[str]) -> list[str]:
    """Return list of validation problems for a 15-field row (empty = ok)."""
    problems = []
    try:
        lon, lat = float(fields[1]), float(fields[2])
        if not (-180.0 <= lon <= 180.0):
            problems.append(f"lon out of range: {lon}")
        if not (-90.0 <= lat <= 90.0):
            problems.append(f"lat out of range: {lat}")
    except ValueError as exc:
        problems.append(f"lon/lat not floats: {exc}")
    for idx, name in ((4, "span_m"), (5, "sag_amp_m"), (6, "score")):
        try:
            float(fields[idx])
        except ValueError:
            problems.append(f"{name} not a float: {fields[idx]!r}")
    if not fields[0].startswith("LV-"):
        problems.append(f"candidate_id not LV-*: {fields[0]!r}")
    if fields[9] not in VALID_TIERS:
        problems.append(f"bad tier: {fields[9]!r}")
    if fields[10] not in VALID_STATUS:
        problems.append(f"bad status: {fields[10]!r}")
    for idx, name in ((11, "first_found"), (12, "updated")):
        if not DATE_RE.match(fields[idx]):
            problems.append(f"{name} not YYYY-MM-DD: {fields[idx]!r}")
    return problems


def parse_run_g(candidate_id: str):
    m = RUNG_RE.search(candidate_id)
    return int(m.group(1)) if m else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--registry", default="01_WORKSPACE/data/candidate_registry.csv")
    ap.add_argument("--backup", default="01_WORKSPACE/data/candidate_registry_backup_2026-09-06.csv")
    ap.add_argument("--report", default="01_WORKSPACE/data/outputs/wp2_sag/registry_repair_2026-09-06.json")
    args = ap.parse_args(argv)

    # ---------------- parse ----------------
    items = []  # ('comment', raw_line) | ('data', fields)
    with open(args.registry, newline="", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\r\n")
            # Comment if the FIRST FIELD (csv-parsed, or the raw leading
            # token) starts with '#'. Both checks needed: one header-block
            # comment line is itself csv-quoted (starts with '"# ...').
            first_raw = line.split(",", 1)[0].strip()
            first_parsed = next(csv.reader([line]))[0].strip()
            if first_raw.startswith("#") or first_parsed.startswith("#"):
                items.append(("comment", line))
                continue
            fields = next(csv.reader([line]))
            items.append(("data", fields))

    header_idx = next(i for i, (k, _) in enumerate(items) if k == "data")
    if items[header_idx][1] != SCHEMA:
        print(f"FATAL: unexpected header: {items[header_idx][1]}", file=sys.stderr)
        return 2

    rows = [v for k, v in items if k == "data"][1:]  # drop header
    rows_in = len(rows)
    quarantined = []
    malformed_fixed = []

    # ---------------- a) tolerate >15-field rows (comma overflow in notes) --
    for i, fields in enumerate(rows):
        if len(fields) == NCOLS:
            continue
        if len(fields) > NCOLS:
            # The defect is commas in the free-text notes column: the extra
            # trailing fields are note fragments. Rejoin with the commas the
            # original writer failed to quote. Notes text is unchanged.
            joined = fields[:NCOLS - 1] + [",".join(fields[NCOLS - 1:])]
            problems = validate_row(joined)
            rows[i] = joined
            malformed_fixed.append(joined[0])
            if problems:
                quarantined.append({
                    "candidate_id": joined[0],
                    "reason": "16-field row rejoined but prefix fields failed "
                              "validation: " + "; ".join(problems),
                })
        else:
            quarantined.append({
                "candidate_id": fields[0] if fields else f"<row {i}>",
                "reason": f"row has {len(fields)} fields (< 15); cannot "
                          "auto-repair; emitted as-is, NOT mutated further",
            })

    # Validate every 15-field row; quarantine failures (no further mutation).
    for i, fields in enumerate(rows):
        if len(fields) != NCOLS:
            continue  # already quarantined above
        problems = validate_row(fields)
        if problems:
            quarantined.append({
                "candidate_id": fields[0],
                "reason": "validation failed: " + "; ".join(problems),
            })
    quarantined_ids = {q["candidate_id"] for q in quarantined}

    # ---------------- c) methods="C" schema violation ----------------------
    # Target value = most common methods among same-DTM siblings that are
    # schema-conformant (not 'C'); fallback = most common overall.
    ok_methods_by_dtm = Counter(
        (f[3], f[8]) for f in rows
        if len(f) == NCOLS and f[8] != "C" and f[0] not in quarantined_ids
    )
    overall = Counter(
        f[8] for f in rows
        if len(f) == NCOLS and f[8] != "C" and f[0] not in quarantined_ids
    )
    methods_fixed = {}
    methods_mapping_used = {}
    for f in rows:
        if len(f) != NCOLS or f[0] in quarantined_ids or f[8] != "C":
            continue
        dtm = f[3]
        dtm_counts = Counter({m: n for (d, m), n in ok_methods_by_dtm.items()
                              if d == dtm})
        target = dtm_counts.most_common(1)[0][0] if dtm_counts else \
            overall.most_common(1)[0][0]
        old = f[8]
        f[8] = target
        methods_fixed[f[0]] = {"from": old, "to": target}
        methods_mapping_used.setdefault(f"{old}->{target} (dtm={dtm})", 0)
        methods_mapping_used[f"{old}->{target} (dtm={dtm})"] += 1

    # ---------------- d) cross-rung dedupe ---------------------------------
    groups = OrderedDict()  # key -> list of (row_index, fields)
    rung_warn = []
    for i, f in enumerate(rows):
        if len(f) != NCOLS or f[0] in quarantined_ids:
            continue
        rung = parse_run_g(f[0])
        if rung is None:
            rung_warn.append(f[0])
        key = (f[3], round(float(f[1]), COORD_DP), round(float(f[2]), COORD_DP))
        groups.setdefault(key, []).append((i, f, rung))

    rows_superseded = []       # final state: every SUPERSEDED row id
    newly_superseded = []      # status flipped ACTIVE->SUPERSEDED this run
    dup_groups = 0             # groups with >1 member
    primary_ids = []
    for key, members in groups.items():
        # PRIMARY = finest rung (smallest value); unknown rung sorts last;
        # tie-break: earliest candidate_id, then file order.
        members_sorted = sorted(
            members,
            key=lambda t: (t[2] is None, t[2] if t[2] is not None else 0,
                           t[1][0], t[0]),
        )
        primary = members_sorted[0]
        primary_ids.append(primary[1][0])
        if len(members) > 1:
            dup_groups += 1
        for i, f, _rung in members_sorted[1:]:
            if f[10] == "ACTIVE":
                f[10] = "SUPERSEDED"
                newly_superseded.append(f[0])
            if SUPERSEDED_MARKER not in f[14]:
                f[14] = f[14] + f"; superseded_by={primary[1][0]}"

    for f in rows:
        if len(f) == NCOLS and f[10] == "SUPERSEDED" and f[0] not in rows_superseded:
            rows_superseded.append(f[0])

    # ---------------- b) emit properly quoted CSV --------------------------
    out_lines = []
    di = 0  # index into data rows (header consumed separately)
    data_rows = [f for f in rows]
    emitted_data = 0
    for kind, val in items:
        if kind == "comment":
            out_lines.append(val)
        else:
            if emitted_data == 0:
                row_to_write = SCHEMA  # header first
            else:
                row_to_write = data_rows[di]
                di += 1
            out_lines.append(None)  # placeholder; csv.writer fills below
            sio = io.StringIO()
            w = csv.writer(sio, quoting=csv.QUOTE_MINIMAL, lineterminator="")
            w.writerow(row_to_write)
            out_lines[-1] = sio.getvalue()
            emitted_data += 1

    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=os.path.dirname(os.path.abspath(args.registry)), suffix=".tmp")
    with os.fdopen(tmp_fd, "w", newline="", encoding="utf-8") as fh:
        fh.write("\n".join(out_lines) + "\n")
    os.replace(tmp_path, args.registry)

    # ---------------- e) repair report -------------------------------------
    tier_counts = Counter(f[9] for f in data_rows if len(f) == NCOLS)
    per_dtm = OrderedDict()
    for f in data_rows:
        if len(f) != NCOLS:
            continue
        d = per_dtm.setdefault(f[3], {"rows": 0, "primaries": 0,
                                      "superseded": 0})
        d["rows"] += 1
        if f[10] == "SUPERSEDED":
            d["superseded"] += 1
        else:
            d["primaries"] += 1
    above_floor = {"total": 0, "primary": 0, "superseded": 0}
    for f in data_rows:
        if len(f) == NCOLS and "below-local-floor" not in f[14]:
            above_floor["total"] += 1
            above_floor["superseded" if f[10] == "SUPERSEDED" else "primary"] += 1

    report = {
        "tool": "repair_registry_v1.py",
        "phase": "Next-Level Plan v2, Phase B1",
        "registry": os.path.abspath(args.registry),
        "backup": os.path.abspath(args.backup),
        "rows_in": rows_in,
        "rows_out": len(data_rows),
        "schema": SCHEMA,
        "malformed_rows_fixed": malformed_fixed,
        "malformed_rows_fixed_count": len(malformed_fixed),
        "methods_fixed": methods_fixed,
        "methods_fixed_count": len(methods_fixed),
        "methods_mapping_used": methods_mapping_used,
        "dup_groups": dup_groups,
        "rows_superseded": rows_superseded,
        "rows_superseded_count": len(rows_superseded),
        "newly_superseded_this_run": newly_superseded,
        "primary_rows": len(primary_ids),
        "unique_feature_count": len(primary_ids),
        "dedupe_key": f"(dtm, lon, lat) rounded to {COORD_DP} dp "
                      "(~30 m at lunar equator; v5 I15 match radius >= 30 m)",
        "tier_counts": dict(sorted(tier_counts.items())),
        "per_dtm": per_dtm,
        "above_floor_rows": above_floor,
        "quarantined": quarantined,
        "rung_parse_failures": rung_warn,
        "md5_backup": md5_of(args.backup) if os.path.exists(args.backup) else None,
        "md5_repaired": md5_of(args.registry),
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, sort_keys=False)
        fh.write("\n")

    print(json.dumps({k: report[k] for k in (
        "rows_in", "rows_out", "malformed_rows_fixed_count",
        "methods_fixed_count", "dup_groups", "rows_superseded_count",
        "primary_rows", "unique_feature_count", "tier_counts",
        "above_floor_rows")}, indent=2))
    print(f"md5_backup={report['md5_backup']} md5_repaired={report['md5_repaired']}")
    if quarantined:
        print(f"QUARANTINED ({len(quarantined)}): "
              + "; ".join(q["candidate_id"] for q in quarantined))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
