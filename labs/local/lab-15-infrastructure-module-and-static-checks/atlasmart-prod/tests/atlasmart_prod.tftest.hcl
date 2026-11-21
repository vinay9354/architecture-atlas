# Checks that the root example reproduces, prefix for prefix, the AtlasMart prod plan in
# docs/networking/networking-fundamentals-ip-cidr-routing-and-dns.md (Step 3 table and Figure 3).

run "prod_plan_matches_the_networking_page" {
  command = plan

  assert {
    condition = output.zone_cidrs == tomap({
      a = "10.10.0.0/18"
      b = "10.10.64.0/18"
      c = "10.10.128.0/18"
    })
    error_message = "Zone blocks must be 10.10.0.0/18, 10.10.64.0/18, and 10.10.128.0/18."
  }

  assert {
    condition     = output.reserved_zone_cidrs == tolist(["10.10.192.0/18"])
    error_message = "10.10.192.0/18 must stay reserved for a future zone or tier."
  }

  assert {
    condition = output.subnets["a"] == tomap({
      "public"       = "10.10.0.0/22"
      "private-app"  = "10.10.16.0/20"
      "private-data" = "10.10.32.0/22"
    })
    error_message = "Zone a must be public 10.10.0.0/22, private-app 10.10.16.0/20, private-data 10.10.32.0/22."
  }

  assert {
    condition = output.subnets["b"] == tomap({
      "public"       = "10.10.64.0/22"
      "private-app"  = "10.10.80.0/20"
      "private-data" = "10.10.96.0/22"
    })
    error_message = "Zone b must be public 10.10.64.0/22, private-app 10.10.80.0/20, private-data 10.10.96.0/22."
  }

  assert {
    condition = output.subnets["c"] == tomap({
      "public"       = "10.10.128.0/22"
      "private-app"  = "10.10.144.0/20"
      "private-data" = "10.10.160.0/22"
    })
    error_message = "Zone c must be public 10.10.128.0/22, private-app 10.10.144.0/20, private-data 10.10.160.0/22."
  }
}
