# Lab 15 — sample results

Recorded on 2026-11-21 on a laptop (macOS, Apple silicon) with Terraform v1.15.6, working in a copy
of `labs/local/lab-15-infrastructure-module-and-static-checks/` outside the repository, with
`CHECKPOINT_DISABLE=1` set so Terraform did not check for a newer version. The module has no
providers and no resources, so every result below is deterministic: the same files give the same
output on any machine with Terraform 1.6.0 or later. OpenTofu was not installed, so the `tofu`
commands on the lab page were not executed; they are expected to behave the same way but that has
not been verified here. Blank lines that `init` prints are trimmed.

## Step 1 — Version

```text
$ terraform version
Terraform v1.15.6
on darwin_arm64
```

## Step 2 — Formatting check

```text
$ terraform fmt -check -recursive
$ echo $?
0
```

After deleting one space before `=` in `zone_newbits  = 2` in `atlasmart-prod/main.tf`:

```text
$ terraform fmt -check -recursive
atlasmart-prod/main.tf
$ echo $?
3

$ terraform fmt -recursive -diff
atlasmart-prod/main.tf
--- old/atlasmart-prod/main.tf
+++ new/atlasmart-prod/main.tf
@@ -16,7 +16,7 @@
 
   supernet_cidr = "10.10.0.0/16"
   zones         = ["a", "b", "c"]
-  zone_newbits = 2 # /16 + 2 bits = /18 per zone, four slots, three used
+  zone_newbits  = 2 # /16 + 2 bits = /18 per zone, four slots, three used
 
   tiers = {
     # index counts blocks of the tier's own size from the start of the zone block:
```

`fmt -check` changes nothing and exits non-zero when any file needs formatting, which is what a CI
job wants; `fmt` without `-check` rewrites the file.

## Step 3 — Initialize without a backend

```text
$ cd modules/network-plan
$ terraform init -backend=false
Initializing provider plugins found in the configuration...

Terraform has been successfully initialized!
...
$ ls -A
main.tf  outputs.tf  tests  variables.tf  versions.tf
```

No `.terraform/` directory and no `.terraform.lock.hcl`: with no providers and no module calls there
is nothing to download or record.

```text
$ cd ../../atlasmart-prod
$ terraform init -backend=false
Initializing modules...
- prod_network_plan in ../modules/network-plan
Initializing provider plugins found in the configuration...

Terraform has been successfully initialized!
...
$ ls -A
.terraform  main.tf  tests
$ find .terraform -type f
.terraform/modules/modules.json
$ cat .terraform/modules/modules.json
{"Modules":[{"Key":"","Source":"","Dir":"."},{"Key":"prod_network_plan","Source":"../modules/network-plan","Dir":"../modules/network-plan"}]}
```

The root example calls a module, so `init` writes a small module manifest. A local-path module is
referenced in place, not copied. Still no lock file, because no provider was selected.

## Step 4 — Validate

```text
$ terraform validate        # in modules/network-plan, then again in atlasmart-prod
Success! The configuration is valid.
```

## Step 5 — Tests

```text
$ cd modules/network-plan
$ terraform test
tests/network_plan.tftest.hcl... in progress
  run "two_zone_practice_plan"... pass
  run "rejects_a_value_that_is_not_a_cidr"... pass
  run "rejects_host_bits_in_the_supernet"... pass
  run "rejects_a_single_zone"... pass
  run "rejects_seven_zones"... pass
  run "rejects_duplicate_zone_names"... pass
  run "rejects_overlapping_tiers"... pass
  run "rejects_more_zones_than_zone_blocks"... pass
  run "rejects_a_tier_larger_than_its_zone"... pass
tests/network_plan.tftest.hcl... tearing down
tests/network_plan.tftest.hcl... pass

Success! 9 passed, 0 failed.

$ cd ../../atlasmart-prod
$ terraform test
tests/atlasmart_prod.tftest.hcl... in progress
  run "prod_plan_matches_the_networking_page"... pass
tests/atlasmart_prod.tftest.hcl... tearing down
tests/atlasmart_prod.tftest.hcl... pass

Success! 1 passed, 0 failed.
```

