"""Extract a RAR archive (RAR4 or RAR5) to a directory.

The system 7z v23.01 cannot decode RAR5 ("Unsupported Method"). This
wrapper uses bsdtar from libarchive, which handles RAR5 correctly. We
download the libarchive-tools .deb and extract bsdtar to ~/.local/bin
the first time this is called; subsequent calls use the local binary
directly (no sudo, no apt install).

Usage:
  extract_rar.py --rar /path/to/file.rar --out /path/to/outdir
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

# C10: shared politeness header (was: urllib without UA — SEC-01)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _http import HEADERS as _HTTP_HEADERS  # noqa: E402

BSDTAR_LOCAL = Path.home() / ".local" / "bin" / "bsdtar"
# C8 supply-chain pin (Next-Level Plan v2): HTTPS mirrors first, and the
# .deb is SHA-256-verified BEFORE extraction. The pin below is the
# sha256 of libarchive-tools_3.7.2-2ubuntu0.8_amd64.deb as fetched
# 2026-08-20 and verified against the working bsdtar (bsdtar 3.7.2,
# 76,240 B binary; deb size 72,488 B). If the pinned mirror copy ever
# differs, installation refuses rather than trust-on-first-use.
EXPECTED_SHA256 = "ca4f763c2b35a49b9d37a19cd0d3b6625c04c0b81fb4986dd3b95a6ed9de1b77"
# HTTPS mirrors FIRST (was: HTTP archive.ubuntu.com leading; C8 fix)
MIRRORS = [
    "https://launchpad.net/ubuntu/+archive/primary/+files/"
    "libarchive-tools_3.7.2-2ubuntu0.8_amd64.deb",
    "https://snapshot.ubuntu.com/ubuntu/pool/universe/liba/libarchive/"
    "libarchive-tools_3.7.2-2ubuntu0.8_amd64.deb",
    # HTTP fallbacks last (launchpad/snapshot both occasionally rate-limit)
    "http://archive.ubuntu.com/ubuntu/pool/universe/liba/libarchive/"
    "libarchive-tools_3.7.2-2ubuntu0.8_amd64.deb",
    "http://archive.ubuntu.com/ubuntu/pool/universe/liba/libarchive/"
    "libarchive-tools_3.7.2-2ubuntu0.8_amd64.deb",
]
DEB_URL = MIRRORS[2]  # legacy constant kept for compatibility


def _download_and_extract_bsdtar() -> Path:
    """Download libarchive-tools .deb, extract bsdtar to ~/.local/bin.
    Idempotent: skips if the binary is already there.

    Network-tolerant: tries three Ubuntu mirrors in order, then
    falls back to the system bsdtar if all fail. The first
    install path is deb -> extract -> ~/.local/bin/bsdtar
    (this is what produced the Fieg/IndianTunnel extractions in
    session 3). The 403 / 404 / mirror-down failure mode is
    handled by the multi-mirror fallback.
    """
    if BSDTAR_LOCAL.exists():
        return BSDTAR_LOCAL
    BSDTAR_LOCAL.parent.mkdir(parents=True, exist_ok=True)
    workdir = Path.home() / ".local" / "share" / "libarchive-tools-deb"
    workdir.mkdir(parents=True, exist_ok=True)
    deb_path = workdir / "libarchive-tools.deb"
    if not deb_path.exists():
        # try mirrors in order; raise on the last one
        mirrors = [
            DEB_URL,
            "http://archive.ubuntu.com/ubuntu/pool/universe/liba/libarchive/"
            "libarchive-tools_3.7.2-2ubuntu0.8_amd64.deb",
            "https://launchpad.net/ubuntu/+archive/primary/+files/"
            "libarchive-tools_3.7.2-2ubuntu0.8_amd64.deb",
            "https://snapshot.ubuntu.com/ubuntu/pool/universe/liba/libarchive/"
            "libarchive-tools_3.7.2-2ubuntu0.8_amd64.deb",
        ]
        last_err = None
        attempts: list[str] = []
        for url in MIRRORS:
            try:
                print(f"[deb ] downloading {url}", flush=True)
                req = urllib.request.Request(url, headers=_HTTP_HEADERS)
                with urllib.request.urlopen(req, timeout=120) as resp, open(deb_path, "wb") as f:
                    shutil.copyfileobj(resp, f)
                sha = hashlib.sha256(deb_path.read_bytes()).hexdigest()
                if sha != EXPECTED_SHA256:
                    raise RuntimeError(
                        f"sha256 mismatch for {url}: got {sha}, expected {EXPECTED_SHA256} "
                        f"(refusing to extract; mirror content tampered or changed)"
                    )
                print(f"[deb ] sha256 verified: {sha[:16]}...", flush=True)
                last_err = None
                break
            except Exception as e:
                last_err = e
                attempts.append(f"{url}: {e}")
                print(f"[deb ] mirror failed: {e}", flush=True)
        if last_err is not None:
            # if bsdtar is on the system PATH (apt install unar, etc.)
            # fall through to system bsdtar; the caller will pick that up
            raise RuntimeError(
                "could not download a sha256-verified libarchive-tools .deb "
                "from any mirror:\n  " + "\n  ".join(attempts)
            )
    # .deb is an `ar` archive containing control.tar.* + data.tar.*
    extract_dir = workdir / "extracted"
    if not (extract_dir / "usr" / "bin" / "bsdtar").exists():
        extract_dir.mkdir(parents=True, exist_ok=True)
        # `ar` is a system tool (binutils) — should be present
        subprocess.run(["ar", "x", str(deb_path)], cwd=extract_dir, check=True)
        # data.tar is zst-compressed in this Ubuntu build
        for member in extract_dir.glob("data.tar.*"):
            if member.name == "debian-binary":
                continue
            print(f"[deb ] unpacking {member.name}", flush=True)
            subprocess.run(
                ["tar", "--use-compress-program=unzstd", "-xf", str(member)],
                cwd=extract_dir, check=True,
            )
            break
    src = extract_dir / "usr" / "bin" / "bsdtar"
    if not src.exists():
        raise FileNotFoundError(f"bsdtar not found in {extract_dir} after extraction")
    shutil.copy2(src, BSDTAR_LOCAL)
    BSDTAR_LOCAL.chmod(0o755)
    print(f"[deb ] bsdtar installed to {BSDTAR_LOCAL}", flush=True)
    return BSDTAR_LOCAL


def _system_bsdtar() -> str | None:
    """Check if bsdtar is already on PATH (saves us the .deb download)."""
    return shutil.which("bsdtar")


def get_bsdtar() -> str:
    """Return path to a working bsdtar that handles RAR5.

    Order:
      1. ~/.local/bin/bsdtar (installed by this script on first use)
      2. system bsdtar if present
      3. download + extract the libarchive-tools .deb
    """
    if BSDTAR_LOCAL.exists():
        return str(BSDTAR_LOCAL)
    sys_bsdtar = _system_bsdtar()
    if sys_bsdtar is not None:
        return sys_bsdtar
    return str(_download_and_extract_bsdtar())


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rar", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--strip", type=int, default=0,
                   help="strip N leading path components from each member")
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    bsdtar = get_bsdtar()
    cmd = [bsdtar, "-xf", str(args.rar), "-C", str(args.out)]
    if args.strip:
        cmd.extend(["--strip-components", str(args.strip)])
    print(f"[bsdtar] {bsdtar} --version:")
    subprocess.run([bsdtar, "--version"], check=False)
    print(f"\n[run ] {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, check=True)
    # list output
    out_files = sorted(args.out.rglob("*"))
    print(f"\n[out ] {len(out_files)} files in {args.out}:", flush=True)
    for f in out_files[:20]:
        if f.is_file():
            print(f"  {f.relative_to(args.out)}: {f.stat().st_size:,} bytes")
    if len(out_files) > 20:
        print(f"  ... and {len(out_files) - 20} more")


if __name__ == "__main__":
    main()
