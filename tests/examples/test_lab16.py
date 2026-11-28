"""Smoke test for Lab 16 (event-driven workflow): outbox, relay, idempotent consumers, choreographed saga."""
import importlib
import io
import py_compile
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-16-event-driven-workflow"


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


class Lab16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bus = load("lab16_bus")
        cls.svc = load("lab16_services")
        cls.wf = load("lab16_workflow")
        cls.results = {name: cls.wf.run_experiment(name) for name in cls.wf.EXPERIMENTS}
        cls.naive = cls.wf.run_experiment("duplicates", idempotent=False)

    def test_sources_compile(self):
        for p in LAB.glob("*.py"):
            py_compile.compile(str(p), doraise=True)

    def test_event_envelope(self):
        event = self.bus.make_event("/atlasmart/orders", "ord-0001", "atlasmart.order.placed", "AM-1001",
                                    {"order_id": "AM-1001"})
        self.bus.check_event(event)
        self.assertEqual((event["specversion"], event["data"]["schema_version"]), ("1.0", 1))
        for missing in ("id", "source", "type", "specversion"):
            broken = dict(event)
            del broken[missing]
            with self.assertRaises(ValueError):
                self.bus.check_event(broken)

    def test_bus_filtering_duplicates_and_replay(self):
        bus = self.bus.EventBus(seed=1, duplicate_rate=1.0)
        seen = []
        bus.subscribe("payments", "shipping", seen.append, ["atlasmart.payment.authorized"])
        ok = self.bus.make_event("/p", "p-1", "atlasmart.payment.authorized", "AM-1", {})
        bad = self.bus.make_event("/p", "p-2", "atlasmart.payment.failed", "AM-2", {})
        bus.publish("payments", ok)
        bus.publish("payments", bad)
        self.assertEqual(bus.pending_count(), 1)          # the filter dropped payment.failed
        for _ in range(3):
            bus.deliver_one()
        self.assertEqual([e["id"] for e in seen], ["p-1"] * 3)   # every ack "lost": redelivered
        self.assertEqual(bus.replay("payments", "shipping"), 1)

    def test_outbox_row_commits_with_the_order_or_not_at_all(self):
        with tempfile.TemporaryDirectory() as d:
            orders = self.svc.OrdersService(str(Path(d) / "orders.db"))
            orders.place_order("AM-1", "SKU-A", 1, 1000, "test-card-ok")
            with self.assertRaises(sqlite3.IntegrityError):
                orders.place_order("AM-1", "SKU-A", 1, 1000, "test-card-ok")   # duplicate key: rolled back
            self.assertEqual(orders.count("SELECT COUNT(*) FROM outbox"), 1)
            self.assertEqual(orders.count("SELECT COUNT(*) FROM orders"), 1)
            orders.db.close()

    def test_happy_path(self):
        r = self.results["happy"]
        s = r["summary"]
        self.assertEqual(r["problems"], [])
        self.assertEqual((s["orders"], s["payments"], s["shipments"]), ({"SHIPPED": 10}, {"AUTHORIZED": 10}, 10))
        self.assertEqual((s["bus"]["published"], s["bus"]["deliveries"], s["duplicates_skipped"]), (40, 60, 0))

    def test_crash_between_commit_and_publish_is_saved_by_the_outbox(self):
        r = self.results["crash"]
        s = r["summary"]
        self.assertEqual(len(s["relay_crashes"]), 2)
        self.assertIn("before publishing ord-0003", s["relay_crashes"][0])
        self.assertEqual(r["problems"], [])
        self.assertEqual(s["orders"], {"SHIPPED": 10})
        self.assertEqual(s["bus"]["published"], 41)                  # pay-0005 was published twice
        self.assertEqual(s["duplicates_skipped"], 2)                 # ...and absorbed by both consumers

    def test_duplicates_are_harmless_only_with_idempotent_consumers(self):
        r = self.results["duplicates"]
        s = r["summary"]
        self.assertGreater(s["bus"]["duplicates_injected"], 0)
        self.assertGreater(s["bus"]["reorders_injected"], 0)
        self.assertEqual(s["duplicates_skipped"], s["bus"]["duplicates_injected"])
        self.assertEqual(r["problems"], [])
        self.assertEqual((r["replay"]["replayed"], r["replay"]["unchanged"]), (10, True))
        self.assertGreaterEqual(r["replay"]["duplicates_skipped"], 10)  # the faulty bus may add more
        n = self.naive["summary"]
        self.assertTrue(self.naive["problems"])
        self.assertGreater(n["payments"]["AUTHORIZED"], 10)
        self.assertGreater(n["shipments"], 10)

    def test_payment_failure_runs_the_compensation(self):
        r = self.results["payment-failure"]
        s = r["summary"]
        self.assertEqual(r["problems"], [])                          # stock restored, nothing shipped
        self.assertEqual(s["orders"], {"CANCELLED": 2, "SHIPPED": 8})
        self.assertEqual(s["payments"], {"AUTHORIZED": 8, "DECLINED": 2})
        self.assertEqual(s["shipments"], 8)
        self.assertEqual(s["duplicates_skipped"], s["bus"]["duplicates_injected"])

    def test_naive_dual_write_loses_an_event_and_creates_a_ghost(self):
        r = self.results["dual-write"]
        self.assertTrue(any(p.startswith("AM-1003: stuck in PENDING") for p in r["problems"]))
        self.assertTrue(any(p.startswith("AM-1006: not in Orders") for p in r["problems"]))
        self.assertEqual(r["summary"]["orders"], {"PENDING": 1, "SHIPPED": 8})

    def test_cli_runs_all_experiments(self):
        out = io.StringIO()
        self.assertEqual(self.wf.main([], out=out), 0)
        text = out.getvalue()
        self.assertEqual(text.count("invariants         OK"), 4)
        self.assertEqual(text.count("BROKEN"), 2)


if __name__ == "__main__":
    unittest.main()
