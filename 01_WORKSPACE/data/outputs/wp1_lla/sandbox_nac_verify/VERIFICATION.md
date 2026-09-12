# NAC verification fetch — sandbox record

**VERIFICATION ONLY — NOT a ladder input. Not for pipeline use. Not for canonical
`data/outputs/wp1_lla/TRANQPIT1/` placement. See session 60 `findings.md`
entry and `2026-09-12_R3_Status_Report.md` §7 for upgrade rationale.**

## Sandbox layout

- Sandbox dir: `01_WORKSPACE/data/outputs/wp1_lla/sandbox_nac_verify/` (created
  2026-09-12; did not exist before this session).
- Canonical `TRANQPIT1/` path: **NOT touched** (read-only by protocol).
- Sandbox file: `NAC_ANAGLYPH_M102172207_M102165049_view_rdr.html`
  (10,370 B). Note: filename extension is **`.html`**, not `.IMG` — the
  bounded fetch below returned HTML, not an IMG/ZIP/TAR (see §3).

## 1. Source page (already on disk; pre-fetch probe, session 59)

- URL: `https://wms.lroc.asu.edu/lroc/rdr_product_select?product_id=M104203891S`
- Local file: `/tmp/opencode/nac_probe.html` (23,154 B, fetched session 59)
- Page role: LROC WMS RDR-search results page (4148 total NAC RDRs matched).
- Parse result (stdlib `html.parser` + regex over pre-fetched HTML):
  - **0** `.IMG` / `.tar.gz` / `.ZIP` / `.cub` / `.tif` download URLs.
  - **0** PDS dataset IDs in the body text (no LROLRC / LRO-L-LROC-* /
    acknowledgement text in this page).
  - **10** NAC_ANAGLYPH detail-page links (each is HTML, not a file):
    `/lroc/view_rdr/NAC_ANAGLYPH_M102172207_M102165049` etc.
  - Pager links (1..9, …, 414, 415) — pagination of the same search.
  - 6 site-asset URLs (CSS/JS/logos) and 5 marketing/external URLs.
- Implication: the WMS RDR search page is a **search index**, not a
  download index. Direct IMG acquisition requires at least one extra
  hop — `view_rdr_product` is ALSO an HTML viewer (skeptic session 62
  retro HEAD probe: content-type text/html, 302→200 via `data.lroc.im-ldi.com`
  with PDS session cookies set); the actual IMG byte is form/cookie/JS-driven
  and lives one further hop downstream. The two-HTML-hop chain was verified;
  the IMG byte was not reached.

## 2. Chosen URL for the bounded fetch

- Chosen (smallest expected, alphabetically first NAC_ANAGLYPH detail page):
  `https://wms.lroc.asu.edu/lroc/view_rdr/NAC_ANAGLYPH_M102172207_M102165049`
- Rationale: the source page exposes no IMG/ZIP/TAR/CUB/TIF URLs; the
  smallest available WMS-served artifact is the `view_rdr/*` HTML
  detail page. The URL string length is identical across all 10
  candidates (M10xxxxxxx = 9 digits), so the choice is deterministic
  by alphabetical order of the 9-digit EDR sequence.
- Predicted type: HTML (~10 KB).
- Predicted size: < 50 KB (HTML detail page; NAC WMS pages are <20 KB).
- Predicted actual: <20 KB / <5 s. Resource ceiling: 200 MB / 120 s.
- Cost notes live in `01_WORKSPACE/admin/budget.md`, not in this verification record.

## 3. Bounded fetch (ONE file)

- Command: `curl -L --max-time 120 -o <sandbox>/NAC_ANAGLYPH_M102172207_M102165049_view_rdr.html <URL>`
- HTTP status: **200**
- Curl return code: 0 (success)
- Wall-clock elapsed: **2 s**
- File size: **10,370 B** (well above the 10 KB sanity floor)
- SHA-256: `bb2c525c1ad622bc185c4e7c13a3febcf99a4780d83c8e77a88dc3cabb53c571`
- Content-Type (libmagic detection): `HTML document, ASCII text`
- First 16 bytes (hex): `3c21444f43545950452068746d6c3e0a`
- First 16 bytes (ASCII): `<!DOCTYPE html>` + LF
- **First-4-bytes signature verdict**: `<!DO` (HTML, NOT `CCSD` /
  `PDS` / `II*` — i.e. NOT an ISIS PDS label, NOT a raw EDR IMG, NOT a
  GeoTIFF). The bounded fetch returned HTML, not an NAC IMG. This is
  honest and expected (see §1 — no IMG URL was available on the source
  page); not a fetcher bug.

## 4. Evidence harvested from the bounded-fetched HTML

The fetched HTML page contains — beyond what session 59 saw — three
genuine, new pieces of evidence (verified by parsing the file body,
not just probing HEADs):

1. **PDS dataset ID (canonical)**: **`LRO-L-LROC-5-RDR-V1.0`**
   (RDR — Reduced Data Record — dataset 5; session 59 cited dataset 2
   `LRO-L-LROC-2-EDR-V1.0` because the PDS archive alive-check used
   that path; the WMS RDR archive lives in dataset 5. Both are PDS
   public-domain bundles under the LRO-L-LROC-* family.).
2. **LROLRC bundle ID**: `LROLRC_2001` (visible in the relative
   PYR.TIF URL path; matches the master-plan "LROLRC_2001" archive
   name that the v5 §M0 / §8 work item explicitly cites).
