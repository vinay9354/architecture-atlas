"""Smoke test for Lab 08 (sharding and consistent hashing): movement matches theory, vnodes even out keys."""
import importlib.util
import py_compile
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-08-sharding-and-consistent-hashing"


def load(name):
    if str(LAB) not in sys.path:
        sys.path.insert(0, str(LAB))  # measure.py does `import placement`
    spec = importlib.util.spec_from_file_location(name, LAB / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Lab08Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.placement, cls.measure = load("placement"), load("measure")
        cls.res = cls.measure.run(keys_count=20_000, n=10, vnodes=100, vnode_list=(1, 10, 100, 200), seed=8)

    def test_sources_compile(self):
        for p in LAB.glob("*.py"):
            py_compile.compile(str(p), doraise=True)

    def test_hash_is_stable_across_processes(self):
        # A fixed value: Python's randomized hash() would give a different number in every process.
        self.assertEqual(self.placement.stable_hash("SHP-0000000042"), 4501211879696065064)

    def test_keys_are_deterministic(self):
        self.assertEqual(self.measure.make_keys(50, 3), self.measure.make_keys(50, 3))
        self.assertNotEqual(self.measure.make_keys(50, 3), self.measure.make_keys(50, 4))

    def test_moved_fractions_match_theory(self):
        tolerance = {"mod-N": 0.02, "ring (100 vnodes)": 0.03, "rendezvous": 0.01}
        for row in self.res["movement"]:
            with self.subTest(scheme=row["scheme"], change=row["change"]):
                self.assertAlmostEqual(row["moved"], row["theory"], delta=tolerance[row["scheme"]])
                # Ring and rendezvous only move keys to the joining node or from the leaving one.
                self.assertEqual(row["only_changed_node"], row["scheme"] != "mod-N")

    def test_more_virtual_nodes_lower_the_spread(self):
        ring = {r["vnodes"]: r for r in self.res["spread"] if r["scheme"] == "ring"}
        self.assertGreater(ring[1]["cv"], ring[10]["cv"])
        self.assertGreater(ring[10]["cv"], ring[100]["cv"])
        self.assertLess(ring[200]["cv"], ring[10]["cv"])
        self.assertGreater(ring[1]["max_over_mean"], ring[200]["max_over_mean"])

    def test_even_keys_are_not_even_load(self):
        none, _, zipf = self.res["hot_keys"]
        self.assertAlmostEqual(none["reads_max_over_mean"], none["keys_max_over_mean"], delta=0.01)
        self.assertGreater(zipf["reads_max_over_mean"], zipf["keys_max_over_mean"] + 0.1)


if __name__ == "__main__":
    unittest.main()
