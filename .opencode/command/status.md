---
description: Reconciliation scan — roadmap checkbox state vs CHANGELOG vs disk, with drift report. Read-only.
agent: lunar-orchestrator
---

Perform a read-only reconciliation of the LUNARVOID project state. Do
NOT modify anything and do NOT dispatch bookkeeping — output the report
only (if drift needs fixing, ask the user to run /task for R0).

1. Parse `01_WORKSPACE/plans/2026-08-19_ZEROCOST_Roadmap.md`: list all
   unticked steps grouped by task number, noting which tasks are
   partial (some steps ticked).
2. Read the last 3 sessions of
   `01_WORKSPACE/admin/CHANGELOG.md` and `git log --oneline -10`.
3. Spot-check disk: do deliverables claimed in recent CHANGELOG
   entries exist (ls the paths)? Does `~/lunarvoid/stereo/TRANQPIT1`
   contain a finished DTM or is Task 8 incomplete?
4. Report: a table of Task # | roadmap state | changelog state | disk
   reality | drift (NONE / TICKED-BUT-UNDONE / DONE-BUT-UNTICKED /
   PARTIAL), then a recommended action list in priority order.

$ARGUMENTS
