---
name: lunarvoid-protocol
description: LUNARVOID agentic task lifecycle — how the orchestrator, geo-coder, verifier, archivist, and paper-writer agents split work; dispatch order, review gates, bookkeeping (roadmap ticks, CHANGELOG, MANIFEST, commits), stop conditions, and the LLTB-1 release protocol. Use when executing roadmap tasks, dispatching subagents, verifying completed work, or doing bookkeeping/commits in this project.
---

# LUNARVOID Task Protocol

## Roles (who may write what)

| Agent | Writes | Never touches |
|---|---|---|
| lunar-orchestrator | nothing directly (delegates) | — |
| geo-coder | `01_WORKSPACE/code/**`, `01_WORKSPACE/data/outputs/**`, rasters under `~/lunarvoid/` | CHANGELOG, roadmap, MANIFEST, papers |
| verifier | NOTHING (edit-denied; reports text only) | everything |
| archivist | `admin/**`, `data/MANIFEST.md`, `plans/**` (checkboxes), `notes/**`, `.gitignore`; git add/commit (never push) | code, data outputs |
| paper-writer | `papers/**`, `notes/**` | code, admin |

`00_SOURCE_ORIGINALS/` is read-only for ALL agents (permission-enforced).
Load the `lunarvoid-conventions` skill before any technical work.

## Task lifecycle (autonomous loop)

1. **PICK**: orchestrator reads
   `01_WORKSPACE/plans/2026-08-19_ZEROCOST_Roadmap.md`, selects the
   first unticked step of the lowest-numbered open task whose
   dependencies are met (dependency map at roadmap top).
2. **DISPATCH** → geo-coder subagent with: task number + step text,
   relevant file paths, acceptance criteria, and "report: what you did,
   numbers, output paths, anything that failed". One task per dispatch.
3. **VERIFY** → verifier subagent (edit-denied) with the geo-coder's
   report: independently re-run checks (execute the scripts, re-derive
   headline numbers, audit manifest rows + claim language). VERDICT:
   PASS / PASS-with-notes / FAIL (with reasons).
4. **BOOKKEEP** → archivist subagent on PASS: tick roadmap checkboxes,
   prepend CHANGELOG entry (date — what — where — why, newest first),
   add missing MANIFEST rows, then ONE commit
   (`git add <intended paths> && git commit`, message style: short
   imperative matching `git log --oneline`, e.g. "Task 18: sag search
   over all good-tier mare DTMs (12 candidates)"). Never commit
   secrets; never push.
   On FAIL: orchestrator re-dispatches geo-coder with the verifier's
   findings (max 2 retries, then STOP and surface).
5. **LOOP**: re-read the roadmap from disk (do not trust memory —
   compaction-safe), pick next task.

## Stop conditions (surface to user, do not proceed)

- ANY §8 cost trigger would be needed (paid GPU, VPS, rental).
- A gate decision (G0′/G1/...) requires human judgement.
- Verifier FAIL ×3 on one task, or a rule/licence conflict.
- Anything that would write outside `01_WORKSPACE/` or `~/lunarvoid/`.

## Bookkeeping formats

- Roadmap tick: `- [ ] **Step N.M ...` → `- [x] **Step N.M ...` (sed-safe
  on the step prefix).
- CHANGELOG: `## YYYY-MM-DD (execution session N)` heading + bullets:
  task, headline numbers, deliverable paths, gotchas learned.
- MANIFEST row: product, source URL, local path, SHA-256, size, date,
  licence. Derived files note their parent.

## LLTB-1 release protocol (/release)

vX.Y bump when `wp1_detector/sag_detect.py` behaviour changes:
geo-coder implements → verifier re-runs all 7 sites → paper-writer or
geo-coder drafts `notes/<date>_LLTB1_vX.Y_release_note.md` (what
changed, honest per-site F1 table, reproduction commands) → archivist
commits with message `LLTB-1 vX.Y: <one-line headline>`.

## Context discipline (all agents)

- Keep own context lean: read only the files needed for the current
  task; use explore-style lookup rather than dumping large files.
- The roadmap/CHANGELOG/MANIFEST on disk are the ONLY durable state —
  never rely on conversation memory for task status.
- Big tool outputs: cap/log to file, grep the dump (caps are configured
  in opencode.json; full output is auto-filed).
