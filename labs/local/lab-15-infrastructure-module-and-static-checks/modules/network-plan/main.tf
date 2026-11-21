locals {
  supernet_prefix = tonumber(split("/", var.supernet_cidr)[1])
  zone_prefix     = local.supernet_prefix + var.zone_newbits
  zone_slots      = pow(2, var.zone_newbits)
  zone_bytes      = pow(2, 32 - local.zone_prefix)

  # Guards checked by the output preconditions. The calculations below fall back to empty
  # results when a guard is false, so the learner sees the precondition's message rather than
  # a raw cidrsubnet() error.
  zones_fit = length(var.zones) <= local.zone_slots
  tiers_fit = alltrue([
    for t in var.tiers : (
      t.prefix_length > local.zone_prefix &&
      (t.index + 1) * pow(2, 32 - t.prefix_length) <= local.zone_bytes
    )
  ])
  plan_ok = local.zones_fit && local.tiers_fit

  # Zone i gets the i-th block of size /zone_prefix inside the supernet.
  # tomap() makes the outputs maps of strings rather than objects, so callers and tests can
  # compare them with map literals.
  zone_cidrs = local.plan_ok ? tomap({
    for i, zone in var.zones : zone => cidrsubnet(var.supernet_cidr, var.zone_newbits, i)
  }) : tomap({})

  # Every tier is carved from its zone block at the same relative offset, so zone b repeats
  # zone a's pattern shifted by one zone block, zone c by two, and so on.
  subnets = tomap({
    for zone, zone_cidr in local.zone_cidrs : zone => tomap({
      for tier, t in var.tiers : tier => cidrsubnet(zone_cidr, t.prefix_length - local.zone_prefix, t.index)
    })
  })

  # Zone blocks that exist in the supernet but are not assigned to a zone.
  reserved_zone_cidrs = local.plan_ok ? [
    for i in range(length(var.zones), local.zone_slots) : cidrsubnet(var.supernet_cidr, var.zone_newbits, i)
  ] : []
}