Each test file ran in well under a second (`time terraform test` reported about 0.1 s of wall time
for the module's nine runs).

## Step 6 — Plan the AtlasMart prod address plan

```text
$ terraform plan

Changes to Outputs:
  + reserved_zone_cidrs = [
      + "10.10.192.0/18",
    ]
  + subnets             = {
      + a = {
          + private-app  = "10.10.16.0/20"
          + private-data = "10.10.32.0/22"
          + public       = "10.10.0.0/22"
        }
      + b = {
          + private-app  = "10.10.80.0/20"
          + private-data = "10.10.96.0/22"
          + public       = "10.10.64.0/22"
        }
      + c = {
          + private-app  = "10.10.144.0/20"
          + private-data = "10.10.160.0/22"
          + public       = "10.10.128.0/22"
        }
    }
  + zone_cidrs          = {
      + a = "10.10.0.0/18"
      + b = "10.10.64.0/18"
      + c = "10.10.128.0/18"
    }

You can apply this plan to save these new output values to the Terraform
state, without changing any real infrastructure.
...
```

Every prefix matches the Step 3 table of the networking fundamentals page. No state file was written
(`plan` never writes state).

## Step 7 — Break it on purpose

### 7a. A wrong offset passes validate and fails test

`"private-data" = { prefix_length = 22, index = 9 }` instead of `index = 8`:

```text
$ terraform validate
Success! The configuration is valid.

$ terraform test
tests/atlasmart_prod.tftest.hcl... in progress
  run "prod_plan_matches_the_networking_page"... fail

Error: Test assertion failed

  on tests/atlasmart_prod.tftest.hcl line 22, in run "prod_plan_matches_the_networking_page":
  22:     condition = output.subnets["a"] == tomap({
  23:       "public"       = "10.10.0.0/22"
  24:       "private-app"  = "10.10.16.0/20"
  25:       "private-data" = "10.10.32.0/22"
  26:     })
    ├────────────────
    │ Diff:
    │ --- actual
    │ +++ expected
    │   {
    │     "private-app": "10.10.16.0/20",
    │ -   "private-data": "10.10.36.0/22",
    │ +   "private-data": "10.10.32.0/22",
    │     "public": "10.10.0.0/22"
    │   }

Zone a must be public 10.10.0.0/22, private-app 10.10.16.0/20, private-data
10.10.32.0/22.
(the same error follows for zones b and c: 10.10.100.0/22 and 10.10.164.0/22)
tests/atlasmart_prod.tftest.hcl... tearing down
tests/atlasmart_prod.tftest.hcl... fail

Failure! 0 passed, 1 failed.
```

`10.10.36.0/22` is a perfectly valid, non-overlapping subnet, so no validation rule can object. Only
a test that knows the intended plan catches it.

### 7b. A duplicate zone name fails validate

`zones = ["a", "b", "a"]`:

```text
$ terraform validate

Error: Invalid value for variable

  on main.tf line 18, in module "prod_network_plan":
  18:   zones         = ["a", "b", "a"]
    ├────────────────
    │ var.zones is list of string with 3 elements

Zone names must be unique.

This was checked by the validation rule at
../modules/network-plan/variables.tf:30,3-13.
```

### 7c. Five zones pass validate and fail plan

`zones = ["a", "b", "c", "d", "e"]` with `zone_newbits = 2` (four slots):

```text
$ terraform validate
Success! The configuration is valid.

$ terraform plan
...
Error: Module output value precondition failed

  on ../modules/network-plan/outputs.tf line 6, in output "zone_cidrs":
   6:     condition     = local.zones_fit
    ├────────────────
    │ local.zones_fit is false

More zones than zone blocks: 5 zones need at least 5 slots, but zone_newbits
= 2 gives 4. Increase zone_newbits.
```

Five zones is within the variable's own rule (2 to 6), so validation passes. The conflict is between
two inputs and is caught by an output precondition, which is evaluated during plan.

### 7d. A missing validation rule fails the module's own tests

With the `length(distinct(var.zones)) == length(var.zones)` validation block deleted from
`modules/network-plan/variables.tf`:

```text
$ terraform test
tests/network_plan.tftest.hcl... in progress
  run "two_zone_practice_plan"... pass
  run "rejects_a_value_that_is_not_a_cidr"... pass
  run "rejects_host_bits_in_the_supernet"... pass
  run "rejects_a_single_zone"... pass
  run "rejects_seven_zones"... pass
  run "rejects_duplicate_zone_names"... fail

Error: Duplicate object key

  on main.tf line 23, in locals:
  22:   zone_cidrs = local.plan_ok ? tomap({
  23:     for i, zone in var.zones : zone => cidrsubnet(var.supernet_cidr, var.zone_newbits, i)
  24:   }) : tomap({})

Two different items produced the key "a" in this 'for' expression. If
duplicates are expected, use the ellipsis (...) after the value expression to
enable grouping by key.

Error: Missing expected failure

  on tests/network_plan.tftest.hcl line 94, in run "rejects_duplicate_zone_names":
  94:   expect_failures = [var.zones]

The checkable object, var.zones, was expected to report an error but did not.
  run "rejects_overlapping_tiers"... skip
  run "rejects_more_zones_than_zone_blocks"... skip
  run "rejects_a_tier_larger_than_its_zone"... skip
tests/network_plan.tftest.hcl... tearing down
tests/network_plan.tftest.hcl... fail

Failure! 5 passed, 1 failed, 3 skipped.
```

The `expect_failures` run is a regression test for the validation rule itself: delete the rule and
the test reports both the raw error the rule was protecting against and the missing expected failure.

## Step 8 — Smoke test

From the repository root:

```text
$ .venv/bin/python -m unittest tests.examples.test_lab15 -v
test_example_inputs_reproduce_the_documented_plan (tests.examples.test_lab15.StaticChecks...) ... ok
test_expected_files_exist (tests.examples.test_lab15.StaticChecks...) ... ok
test_module_validates_inputs_and_tests_bad_input (tests.examples.test_lab15.StaticChecks...) ... ok
test_no_providers_resources_or_backends (tests.examples.test_lab15.StaticChecks...) ... ok
test_required_version_is_1_6_or_later (tests.examples.test_lab15.StaticChecks...) ... ok
test_tftest_and_networking_page_agree_with_expected (tests.examples.test_lab15.StaticChecks...) ... ok
test_fmt_check (tests.examples.test_lab15.ToolChecks...) ... ok
test_init_validate_and_test_each_root (tests.examples.test_lab15.ToolChecks...) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.663s

OK
```

With neither `terraform` nor `tofu` on `PATH`, the two `ToolChecks` tests report
`skipped 'neither terraform nor tofu is on PATH'` and the six static checks still run.

## What to notice

1. **Each check catches a different class of mistake.** `fmt -check` catches layout only.
   `validate` catches syntax, type errors, references to things that do not exist, and variable
   validation rules whose inputs are known. `plan` adds preconditions that compare several inputs.
   `test` catches a configuration that is valid but wrong (7a), which only a statement of intent can
   detect.
2. **No providers means nothing to download, lock, or authenticate.** The whole lab runs offline,
   leaves no state, and needs no cloud account. Real modules add providers, and then `init` downloads
   plugins and writes `.terraform.lock.hcl`, which you commit.
3. **Validation lives as close to the input as possible.** Single-input rules sit in `validation`
   blocks; rules that compare inputs sit in output preconditions; the overlap rule is written in
   relative offsets so it needs only one variable.
4. **`expect_failures` tests the guard rails.** Without the negative runs, deleting a validation rule
   would go unnoticed until someone supplied a bad input in production (7d).
