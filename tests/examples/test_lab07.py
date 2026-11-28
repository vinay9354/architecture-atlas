"""Smoke test for Lab 07 (SQL vs NoSQL access patterns): same answers, partitions touched, hot partition."""
import importlib
import io
import py_compile
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-07-sql-vs-nosql-access-patterns"


def load(name):
    """Import a lab module by name, making sure it comes from THIS lab's folder.

    Several labs reuse module names (for example tracking_api.py in Labs 10 and 11). When the whole
    suite runs in one process, a module cached by another lab's test would otherwise be reused here.
    """
    lab = str(LAB)
    if lab in sys.path:
        sys.path.remove(lab)
    sys.path.insert(0, lab)  # the lab modules import each other by name
    cached = sys.modules.get(name)
    if cached is not None and not str(getattr(cached, "__file__", "")).startswith(lab):
        for mod_name, mod in list(sys.modules.items()):
            mod_file = str(getattr(mod, "__file__", "") or "")
            if mod_file.startswith(str(LAB.parent)) and not mod_file.startswith(lab):
                del sys.modules[mod_name]
    return importlib.import_module(name)


class Lab07Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_mod = load("lab07_data")
        cls.sql = load("lab07_sql")
        cls.kv = load("lab07_tracking_kv")
        cls.hot = load("lab07_hot")
        cls.lab = load("lab07_run")

    def setUp(self):
        self.ctx = None

    def tearDown(self):
        if self.ctx is not None:
            self.ctx[1].close()                                       # the SQLite connection

    def stores(self):
        self.ctx = self.lab.setup(7)
        return self.ctx

    def test_sources_compile(self):
        for p in LAB.glob("*.py"):
            py_compile.compile(str(p), doraise=True)

    def test_data_is_seeded(self):
        a, b = self.data_mod.generate(7), self.data_mod.generate(7)
        self.assertEqual(a["events"], b["events"])
        self.assertNotEqual(a["events"], self.data_mod.generate(8)["events"])
        self.assertEqual(len({s["carrier"] for s in a["shipments"]}), 12)

    def test_designed_patterns_same_answers_one_partition(self):
        results = self.lab.run_patterns(self.stores(), seed=3)
        self.assertEqual(len(results), 3)
        for name, r in results.items():
            self.assertEqual(r["same"], r["n"], name)                  # identical answers
            self.assertEqual(r["kv_partitions_max"], 1, name)          # one partition per query
            self.assertEqual(r["kv_requests_max"], 1, name)
            self.assertAlmostEqual(r["kv_items_read_avg"], r["rows_avg"], places=6, msg=name)
            self.assertTrue(all(line.startswith(("SEARCH", "USE TEMP")) for line in r["plan"]), r["plan"])
        self.assertEqual(results["get shipment by id"]["kv_items_read_avg"], 1.0)
        # The relational answer joins three normalized tables; the key-value answer is one item.
        self.assertEqual(len(results["get shipment by id"]["plan"]), 3)

    def test_adhoc_query_scan_versus_index(self):
        r = self.lab.run_adhoc(self.stores())
        answers = [r["sql_before"]["answer"], r["sql_after"]["answer"], r["kv_scan"]["answer"],
                   r["kv_index"]["answer"]]
        self.assertGreater(len(answers[0]), 0)
        self.assertTrue(all(a == answers[0] for a in answers))
        # SQL answers it as designed, with a scan; an added index makes it a search.
        self.assertTrue(any(line.startswith("SCAN") for line in r["sql_before"]["plan"]))
        self.assertFalse(any(line.startswith("SCAN") for line in r["sql_after"]["plan"]))
        self.assertGreater(r["sql_before"]["steps"], 5 * r["sql_after"]["steps"])
        # The key-value store can only scan everything until an index is built (which also scans).
        scan = r["kv_scan"]
        self.assertEqual(scan["items_read"], scan["total_items"])
        self.assertEqual(scan["partitions_touched"], scan["partitions"])
        self.assertEqual(r["kv_backfill"]["base_items_read"], scan["total_items"])
        self.assertEqual(r["kv_index"]["partitions_touched"], 1)
        self.assertLess(r["kv_index"]["items_read"], scan["total_items"] / 100)

    def test_global_index_is_eventually_consistent(self):
        r = self.lab.run_index_lag(self.stores())
        self.assertEqual(r["sql_recent"][0], "S900001")
        self.assertTrue(r["kv_base_get"])
        self.assertEqual(r["pending"], 1)
        self.assertNotIn("S900001", r["kv_index_before"])
        self.assertEqual(r["kv_index_after"][0], "S900001")
        # The run left both stores as built.
        self.assertIsNone(self.kv.get_shipment(self.ctx[2], "S900001"))
        self.assertNotIn("S900001", self.sql.customer_recent(self.ctx[1], r["customer"])[0])

    def test_hot_partition_and_write_sharding(self):
        plain = self.hot.simulate(shards=1, seconds=4)
        sharded = self.hot.simulate(shards=8, seconds=4)
        self.assertLess(plain["base"]["hot_ratio"], 1.5)            # keyed by shipment: even
        self.assertEqual(plain["base"]["throttled"], 0)
        self.assertGreater(plain["hottest_key_share"], 0.35)        # carrier-a about 40%
        self.assertGreater(plain["index"]["hot_ratio"], 5)
        self.assertGreater(plain["index"]["throttled"], 0)
        self.assertLess(sharded["index"]["hot_ratio"], plain["index"]["hot_ratio"] / 3)
        self.assertEqual(sharded["index"]["throttled"], 0)
        self.assertEqual(sharded["read_fanout"], 8)
        self.assertEqual(sharded["index_partition_keys"], 8 * plain["index_partition_keys"])

    def test_cli_all_runs(self):
        out = io.StringIO()
        self.assertEqual(self.lab.main(["all"], out=out), 0)
        text = out.getvalue()
        self.assertIn("same answer from both stores: 200 of 200", text)
        self.assertIn("same answer from all four: True", text)


if __name__ == "__main__":
    unittest.main()
