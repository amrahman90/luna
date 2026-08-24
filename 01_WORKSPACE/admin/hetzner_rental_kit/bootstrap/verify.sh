#!/usr/bin/env bash
# bootstrap/verify.sh — post-install smoke test for LUNARVOID Tier-1.
#
# Run remotely on the Hetzner cx52 server (launch.sh step 5). Checks:
#   - ISIS3 version (isis3version command)
#   - ASP version (parallel_stereo --version)
#   - Python venv + numpy import
#   - Disk space on /mnt/lunarvoid-data
#
# Outputs: a JSON record to /opt/lunarvoid/data/admin/rental_versions.json
# for the audit trail. Pass criterion: every command exits 0.
#
# ⚠️  Hetzner Tier-1 — DO NOT RUN WITHOUT USER AUTHORIZATION  ⚠️

set -uo pipefail

RESULT_JSON=/opt/lunarvoid/data/admin/rental_versions.json
mkdir -p "$(dirname "${RESULT_JSON}")"
RESULTS=()

check() {
    local NAME="$1"; shift
    local CMD="$1"; shift
    local EXPECTED="$1"; shift
    local OUT
    OUT=$(${CMD} 2>&1) && EXIT=0 || EXIT=$?
    if [[ ${EXIT} -eq 0 && -n "${OUT}" ]]; then
        echo "PASS: ${NAME} -> ${OUT}" | head -1
        RESULTS+=("\"${NAME}\": \"${OUT//\"/\\\"}\"")
    else
        echo "FAIL: ${NAME} (exit=${EXIT}, output=${OUT:0:200})"
        RESULTS+=("\"${NAME}\": null")
    fi
}

echo "============================================================"
echo "LUNARVOID post-install verification"
echo "============================================================"

# ISIS3
check "isis3" "isis3version" "8."

# ASP
check "asp_parallel_stereo" "parallel_stereo --version" "3."

# Python + numpy
/opt/lunarvoid/venv/bin/python -c "import numpy; print('numpy', numpy.__version__)" \
    && RESULTS+=("\"numpy\": \"$(/opt/lunarvoid/venv/bin/python -c 'import numpy; print(numpy.__version__)')\"") \
    || RESULTS+=("\"numpy\": null")

# scipy
/opt/lunarvoid/venv/bin/python -c "import scipy; print('scipy', scipy.__version__)" \
    && RESULTS+=("\"scipy\": \"$(/opt/lunarvoid/venv/bin/python -c 'import scipy; print(scipy.__version__)')\"") \
    || RESULTS+=("\"scipy\": null")

# rasterio
/opt/lunarvoid/venv/bin/python -c "import rasterio; print('rasterio', rasterio.__version__)" \
    && RESULTS+=("\"rasterio\": \"$(/opt/lunarvoid/venv/bin/python -c 'import rasterio; print(rasterio.__version__)')\"") \
    || RESULTS+=("\"rasterio\": null")

# Disk space
DISK_FREE=$(df -BG /mnt/lunarvoid-data 2>/dev/null | awk 'NR==2 {print $4}' | tr -d 'G')
RESULTS+=("\"disk_free_gb\": \"${DISK_FREE:-unknown}\"")

# Total RAM
RAM_TOTAL=$(free -g | awk 'NR==2 {print $2}')
RESULTS+=("\"ram_total_gb\": \"${RAM_TOTAL}\"")

# CPU count
CPU_COUNT=$(nproc)
RESULTS+=("\"cpu_count\": \"${CPU_COUNT}\"")

# Write JSON.
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
{
    echo "{"
    echo "  \"timestamp_utc\": \"${TIMESTAMP}\","
    echo "  \"host\": \"$(hostname)\","
    for ((i = 0; i < ${#RESULTS[@]}; i++)); do
        if ((i < ${#RESULTS[@]} - 1)); then
            echo "  ${RESULTS[$i]},"
        else
            echo "  ${RESULTS[$i]}"
        fi
    done
    echo "}"
} > "${RESULT_JSON}"

echo "============================================================"
echo "Smoke test complete. JSON written to ${RESULT_JSON}"
echo "  cat ${RESULT_JSON}"
echo "============================================================"
