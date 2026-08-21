---
description: Execute one full roadmap task cycle — dispatch implementer, verify independently, bookkeep + commit. Usage /task 13 or /task R0 (reconciliation).
agent: lunar-orchestrator
---

Run ONE complete task cycle per the lunarvoid-protocol skill for:
$ARGUMENTS

(If the argument is a task number, quote that task's steps from
`01_WORKSPACE/plans/2026-08-19_ZEROCOST_Roadmap.md` in the dispatch.
If it is R0, run the reconciliation cycle described in your agent
instructions. If empty, pick the first open task whose dependencies
are met and confirm the choice with the user before dispatching.)

Cycle: geo-coder dispatch → verifier dispatch (PASS required) →
archivist dispatch (tick + CHANGELOG + MANIFEST + single commit).
On verifier FAIL: one re-dispatch with findings, then STOP and report
if it fails again. Halt immediately at any cost trigger or rule
conflict. End with a 5-line summary: task, verdict, headline numbers,
commit hash, next open task.
