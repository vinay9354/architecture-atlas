output "zone_cidrs" {
  description = "Zone summary block per zone, for example { a = \"10.10.0.0/18\" }."
  value       = local.zone_cidrs

  precondition {
    condition     = local.zones_fit
    error_message = "More zones than zone blocks: ${length(var.zones)} zones need at least ${length(var.zones)} slots, but zone_newbits = ${var.zone_newbits} gives ${local.zone_slots}. Increase zone_newbits."
  }
}

output "subnets" {
  description = "Subnet CIDR per zone and tier, for example subnets[\"a\"][\"public\"]."
  value       = local.subnets

  precondition {
    condition     = local.tiers_fit
    error_message = "A tier does not fit inside a /${local.zone_prefix} zone block: its prefix_length must be longer than ${local.zone_prefix} and its index small enough for the block to end inside the zone."
  }
}

output "subnets_flat" {
  description = "The same subnets keyed \"zone/tier\", convenient for for_each on subnet resources."
  value = merge([
    for zone, tiers in local.subnets : { for tier, cidr in tiers : "${zone}/${tier}" => cidr }
  ]...)
}

output "reserved_zone_cidrs" {
  description = "Zone-sized blocks of the supernet left unassigned for a future zone or region."
  value       = local.reserved_zone_cidrs
}
