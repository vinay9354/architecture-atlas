"""Smoke test for Lab 04 (idempotency and duplicates): keys and an inbox table remove duplicate effects."""
import contextlib
import importlib.util
import io
import py_compile
import random
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-04-idempotency-and-duplicates"


def load(name):
    spec = importlib.util.spec_from_file_location(name, LAB / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Lab04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sim = load("idempotency_sim")

    def test_sources_compile(self):
        for p in LAB.glob("*.py"):
            py_compile.compile(str(p), doraise=True)

    def test_server_replays_stored_response_for_same_key(self):
        server = self.sim.PaymentService()
        req = {"order_id": "AM-1", "amount_cents": 4999}
        s1, b1, r1 = server.capture(req, "key-1")
        s2, b2, r2 = server.capture(req, "key-1")
        self.assertEqual((s1, r1), (201, False))
        self.assertEqual((s2, r2), (201, True))
        self.assertEqual(b1, b2)  # byte-identical replay
        self.assertEqual(server.db.execute("SELECT COUNT(*) FROM charges").fetchone()[0], 1)
        s3, _, _ = server.capture({"order_id": "AM-1", "amount_cents": 1}, "key-1")
        self.assertEqual(s3, 422)  # same key, different request: refused

    def test_no_key_double_charges(self):
        r = self.sim.run_api("no-key", orders=300, loss_rate=0.2, max_attempts=4, seed=11)
        self.assertGreater(r["double_charged_orders"], 0)
        self.assertEqual(r["charges"], r["requests"])  # every request charged
        self.assertGreater(r["overcharged"], 0)
        self.assertEqual(r["identical_on_retry"], 0)

    def test_key_prevents_double_charges(self):
        r = self.sim.run_api("key", orders=300, loss_rate=0.2, max_attempts=4, seed=11)
        self.assertEqual(r["double_charged_orders"], 0)
        self.assertEqual(r["charges"], 300)
        self.assertEqual(r["overcharged"], 0)
        self.assertGreater(r["replays"], 0)
        self.assertEqual(r["identical_on_retry"], r["retried_orders"])
        self.assertEqual(r["key_reuse_status"], 422)

    def test_modes_see_the_same_lost_responses(self):
        a = self.sim.run_api("no-key", orders=200, loss_rate=0.3, max_attempts=3, seed=5)
        b = self.sim.run_api("key", orders=200, loss_rate=0.3, max_attempts=3, seed=5)
        self.assertEqual((a["requests"], a["lost_responses"]), (b["requests"], b["lost_responses"]))

    def test_delivery_log_is_at_least_once(self):
        events = [{"message_id": str(i)} for i in range(200)]
        log = self.sim.delivery_log(events, 0.2, random.Random(3))
        self.assertGreater(len(log), len(events))
        self.assertEqual({e["message_id"] for e in log}, {e["message_id"] for e in events})

    def test_inbox_consumer_deduplicates(self):
        naive, inbox = self.sim.run_inbox(orders=300, redelivery_rate=0.15, seed=11)
        self.assertGreater(naive["double_applied_orders"], 0)
        self.assertGreater(naive["ledger_total"], naive["expected_total"])
        self.assertEqual(inbox["applied"], 300)
        self.assertEqual(inbox["double_applied_orders"], 0)
        self.assertEqual(inbox["ledger_total"], inbox["expected_total"])
        self.assertEqual(inbox["dropped_duplicates"], inbox["deliveries"] - inbox["events"])

    def test_cli_is_deterministic(self):
        outputs = []
        for _ in range(2):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(self.sim.main(["--orders", "100"]), 0)
            outputs.append(buf.getvalue())
        self.assertEqual(outputs[0], outputs[1])
        self.assertIn("HTTP 422", outputs[0])


if __name__ == "__main__":
    unittest.main()
