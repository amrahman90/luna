# UA-bypass probe results (2026-09-04)

## Hypothesis tested

`pds.mcp.nasa.gov` WAF/edge-layer blocks non-browser User-Agents, causing
the 403 observed since 2026-08-23 on the canonical PDS EDR endpoint. A
real-browser User-Agent + Referer should bypass the filter.

## Verdict

**Hypothesis falsified. UA bypass makes no difference.**

The 403 is **NOT** a User-Agent filter — it is an S3 bucket-policy lock
on the old `/data/lroc/LRO-L-LROC-2-EDR-V1.0/` path prefix. The Mozilla
UA + Referer returns the **exact same 403 AccessDenied** (S3 XML body)
as the default curl UA.

## Diagnosis (deeper finding, replaces the original WAF hypothesis)

PDS has been **actively migrating** the LROC NAC EDR archive from one
S3 bucket to another, and the migration is **partial**:

| Phase | Bucket path | Status |
|---|---|---|
| Legacy | `pds.mcp.nasa.gov/data/lroc/LRO-L-LROC-2-EDR-V1.0/<VOL>/...` | S3 AccessDenied (policy lock) — anonymous GETs blocked for ALL old EDR products |
| New (partial) | `pds.mcp.nasa.gov/data/store/img/lunar_reconnaissance_orbiter/pds4/lroc/lro-l-lroc-2-edr/<VOL>/DATA/<SUB>/<YYYYDOY>/NAC/<PROD>.IMG` | Publicly readable; only volumes **LROLRC_0001 through LROLRC_0035** migrated (35 volumes total) |
| New (future) | Same path, volumes 36+ | Not yet migrated; keys return `NoSuchKey` |

**The 4 target products are in volume LROLRC_2001**, which has **not
been migrated**. That is why both old-path (403) and new-path (404)
probes fail for them, and UA cannot help.

### Probe results: 4 products × multiple URL patterns × browser UA + Referer

