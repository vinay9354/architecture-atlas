"""Smoke test for Lab 09 (replication lag): session guarantees hold exactly where each policy promises."""
import importlib.util
import py_compile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-09-replication-lag"


def load(name):
    spec = importlib.util.spec_from_file_location(name, LAB / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Lab09Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sim = load("replication_sim")
        cls.normal = cls.sim.run(cls.sim.Config())
        cls.spike = cls.sim.run(cls.sim.Config(lag_spike=True))
        cls.by_policy = {r["policy"]: r for r in cls.normal["policies"]}
        cls.spike_by_policy = {r["policy"]: r for r in cls.spike["policies"]}

    def test_sources_compile(self):
        for p in LAB.glob("*.py"):
            py_compile.compile(str(p), doraise=True)

    def test_deterministic_for_a_seed(self):
        self.assertEqual(self.sim.run(self.sim.Config()), self.normal)

    def test_followers_apply_in_order(self):
        cluster = self.sim.Cluster(self.sim.Config())
        for applied in cluster.applied_ms:
            self.assertTrue(all(a <= b for a, b in zip(applied, applied[1:])))
            self.assertTrue(all(a >= c for a, c in zip(applied, cluster.commit_ms)))

    def test_read_your_writes_policies(self):
        self.assertGreater(self.by_policy["any-follower"]["ryw_violations"], 0)
        self.assertEqual(self.by_policy["leader-after-write"]["ryw_violations"], 0)
        self.assertEqual(self.by_policy["wait-for-position"]["ryw_violations"], 0)

    def test_monotonic_reads_policies(self):
        self.assertGreater(self.by_policy["any-follower"]["monotonic_violations"], 0)
        self.assertEqual(self.by_policy["sticky-follower"]["monotonic_violations"], 0)

    def test_lag_spike(self):
        # Waiting for the log position still guarantees read-your-writes, by falling back to the leader.
        self.assertEqual(self.spike_by_policy["wait-for-position"]["ryw_violations"], 0)
        self.assertGreater(self.spike_by_policy["wait-for-position"]["fallbacks"], 0)
        # A fixed time window is only a guess about lag: a long spike breaks it.
        self.assertGreater(self.spike_by_policy["leader-after-write"]["ryw_violations"], 0)
        self.assertEqual(self.spike_by_policy["sticky-follower"]["monotonic_violations"], 0)


if __name__ == "__main__":
    unittest.main()
