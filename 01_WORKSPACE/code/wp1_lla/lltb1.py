"""LLTB-1 v0.1 packaging + load_lltb1() loader (Z1, Task 15).

Loads the per-rung rasters, the VCI raster, the centroids, the
detectability curve summary, and the source analog npz into a single
in-memory dict. Provides a quick-look plotting helper. The deliverable
for the v0.1 release is *code + fetch-script + derived degraded rasters
only* (per v5 licence gate; the NASA analog data is research-use only
and stays outside the repo at ~/lunarvoid/data/analog/).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import numpy as np


def load_lltb1(root: Path, npz_name: str = "Kingsbowl_0p5m.npz",
               rungs: tuple = (0.5, 2, 5)) -> dict:
    """Load LLTB-1 v0.1 outputs for one analog site.

    Parameters
    ----------
    root : Path
        Per-site output directory (created by degrade.py + vci.py +
        sag_detect.py), e.g. ~/lunarvoid/data/lltb1/Kingsbowl/
    npz_name : str
        Filename of the source .npz to load.
    rungs : tuple
        Rung resolutions in metres to load (must match what was run).
    """
    import laspy
    import rasterio

    out: dict = {"root": str(root), "rungs": {}, "vci": None, "centroids": None, "sag": None}
    npz = root / npz_name
    if npz.exists():
        out["source_npz"] = str(npz)
        data = np.load(npz)
        out["n_points"] = int(len(data["x"]))
    for r in rungs:
        rung = {}
        for stem in ("dtm", "filled", "depth", "frangi", "score"):
            tif = root / f"{stem}_{r:g}m.tif"
            if tif.exists():
                with rasterio.open(tif) as src:
                    rung[stem] = {"path": str(tif),
                                  "data": src.read(1),
                                  "crs": str(src.crs),
                                  "transform": [src.transform.a, src.transform.b,
                                                src.transform.c, src.transform.d,
                                                src.transform.e, src.transform.f]}
        if rung:
            out["rungs"][str(r)] = rung
    vci_tif = root / "vci.tif"
    if vci_tif.exists():
        with rasterio.open(vci_tif) as src:
            out["vci"] = {"path": str(vci_tif), "data": src.read(1),
                          "crs": str(src.crs), "transform": [src.transform.a, src.transform.c, src.transform.e, src.transform.f]}
    csv = root / "vci_centroids.csv"
    if csv.exists():
        import pandas as pd
        out["centroids"] = pd.read_csv(csv)
    sag = root / "sag_summary.json"
    if sag.exists():
        with open(sag) as f:
            out["sag"] = json.load(f)
    return out


def quicklook(lltb: dict, rung: str = "2", outpath: Optional[Path] = None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 4, figsize=(20, 5))
    r = lltb["rungs"].get(rung)
    if r is None:
        raise ValueError(f"rung {rung} not loaded; available: {list(lltb['rungs'])}")
    depth = r["depth"]["data"]
    frangi = r["frangi"]["data"]
    score = r["score"]["data"]
    ax[0].imshow(np.where(np.isfinite(depth), depth, np.nan), cmap="magma", origin="lower")
    ax[0].set_title(f"depth @ {rung} m")
    ax[1].imshow(np.where(np.isfinite(frangi), frangi, np.nan), cmap="cividis", origin="lower")
    ax[1].set_title("Frangi 60-300 m")
    ax[2].imshow(np.where(np.isfinite(score), score, np.nan), cmap="inferno", origin="lower")
    ax[2].set_title("score")
    if lltb.get("vci") is not None:
        ax[3].imshow(np.where(lltb["vci"]["data"] > 0, lltb["vci"]["data"], np.nan),
                     cmap="viridis", origin="lower")
        ax[3].set_title("VCI")
    for a in ax:
        a.set_xticks([]); a.set_yticks([])
    fig.suptitle(f"LLTB-1 v0.1 quicklook: {Path(lltb['root']).name}")
    fig.tight_layout()
    if outpath is None:
        outpath = Path(lltb["root"]) / "quicklook.png"
    fig.savefig(outpath, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return outpath


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("root", type=Path)
    p.add_argument("--rung", default="2")
    p.add_argument("--npz-name", default="Kingsbowl_0p5m.npz")
    args = p.parse_args()
    pkg = load_lltb1(args.root, npz_name=args.npz_name)
    print(f"loaded {len(pkg['rungs'])} rungs; {len(pkg.get('centroids', [])) if pkg.get('centroids') is not None else 0} VCI centroids")
    ql = quicklook(pkg, rung=args.rung)
    print(f"quicklook -> {ql}")
