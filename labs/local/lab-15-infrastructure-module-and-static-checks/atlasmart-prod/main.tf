# Root example: AtlasMart's production address plan, as documented on the page
# "Networking fundamentals: IP, CIDR, routing, and DNS" (worked example, Steps 2 and 3).
# AtlasMart is a fictional company; every value below is a documented course assumption.
#
#   prod virtual network   10.10.0.0/16
#   zone blocks            a 10.10.0.0/18, b 10.10.64.0/18, c 10.10.128.0/18, 10.10.192.0/18 reserved
#   inside each zone       public /22 at offset 0, private-app /20 at offset 16, private-data /22 at offset 32
#                          (third-octet offsets from the start of the zone block)

terraform {
  required_version = ">= 1.6.0"
}

module "prod_network_plan" {
  source = "../modules/network-plan"

  supernet_cidr = "10.10.0.0/16"
  zones         = ["a", "b", "c"]
  zone_newbits  = 2 # /16 + 2 bits = /18 per zone, four slots, three used

  tiers = {
    # index counts blocks of the tier's own size from the start of the zone block:
    # /22 blocks are 4 apart in the third octet, /20 blocks 16 apart.
    "public"       = { prefix_length = 22, index = 0 } # third octet +0
    "private-app"  = { prefix_length = 20, index = 1 } # third octet +16
    "private-data" = { prefix_length = 22, index = 8 } # third octet +32
  }
}

output "zone_cidrs" {
  description = "Zone summary blocks for AtlasMart prod."
  value       = module.prod_network_plan.zone_cidrs
}

output "subnets" {
  description = "AtlasMart prod subnets per zone and tier."
  value       = module.prod_network_plan.subnets
}

output "reserved_zone_cidrs" {
  description = "Unassigned zone blocks in the prod /16."
  value       = module.prod_network_plan.reserved_zone_cidrs
}
