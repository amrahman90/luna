---
description: Zero-cost audit — confirm $0 spend, no cost triggers tripped, disk/licence discipline holds. Read-only.
agent: lunar-orchestrator
---

Perform a read-only cost audit:

1. Since the last audit (check CHANGELOG for the previous
   /costcheck note, else project start): list every acquisition in
   `01_WORKSPACE/data/MANIFEST.md` with its source. All must be
   public-domain/CC/open-access (PDS, Zenodo, Wayback) — flag
   anything else.
2. Check the §8 cost triggers (roadmap section 8): no Tier-1 rental,
   paid GPU, VPS, or reproduction rental may have been invoked.
3. Disk: `df -h /` (floor 40 GB) and `du -sh ~/lunarvoid/*` — flag the
   top consumers and anything deletable (stereo intermediates,
   caches).
4. Licence gates: confirm no NASA-analog redistribution happened
   (research/academic use only), ISRO acknowledgement still pending
   if Chandrayaan data used.
5. Output: a 10-line audit table + verdict "STILL $0 / TRIGGERED
   (what, when, decision needed)" + housekeeping recommendations.

$ARGUMENTS
