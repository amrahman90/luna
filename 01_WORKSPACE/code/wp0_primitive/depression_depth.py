"""Depression-depth raster = sink_filled(DTM) - DTM (the CHM mirror, v5 S2).

Engine: Planchon & Darboux (2001) epsilon-gradient fill (WhiteboxTools
fill_depressions_planchon_and_darboux). Chosen over the Wang & Liu fill
after Task-3 acceptance testing on TRANQPIT1: the Mare Tranquillitatis
pit interior is mostly NoData (shadowed floor), and Wang & Liu
(fill_depressions) plus breach_depressions_least_cost both drain the pit
through the NoData gap (recovered depth 3.2 m / 0.3 m vs catalogued
~105 m). The PD epsilon fill ponds the interior floor pixels and
recovers 129.7 m. See 01_WORKSPACE/notes/ for the full variant log.
"""
import argparse
from pathlib import Path

import numpy as np
import rasterio
import whitebox


def depression_depth(dtm_path: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    filled_path = out_dir / (dtm_path.stem + "_filled.tif")
    depth_path = out_dir / (dtm_path.stem + "_depth.tif")

    import os, whitebox
    wbt = whitebox.WhiteboxTools()
    wbt_dir = os.path.join(os.path.dirname(whitebox.__file__))
    if os.path.isfile(os.path.join(wbt_dir, "whitebox_tools")):
        wbt.set_whitebox_dir(wbt_dir)
    import tempfile
    wbt.set_working_dir(tempfile.gettempdir())
    wbt.verbose = False
    wbt.fill_depressions_planchon_and_darboux(
        dem=str(dtm_path), output=str(filled_path), fix_flats=True
    )  # WhiteboxTools FillDepressionsPlanchonDarboux (epsilon fill)

    with rasterio.open(filled_path) as f, rasterio.open(dtm_path) as d:
        depth = f.read(1, masked=True) - d.read(1, masked=True)
        depth = np.ma.filled(np.maximum(depth, 0), d.nodata)
        profile = d.profile.copy()
        profile.update(dtype="float32", compress="deflate", nodata=d.nodata)
    with rasterio.open(depth_path, "w", **profile) as out:
        out.write(depth.astype("float32"), 1)
    return depth_path


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("dtm", type=Path)
    p.add_argument("outdir", type=Path)
    a = p.parse_args()
    print(depression_depth(a.dtm, a.outdir))
