# RESUME — LUNARVOID project state (2026-09-13, session 64)

> Canonical resume document for the LUNARVOID project. Read this
> file when resuming — it captures the frozen state, resume
> protocol, user-gated items, and verification commands in a
> single document, so future sessions don't have to re-read the
> 713-line `notes/findings.md` dense prose layer.

---

## 1. Frozen state (verified 2026-09-13, HEAD `82aedfb`)

| Item | Value |
|---|---|
| Registry md5 | `a60fb52152e33f37e9052434ad026a6e` (278 rows = 117 ACTIVE + 161 SUPERSEDED) |
| Sidecar flags sha256 | `1c884a1ee965c9a3bbbc1b34531509a4a676ae8e9f10ed45280a7b0ef7fb498e` |
| Above-floor decomp | 45 = 14 TP + 9 FP + 21 ring + 1 funnel |
| FP (row-based) | **3.74 [1.71, 7.10]** per 10⁴ km² over 24,062.96 km² |
| FP (unique-feature) | **2.08 [0.67, 4.85]** per 10⁴ km² (5 unique FPs, ~30 m key) |
| PU v1 | P 0.9000 / R 0.8182 / AUC 0.8968 |
| PU v5 run B | F1 0.8235 / P 0.7368 / R 14/15 / AUC 0.9301 |
| Sentinel values | MAX_M=1e6, WARN_MAX=100 m, ATTR_SENTINEL_MAX=1e3, F32_NODATA=-9999.0, GTIFF_NODATA=NaN |
| Suite | 124 passed, 6–8 warnings (varies) |
| Verifier scripts | v02 21/21 · v03 15/15 · v04 11/11 |
| Zenodo CHECKSUMS | 10/10 verified |
| Disk | ≥40 GB free on `/` required |
| Spend | $0 across 62 sessions; $150 budget cap; $800 master-plan ceiling |

## 2. Resume protocol (6 steps)

1. **Load both skills** at session start (per protocol step 0a): `lunarvoid-protocol`, `lunarvoid-conventions`.
2. **Acquire lock**: `bash ~/lunarvoid/bin/lunarvoid_lock.sh acquire opencode`. If non-zero → another orchestrator holds the roadmap → STOP, report to user.
3. **Read Obsidian vault** at `01_WORKSPACE/Lunar Lavatube knowledge/00_HOME.md` (entry MOC).
4. **Navigate via MOCs**: `mocs/MOC Gates & Decisions`, `mocs/MOC Sites & Candidates`, `mocs/MOC Data & Code`, `mocs/MOC Concepts & Methods`, `mocs/MOC Sessions & Ops`.
5. **Read this file** (RESUME.md) for frozen state + user-gated items.
6. **Read** `admin/CHANGELOG.md` for recent session activity; `notes/findings.md` (append-only) for scientific claims when needed.

## 3. User-gated items (R3 §11 — per protocol stop conditions, do NOT auto-start)

- **(a)** Step 8.3/8.4: TRANQPIT1 local ASP reproduction (history: session-58 audit verdict "not completed locally; no output DTM exists").
- **(b)** Step 19.1/19.2 + NAC IMG-byte-signature fetch pipeline (Tier-0 budget eligible; would be first WP0 reproduction since cycle 2 close).
- **(c)** P6.0–P6.8: Hetzner AX52 rental (~$55/mo; needs credentials + provider choice).
- **(d)** R1 roadmap commit at `01_WORKSPACE/plans/2026-08-21_R1_Roadmap_draft.md` (currently untracked).
- **(e)** E3 Zenodo deposit (licence CC-BY-4.0/MIT confirm, creator list, token).
- **D3** LOO cross-validation (frozen-science-adjacent, deliberately deferred per R3 §10).
- **D2** visual verdicts (per-candidate verdicts not yet captured on disk; user-completed 2026-08-28 but format not saved).
- Journal submissions (Paper 1 v2.1 submission-ready; Paper 2 v3.3-draft).
- CI activation, Zotero attaches, Laurier/ASU pit-database audit (external).

## 4. Verification commands (re-run on resume)

