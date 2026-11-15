"""Smoke test for Lab 01 (latency and throughput): the server and load generator run end to end."""
import importlib.util
import py_compile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-01-latency-and-throughput"


def load(name):
    spec = importlib.util.spec_from_file_location(name, LAB / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Lab01Tests(unittest.TestCase):
    def test_sources_compile(self):
        for p in LAB.glob("*.py"):
            py_compile.compile(str(p), doraise=True)

    def test_percentile_nearest_rank(self):
        loadgen = load("loadgen")
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.assertEqual(loadgen.percentile(values, 50), 5)
        self.assertEqual(loadgen.percentile(values, 95), 10)
        self.assertEqual(loadgen.percentile([7], 99), 7)

    def test_server_and_loadgen_end_to_end(self):
        server_mod, loadgen = load("server"), load("loadgen")
        server = server_mod.make_server("127.0.0.1", 0, service_ms=5, jitter_ms=0, max_workers=4)
        port = server.server_address[1]
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        try:
            r = loadgen.run_level(f"http://127.0.0.1:{port}/status/1", concurrency=2, duration_s=0.6, warmup_s=0.1)
        finally:
            server.shutdown()
            server.server_close()
        self.assertEqual(r["errors"], 0)
        self.assertGreater(r["requests"], 20)
        self.assertGreaterEqual(r["p50_ms"], 5.0)  # cannot be faster than the service time
        self.assertLess(r["p50_ms"], 100.0)
        self.assertAlmostEqual(r["littles_law_L"], 2, delta=0.6)  # closed loop: L ~ concurrency


if __name__ == "__main__":
    unittest.main()
