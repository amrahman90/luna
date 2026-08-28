# NAC EDR retry status (2026-08-28)

## Summary numbers

## Total products tried: 10
## Successful downloads: 0
## SKIP_EXISTS (already on disk): 6
## Failures (all PDS endpoints non-200): 4
## PDS still down? yes (effectively; see endpoint breakdown below)

## Endpoint breakdown (4 failing products × 3 endpoints = 12 probes)

| Endpoint | Result | Notes |
|---|---|---|
| `pds.lroc.im-ldi.com` (legacy) | **404** x4 | unchanged from 2026-08-23 baseline |
| `pds.mcp.nasa.gov` (current canonical) | **403** x4 | **changed** — was 404 on 2026-08-23, now 403 (Forbidden) |
| `wms.lroc.im-ldi.com` (WMS probe) | **404** x4 | unchanged from 2026-08-23 baseline |

Wayback CDX returned no snapshots for the 4 missing products. No wayback fallback fired.

## Comparison vs 2026-08-23 baseline

- 0/10 products recovered from PDS (6 already on disk from earlier fetch, 4 still unreachable).
- Endpoint behaviour changed for `pds.mcp.nasa.gov`: 404 -> **403**. This is a SLIGHT signal that the mcp.nasa.gov CDN is responding to requests now, but is denying access (likely bot/WAF filter on the user-agent). The 2026-08-23 404 may have been a CDN edge that did not respond at all; the 2026-08-28 403 suggests the edge is live and the request reached an auth/policy layer.
- Legacy `pds.lroc.im-ldi.com` and `wms.lroc.im-ldi.com` still 404 (likely DNS/path migration, not transient).
- Wayback has never archived any of the 4 missing product IDs; no surprise there (Wayback crawls respect robots.txt and NAC IMGs are large).

## Recommendation

**KEEP Cycles 3-5 of the stereo pipeline DEFERRED.** Reasoning:

1. Only the 4 products in the INGENIIPIT and MARIUSPIT01 legs failed; TRANQPIT1 (6 products) is fully covered.
2. Only 2 of the 8 originally deferred cycles depended on these 4 products (the INGENIIPIT and MARIUSPIT01 stereo legs). TRANQPIT1's Cycle 4 stereo work is unblocked since all 6 EDRs are present.
3. PDS recovery is partial, not complete. Rerunning Cycles 3-5 now would burn the retry budget on still-broken endpoints.
4. Re-check in 7 days (2026-09-04). If `pds.mcp.nasa.gov` is still 403, escalate - either (a) add a polite browser UA + Referer to the request (WAF bypass hypothesis) or (b) wait for the PDS team to fix the bot-block.

## Suggested next action (orchestrator decides)

Try one product with a browser User-Agent + Referer header as a probe (manual `curl -A 'Mozilla/5.0 ...' -e 'https://wms.lroc.asu.edu/' ...`). If the mcp.nasa.gov 403 flips to 200, the fix is a one-liner in `retry_nac_edr_fetch.py`'s `_head_request`/`_download` Request construction. Otherwise, keep deferred.

## Audit trail

- Run: `2026-08-28T10:23:19Z` -> `2026-08-28T10:26:10Z` (171 s wall, under the 300 s cap).
- Script: `01_WORKSPACE/code/wp8_stereo/retry_nac_edr_fetch.py`.
- Queue: `01_WORKSPACE/data/wp8_stereo/nac_edr_retry_queue.csv` (10 rows).
- Updated log: `01_WORKSPACE/data/wp8_stereo/nac_edr_retry_log.csv` (now 12 rows; +11 new entries from this run).
- No files written outside `01_WORKSPACE/` and `~/lunarvoid/data/`.
