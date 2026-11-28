"""Smoke test for Lab 06 (indexing and query plans): plan shapes from EXPLAIN QUERY PLAN and relative costs."""
import importlib
import py_compile
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-06-indexing-and-query-plans"
SCAN = re.compile(r"^SCAN (TABLE )?scan_events$")   # SQLite before 3.36 printed "SCAN TABLE"


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


SHIPMENTS = 2_500          # 20,000 rows: plans are the same as at 300,000 (no ANALYZE statistics)
BUDGET = 0.02              # seconds of repeated runs per timed query


class Lab06Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load("lab06_data")
        cls.plans = load("lab06_plans")
        cls.conn = cls.data.connect()
        cls.rows = cls.data.build(cls.conn, SHIPMENTS, seed=6)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def labels(self, result):
        return {c["label"]: c for c in result["cases"]}

    def test_sources_compile(self):
        for p in LAB.glob("*.py"):
            py_compile.compile(str(p), doraise=True)

    def test_data_is_seeded_and_shaped(self):
        self.assertEqual(self.rows, SHIPMENTS * 8)
        first = list(self.data.generate(3, 6))
        self.assertEqual(first, list(self.data.generate(3, 6)))
        self.assertNotEqual(first, list(self.data.generate(3, 7)))
        s = self.data.summary(self.conn)
        self.assertEqual((s["shipments"], s["carriers"]), (SHIPMENTS, 12))
        self.assertGreaterEqual(s["first"], "2026-05-31")
        self.assertLess(s["last"], "2026-11-27")
        # ISO text sorts as time: within a shipment, received_at never precedes occurred_at.
        bad = self.conn.execute("SELECT count(*) FROM scan_events WHERE received_at <= occurred_at").fetchone()[0]
        self.assertEqual(bad, 0)

    def test_scan_then_index_search(self):
        r = self.plans.step_scan_vs_search(self.conn, BUDGET)
        before, after = r["cases"]
        self.assertRegex(before["plan"][0], SCAN)
        self.assertEqual(after["plan"], ["SEARCH scan_events USING INDEX idx_ship (shipment_id=?)"])
        self.assertEqual(before["rows"], after["rows"])
        self.assertEqual(after["rows"], 8)
        self.assertGreater(r["speedup"], 5)   # a wide margin; typically far higher

    def test_equality_column_first(self):
        r = self.plans.step_composite_order(self.conn, BUDGET)
        range_first, eq_first = r["cases"]
        self.assertIn("USING COVERING INDEX idx_recv_carrier (received_at>?)", range_first["plan"][0])
        self.assertIn("USING COVERING INDEX idx_carrier_recv (carrier_id=? AND received_at>?)", eq_first["plan"][0])
        self.assertTrue(range_first["plan"][0].startswith("SEARCH"))
        self.assertGreater(r["walked"]["range_first"], 5 * r["walked"]["equality_first"])

    def test_covering_index_skips_the_table(self):
        r = self.plans.step_covering(self.conn, BUDGET)
        plain, covering = r["cases"]
        self.assertIn("USING INDEX idx_carrier_recv (carrier_id=? AND received_at>?)", plain["plan"][0])
        self.assertNotIn("COVERING", plain["plan"][0])
        self.assertIn("USING COVERING INDEX idx_carrier_recv_status", covering["plan"][0])
        self.assertEqual(plain["rows"], covering["rows"])

    def test_unusable_predicates_and_fixes(self):
        cases = self.plans.step_unusable(self.conn, BUDGET)["cases"]
        function, rng, leading, like_prefix, glob_prefix, expr = cases
        self.assertRegex(function["plan"][0], SCAN)
        self.assertIn("USING INDEX idx_recv (received_at>? AND received_at<?)", rng["plan"][0])
        self.assertEqual(function["rows"], rng["rows"])
        self.assertRegex(leading["plan"][0], SCAN)
        self.assertRegex(like_prefix["plan"][0], SCAN)
        self.assertIn("USING INDEX idx_carrier_event (carrier_event_id>? AND carrier_event_id<?)",
                      glob_prefix["plan"][0])
        self.assertEqual((leading["rows"], like_prefix["rows"], glob_prefix["rows"]), (12, 10, 10))
        self.assertGreater(rng["rows"], 0)
        self.assertIn("USING INDEX idx_recv_day (<expr>=?)", expr["plan"][0])
        self.assertEqual(expr["rows"], function["rows"])

    def test_order_by_from_index_or_temp_btree(self):
        latest_none, latest_idx, timeline_ship, timeline_ship_time = self.plans.step_order_by(
            self.conn, BUDGET)["cases"]
        temp = "USE TEMP B-TREE FOR ORDER BY"
        self.assertTrue(any(temp in line for line in latest_none["plan"]))
        self.assertEqual(latest_idx["plan"], ["SCAN scan_events USING INDEX idx_recv"])
        self.assertTrue(any(temp in line for line in timeline_ship["plan"]))
        self.assertFalse(any(temp in line for line in timeline_ship_time["plan"]))
        self.assertIn("USING INDEX idx_ship_time (shipment_id=?)", timeline_ship_time["plan"][0])
        self.assertEqual(latest_none["rows"], 20)

    def test_plan_helper_is_not_fooled_by_the_statement_cache(self):
        conn = self.data.connect()
        conn.execute("CREATE TABLE t (a INTEGER, b TEXT)")
        conn.execute("CREATE INDEX t_b ON t (b)")
        sql = "SELECT * FROM t ORDER BY b LIMIT 5"
        self.assertEqual(self.plans.plan(conn, sql), ["SCAN t USING INDEX t_b"])
        conn.execute("DROP INDEX t_b")
        self.assertIn("USE TEMP B-TREE FOR ORDER BY", " ".join(self.plans.plan(conn, sql)))
        conn.close()

    def test_more_indexes_cost_more_writes(self):
        r = self.plans.step_write_cost(SHIPMENTS, 6, index_counts=(0, 1, 5), repeats=2)
        none, one, five = r["results"]
        self.assertEqual(r["rows"], SHIPMENTS * 8)
        self.assertLess(none["pages"], one["pages"])
        self.assertLess(one["pages"], five["pages"])
        self.assertGreater(five["seconds"], none["seconds"])   # relative only, never an absolute time


if __name__ == "__main__":
    unittest.main()
