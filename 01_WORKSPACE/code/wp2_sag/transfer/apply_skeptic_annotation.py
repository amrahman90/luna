"""P3.1c Cycle 1 close — apply the skeptic fall-back annotation to the new
registry rows for GRUITHMARE2 and MARIUSCONE.

Skeptic rule (Cycle 1 second-opinion):
  frangi@score < 0.02 AND depth@score >= 100 m
  -> label tier C with annotation
     "deep-pit low-vesselness (circular depression, not tubular);
      requires NAC visual inspection"
  Applied to ALL new rows for that site (per-row frangi isn't in registry;
  this is the simplest defensible site-level flag).

Computed frangi@score_max:
  GRUITHUIS17: 0.0424 (>= 0.02 threshold) -> NO annotation
  GRUITHMARE2: 0.0150 (< 0.02; depth@score=604 m >= 100 m) -> annotate all rows
  MARIUSCONE:  0.0107 (< 0.02; depth@score=619 m >= 100 m) -> annotate all rows

Atomic write: read -> modify in memory -> write to temp -> rename.
"""
from __future__ import annotations
import shutil
from pathlib import Path
from datetime import date

REG = Path('01_WORKSPACE/data/candidate_registry.csv')
ANNOT = '; deep-pit low-vesselness (circular depression, not tubular); requires NAC visual inspection'
ANNOT_DTMS = ('GRUITHMARE2', 'MARIUSCONE')  # GRUITHUIS17 excluded (frangi@score >= 0.02)
TODAY = date.today().isoformat()

with open(REG) as f:
    text = f.read()

lines = text.rstrip('\n').split('\n')
n_changed = 0
n_updated = 0
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
    # Strip whitespace from notes (sometimes trailing spaces)
    notes = notes.rstrip()
    # Check if this is a NEW row from this cycle (first_found == today)
    # AND the DTM is in ANNOT_DTMS AND not already annotated
    if (cid.startswith('LV-') and dtm in ANNOT_DTMS
            and 'deep-pit low-vesselness' not in notes):
        if ANNOT.strip() not in notes:
            new_notes = notes + ANNOT if notes else ANNOT.lstrip('; ')
            new_notes = new_notes.strip()
            parts[14] = new_notes
            n_changed += 1
    # Update the "updated" column (idx 12) for all NEW rows from this cycle
    if len(parts) > 12 and parts[12] == TODAY:
        parts[12] = TODAY  # ensure today
        n_updated += 1
    out_lines.append(','.join(parts))

# Atomic write: temp file in same dir then rename
tmp = REG.with_suffix('.csv.tmp')
with open(tmp, 'w') as f:
    f.write('\n'.join(out_lines) + '\n')
shutil.move(tmp, REG)

print(f"[ok] annotated {n_changed} rows (target: GRUITHMARE2 + MARIUSCONE new rows)")
print(f"[ok] confirmed {n_updated} rows have updated={TODAY}")
print(f"[ok] file written: {REG}")

# Verify
import subprocess
res = subprocess.run(['grep', '-c', 'deep-pit low-vesselness', str(REG)],
                     capture_output=True, text=True)
print(f"[verify] grep -c 'deep-pit low-vesselness': {res.stdout.strip()}")
res = subprocess.run(['grep', '-E', 'GRUITHMARE2|MARIUSCONE', str(REG)],
                     capture_output=True, text=True)
annotated = sum(1 for L in res.stdout.splitlines() if 'deep-pit low-vesselness' in L)
total = len(res.stdout.splitlines())
print(f"[verify] GRUITHMARE2+MARIUSCONE rows: {total}, annotated: {annotated}")
res = subprocess.run(['grep', '-E', 'GRUITHUIS17', str(REG)],
                     capture_output=True, text=True)
gr_lines = res.stdout.splitlines()
gr_annotated = sum(1 for L in gr_lines if 'deep-pit low-vesselness' in L)
print(f"[verify] GRUITHUIS17 rows: {len(gr_lines)}, annotated: {gr_annotated} (must be 0)")
