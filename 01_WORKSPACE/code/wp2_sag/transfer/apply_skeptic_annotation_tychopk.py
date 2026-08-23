"""Cycle 2 close — apply the skeptic fall-back annotation to the new
registry rows for TYCHOPK.

Skeptic rule (Cycle 2 second-opinion):
  Computed frangi@score_max and depth@score_max for TYCHOPK:
    - frangi@score = 0.0185 (borderline < 0.02 nominal threshold by 7.5%)
    - depth@score  = 18.35 m (NOT >= 100 m)

  Classification:
    - NOT deep-pit low-vesselness (would require depth@score >= 100 m).
    - central-peak-relief terrain_extrapolation risk (Tycho central peak;
      matches TYCHOPK02/03/04/07 precedent from Cycle 1).
    - All 3 new peaks marked below-local-floor by transfer_apply.py
      (no_local_floor=True; FROZEN TRANQPIT1 is mare-only).
    - Annotation: "; terrain_extrapolation risk (central-peak relief,
      similar to TYCHOPK02/03/04/07); below-local-floor; not an
      independent void candidate"

Target: LV-TYCHOPK-* rows (the bare DTM, NOT TYCHOPK02/03/04/07 which
already carry the same annotation from Cycle 1).

Atomic write: read -> modify in memory -> write to temp -> rename.
"""
from __future__ import annotations
import shutil
from pathlib import Path
from datetime import date

REG = Path('01_WORKSPACE/data/candidate_registry.csv')
ANNOT = '; terrain_extrapolation risk (central-peak relief, similar to TYCHOPK02/03/04/07); below-local-floor; not an independent void candidate'
ANNOT_DTM = 'TYCHOPK'  # bare DTM only (TYCHOPK02/03/04/07 already annotated)
TODAY = date.today().isoformat()

with open(REG) as f:
    text = f.read()

lines = text.rstrip('\n').split('\n')
n_changed = 0
out_lines = []
for line in lines:
    # preserve all comments and header exactly
    if line.startswith('#') or line.startswith('candidate_id'):
        out_lines.append(line)
        continue
    parts = line.split(',')
    if not parts or not parts[0].startswith('LV-'):
        out_lines.append(line)
        continue
    cid = parts[0]
    dtm = parts[3] if len(parts) > 3 else ''
    notes = parts[14] if len(parts) > 14 else ''
    notes = notes.rstrip()
    # Target LV-TYCHOPK-* (bare DTM, distinct from LV-TYCHOPK02-* etc.)
    # cid.startswith('LV-TYCHOPK-') matches the bare-DTM pattern; cid.startswith('LV-TYCHOPK0')
    # (i.e. TYCHOPK02/03/04/07/08/09) would NOT match because the next char after 'K' is '-'
    # for the bare DTM, and a digit for the numbered ones.
    if (cid.startswith('LV-TYCHOPK-') and dtm == ANNOT_DTM
            and 'terrain_extrapolation risk (central-peak relief' not in notes):
        new_notes = notes + ANNOT if notes else ANNOT.lstrip('; ')
        new_notes = new_notes.strip()
        parts[14] = new_notes
        n_changed += 1
    out_lines.append(','.join(parts))

# Atomic write: temp file in same dir then rename
tmp = REG.with_suffix('.csv.tmp')
with open(tmp, 'w') as f:
    f.write('\n'.join(out_lines) + '\n')
shutil.move(tmp, REG)

print(f"[ok] annotated {n_changed} rows (target: 3 LV-TYCHOPK-* rows)")
print(f"[ok] file written: {REG}")

# Verify
import subprocess
res = subprocess.run(['grep', '-c', 'terrain_extrapolation risk (central-peak relief', str(REG)],
                     capture_output=True, text=True)
print(f"[verify] grep -c 'terrain_extrapolation risk (central-peak relief': {res.stdout.strip()}")
res = subprocess.run(['grep', '^LV-TYCHOPK-', str(REG)],
                     capture_output=True, text=True)
n_total = 0
n_annotated = 0
for L in res.stdout.splitlines():
    n_total += 1
    if 'terrain_extrapolation risk (central-peak relief' in L:
        n_annotated += 1
print(f"[verify] LV-TYCHOPK- rows: {n_total}, annotated: {n_annotated} (must equal)")
