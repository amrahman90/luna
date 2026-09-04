"""Shared HTTP helper for LUNARVOID (C10 — Next-Level Plan v2).

Single source-of-truth for politeness + UA across PDS, Wayback,
Zenodo, Brown, and GDS fetchers. Replaces the per-script urllib calls
that previously sent no UA header (SEC-01).

Public surface:
  UA          : user-agent string
  HEADERS     : standard headers dict
  urlopen_retry(url, ...) : urllib wrapper with polite UA + retry

Used by: retry_nac_edr_fetch.py, parallel_range_download.py, etc.
"""
from __future__ import annotations

import time
import urllib.error
import urllib.request
from typing import Iterable

# Identify the project; a contact email is included per polite-bot
# convention. Update the email if the operator changes.
UA = "lunarvoid/0.1 (+contact: muhammad.ahnaf.sarker@gmail.com)"
HEADERS = {"User-Agent": UA}


def urlopen_retry(
    url: str,
    *,
    max_retries: int = 3,
    backoff: float = 1.5,
    timeout: float = 60,
    headers: dict[str, str] | None = None,
):
    """Open `url` with our standard headers + retry on transient errors.

    Returns the urllib response. Caller is responsible for .read() /
    context-manager usage.

    Retries on 429 / 5xx with exponential backoff (factor `backoff`).
    Raises the last exception on persistent failure.
    """
    hdrs = dict(HEADERS)
    if headers:
        hdrs.update(headers)
    last_err: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            return urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code in (304, 400, 401, 403, 404):
                # client error — retrying won't help; surface immediately
                raise
            last_err = e
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last_err = e
        if attempt < max_retries:
            time.sleep(backoff ** attempt)
    raise last_err  # type: ignore[misc]