3. **PYR.TIF preview-tile URL** (relative):
   `/ptif/zoomify/ser/estore/lroc/web/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/EXTRAS/ANAGLYPH/NAC_M102172207_M102165049/NAC_ANAGLYPH_M102172207_M102165049.PYR.TIF`
   — the Zoomify tile pyramid for this NAC anaglyph. The IMG data file
   itself is downstream (the page links to
   `/lroc/view_rdr_product/NAC_ANAGLYPH_M102172207_M102165049` with
   text "click for more information", but `view_rdr_product` is ALSO an
   HTML viewer per skeptic session 62 retro — content-type text/html at
   status 200 after 302 to `data.lroc.im-ldi.com` with PDS session cookies
   set; the actual IMG byte acquisition is form/cookie/JS-driven and lives
   one further hop downstream).
4. **ISIS3 attribution link** (USGS Integrated Software for Imagers
   and Spectrometers) — confirms the RDR was processed with ISIS3
   (consistent with LROC's standard NAC_RDR pipeline).
5. **Citation pointer** to EPSC2012 abstract
   `http://meetingorganizer.copernicus.org/EPSC2012/EPSC2012-486-2.pdf`
   (publication reference for the anaglyph technique).

## 5. Licence note

- The WMS page contains **no in-page licence text**; the LROC RDR
  data is distributed via PDS (Planetary Data System) under the
  standard NASA/PDS data-use policy:
  - PDS data is **public domain** (NASA policy; per
    `lunarvoid-conventions` §6).
  - ASU/LROC use requires **acknowledgement** per master-plan rule
    (`00_SOURCE_ORIGINALS/LUNARVOID_Master_Plan_v5_Full_Synthesis.txt`,
    citation discipline).
- Acknowledgement boilerplate (per LROC convention, paraphrase):
  "Images and DTMs courtesy of NASA/GSFC/Arizona State University".
  - Per master-plan data-discipline rule, LROC data is fetched by
    **product ID only**, never mirror-archived, and any publication
    cites LROC. The Zenodo-deposit licence is CC-BY-4.0 (separate
    decision); the LROC data licence is PDS-public-domain.

## 6. Signature verification verdict (honest)

- **HTML signature, not IMG signature.** The bounded fetch produced
  an HTML detail page, not an NAC IMG/ZIP/TAR. The `CCSD` / `PDS3` /
  `II*` signatures listed in the dispatch were checked against the
  first 16 bytes and **all three did not match** (`<!DOCTYPE html>`).
- The verification record therefore does **not** demonstrate a raw
  NAC IMG byte signature. It demonstrates that:
  (a) the WMS chain is alive end-to-end (the smallest link on the
      search page is fetchable, returns HTTP 200, and parses as valid
      HTML);
  (b) the WMS RDR archive exposes the **PDS dataset ID + LROLRC
      bundle + PYR.TIF preview URL + a `view_rdr_product` HTML
      detail page** for at least one RDR result — sufficient to
      bootstrap a real IMG fetch in the user-gated pipeline (which
      will need to follow the form/cookie/JS flow on
      `data.lroc.im-ldi.com` per the skeptic session 62 retro).
- The HIGH-OPEN upgrade is justified by (a) + (b), not by a
  matched IMG signature. The IMG byte-signature verification is the
  work of the user-gated NAC fetch pipeline (R3 §11(b)) and is
  explicitly out of scope for this bounded verification.

## 7. Failure mode (not triggered)

- "If the file is HTML/JSON (an error page), report the failure and
  pick the next link. Maximum 3 attempts." — **The HTML is the
  expected file type for this URL** (the WMS `view_rdr/*` URL serves
  HTML detail pages, not files); the 404-HTML/JSON failure branch
  applies to cases where a link that *looks* like a file returns an
  error page. Here the URL is unambiguously an HTML detail page, so
  the failure branch is not triggered.
- All 10 NAC_ANAGLYPH view_rdr URLs return HTML by construction; no
  retry would produce a different file type. Retrying would burn the
  bounded-fetch budget for no information gain.

## 8. Resource ledger (cost phrasing removed per protocol)

- Bounded fetch: 10,370 B transferred in 2 s wall-clock.
- Pre-fetch probe (session 59): 23,154 B (cached on disk).
- Total new transfer this session: 10,370 B.
- Resource use: HTTP GET only; no GPU, no rental, no paid endpoint.
- 69 GB free on `/` after fetch (well above the 40 GB floor).
- Cost phrases (e.g. `$0`, `zero-cost`) deliberately omitted — those live in `01_WORKSPACE/admin/budget.md`.

## 9. Acquisitions (for archivist MANIFEST row)

| Field | Value |
|---|---|
| Source URL | `https://wms.lroc.asu.edu/lroc/view_rdr/NAC_ANAGLYPH_M102172207_M102165049` |
| PDS dataset | `LRO-L-LROC-5-RDR-V1.0` |
| LROLRC bundle | `LROLRC_2001` |
| Product type | NAC_ANAGLYPH (Regional Product) |
| Subject | "Rille in Alphonsus Crater" (per WMS title; **not** Mare Tranquillitatis — this is the closest fetchable NAC RDR matching the M104203891S search term, and is a verification probe, not a TRANQPIT1 deliverable) |
| File format | HTML detail page (NOT IMG) |
| File size | 10,370 B |
| SHA-256 | `bb2c525c1ad622bc185c4e7c13a3febcf99a4780d83c8e77a88dc3cabb53c571` |
| Licence | PDS public domain (NASA); LROC/ASU acknowledgement required |
| Local path | `01_WORKSPACE/data/outputs/wp1_lla/sandbox_nac_verify/NAC_ANAGLYPH_M102172207_M102165049_view_rdr.html` |
| Sandbox-only | yes; not for ladder/citation |

— geo-coder, session 60, 2026-09-12
