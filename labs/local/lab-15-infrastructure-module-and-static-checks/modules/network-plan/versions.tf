# network-plan: a pure-calculation module. It declares no providers and creates no resources,
# so `terraform init` (or `tofu init`) has nothing to download and the module costs nothing to run.
#
# 1.6.0 is the first release with `terraform test` (.tftest.hcl files with run, assert,
# expect_failures, and `command = plan`). Variable validation (0.13) and output preconditions
# (1.2) are older. OpenTofu 1.6.0 and later read the same files.
terraform {
  required_version = ">= 1.6.0"
}
