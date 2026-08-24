# Work Queue 00 — PDS NAC EDR Retry

**Priority:** 1 (highest; quick win)
**Wall time:** 1-2 hours
**Cost:** $0 (network only; no compute)
**Pre-req:** Hetzner cx22 or higher (Python 3 + urllib3); any Hetzner
server is fine because the script is pure-Python.

## Task

Run `code/wp8_stereo/retry_nac_edr_fetch.py` against the retry queue
at `01_WORKSPACE/data/wp8_stereo/nac_edr_retry_queue.csv` and report
which NAC_EDR products are reachable from the Hetzner network path.

PDS endpoints have been 404 since ~2026-08-23. The Hetzner network
may have a different outbound path (different ASN, different CDN
peering) that can reach the legacy endpoint. If so, the script will
download the missing NAC EDRs that the local path cannot reach.

## Steps

1. SSH to the Hetzner server: `ssh root@<server_ip>`.
2. Pull the latest project repo (or rsync from local):
   ```
   rsync -avz /home/frostflux/Ahnaf_Shafin/research_project/Lunar_LavaTube/ \
       root@<server_ip>:/opt/lunarvoid/repo/
   ```
3. Run the retry script with a small max to probe:
   ```
   /opt/lunarvoid/venv/bin/python \
       /opt/lunarvoid/repo/01_WORKSPACE/code/wp8_stereo/retry_nac_edr_fetch.py \
       --max 3
   ```
4. Inspect `01_WORKSPACE/data/wp8_stereo/nac_edr_retry_log.csv`. The
   status column should have entries like `OK_mcp`, `URL_NOT_FOUND`,
   `WAYBACK_FOUND`, or `SKIP_EXISTS` (for products already on disk).
5. If the mcp endpoint works, re-run with `--max 0` (all rows).

## Success criteria

- The retry log has a row for every product_id in the queue.
- At least one `OK_<endpoint>` row OR a documented `URL_NOT_FOUND`
  status for the queue (negative result is fine; just documented).
- If products were downloaded, their SHA-256 matches the row in
  `~/lunarvoid/data/fetch_log_lroc.csv` after a successful transfer
  back to local.

## Output paths

- Retry queue: `01_WORKSPACE/data/wp8_stereo/nac_edr_retry_queue.csv`
- Retry log: `01_WORKSPACE/data/wp8_stereo/nac_edr_retry_log.csv`
- Downloaded EDRs: `~/lunarvoid/data/edr/<dtm>/<product_id>.IMG`
- Hetzner-side JSON smoke record:
  `/opt/lunarvoid/data/admin/rental_versions.json` (from verify.sh)

## Rollback

If PDS returns 404 from the Hetzner path too (the most likely outcome
as of 2026-08-24), this task is a documented negative result. The
retry log becomes the audit trail. Move to work-queue #1 without
further retry.

## Cost

$0 (network only). Egress is well under Hetzner's 20 TB/month cap.

## Verification

After completion, the orchestrator adds a row to `admin/budget.md`
"anomalies" section noting the PDS state and the retry-log path.
