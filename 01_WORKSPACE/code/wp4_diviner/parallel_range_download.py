#!/usr/bin/env python3
"""Parallel HTTP range-download script for PDS Geosciences files.

Usage: parallel_range_download.py URL OUTPUT [--chunks N]

Concurrency note (C15-2): each chunk is written via
`os.pwrite(fd, buf, offset)` which is POSIX-atomic per call
(up to filesystem limits), avoiding the seek/write interleaving
that the earlier `fh.seek + fh.write` pattern allowed on
NFS / shared storage. Sequential runs of the chunks
still work fine; this only matters under real parallelism
on NFS-class storage.
"""
from __future__ import annotations
import argparse
import hashlib
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import urlopen, Request


def fetch_range_to_file(url: str, start: int, end: int, fd: int, retries: int = 5) -> int:
    """Stream bytes [start, end] inclusive to file descriptor fd at offset `start`.
    Returns bytes written.

    Uses os.pwrite for atomic per-call writes at the given offset;
    no seek, no interleaving window for concurrent threads.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "setup"))
    from _http import HEADERS as _HDRS  # C10: shared UA
    last_err = None
    for attempt in range(retries):
        try:
            req = Request(url, headers=_HDRS)
            req.add_header("Range", f"bytes={start}-{end}")
            with urlopen(req, timeout=300) as resp:
                written = 0
                while written < end - start + 1:
                    chunk = resp.read(1 << 20)  # 1 MB
                    if not chunk:
                        break
                    n = os.pwrite(fd, chunk, start + written)
                    written += n
                if written != end - start + 1:
                    raise RuntimeError(
                        f"short read: {written} of {end - start + 1} bytes"
                    )
                return written
        except Exception as e:
            last_err = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"failed after {retries} retries: {last_err}")


def head_size(url: str) -> int:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "setup"))
    from _http import HEADERS as _HDRS  # C10: shared UA
    req = Request(url, method="HEAD", headers=_HDRS)
    with urlopen(req, timeout=60) as resp:
        return int(resp.headers["Content-Length"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("output")
    ap.add_argument("--chunks", type=int, default=4)
    ap.add_argument("--max-workers", type=int, default=4)
    ap.add_argument("--sha256-out", default=None)
    args = ap.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    size = head_size(args.url)
    print(f"[info] {args.url}  size={size} bytes ({size / 1e9:.2f} GB)", flush=True)

    n_chunks = args.chunks
    chunk_size = (size + n_chunks - 1) // n_chunks
    ranges = []
    for i in range(n_chunks):
        s = i * chunk_size
        e = min(s + chunk_size - 1, size - 1)
        if s > e:
            break
        ranges.append((i, s, e))

    # Pre-allocate sparse file
    with open(out, "wb") as f:
        f.truncate(size)

    t0 = time.time()
    done_bytes = 0

    def worker(idx_s_e):
        idx, s, e = idx_s_e
        # Open with O_WRONLY; pwrite positions per call (no seek)
        fd = os.open(str(out), os.O_WRONLY)
        try:
            n = fetch_range_to_file(args.url, s, e, fd)
        finally:
            os.close(fd)
        return idx, s, n

    with ThreadPoolExecutor(max_workers=args.max_workers) as ex:
        futs = [ex.submit(worker, r) for r in ranges]
        for fut in as_completed(futs):
            idx, s, n = fut.result()
            done_bytes += n
            elapsed = time.time() - t0
            rate = done_bytes / elapsed / 1e6 if elapsed > 0 else 0
            eta = (size - done_bytes) / (done_bytes / elapsed) if done_bytes > 0 else 0
            pct = 100 * done_bytes / size
            print(f"[{idx+1}/{n_chunks}] chunk_done {n/1e6:.0f} MB "
                  f"total {pct:5.1f}% {done_bytes/1e6:.0f}/{size/1e6:.0f} MB "
                  f"{rate:.2f} MB/s eta {eta:.0f} s", flush=True)

    elapsed = time.time() - t0
    print(f"[done] {elapsed:.1f}s, {(size / elapsed / 1e6):.2f} MB/s aggregate", flush=True)

    # Verify SHA-256 of assembled file
    h = hashlib.sha256()
    with open(out, "rb") as f:
        while True:
            chunk = f.read(1 << 24)  # 16 MB
            if not chunk:
                break
            h.update(chunk)
    sha = h.hexdigest()
    print(f"[sha256] {sha}", flush=True)
    if args.sha256_out:
        Path(args.sha256_out).write_text(sha + "\n")


if __name__ == "__main__":
    sys.exit(main())
