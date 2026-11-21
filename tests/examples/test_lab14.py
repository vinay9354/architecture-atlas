"""Smoke test for Lab 14 (network segmentation): the four experiments produce the outcomes taught."""
import contextlib
import importlib.util
import io
import py_compile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-14-network-segmentation"


def load(name):
    spec = importlib.util.spec_from_file_location(name, LAB / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Lab14Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sim = load("segmentation_sim")

    def outcomes(self, experiment):
        """Map (sg_mode, nacl_mode, flow) to (outcome, dropped, decided_by)."""
        return {(r["sg_mode"], r["nacl_mode"], r["flow"]): (r["outcome"], r["dropped"], r["decided_by"])
                for r in self.sim.run_experiment(experiment)}

    def test_sources_compile(self):
        for p in LAB.glob("*.py"):
            py_compile.compile(str(p), doraise=True)

    def test_hosts_sit_in_zone_a_address_plan(self):
        plan = {"public-a": "10.10.0.0/22", "app-a": "10.10.16.0/20", "data-a": "10.10.32.0/22",
                "app-a2": "10.10.48.0/20"}
        self.assertEqual({s.name: s.cidr for s in self.sim.SUBNETS}, plan)
        for h in self.sim.HOSTS:
            self.assertTrue(self.sim.ip_in(h.ip, plan[h.subnet]), h)
            self.assertTrue(self.sim.ip_in(h.ip, "10.10.0.0/18"), h)   # all inside zone a

    def test_a_flat_network_lets_the_web_host_reach_the_database(self):
        out = self.outcomes("flat")
        self.assertEqual(out[("flat", "default", "web-1 -> db-1:5432")][0], "CONNECTED")
        self.assertEqual(out[("flat", "default", "app-1 -> db-1:5432")][0], "CONNECTED")

    def test_b_security_groups_block_web_to_db_but_allow_app_to_db(self):
        out = self.outcomes("segmented")
        web_db = out[("group", "default", "web-1 -> db-1:5432")]
        self.assertEqual(web_db[:2], ("TIMEOUT", "request"))
        self.assertTrue(web_db[2].startswith("sg-db in"))
        self.assertEqual(out[("group", "default", "app-1 -> db-1:5432")][0], "CONNECTED")
        self.assertEqual(out[("group", "default", "web-1 -> app-1:8080")][0], "CONNECTED")
        self.assertEqual(out[("group", "default", "ingest-1 -> db-1:5432")][0], "TIMEOUT")

    def test_c_missing_ephemeral_rule_drops_the_response_and_flow_log_shows_it(self):
        broken = [r for r in self.sim.run_experiment("nacl") if r["nacl_mode"] == "data-broken"
                  and r["flow"] == "app-1 -> db-1:5432"][0]
        self.assertEqual((broken["outcome"], broken["dropped"]), ("TIMEOUT", "response"))
        self.assertEqual(broken["decided_by"], "nacl-data out * (implicit deny)")
        # Flow log on the database interface: the request ACCEPTed, then the response REJECTed.
        self.assertEqual(len(broken["flow_log"]), 2)
        self.assertIn("-> 10.10.32.10:5432 tcp ACCEPT", broken["flow_log"][0])
        self.assertIn("10.10.32.10:5432 ->", broken["flow_log"][1])
        self.assertIn("REJECT by=nacl-data out *", broken["flow_log"][1])
        out = self.outcomes("nacl")
        self.assertEqual(out[("group", "data-fixed", "app-1 -> db-1:5432")][0], "CONNECTED")
        for mode in ("data-broken", "data-fixed"):   # explicit deny rule 50 stops the public tier first
            self.assertEqual(out[("group", mode, "web-1 -> db-1:5432")][2], "nacl-data in 50 deny")

    def test_d_cidr_reference_breaks_on_scale_out_and_over_trusts_neighbours(self):
        out = self.outcomes("scale")
        self.assertEqual(out[("cidr", "default", "app-1 -> db-1:5432")][0], "CONNECTED")
        self.assertEqual(out[("cidr", "default", "app-2 -> db-1:5432")][0], "TIMEOUT")
        self.assertEqual(out[("cidr", "default", "ingest-1 -> db-1:5432")][0], "CONNECTED")
        self.assertEqual(out[("group", "default", "app-2 -> db-1:5432")][0], "CONNECTED")
        self.assertEqual(out[("group", "default", "ingest-1 -> db-1:5432")][0], "TIMEOUT")
        # NACLs only know CIDRs: the group reference does not help if the subnet NACL was not updated.
        self.assertEqual(out[("group", "data-fixed", "app-2 -> db-1:5432")][2], "nacl-data in * (implicit deny)")

    def test_deterministic_for_a_seed(self):
        self.assertEqual(self.sim.run_experiment("nacl", seed=3), self.sim.run_experiment("nacl", seed=3))
        ports = {r["flow_log"][0].split()[1] for r in self.sim.run_experiment("flat", seed=3)}
        for p in ports:
            self.assertTrue(32768 <= int(p.rsplit(":", 1)[1]) <= 60999)

    def test_cli_prints_flow_log(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.sim.main(["all", "--rules"])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("REJECT by=nacl-data out * (implicit deny)", text)
        self.assertEqual(text.count("=== "), 4)

    def test_compose_appendix_parses_and_isolates_the_data_network(self):
        # Docker is not run by this test; the appendix is checked statically only.
        doc = yaml.safe_load((LAB / "compose" / "docker-compose.yml").read_text(encoding="utf-8"))
        nets = {name: svc["networks"] for name, svc in doc["services"].items()}
        self.assertEqual(nets, {"web": ["frontend"], "app": ["frontend", "data"], "db": ["data"]})
        self.assertIs(doc["networks"]["data"]["internal"], True)
        self.assertNotIn("ports", doc["services"]["db"])
        for svc in doc["services"].values():
            self.assertRegex(svc["image"], r":\d")   # pinned tag, never "latest"
            for mapping in svc.get("ports", []):
                self.assertTrue(mapping.startswith("127.0.0.1:"))


if __name__ == "__main__":
    unittest.main()
