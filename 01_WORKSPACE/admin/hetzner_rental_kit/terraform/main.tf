# terraform/main.tf — Hetzner Cloud cx52 server definition.
#
# ⚠️  DO NOT RUN WITHOUT USER AUTHORIZATION  ⚠️
#
# Provisions a single cx52 server (24 vCPU AMD EPYC, 128 GB DDR4 ECC,
# 2x1 TB NVMe) running Ubuntu 22.04 LTS for the LUNARVOID Tier-1
# burst cycle. Cost: ~$55/month (verify in Hetzner Cloud Console).
#
# Trigger: v5 Master Plan §8 T1; user-approved 2026-08-22 (D2, $150
# ceiling). See ../README.md and ../launch.sh.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.45"
    }
  }
}

provider "hcloud" {
  # Token read from ~/.config/hcloud/cli.toml via hcloud context.
  # NEVER hard-code the token here. Do not commit cli.toml either.
}

# ----- Data sources -----

data "hcloud_ssh_key" "lunarvoid" {
  # The SSH keypair uploaded to the Hetzner project. Required for
  # the server to be reachable on port 22 post-provisioning.
  # Upload via `hcloud ssh-key create --name lunarvoid --public-key \
  #   ~/.ssh/lunarvoid.pub`
  name = "lunarvoid"
}

data "hcloud_image" "ubuntu_2204" {
  with_architecture = "x86"
  most_recent       = true
  name              = "ubuntu-22.04"
}

# ----- Primary compute server -----
#
# Note on server_type: "cx52" provides 24 vCPU / 128 GB RAM / 2 NVMe
# (Hetzner folds the 2x1 TB NVMe into the server's local storage;
# no separate volume is needed). If storage_layout = "split" (set in
# variables.tf), the 2 NVMe are visible as separate mount points;
# otherwise they appear as one filesystem.

resource "hcloud_server" "lunarvoid_t1" {
  name               = "lunarvoid-t1-${formatdate("YYYYMMDD", timestamp())}"
  image              = data.hcloud_image.ubuntu_2204.id
  server_type        = var.server_type
  location           = var.location
  ssh_keys           = [data.hcloud_ssh_key.lunarvoid.id]
  user_data          = file("${path.module}/cloud-init.yaml")
  labels = {
    project     = "lunarvoid"
    environment = "tier-1"
    budget      = "d2-150usd"
    trigger     = "v5-s8-t1"
  }

  # Lifecycle: protect against accidental destroy from the CLI.
  # To teardown, run ../teardown/nuke.sh which sets the protection
  # to false before running `hcloud server delete`.
  lifecycle {
    prevent_destroy = false  # set to true after a successful test launch
  }
}

# ----- Outputs -----

output "server_name" {
  description = "The server name (used by teardown/nuke.sh)."
  value       = hcloud_server.lunarvoid_t1.name
}

output "ipv4_address" {
  description = "Public IPv4 address; SSH target post-launch."
  value       = hcloud_server.lunarvoid_t1.ipv4_address
}

output "server_type" {
  description = "The Hetzner server type (cx52 by default)."
  value       = hcloud_server.lunarvoid_t1.server_type
}

output "datacenter" {
  description = "The Hetzner datacenter location."
  value       = hcloud_server.lunarvoid_t1.datacenter
}