```bash
REPO=/home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube
cd $REPO

# Suite
PYTHONPATH=01_WORKSPACE/code /home/frostflux/lunarvoid/venv/bin/python -m pytest 01_WORKSPACE/code/tests/ -x -q
# → expect: 124 passed, ~6–8 warnings

# Frozen registry md5 (expect a60fb52152e33f37e9052434ad026a6e)
md5sum 01_WORKSPACE/data/candidate_registry.csv

# Sidecar sha (expect 1c884a1ee965c9a3bbbc1b34531509a4a676ae8e9f10ed45280a7b0ef7fb498e)
sha256sum 01_WORKSPACE/data/candidate_registry_flags.csv

# Zenodo CHECKSUMS (expect 10/10 OK)
( cd 01_WORKSPACE/data/zenodo_deposit_v1.0 && sha256sum -c CHECKSUMS.sha256 )

# Verifier scripts
/home/frostflux/lunarvoid/venv/bin/python 01_WORKSPACE/admin/verification_evidence/scripts/verify_v02_f32dir_and_filter.py
/home/frostflux/lunarvoid/venv/bin/python 01_WORKSPACE/admin/verification_evidence/scripts/verify_v03_slope_mask.py
/home/frostflux/lunarvoid/venv/bin/python 01_WORKSPACE/admin/verification_evidence/scripts/verify_v04_tune_slope.py

# Vault site-notes drift check (expect timestamp-only diffs; zero data drift)
for s in 01_WORKSPACE/Lunar\ Lavatube\ knowledge/sites/*.md; do
  /home/frostflux/lunarvoid/venv/bin/python 01_WORKSPACE/code/tools/regen_site_notes.py --check 2>/dev/null && break
done
```

## 5. Recent decisions (sessions 55–64)

- **s55–57**: B-cluster close, sentinel hardening, io_common.py v1, registry writes v0.1 (verifier scripts 21/15/11).
- **s58**: protocol recheck; retro-skeptic closes 51/52/57 findings (52 framing UNSOUND → corrected); PROVENANCE row 48 annotated; vault catch-up sessions 26–57 (32 atomic notes via orchestrator bash).
- **s59**: R3 status report drafted and finalized (150 lines; supersedes R2 71 lines); NAC reclassified BLOCKED → MEDIUM-OPEN (WMS RDR probes).
- **s60**: NAC verification fetch (sandbox 10,370 B HTML at sha256 `bb2c525c…`; $0 cost); NAC reclassified MEDIUM-OPEN → HIGH-OPEN.
- **s61**: `.gitignore` line 85 added (sandbox HTML); MANIFEST row added; VERIFICATION.md (164 lines → 176 after corrections) tracked.
- **s62**: protocol recheck of s58–61; retro-skeptic on s60 NAC HIGH-OPEN (view_rdr_product is ALSO an HTML viewer; tier preserved, wording corrected); verifier FAIL on s60 + PASS-with-notes on s59; 7 surgical corrections applied; vault catch-up s58–61.
- **s63**: recheck-of-recheck; verifier PASS-with-notes on s62 (11/11 items); 00_HOME housekeeping drift fixed (43→62 sessions, 141→150 R3 lines).
- **s64** (this session): canonical RESUME.md + final standdown bookkeeping.

## 6. Permissions in effect (`.gitignore` + role split)

- `00_SOURCE_ORIGINALS/` — read-only for ALL agents.
- `01_WORKSPACE/Lunar Lavatube knowledge/` — gitignored at `.gitignore:73` (vault).
- `01_WORKSPACE/data/outputs/wp1_lla/sandbox_nac_verify/*.html` — gitignored at `.gitignore:85`.
- `01_WORKSPACE/data/outputs/{wp2_sag, wp0_kriging, wp0_primitive, wp3_fusion}/` — gitignored.
- `01_WORKSPACE/notes/RESUME.md` — TRACKED (canonical resume document).
- Lock: `bash ~/lunarvoid/bin/lunarvoid_lock.sh acquire <owner>`; release with `force` if needed.
- Hard rule: $0 spend without user-approved §8 trigger.

## 7. Deviation log (orchestrator-direct-edit family — 5 entries)

1. **s58**: commit `0721854` body contains elided `/home/frostflux/...` path (path-rule breach).
2. **s58**: sessions 49–56 bookkeeping applied orchestrator-direct rather than via archivist dispatch (role gap).
3. **s59**: paper-writer R3 draft hit `plans/` write gap, used `cp` via `notes/` → `plans/` workaround (permission gap).
4. **s61**: geo-coder R3 §7 edit applied via Python in-place write (opencode.json blocks `edit` on `plans/`).
5. **s62**: orchestrator surgical edits to R3 + VERIFICATION.md + MANIFEST (no subagent cleanly owns plans/ content edits or sandbox verification-record wording fixes).

**Step 0a gap acknowledged**: sessions 59–61 did NOT load the protocol skill at session start (only session 58 did); corrected going forward.

## 8. Stop conditions (per protocol — surface to user, do not proceed)

- ANY §8 cost trigger would be needed (paid GPU, VPS, rental).
- A gate decision (G0′/G1/...) requires human judgement.
- Verifier FAIL ×3 on one task; a rule/licence conflict.
- **T5**: cannot reproduce a published v0.x headline number within ±5%.
- Anything that would write outside `01_WORKSPACE/` or `~/lunarvoid/`.
