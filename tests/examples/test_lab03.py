"""Smoke test for Lab 03 (queue retries and dead-letter): the discrete-event simulation behaves as taught."""
import contextlib
import importlib.util
import io
import py_compile
import random
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-03-queue-retries-and-dead-letter"


def load(name):
    spec = importlib.util.spec_from_file_location(name, LAB / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Lab03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sim = load("queue_sim")
        cls.base = cls.sim.Config()

    def run_cfg(self, **changes):
        return self.sim.simulate(replace(self.base, **changes))

    def test_sources_compile(self):
        for p in LAB.glob("*.py"):
            py_compile.compile(str(p), doraise=True)

    def test_backoff_schedule(self):
        rng = random.Random(1)
        delays = [self.sim.backoff_delay(n, 1.0, 60.0, "none", rng) for n in range(1, 9)]
        self.assertEqual(delays, [1, 2, 4, 8, 16, 32, 60, 60])  # doubles, then capped
        for n in range(1, 9):
            d = self.sim.backoff_delay(n, 1.0, 60.0, "full", rng)
            self.assertGreaterEqual(d, 0.0)
            self.assertLessEqual(d, min(60.0, 2 ** (n - 1)))

    def test_deterministic_for_a_seed(self):
        self.assertEqual(self.run_cfg(), self.run_cfg())
        self.assertNotEqual(self.run_cfg(seed=1), self.run_cfg(seed=2))

    def test_every_message_settles_and_poison_reaches_dlq(self):
        r = self.run_cfg()
        self.assertEqual(r["processed"] + r["dead_lettered"], r["published"])
        self.assertEqual(r["dlq_poison"], 1)
        self.assertGreater(r["retried"], 0)
        self.assertLessEqual(r["p50_s"], r["p99_s"])

    def test_full_jitter_spreads_retries(self):
        none, full = self.run_cfg(jitter="none"), self.run_cfg(jitter="full")
        self.assertGreater(none["retry_peak"], full["retry_peak"])

    def test_max_receive_count_one_dead_letters_healthy_messages(self):
        one, five = self.run_cfg(max_receives=1), self.run_cfg(max_receives=5)
        self.assertGreater(one["dlq_healthy"], 10 * max(1, five["dlq_healthy"]))
        self.assertGreater(five["processed"], one["processed"])

    def test_more_consumers_finish_sooner(self):
        one, four = self.run_cfg(consumers=1), self.run_cfg(consumers=4)
        self.assertLess(four["p50_s"], one["p50_s"])
        self.assertLess(four["drain_s"], one["drain_s"])

    def test_short_visibility_timeout_causes_duplicates(self):
        short = self.run_cfg(consumers=16, visibility_timeout_s=0.1)
        normal = self.run_cfg(consumers=16, visibility_timeout_s=5.0)
        self.assertGreater(short["duplicates"], normal["duplicates"])

    def test_cli_prints_table(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.sim.main(["--jitter", "none", "full", "--messages", "50"])
        self.assertEqual(code, 0)
        self.assertIn("retry peak", out.getvalue())
        rows = [line for line in out.getvalue().splitlines() if line.strip().startswith("4 |")]
        self.assertEqual(len(rows), 2)  # one row per jitter mode


if __name__ == "__main__":
    unittest.main()
