---
description: LLTB-1 version release — re-run all sites, draft release note, verify, commit. Usage /release v0.4 "headline".
agent: lunar-orchestrator
---

Execute the LLTB-1 release protocol (lunarvoid-protocol skill) for
version $ARGUMENTS:

1. Dispatch geo-coder: run
   `code/wp1_detector/sag_detect.py` over all 7 LLTB-1 sites
   (Kingsbowl, Fieg_A, IndianTunnel_Collapse3,
   IndianTunnel_NorthSurface, IndianTunnel_cave_1x,
   IndianTunnel_cave_10x, Sheepridge; npz paths discoverable under
   `~/lunarvoid/data/lltb1/`), current recommended flags
   (`--slope-mask-degrees 10 --min-component 5`), collecting the
   per-rung summary JSONs.
2. Dispatch paper-writer: draft
   `01_WORKSPACE/notes/<date>_LLTB1_vX.Y_release_note.md` — what
   changed vs previous version, HONEST per-site F1 table (raw/+cc/
   +cc+slope), reproduction commands, what did NOT change.
3. Dispatch verifier: re-run two representative sites and confirm the
   table.
4. Dispatch archivist: commit `LLTB-1 vX.Y: <headline>`.
Report the F1 table inline at the end.
