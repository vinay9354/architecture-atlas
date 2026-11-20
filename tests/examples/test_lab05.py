"""Smoke test for Lab 05 (race condition): lost updates appear in the racy modes and vanish in the fixed ones."""
import contextlib
import importlib.util
import io
import os
import py_compile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-05-race-condition"


def load(name):
    spec = importlib.util.spec_from_file_location(name, LAB / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Lab05CounterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lab = load("counter_race")

    def test_sources_compile(self):
        for p in LAB.glob("*.py"):
            py_compile.compile(str(p), doraise=True)

    def test_threads_racy_loses_updates(self):
        # The forced yield between read and write made the race show up on every run we tried. Thread
        # scheduling is still up to the platform, so allow up to three runs before calling it a failure.
        for _ in range(3):
            r = self.lab.run_threads("racy", threads=4, increments=2000)
            if r["lost_updates"]:
                break
        self.assertGreater(r["lost_updates"], 0)
        self.assertEqual(r["final"] + r["lost_updates"], r["expected"])

    def test_threads_locked_is_exact(self):
        r = self.lab.run_threads("locked", threads=4, increments=2000)
        self.assertEqual(r["final"], 8000)
        self.assertEqual(r["lost_updates"], 0)

    def test_sim_is_deterministic_and_racy(self):
        a = self.lab.run_sim("racy", threads=3, increments=500, seed=3)
        b = self.lab.run_sim("racy", threads=3, increments=500, seed=3)
        self.assertEqual(a, b)
        self.assertGreater(a["lost_updates"], 0)
        self.assertIn("lost", a["first_loss"][-1])

    def test_sim_locked_is_exact(self):
        r = self.lab.run_sim("locked", threads=3, increments=500, seed=3)
        self.assertEqual(r["lost_updates"], 0)
        self.assertIsNone(r["first_loss"])

    def test_cli_runs(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(self.lab.main(["--engine", "sim", "--increments", "200"]), 0)
        self.assertIn("First lost update", buf.getvalue())


class Lab05ShipmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lab = load("shipment_race")

    def run_mode(self, mode):
        with tempfile.TemporaryDirectory() as parent:
            r = self.lab.run_mode(mode, workers=2, scans=150, seed=5, directory=parent)
            self.assertEqual(os.listdir(parent), [])  # the lab removed its database directory
        return r

    def test_racy_read_then_write_loses_updates(self):
        for _ in range(3):  # same allowance as the counter test: scheduling is up to the platform
            r = self.run_mode("racy")
            if r["lost_updates"]:
                break
        self.assertGreater(r["lost_updates"], 0)
        self.assertEqual(r["scan_count"] + r["lost_updates"], r["expected"])

    def test_optimistic_version_check_is_exact(self):
        r = self.run_mode("optimistic")
        self.assertEqual(r["scan_count"], 300)
        self.assertEqual(r["version"], 300)  # one successful versioned write per scan

    def test_atomic_update_is_exact(self):
        r = self.run_mode("atomic")
        self.assertEqual(r["scan_count"], 300)
        self.assertEqual(r["conflicts_retried"], 0)


if __name__ == "__main__":
    unittest.main()
