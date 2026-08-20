"""LLTB-1 v0.1 end-to-end driver (Z1, Task 15.3).

Runs the full chain for a single analog site (assumes the RAR archive
is already extracted into a directory of .f32 files):

  1. convert_f32.py   (.f32 -> .npz + summary JSON)
  2. degrade.py        (.npz -> GSD ladder rungs)
  3. vci.py            (.npz -> VCI raster + centroids)
  4. sag_detect.py     (.npz + rungs -> score + detectability curve)

Then load_lltb1() + quicklook() produce the v0.1 deliverable.

Usage:
  python run_lltb1.py --site Kingsbowl \
                      --f32-dir ~/lunarvoid/data/analog/extracted/Kingsbowl \
                      --outdir ~/lunarvoid/data/lltb1/Kingsbowl \
                      [--rungs 0.5 2 5]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def run_module(module: str, args: list[str]) -> int:
    cmd = [sys.executable, str(REPO / "01_WORKSPACE" / "code" / module), *args]
    print(f"\n>>> {' '.join(cmd)}\n", flush=True)
    return subprocess.call(cmd)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--site", required=True, help="site name (used for output dir naming)")
    p.add_argument("--f32-dir", type=Path, required=True,
                   help="directory containing the extracted .f32 files")
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--rungs", type=float, nargs="+", default=[0.5, 2, 5])
    p.add_argument("--grid-spacing", type=float, default=0.5)
    p.add_argument("--f32-name", default=None,
                   help="specific .f32 file to use (default: smallest one in --f32-dir)")
    args = p.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    # 1. pick the .f32
    f32s = sorted(args.f32_dir.glob("*.f32"))
    if not f32s:
        raise SystemExit(f"no .f32 files in {args.f32_dir}")
    f32 = args.f32_name or str(f32s[0])
    if not Path(f32).exists():
        f32 = str(f32s[0])
    print(f"[site] using {f32}", flush=True)

    # 2. convert to .npz
    npz = args.outdir / f"{args.site}_{args.grid_spacing:g}m.npz"
    rc = run_module("wp1_lla/convert_f32.py",
                    ["--f32", f32, "--out", str(npz), "--site", args.site])
    if rc != 0:
        raise SystemExit(f"convert_f32 failed (rc={rc})")
    if not npz.exists():
        # fallback: writer may have used .npz extension via out; check
        if (args.outdir / f"{args.site}_{args.grid_spacing:g}m.npz").exists():
            pass
        else:
            raise SystemExit(f"convert_f32 did not produce {npz}")

    # 3. degradation ladder
    rc = run_module("wp1_ladder/degrade.py",
                    ["--npz", str(npz), "--outdir", str(args.outdir / "ladder"),
                     "--rungs", *[str(r) for r in args.rungs],
                     "--grid-spacing", str(args.grid_spacing)])
    if rc != 0:
        raise SystemExit(f"degrade failed (rc={rc})")

    # 4. VCI on the source cloud
    rc = run_module("wp1_detector/vci.py",
                    ["--npz", str(npz), "--outdir", str(args.outdir / "vci"),
                     "--pixel", str(args.grid_spacing),
                     "--h-min", "0.5", "--h-max", "30.0", "--h-bin", str(args.grid_spacing),
                     "--threshold", "0.4", "--name", args.site])
    if rc != 0:
        raise SystemExit(f"vci failed (rc={rc})")

    # 5. sag detection per rung
    rc = run_module("wp1_detector/sag_detect.py",
                    ["--npz", str(npz), "--outdir", str(args.outdir / "sag"),
                     "--rungs", *[str(r) for r in args.rungs],
                     "--grid-spacing", str(args.grid_spacing)])
    if rc != 0:
        print(f"[warn] sag_detect rc={rc}; continuing", flush=True)

    # 6. v0.1 quicklook
    rc = run_module("wp1_lla/lltb1.py",
                    ["str(args.outdir)", "--rung", str(args.rungs[len(args.rungs) // 2]),
                     "--npz-name", str(npz.name)])
    if rc != 0:
        print(f"[warn] quicklook rc={rc}; continuing", flush=True)

    # final summary
    summary_path = args.outdir / "v01_summary.json"
    summary = {
        "site": args.site,
        "source_f32": str(f32),
        "npz": str(npz),
        "outdir": str(args.outdir),
        "rungs": list(args.rungs),
        "stages": ["convert_f32", "degrade", "vci", "sag_detect", "quicklook"],
    }
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[done] LLTB-1 v0.1 for {args.site}; summary -> {summary_path}", flush=True)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
