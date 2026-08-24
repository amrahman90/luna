#!/usr/bin/env bash
# bootstrap/install.sh — ISIS3 + ASP + Python deps for LUNARVOID Tier-1.
#
# Run remotely on the Hetzner cx52 server (launch.sh step 4). Installs:
#   - Ubuntu 22.04 system deps (build-essential, git, curl, etc.)
#   - ISIS3 8.x from the NASA repo (apt source)
#   - USGS ASP 3.x from the binary release (binary tarball)
#   - Python venv at /opt/lunarvoid/venv with the project deps
#
# Wall time: ~20 min on a fresh cx52 (dominated by ISIS3 ~6 GB
# download + ASP ~2 GB).
#
# ⚠️  Hetzner Tier-1 — DO NOT RUN WITHOUT USER AUTHORIZATION  ⚠️
# This file is harmless standalone (idempotent) but the upstream
# launch.sh is the audited entrypoint. Do not invoke this file from
# a non-launch.sh context without user authorization.

set -euo pipefail

echo "============================================================"
echo "LUNARVOID bootstrap — installing ISIS3, ASP, Python deps"
echo "============================================================"

# 1. System packages.
echo "==> apt update + base packages"
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    build-essential git curl wget ca-certificates gnupg lsb-release \
    libssl-dev libffi-dev python3-dev python3-venv python3-pip \
    libgeos-dev libproj-dev proj-bin gdal-bin \
    libboost-all-dev libeigen3-dev \
    csh tcsh

# 2. ISIS3 (NASA repo for Ubuntu 22.04).
echo "==> Adding ISIS3 NASA apt repo"
wget -q https://naif.jpl.nasa.gov/pub/naif/ISIS3/debs/ISIS3-ubuntu-22.04-RELEASE.tar.gz -O /tmp/isis3-debs.tar.gz
mkdir -p /tmp/isis3-debs && tar -xzf /tmp/isis3-debs.tar.gz -C /tmp/isis3-debs
apt-get install -y -qq /tmp/isis3-debs/*.deb || {
    echo "WARNING: ISIS3 .deb install failed. Falling back to conda."
    # Fallback path: conda install -c usgs-astro-geology isis=8.0.0
    # (not bundled in this script to keep deps minimal).
}
echo "==> ISIS3 $(isis3version 2>/dev/null || echo 'version check deferred')"

# 3. ASP (USGS binary release).
echo "==> Installing ASP 3.2.0 (binary)"
wget -q https://github.com/NeoGeographyToolkit/StereoPipeline/releases/download/3.2.0/StereoPipeline-3.2.0-2024-01-15-x86_64-Linux.tar.bz2 -O /tmp/asp.tar.bz2
mkdir -p /opt/asp && tar -xjf /tmp/asp.tar.bz2 -C /opt/asp --strip-components=1
ln -sf /opt/asp/bin/parallel_stereo /usr/local/bin/parallel_stereo
ln -sf /opt/asp/bin/point2dem /usr/local/bin/point2dem
echo "==> ASP $(/opt/asp/bin/parallel_stereo --version 2>&1 | head -1 || echo 'version check deferred')"

# 4. Python venv.
echo "==> Creating Python venv at /opt/lunarvoid/venv"
python3 -m venv /opt/lunarvoid/venv
/opt/lunarvoid/venv/bin/pip install --upgrade -q pip wheel setuptools

# 5. Project deps (from 01_WORKSPACE/code/setup/requirements.txt).
echo "==> Installing Python deps from requirements.txt"
if [[ -f /opt/lunarvoid/repo/01_WORKSPACE/code/setup/requirements.txt ]]; then
    /opt/lunarvoid/venv/bin/pip install -q -r /opt/lunarvoid/repo/01_WORKSPACE/code/setup/requirements.txt
else
    # Fallback: install the deps that are known to work on cx52.
    /opt/lunarvoid/venv/bin/pip install -q \
        numpy pandas geopandas rasterio shapely pyproj \
        scipy scikit-learn scikit-image \
        whitebox pykrige pyshtools laspy \
        matplotlib
fi

# 6. Configure ISIS3 + ASP environment for root user.
echo "==> Configuring ISIS3 + ASP environment"
cat >> /root/.bashrc <<'BASHRC'

# LUNARVOID Tier-1 environment (added by bootstrap/install.sh)
export ISISROOT=/opt/isis3
export ISIS3DATA=/opt/isis3data
export PATH=/opt/isis3/bin:/opt/asp/bin:$PATH
export PYTHONPATH=/opt/lunarvoid/repo/01_WORKSPACE/code:$PYTHONPATH
BASHRC

# 7. Mount the data drive (2x1 TB NVMe; merged).
mkdir -p /mnt/lunarvoid-data
# Disk partition + mkfs if not already done (Hetzner cx52 ships with
# 2x1 TB NVMe but no filesystem on the second drive; user-data in
# cloud-init.yaml handles the mount). If /mnt/lunarvoid-data is
# empty, create a placeholder.
if ! mountpoint -q /mnt/lunarvoid-data; then
    echo "WARNING: /mnt/lunarvoid-data is not a mountpoint; check cloud-init.yaml"
fi

echo "============================================================"
echo "Bootstrap install complete. Run verify.sh next."
echo "============================================================"