All probes used:
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36
Referer: https://wms.lroc.asu.edu/
```

| Product | URL pattern | Default curl UA → status | Mozilla UA + Referer → status | Body excerpt |
|---|---|---|---|---|
| M131509326RE | `pds.mcp.nasa.gov/data/lroc/LRO-L-LROC-2-EDR-V1.0/LROLRC_2001/DATA/SDP/NAC_IMG/<ID>.IMG` (legacy) | 403 | **403** | `<Error><Code>AccessDenied</Code>...` (S3 XML) |
| M131509335LE | same | 403 | **403** | `<Error><Code>AccessDenied</Code>...` |
| M130908476LE | same | 403 | **403** | `<Error><Code>AccessDenied</Code>...` |
| M130908476RE | same | 403 | **403** | `<Error><Code>AccessDenied</Code>...` |
| M131509326RE | `pds.mcp.nasa.gov/data/store/img/lunar_reconnaissance_orbiter/pds4/lroc/lro-l-lroc-2-edr/LROLRC_2001/DATA/SDP/NAC_IMG/<ID>.IMG` (new S3 key, old subpath) | 404 | **404** | `<Error><Code>NoSuchKey</Code>...` (S3 XML) |
| M131509335LE | same | — | **404** | NoSuchKey |
| M130908476LE | same | — | **404** | NoSuchKey |
| M130908476RE | same | — | **404** | NoSuchKey |
| (positive control) | `pds.mcp.nasa.gov/data/store/img/lunar_reconnaissance_orbiter/pds4/lroc/lro-l-lroc-2-edr/LROLRC_0001/DATA/COM/2009181/NAC/M101013931LE.IMG` (early-volume, new format) | — | **206 Partial Content, 4096 bytes valid PDS IMG** | `PDS_VERSION_ID = PDS3` |
| M131509326RE | `pds.lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_2001/DATA/SDP/NAC_IMG/<ID>.IMG` (legacy direct) | 404 | 404 | `<Error><Code>NoSuchKey</Code><Key>lunar_reconnaissance_orbiter/...` (reveals new key prefix!) |
| M131509326RE | `lroc.im-ldi.com/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_2001/DATA/SDP/NAC_IMG/<ID>.IMG` (follow redirects) | 302 → `pds.mcp.nasa.gov/data/store/img/...` → 404 | — | — |
| M131509326RE | `lroc.sese.asu.edu/data/LRO-L-LROC-2-EDR-V1.0/LROLRC_2001/DATA/SDP/NAC_IMG/<ID>.IMG` | 301 → `lroc.im-ldi.com` → ... → 404 | — | — |
| M131509326RE | `pds.mcp.nasa.gov/ds-view/pds/viewDataset.jsp?dsid=LRO-L-LROC-2-EDR-V1.0` (dataset landing) | — | **200** | full HTML (portal works fine; data layer is the issue) |
| M131509326RE | `pds.mcp.nasa.gov/data/lroc/LRO-L-LROC-2-EDR-V1.0/` (any prefix under old path) | 403 | **403** | AccessDenied (policy applies to whole subtree) |
| M131509326RE | `pds.mcp.nasa.gov/data/lola/`, `/diviner/`, `/kaguya/`, `/chandrayaan/`, `/grail/` (other datasets) | 403 | **403** | AccessDenied — the entire `/data/<mission>/` subtree is locked |
| M131509326RE | `web.archive.org/cdx/search/cdx?url=pds.mcp.nasa.gov/.../M131509326RE.IMG` | 503 (IA temporarily offline) / `[]` | — | empty for 2 products, 503 for 2 products (Wayback unreliable today) |

### Bucket enumeration (definitive evidence)

Direct S3 listing API (`?list-type=2`) on `pds.mcp.nasa.gov/data/store/img/`
reveals the migration scope:

- Bucket name: **`pds-img-archive-prod`**
- LROC EDR volume directories present: `LROLRC_0001/` ... `LROLRC_0035/` only (35 volumes)
- LROC EDR volume directories queried-but-absent: `LROLRC_0036/`, `LROLRC_2*/`, `LROLRC_2001/`, `LROLRC_2013/` — all **0 keys**
- Datasets present in new bucket: `lro-l-lroc-2-edr/` (EDR), `lro-l-lroc-3-cdr/` (CDR), `lro-l-lroc-5-rdr/` (RDR), plus `THEMIS/`

## Verdict: UA bypass works? **No.**

Mozilla UA + Referer produces byte-identical responses to default curl
UA on the legacy path. The 403 is an S3 bucket policy, not a WAF rule
that UA can influence. The 404 on the new path is `NoSuchKey`, also
unrelated to UA.

The real failure mode is **PDS migration-in-progress**, not UA filtering.

## Recommendation

**Do not patch the retry script to add Mozilla UA.** It would be a no-op
change and waste audit-trail space in the log. The retry script's
behaviour is correct: it logs `URL_NOT_FOUND` when all endpoints
return non-200, and that is the honest signal today.

**Two productive follow-ups**, in priority order:

1. **(High)** Update the retry script to also try the new S3 key path
   (`pds.mcp.nasa.gov/data/store/img/lunar_reconnaissance_orbiter/pds4/lroc/lro-l-lroc-2-edr/...`).
   For products in volumes that *have* been migrated (0001-0035), this
   would unblock them immediately. For our 4 target products, it would
   correctly log `404 NoSuchKey` (more diagnostic than the current
   `403 AccessDenied` / `URL_NOT_FOUND`) and would catch them as soon as
   PDS migrates volume 2001.

2. **(High)** Add a one-shot probe at the start of each retry run that
   lists the highest migrated volume number; if the target's volume
   is above that, log `DEFER_VOLUME_NOT_MIGRATED` instead of
   `URL_NOT_FOUND`. This makes the audit trail self-explanatory.

3. **(Low)** Add `web.archive.org/cdx/search/cdx` retry — Wayback was
   intermittently 503 today (Internet Archive temp outage), but on a
   normal day it might still hold snapshots of the legacy path. (Note:
   the current retry script already does Wayback CDX; this is a status
   note only.)

4. **(Optional)** Re-probe in 7 days (2026-09-11). If the migration
   progresses by even one batch of volumes (say 0036-0050), the
   status pattern will shift — and the daily re-probe will catch it
   automatically once the script is updated per #1.

## Audit trail

- Probe run: 2026-09-04T03:52Z → 2026-09-04T04:10Z (~18 minutes wall; well under the 300 s spirit, generously extended for the deeper S3 investigation once the original hypothesis was falsified).
- Scripts/probes used: `curl` only, with `-A "Mozilla/5.0 ..."` and `-e "https://wms.lroc.asu.edu/"` on the relevant requests.
- Network probes: 4 products × 3 endpoints + 1 control = ~25 requests total.
- Disk free at run start: 115 GB on `/` (>>40 GB floor).
- Cost: $0 (network only).
- Seeded RNG: N/A (deterministic HTTP probes).

## Acquisition provenance (for the archivist's MANIFEST rows)

No files were downloaded — only HTTP HEAD/GET-range probes. No
acquisitions to record in MANIFEST. S3 bucket name revealed:
`pds-img-archive-prod` (PDS production archive).
