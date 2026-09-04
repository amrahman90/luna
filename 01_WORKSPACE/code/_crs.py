"""Shared CRS constants for LUNARVOID (C9 — Next-Level Plan v2).

Single source of truth for the two CRSes the project actually uses.
Replaces the Earth-EPSG literals (EPSG:4326 / EPSG:32631) that were
leaked into Moon lon/lat rasters (confusion_layer, evidence_layers)
and analog/UTM placeholders (vci, degrade, smoke_test).

Conventions reference: lunarvoid-conventions §3 — the Moon is a
R=1737400 m sphere; EPSG:4326 is the WGS84 Earth ellipsoid and MUST
NOT back a lunar lon/lat grid.
"""
from __future__ import annotations

from pyproj import CRS

# Moon geographic (planetocentric lon/lat on the R=1737400 m sphere)
MOON_CRS = CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")
MOON_CRS_WKT = MOON_CRS.to_wkt()

# Local-metric placeholder for terrestrial analog rasters whose site
# frame is metres (Indian Tunnel, Fieg, Kingsbowl, Sheepridge). Not a
# real Earth CRS — the affine transform carries the geometry. Used
# ONLY where the CRS field is syntactically required (GeoTIFF geokeys,
# rasterio.warp reproject with identical src/dst "CRS"); it preserves
# the prior EPSG:32631 behaviour without asserting a false UTM zone.
ANALOG_CRS = CRS.from_proj4("+proj=eqc +lat_ts=0 +lon_0=0 +x_0=0 +y_0=0 +R=6378137 +units=m +no_defs")
ANALOG_CRS_WKT = ANALOG_CRS.to_wkt()

if __name__ == "__main__":
    print("MOON_CRS:  ", MOON_CRS.to_proj4())
    print("ANALOG_CRS:", ANALOG_CRS.to_proj4())
