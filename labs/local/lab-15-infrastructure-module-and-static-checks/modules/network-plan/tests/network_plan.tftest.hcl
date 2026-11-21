# Tests for the network-plan module itself. Every run uses `command = plan`: the module has no
# resources, so a plan computes every output without creating state or calling any API.
#
# The default inputs are the two-zone practice plan from the networking fundamentals page's lab:
# 10.42.0.0/16, a /23 public, /21 application, and /23 data subnet per zone.

variables {
  supernet_cidr = "10.42.0.0/16"
  zones         = ["a", "b"]
  zone_newbits  = 2
  tiers = {
    "public"       = { prefix_length = 23, index = 0 }
    "private-app"  = { prefix_length = 21, index = 1 }
    "private-data" = { prefix_length = 23, index = 8 }
  }
}

run "two_zone_practice_plan" {
  command = plan

  assert {
    condition     = output.zone_cidrs == tomap({ a = "10.42.0.0/18", b = "10.42.64.0/18" })
    error_message = "Zone blocks should be the first two /18s of 10.42.0.0/16."
  }

  assert {
    condition     = output.subnets["a"]["public"] == "10.42.0.0/23" && output.subnets["a"]["private-app"] == "10.42.8.0/21" && output.subnets["a"]["private-data"] == "10.42.16.0/23"
    error_message = "Zone a subnets do not match the networking page's lab hint."
  }

  assert {
    condition     = output.subnets["b"]["public"] == "10.42.64.0/23" && output.subnets["b"]["private-app"] == "10.42.72.0/21" && output.subnets["b"]["private-data"] == "10.42.80.0/23"
    error_message = "Zone b should repeat zone a's pattern offset by 64 in the third octet."
  }

  assert {
    condition     = output.reserved_zone_cidrs == tolist(["10.42.128.0/18", "10.42.192.0/18"])
    error_message = "The two unused /18s should be reported as reserved."
  }

  assert {
    condition     = length(output.subnets_flat) == 6 && output.subnets_flat["b/private-data"] == "10.42.80.0/23"
    error_message = "subnets_flat should hold one entry per zone and tier."
  }
}

run "rejects_a_value_that_is_not_a_cidr" {
  command = plan

  variables {
    supernet_cidr = "10.42.0.0"
  }

  expect_failures = [var.supernet_cidr]
}

run "rejects_host_bits_in_the_supernet" {
  command = plan

  variables {
    supernet_cidr = "10.42.5.0/16"
  }

  expect_failures = [var.supernet_cidr]
}

run "rejects_a_single_zone" {
  command = plan

  variables {
    zones = ["a"]
  }

  expect_failures = [var.zones]
}

run "rejects_seven_zones" {
  command = plan

  variables {
    zones = ["a", "b", "c", "d", "e", "f", "g"]
  }

  expect_failures = [var.zones]
}

run "rejects_duplicate_zone_names" {
  command = plan

  variables {
    zones = ["a", "b", "a"]
  }

  expect_failures = [var.zones]
}

run "rejects_overlapping_tiers" {
  command = plan

  variables {
    tiers = {
      "public"      = { prefix_length = 23, index = 0 }
      "private-app" = { prefix_length = 21, index = 0 }
    }
  }

  expect_failures = [var.tiers]
}

run "rejects_more_zones_than_zone_blocks" {
  command = plan

  variables {
    zones = ["a", "b", "c", "d", "e"]
  }

  expect_failures = [output.zone_cidrs]
}

run "rejects_a_tier_larger_than_its_zone" {
  command = plan

  variables {
    tiers = {
      "public" = { prefix_length = 17, index = 0 }
    }
  }

  expect_failures = [output.subnets]
}
