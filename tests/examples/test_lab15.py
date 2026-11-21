"""Smoke test for Lab 15 (infrastructure module and static checks).

Two layers:

* StaticChecks always runs (standard library only): the module declares no providers, the root
  example and its test assert exactly the AtlasMart prod prefixes, and those prefixes agree with
  Python's ipaddress arithmetic and with the networking fundamentals page.
* ToolChecks runs only when `terraform` or `tofu` is on PATH. It copies the lab to a temporary
  directory (so no .terraform/ directory, lock file, or state is ever written inside the
  repository) and runs fmt -check, init -backend=false, validate, and test in both roots.
"""
import ipaddress
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-15-infrastructure-module-and-static-checks"
MODULE = LAB / "modules" / "network-plan"
EXAMPLE = LAB / "atlasmart-prod"
NETWORK_PAGE = ROOT / "docs" / "networking" / "networking-fundamentals-ip-cidr-routing-and-dns.md"

TOOL = shutil.which("terraform") or shutil.which("tofu")

# The AtlasMart prod plan as documented on the networking page (zone blocks and per-zone tiers).
EXPECTED = {
    "a": {"zone": "10.10.0.0/18", "public": "10.10.0.0/22", "private-app": "10.10.16.0/20", "private-data": "10.10.32.0/22"},
    "b": {"zone": "10.10.64.0/18", "public": "10.10.64.0/22", "private-app": "10.10.80.0/20", "private-data": "10.10.96.0/22"},
    "c": {"zone": "10.10.128.0/18", "public": "10.10.128.0/22", "private-app": "10.10.144.0/20", "private-data": "10.10.160.0/22"},
}
RESERVED = "10.10.192.0/18"


def tf_files(path):
    return sorted(p for p in path.rglob("*") if p.suffix in {".tf", ".hcl"})


class StaticChecks(unittest.TestCase):
    def test_expected_files_exist(self):
        for rel in [
            "modules/network-plan/versions.tf",
            "modules/network-plan/variables.tf",
            "modules/network-plan/main.tf",
            "modules/network-plan/outputs.tf",
            "modules/network-plan/tests/network_plan.tftest.hcl",
            "atlasmart-prod/main.tf",
            "atlasmart-prod/tests/atlasmart_prod.tftest.hcl",
        ]:
            self.assertTrue((LAB / rel).is_file(), rel)

    def test_no_providers_resources_or_backends(self):
        for path in tf_files(LAB):
            text = path.read_text()
            for pattern in (r'^\s*provider\s+"', r"required_providers", r'^\s*resource\s+"', r'^\s*data\s+"', r"\bbackend\s+\""):
                self.assertIsNone(re.search(pattern, text, re.M), f"{pattern} found in {path.name}")

    def test_required_version_is_1_6_or_later(self):
        for path in (MODULE / "versions.tf", EXAMPLE / "main.tf"):
            self.assertIn('required_version = ">= 1.6.0"', path.read_text(), path)

    def test_module_validates_inputs_and_tests_bad_input(self):
        variables = (MODULE / "variables.tf").read_text()
        self.assertGreaterEqual(variables.count("validation {"), 8)
        self.assertIn("cidrhost(var.supernet_cidr, 0)", variables)
        self.assertIn("length(distinct(var.zones)) == length(var.zones)", variables)
        self.assertIn("length(var.zones) >= 2 && length(var.zones) <= 6", variables)
        module_tests = (MODULE / "tests" / "network_plan.tftest.hcl").read_text()
        self.assertGreaterEqual(module_tests.count("expect_failures"), 6)
        for path in (MODULE / "tests" / "network_plan.tftest.hcl", EXAMPLE / "tests" / "atlasmart_prod.tftest.hcl"):
            text = path.read_text()
            runs = len(re.findall(r'^run "', text, re.M))
            self.assertEqual(runs, len(re.findall(r"^\s+command = plan$", text, re.M)), f"every run uses plan: {path.name}")

    def test_example_inputs_reproduce_the_documented_plan(self):
        main = (EXAMPLE / "main.tf").read_text()
        supernet = ipaddress.ip_network(re.search(r'supernet_cidr\s*=\s*"([^"]+)"', main).group(1))
        zones = re.findall(r'"([a-z])"', re.search(r"zones\s*=\s*\[([^\]]*)\]", main).group(1))
        newbits = int(re.search(r"zone_newbits\s*=\s*(\d+)", main).group(1))
        tiers = {
            name: (int(plen), int(idx))
            for name, plen, idx in re.findall(r'"([a-z-]+)"\s*=\s*\{\s*prefix_length\s*=\s*(\d+),\s*index\s*=\s*(\d+)\s*\}', main)
        }
        self.assertEqual(zones, ["a", "b", "c"])
        self.assertEqual(set(tiers), {"public", "private-app", "private-data"})
        zone_blocks = list(supernet.subnets(prefixlen_diff=newbits))
        for i, zone in enumerate(zones):
            block = zone_blocks[i]
            self.assertEqual(str(block), EXPECTED[zone]["zone"])
            for tier, (plen, idx) in tiers.items():
                subnet = list(block.subnets(new_prefix=plen))[idx]
                self.assertEqual(str(subnet), EXPECTED[zone][tier], f"{zone}/{tier}")
        self.assertEqual([str(b) for b in zone_blocks[len(zones):]], [RESERVED])

    def test_tftest_and_networking_page_agree_with_expected(self):
        tftest = (EXAMPLE / "tests" / "atlasmart_prod.tftest.hcl").read_text()
        page = NETWORK_PAGE.read_text()
        for zone, prefixes in EXPECTED.items():
            for tier, cidr in prefixes.items():
                self.assertIn(f'"{cidr}"', tftest, f"{zone}/{tier} missing from tftest")
                self.assertIn(f"`{cidr}`", page, f"{zone}/{tier} not on the networking page")
        self.assertIn(RESERVED, tftest)
        self.assertIn(RESERVED, page)


@unittest.skipUnless(TOOL, "neither terraform nor tofu is on PATH")
class ToolChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="lab15-")
        cls.lab = Path(cls.tmp.name) / "lab"
        shutil.copytree(LAB, cls.lab, ignore=shutil.ignore_patterns(".terraform", "*.tfstate*", ".terraform.lock.hcl"))
        cls.env = dict(os.environ, CHECKPOINT_DISABLE="1", TF_IN_AUTOMATION="1", NO_COLOR="1")
        cls.env.pop("TF_CLI_ARGS", None)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_tool(self, cwd, *args):
        result = subprocess.run(
            [TOOL, *args], cwd=cwd, env=self.env, capture_output=True, text=True, timeout=60, check=False
        )
        self.assertEqual(result.returncode, 0, f"{' '.join(args)} failed:\n{result.stdout}\n{result.stderr}")
        return result.stdout

    def test_fmt_check(self):
        self.run_tool(self.lab, "fmt", "-check", "-recursive", "-no-color")

    def test_init_validate_and_test_each_root(self):
        for name, runs in (("modules/network-plan", 9), ("atlasmart-prod", 1)):
            cwd = self.lab / name
            with self.subTest(root=name):
                self.run_tool(cwd, "init", "-backend=false", "-input=false", "-no-color")
                self.assertIn("The configuration is valid", self.run_tool(cwd, "validate", "-no-color"))
                out = self.run_tool(cwd, "test", "-no-color")
                self.assertIn(f"{runs} passed, 0 failed", out)
                self.assertFalse((cwd / ".terraform.lock.hcl").exists(), "no providers, so no lock file")


if __name__ == "__main__":
    unittest.main()
