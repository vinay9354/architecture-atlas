variable "supernet_cidr" {
  description = "IPv4 block for one environment's virtual network, for example 10.10.0.0/16. Must be a network address (no host bits set)."
  type        = string

  validation {
    condition     = can(regex("^[0-9]{1,3}(\\.[0-9]{1,3}){3}/[0-9]{1,2}$", var.supernet_cidr)) && can(cidrhost(var.supernet_cidr, 0))
    error_message = "The supernet_cidr value must be an IPv4 CIDR block such as 10.10.0.0/16."
  }

  validation {
    condition     = can(cidrsubnet(var.supernet_cidr, 0, 0)) && try(cidrsubnet(var.supernet_cidr, 0, 0) == var.supernet_cidr, false)
    error_message = "The supernet_cidr value has host bits set: use the network address of the block (for example 10.10.0.0/16, not 10.10.5.0/16)."
  }

  validation {
    condition     = try(tonumber(split("/", var.supernet_cidr)[1]) >= 8 && tonumber(split("/", var.supernet_cidr)[1]) <= 24, false)
    error_message = "The supernet_cidr prefix length must be between /8 and /24."
  }
}

variable "zones" {
  description = "Availability-zone labels, in allocation order. Zone i receives the i-th zone block of the supernet."
  type        = list(string)

  validation {
    condition     = length(var.zones) >= 2 && length(var.zones) <= 6
    error_message = "Provide between 2 and 6 zones: one zone is not zone-redundant, and more than 6 is outside this module's design."
  }

  validation {
    condition     = length(distinct(var.zones)) == length(var.zones)
    error_message = "Zone names must be unique."
  }

  validation {
    condition     = alltrue([for z in var.zones : can(regex("^[a-z0-9][a-z0-9-]{0,31}$", z))])
    error_message = "Zone names must be 1-32 characters of lower-case letters, digits, and hyphens, starting with a letter or digit."
  }
}

variable "zone_newbits" {
  description = "Bits added to the supernet prefix to form one zone block. 2 turns a /16 into four /18 zone blocks."
  type        = number
  default     = 2

  validation {
    condition     = var.zone_newbits >= 1 && var.zone_newbits <= 4 && floor(var.zone_newbits) == var.zone_newbits
    error_message = "The zone_newbits value must be a whole number from 1 to 4."
  }
}

variable "tiers" {
  description = <<-EOT
    Subnet tiers created in every zone. Each tier has a prefix_length (its size, for example 22 for
    1,024 addresses) and an index: the position of the tier inside the zone block, counted in blocks
    of the tier's own size. Example: a /22 at index 8 starts 8 x 1,024 addresses into the zone.
  EOT
  type = map(object({
    prefix_length = number
    index         = number
  }))

  validation {
    condition     = length(var.tiers) >= 1
    error_message = "Define at least one tier."
  }

  validation {
    condition     = alltrue([for name, t in var.tiers : can(regex("^[a-z][a-z0-9-]{0,31}$", name))])
    error_message = "Tier names must start with a lower-case letter and contain only lower-case letters, digits, and hyphens."
  }

  validation {
    condition     = alltrue([for t in var.tiers : t.prefix_length >= 16 && t.prefix_length <= 28 && floor(t.prefix_length) == t.prefix_length])
    error_message = "Each tier prefix_length must be a whole number from 16 to 28."
  }

  validation {
    condition     = alltrue([for t in var.tiers : t.index >= 0 && floor(t.index) == t.index])
    error_message = "Each tier index must be a whole number, 0 or greater."
  }

  # Two tiers overlap when their address ranges, measured from the start of the zone block,
  # intersect. Offsets do not depend on which zone or supernet is used, so this check needs only
  # var.tiers: start = index x 2^(32 - prefix_length), end = start + 2^(32 - prefix_length) - 1.
  validation {
    condition = alltrue(flatten([
      for a_name, a in var.tiers : [
        for b_name, b in var.tiers : (
          a_name == b_name ||
          a.index * pow(2, 32 - a.prefix_length) + pow(2, 32 - a.prefix_length) - 1 < b.index * pow(2, 32 - b.prefix_length) ||
          b.index * pow(2, 32 - b.prefix_length) + pow(2, 32 - b.prefix_length) - 1 < a.index * pow(2, 32 - a.prefix_length)
        )
      ]
    ]))
    error_message = "Two tiers overlap inside the zone block. Change a prefix_length or an index so their ranges are disjoint."
  }
}
