#!/usr/bin/env bash
# launch.sh — Hetzner Cloud rental launcher for LUNARVOID Tier-1 burst.
#
# ⚠️  DO NOT RUN WITHOUT USER AUTHORIZATION  ⚠️
#
# This script provisions a Hetzner Cloud cx52 server (24 vCPU, 128 GB
# RAM, 2x1 TB NVMe) and bootstraps the LUNARVOID pipeline environment
# (ISIS3, ASP, Python deps). It will incur real-world cost (~$55/month
# for the cx52; $150 ceiling covers 2 months max).
#
# MANDATORY pre-launch checklist (see README.md):
#   1. User has explicitly said "launch the Hetzner rental" in chat.
#   2. Approval is logged in admin/budget.md.
#   3. ~/.config/hcloud/cli.toml is configured (hcloud context).
#   4. SSH keypair uploaded to the Hetzner project.
#
# Usage:   ./launch.sh
# Outputs: server IP, SSH command, first work-queue task.
# Cost:    see $150 ceiling guard below.

set -euo pipefail

KITS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="${KITS_DIR}/terraform"

echo "============================================================"
echo "⚠️  Hetzner Tier-1 launch — USER AUTHORIZATION REQUIRED  ⚠️"
echo "============================================================"
echo
echo "This will provision a cx52 server (~\$55/month) and run"
echo "bootstrap (ISIS3 + ASP download, ~20 min)."
echo
echo "Pre-launch checklist (ALL FOUR must be true):"
echo "  [ ] User has explicitly authorized in chat."
echo "  [ ] Approval row logged in admin/budget.md."
echo "  [ ] hcloud CLI authenticated (hcloud context list)."
echo "  [ ] SSH keypair uploaded to Hetzner project."
echo

# Guard 1: explicit user authorization token. The user must set this
# environment variable before running launch.sh. The default is "NO".
if [[ "${LV_LAUNCH_AUTHORIZED:-NO}" != "YES" ]]; then
    echo "ABORTED: LV_LAUNCH_AUTHORIZED != YES"
    echo "  Set this environment variable ONLY after the user has"
    echo "  explicitly authorized the launch in chat:"
    echo "      export LV_LAUNCH_AUTHORIZED=YES"
    echo "  Then re-run ./launch.sh."
    exit 1
fi

# Guard 2: cost ceiling. Read from variables.tf default and project
# the worst-case cost (assume 2 months = max under ceiling).
MONTHLY_USD=55
PROJECTED_MONTHS=2
TOTAL_USD=$((MONTHLY_USD * PROJECTED_MONTHS))
if (( TOTAL_USD > 150 )); then
    echo "ABORTED: projected cost \$${TOTAL_USD} exceeds \$150 ceiling"
    echo "  Adjust terraform/variables.tf::projected_rental_months to <=2"
    exit 1
fi
echo "Cost projection: \$${TOTAL_USD} (\$${MONTHLY_USD}/month × ${PROJECTED_MONTHS} months) — under \$150 ceiling."

# Guard 3: explicit confirmation prompt.
read -r -p "Proceed with terraform apply? [yes/NO] " CONFIRM
if [[ "${CONFIRM}" != "yes" ]]; then
    echo "ABORTED by user"
    exit 1
fi

# Step 1: terraform init + apply.
cd "${TF_DIR}"
echo "==> terraform init"
terraform init -input=false
echo "==> terraform apply (auto-approve)"
terraform apply -auto-approve -input=false

# Step 2: extract server IP from terraform output.
SERVER_IP=$(terraform output -raw ipv4_address 2>/dev/null || true)
if [[ -z "${SERVER_IP}" ]]; then
    echo "ERROR: terraform output did not return ipv4_address"
    echo "  Run: terraform output to debug"
    exit 1
fi
echo "==> Server IP: ${SERVER_IP}"

# Step 3: wait for SSH to come up (server reboot post-cloud-init can
# take 1-3 min on a fresh image).
echo "==> Waiting for SSH (up to 3 min)..."
for i in $(seq 1 60); do
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@"${SERVER_IP}" "echo ok" 2>/dev/null; then
        echo "==> SSH up after ${i} attempts"
        break
    fi
    sleep 3
done

# Step 4: bootstrap (install ISIS3, ASP, Python deps).
echo "==> Running bootstrap/install.sh"
ssh -o StrictHostKeyChecking=no root@"${SERVER_IP}" "bash -s" < "${KITS_DIR}/bootstrap/install.sh"

# Step 5: verify.
echo "==> Running bootstrap/verify.sh"
ssh -o StrictHostKeyChecking=no root@"${SERVER_IP}" "bash -s" < "${KITS_DIR}/bootstrap/verify.sh"

# Step 6: hand off to the work queue.
cat <<HANDOFF

============================================================
Hetzner Tier-1 rental is UP at ${SERVER_IP}.
============================================================

SSH:        ssh root@${SERVER_IP}
Work queue: ${KITS_DIR}/work_queue/00_pds_retry.md (start here)

When done, teardown with: ${KITS_DIR}/teardown/nuke.sh
HANDOFF
