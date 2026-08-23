#!/usr/bin/env python3
"""Parallel HTTP range-download script for PDS Geosciences files.

Usage: parallel_range_download.py URL OUTPUT [--chunks N]
"""
from __future__ import annotations
import argparse
import hashlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import urlopen, Request


def fetch_range_to_file(url: str, start: int, end: int, fh, retries: int = 5) -> int:
    """Stream bytes [start, end] inclusive to file handle fh, returns bytes written."""
    last_err = None
    for attempt in range(retries):
        try:
            req = Request(url, headers={"Range": f"bytes={start}-{end}"})
            with urlopen(req, timeout=300) as resp:
                fh.seek(start)
                written = 0
                while written < end - start + 1:
                    chunk = resp.read(1 << 20)  # 1 MB
                    if not chunk:
                        break
                    fh.write(chunk)
                    written += len(chunk)
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
    req = Request(url, method="HEAD")
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

    # Use sparse file: preallocate
    with open(out, "wb") as f:
        f.truncate(size)

    t0 = time.time()
    done_bytes = 0

    def worker(idx_s_e):
        idx, s, e = idx_s_e
        with open(out, "r+b") as fh:
            n = fetch_range_to_file(args.url, s, e, fh)
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
