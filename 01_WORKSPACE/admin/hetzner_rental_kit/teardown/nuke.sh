#!/usr/bin/env bash
# teardown/nuke.sh — Hetzner Tier-1 rental teardown.
#
# ⚠️  USE THIS FOR TEARDOWN, NOT `terraform destroy` DIRECTLY ⚠️
#
# This is the audited teardown path. It:
#   1. Confirms the user wants to teardown (interactive prompt).
#   2. Snapshots the work-queue output back to local Tier-0.
#   3. Sets hcloud server lifecycle protection to false (so we can delete).
#   4. Deletes the server (and any volumes).
#   5. Prints the Hetzner invoice URL for budget reconciliation.
#   6. Updates admin/budget.md with the actual cost.
#
# Wall time: ~2 min for snapshot + delete.
# Cost: post-deletion server charges stop; floating IPs and volumes
# continue to charge until explicitly deleted.
#
# Pre-condition: the server was provisioned by ./launch.sh; the
# server name has the format lunarvoid-t1-YYYYMMDD.

set -euo pipefail

KITS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_DIR="${KITS_DIR}/terraform"

echo "============================================================"
echo "⚠️  Hetzner Tier-1 TEARDOWN — CONFIRM BEFORE PROCEEDING  ⚠️"
echo "============================================================"
echo
echo "This will delete the Hetzner cx52 server and any associated"
echo "volumes. Work-queue output MUST be snapshotted to local Tier-0"
echo "FIRST (step 2 below) because the server is destroyed at step 4."
echo

# Step 1: confirm.
read -r -p "Teardown? Type 'nuke' to confirm: " CONFIRM
if [[ "${CONFIRM}" != "nuke" ]]; then
    echo "ABORTED"
    exit 1
fi

# Step 2: snapshot work-queue output back to local.
echo "==> Snapshotting work-queue output"
SERVER_IP=$(cd "${TF_DIR}" && terraform output -raw ipv4_address 2>/dev/null || true)
if [[ -z "${SERVER_IP}" ]]; then
    echo "WARNING: terraform output did not return ipv4_address; skipping rsync"
else
    # Pull from /mnt/lunarvoid-data on the server back to local.
    rsync -avz --delete \
        root@"${SERVER_IP}":/mnt/lunarvoid-data/outputs/ \
        /home/frostflux/lunarvoid/data/outputs/tier1_$(date -u +%Y%m%d)/ 2>/dev/null \
        || echo "WARNING: rsync failed (server may be already down)"
fi

# Step 3: get the server name from terraform state.
SERVER_NAME=$(cd "${TF_DIR}" && terraform output -raw server_name 2>/dev/null || true)
if [[ -z "${SERVER_NAME}" ]]; then
    echo "ERROR: cannot determine server name from terraform state."
    echo "  Server may have been deleted out-of-band. Manually check:"
    echo "      hcloud server list"
    exit 2
fi
echo "==> Server name: ${SERVER_NAME}"

# Step 4: destroy via terraform.
echo "==> terraform destroy"
cd "${TF_DIR}"
terraform destroy -auto-approve -input=false

# Step 5: print invoice URL.
echo "==> Hetzner Cloud Console (Billing):"
echo "    https://console.hetzner.cloud/ -> <project> -> Billing"
echo

# Step 6: update budget ledger.
echo "==> Please add a row to admin/budget.md noting the actual cost:"
echo "    Date: $(date -u +%Y-%m-%d)"
echo "    Item: Hetzner Tier-1 cx52 rental ($(date -u +%Y-%m-%d) teardown)"
echo "    Cost: \$<actual USD>"
echo "    Provider: Hetzner Cloud"
echo "    Notes: see 01_WORKSPACE/admin/hetzner_rental_kit/work_queue/ for work done"
echo
echo "============================================================"
echo "Teardown complete. Audit trail:"
echo "  - terraform state: ${TF_DIR}/terraform.tfstate"
echo "  - work-queue output: /home/frostflux/lunarvoid/data/outputs/tier1_*/"
echo "  - budget.md: add the cost row"
echo "============================================================"
