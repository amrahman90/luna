# terraform/variables.tf — Hetzner rental variables + $150 ceiling guard.
#
# ⚠️  DO NOT RUN WITHOUT USER AUTHORIZATION  ⚠️
#
# Trigger: v5 Master Plan §8 T1; user-approved 2026-08-22 (D2).
# See ../README.md and ../launch.sh.

# ----- Cost ceiling guard -----
#
# The user-set cost ceiling is $150 (D2, 2026-08-22, ~$55/month).
# Three-month projections exceed this and are rejected by the
# launch.sh script before terraform apply. Adjusting this variable
# below 2 requires re-approval in admin/budget.md.

variable "cost_ceiling_usd" {
  description = "Hard cost ceiling in USD for the Tier-1 rental cycle."
  type        = number
  default     = 150  # user-set 2026-08-22; do NOT lower without re-approval
}

variable "projected_rental_months" {
  description = "How many months the rental is expected to run. Must keep total <= cost_ceiling_usd."
  type        = number
  default     = 2  # $55/month × 2 = $110; under $150 ceiling

  validation {
    condition     = var.projected_rental_months >= 1 && var.projected_rental_months <= 2
    error_message = "projected_rental_months must be 1 or 2 (3+ exceeds the $150 ceiling at $55/month)."
  }
}

# ----- Server specification -----

variable "server_type" {
  description = "Hetzner Cloud server type. cx52 = 24 vCPU, 128 GB RAM, 2x1 TB NVMe."
  type        = string
  default     = "cx52"
}

variable "location" {
  description = "Hetzner datacenter location. nbg1 (Nuremberg) is cheapest; fsn1 (Falkenstein) is alternative."
  type        = string
  default     = "nbg1"
}

variable "storage_layout" {
  description = "Storage layout. 'merged' = single filesystem on 2x1 TB NVMe (default); 'split' = separate mount points (manual LVM). The DTM scratch volume at /mnt/lunarvoid-data expects 'merged'."
  type        = string
  default     = "merged"

  validation {
    condition     = contains(["merged", "split"], var.storage_layout)
    error_message = "storage_layout must be 'merged' or 'split'."
  }
}

# ----- Cost projection -----

locals {
  # cx52 monthly cost (Hetzner Cloud Console public pricing, 2026-Q3).
  # Verify at https://www.hetzner.com/cloud before launch.
  monthly_cost_usd = 55

  # Worst-case cost over the rental cycle. Used by launch.sh to abort
  # if it exceeds the user-set ceiling.
  projected_cost_usd = local.monthly_cost_usd * var.projected_rental_months
}

output "cost_projection" {
  description = "Projected total cost in USD. Must be <= var.cost_ceiling_usd."
  value = {
    monthly_usd    = local.monthly_cost_usd
    months         = var.projected_rental_months
    total_usd      = local.projected_cost_usd
    ceiling_usd    = var.cost_ceiling_usd
    under_ceiling  = local.projected_cost_usd <= var.cost_ceiling_usd
  }
}
