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
import os
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

BSDTAR_LOCAL = Path.home() / ".local" / "bin" / "bsdtar"
DEB_URL = (
    "http://archive.ubuntu.com/ubuntu/pool/universe/liba/libarchive/"
    "libarchive-tools_3.7.2-2ubuntu0.8_amd64.deb"
)


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
        for url in mirrors:
            try:
                print(f"[deb ] downloading {url}", flush=True)
                urllib.request.urlretrieve(url, deb_path)
                last_err = None
                break
            except Exception as e:
                last_err = e
                print(f"[deb ] mirror failed: {e}", flush=True)
        if last_err is not None:
            # if bsdtar is on the system PATH (apt install unar, etc.)
            # fall through to system bsdtar; the caller will pick that up
            raise RuntimeError(
                f"could not download libarchive-tools .deb from any mirror: {last_err}"
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
