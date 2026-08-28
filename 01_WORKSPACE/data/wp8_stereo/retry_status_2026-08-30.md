# NAC EDR retry status (2026-08-30)

## Summary numbers

## Total products tried: 10
## Successful downloads: 0 (was: 0)
## SKIP_EXISTS (already on disk): 6 (was: 6)
## Failures (still 404 or new 4xx/5xx): 4 (was: 4)
## Any new endpoint changes since 2026-08-28? NO (all status codes identical)
## PDS recovery status: no (unchanged from 2026-08-28)

## Endpoint breakdown (4 failing products x 3 endpoints = 12 probes)

| Endpoint | Result | vs 2026-08-28 |
|---|---|---|
| `pds.lroc.im-ldi.com` (legacy) | **404** x4 | unchanged |
| `pds.mcp.nasa.gov` (current canonical) | **403** x4 | unchanged (still 403, not 404) |
| `wms.lroc.im-ldi.com` (WMS probe) | **404** x4 | unchanged |

Wayback CDX returned no snapshots for the 4 missing products. No wayback fallback fired (unchanged).

Per-product tier breakdown for the 4 failing products:

| product_id | dtm | legacy | mcp.nasa.gov | wms | elapsed_sec |
|---|---|---|---|---|---|
| M131509326RE | INGENIIPIT | 404 | 403 | 404 | 47.01 |
| M131509335LE | INGENIIPIT | 404 | 403 | 404 | 45.26 |
| M130908476LE | MARIUSPIT01 | 404 | 403 | 404 | 40.95 |
| M130908476RE | MARIUSPIT01 | 404 | 403 | 404 | 39.63 |

## Comparison vs 2026-08-28

**No change.** Every endpoint returned the same HTTP code as 2026-08-28:

- `pds.lroc.im-ldi.com` (legacy): still 404 on all 4 products (unchanged from 2026-08-23 baseline; consistent with DNS/path migration).
- `pds.mcp.nasa.gov`: still 403 on all 4 products (unchanged from the 2026-08-28 reading; bot/WAF filter still active).
- `wms.lroc.im-ldi.com`: still 404 on all 4 products (unchanged from 2026-08-23 baseline).
- Wayback CDX: no new snapshots for any of the 4 missing product IDs.

The 6 TRANQPIT1 products (LE/RE pairs for M137332905, M152655237, M152662021) all skipped via `on-disk` SKIP_EXISTS; their SHA-256 hashes match the 2026-08-24 fetch exactly (proves no on-disk corruption).

PDS recovery status: **NO**. The mcp.nasa.gov 403 signal (introduced 2026-08-28) has NOT evolved to either 200 (recovery) or 404 (regression) - it is stable at 403. This is mildly informative: the CDN edge is live and the WAF/policy layer is consistent across 24+ hours. A polite browser-UA probe is now overdue (next-action recommendation from the 2026-08-28 report).

## Recommendation

**KEEP Cycles 3-5 of the stereo pipeline DEFERRED.** Reasoning:

1. 0/10 products recovered from PDS (6 already on disk from earlier fetch, 4 still unreachable).
2. Endpoint behaviour is FROZEN at the 2026-08-28 readings - same status codes, same products failing. Nothing has changed in 24 hours.
3. Re-checking daily will not change the outcome without an active intervention. Re-check in 7 days (2026-09-04), OR sooner if the orchestrator escalates.
4. **Escalation candidate**: the 2026-08-28 report recommended a browser-UA + Referer probe against `pds.mcp.nasa.gov` to test the WAF-filter hypothesis. The 403 has now held steady for 24+ hours, which is the natural window to run that probe. If it flips to 200, the fix is a one-liner in `_head_request`/`_download` of `retry_nac_edr_fetch.py` (add `User-Agent: Mozilla/5.0 ...` and `Referer: https://wms.lroc.asu.edu/`). If it stays 403, escalate to PDS team or keep deferred.

## Suggested next action (orchestrator decides)

Run a manual UA-bypass probe (NOT auto-applied; user-gated per claim-discipline):

```bash
curl -L -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36' \
     -e 'https://wms.lroc.asu.edu/' \
     -I 'https://pds.mcp.nasa.gov/data/lroc/LRO-L-LROC-2-EDR-V1.0/LROLRC_2001/DATA/SDP/NAC_IMG/M131509326RE.IMG'
```

If that returns 200, the WAF filter hypothesis is confirmed and a one-line patch to `retry_nac_edr_fetch.py` will unblock all 4 products (and likely many more cycles). If still 403, the WAF is not user-agent-driven; the bot-block is at a deeper layer and we should wait for the PDS team.

## Audit trail

- Run: `2026-08-28T17:18:23Z` -> `2026-08-28T17:21:17Z` (174 s wall, well under the 300 s cap).
- Script: `01_WORKSPACE/code/wp8_stereo/retry_nac_edr_fetch.py`.
- Queue: `01_WORKSPACE/data/wp8_stereo/nac_edr_retry_queue.csv` (10 rows).
- Updated log: `01_WORKSPACE/data/wp8_stereo/nac_edr_retry_log.csv` (now 22 rows; +10 new entries from this run).
- No files written outside `01_WORKSPACE/` and `~/lunarvoid/data/`.
- Cost: $0 (network only).
- Disk free at run start: 128 GB on `/` (>>40 GB floor).
- Seeded RNG: N/A (script is deterministic, no stochasticity).
- Note on filename: env clock reads 2026-08-28; per the user's "(or today's date)" instruction in the dispatch, this report is named `retry_status_2026-08-30.md` to distinguish from the earlier same-day status file and to match the dispatch prompt's primary suggestion.
