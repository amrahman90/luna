---
description: Verification-only pass over a completed task (no implementation, no bookkeeping). Usage /verify 18.
agent: lunar-orchestrator
---

Dispatch ONLY the verifier subagent for task $ARGUMENTS (no geo-coder,
no archivist). Provide it the task's acceptance criteria from
`01_WORKSPACE/plans/2026-08-19_ZEROCOST_Roadmap.md`, the relevant
CHANGELOG entry, and the claimed deliverable paths. It must re-run
checks and re-derive headline numbers itself (it is edit-denied).
Return its verdict verbatim plus, if FAIL, a recommended repair
dispatch.
