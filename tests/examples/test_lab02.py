"""Smoke test for Lab 02 (cache hit and miss): LRU and TTL rules, and the relationships the lab teaches."""
import contextlib
import importlib
import io
import json
import py_compile
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "labs" / "local" / "lab-02-cache-hit-and-miss"


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


class Lab02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cache = load("lab02_cache")
        cls.workload = load("lab02_workload")
        cls.sim = load("lab02_cache_aside")
        cls.cli = load("lab02_run")
        # Shorter simulated runs than the lab's defaults keep the test fast; the shape is the same.
        cls.size_rows = cls.cli.run_size(duration_s=120.0)
        cls.ttl_rows = cls.cli.run_ttl(duration_s=120.0, ttls=[1, 30, 600])

    def test_sources_compile(self):
        for p in LAB.glob("*.py"):
            py_compile.compile(str(p), doraise=True)

    def test_lru_eviction_and_lazy_ttl_expiry(self):
        c = self.cache.LRUCache(capacity=2)
        c.set("a", "x", 1, ttl_s=30, now=0)
        c.set("b", "x", 1, ttl_s=30, now=0)
        self.assertIsNotNone(c.get("a", now=1))        # a is now most recently used
        c.set("c", "x", 1, ttl_s=30, now=2)            # evicts b, the least recently used
        self.assertEqual(c.keys_lru_first(), ["a", "c"])
        self.assertEqual(c.evictions, 1)
        self.assertIsNotNone(c.get("a", now=29.9))
        self.assertIsNone(c.get("a", now=30.0))        # expiry is inclusive of the deadline
        self.assertEqual(c.expirations, 1)
        self.assertTrue(c.delete("c"))
        self.assertFalse(c.delete("c"))
        with self.assertRaises(ValueError):
            self.cache.LRUCache(0)

    def test_workload_is_seeded_and_skewed(self):
        a = self.workload.tracking_workload(duration_s=20.0, seed=7)
        self.assertEqual(a, self.workload.tracking_workload(duration_s=20.0, seed=7))
        self.assertNotEqual(a, self.workload.tracking_workload(duration_s=20.0, seed=8))
        self.assertEqual(a, sorted(a, key=lambda e: (e[0], e[1])))
        reads = [k for _, kind, k in a if kind == "read"]
        self.assertAlmostEqual(len(reads) / 20.0, 210, delta=25)
        top100 = sum(1 for k in reads if k < 100) / len(reads)
        self.assertGreater(top100, 0.35)                # Zipf s=1: about 45% of reads hit the top 100
        import random
        z = self.workload.Zipf(50_000, 1.0, random.Random(1))
        self.assertAlmostEqual(z.share_of_top(100), 0.455, places=2)

    def test_hit_ratio_rises_with_cache_size(self):
        ratios = [r["hit_ratio"] for r in self.size_rows]
        self.assertEqual(ratios, sorted(ratios))        # never falls as the cache grows
        self.assertGreater(ratios[-1] - ratios[0], 0.15)
        calls = [r["backend_calls"] for r in self.size_rows]
        self.assertEqual(calls, sorted(calls, reverse=True))
        self.assertEqual(self.size_rows[-1]["evictions"], 0)   # every shipment fits
        self.assertGreater(self.size_rows[0]["evictions"], 0)

    def test_hit_ratio_matches_the_arithmetic(self):
        for r in self.size_rows:
            m = self.cli.model(r["hit_ratio"])
            self.assertAlmostEqual(r["avg_latency_ms"], m["avg_ms"], places=6)
            self.assertEqual(r["backend_calls"], r["reads"] - r["hits"])
        self.assertAlmostEqual(self.cli.model(0.9)["backend_per_s"], 21.0)
        self.assertAlmostEqual(self.cli.model(0.9)["avg_ms"], 3.0)

    def test_longer_ttl_more_hits_and_more_stale_reads(self):
        ttl_only = [r for r in self.ttl_rows if not r["invalidate"]]
        invalidated = [r for r in self.ttl_rows if r["invalidate"]]
        self.assertEqual([r["ttl_s"] for r in ttl_only], [1, 30, 600])
        hits = [r["hit_ratio"] for r in ttl_only]
        stale = [r["stale_reads"] for r in ttl_only]
        self.assertEqual(hits, sorted(hits))
        self.assertEqual(stale, sorted(stale))
        self.assertGreater(stale[-1], 10 * max(stale[0], 1))
        for r in ttl_only:
            self.assertLessEqual(r["max_staleness_s"], r["ttl_s"])   # TTL bounds staleness
        # Delete-on-write removes almost all staleness at the same TTL.
        for a, b in zip(ttl_only, invalidated):
            self.assertLessEqual(b["stale_reads"], a["stale_reads"])
        self.assertLess(invalidated[-1]["stale_reads"], ttl_only[-1]["stale_reads"] / 50)

    def test_single_flight_stops_the_stampede(self):
        off, on = self.cli.run_stampede(duration_s=120.0)
        self.assertEqual(off["reads"], on["reads"])
        self.assertGreater(off["backend_calls"], 10 * on["backend_calls"])
        self.assertGreater(off["peak_inflight"], 10)
        self.assertEqual(on["peak_inflight"], 1)
        self.assertEqual(on["backend_calls"], off["expirations"] + 1)   # one load per expiry
        self.assertEqual(on["hits"] + on["coalesced"] + on["backend_calls"], on["reads"])

    def test_jitter_flattens_the_expiry_wave(self):
        fixed, jittered = self.cli.run_jitter(duration_s=120.0)
        self.assertLess(jittered["peak_calls"], 0.75 * fixed["peak_calls"])
        self.assertAlmostEqual(jittered["backend_calls"], fixed["backend_calls"], delta=0.02 * fixed["backend_calls"])

    def test_cli_prints_tables_and_json(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(self.cli.main(["stampede"], out=out), 0)
        self.assertIn("loads per expiry without single-flight", out.getvalue())
        out = io.StringIO()
        self.assertEqual(self.cli.main(["jitter", "--json"], out=out), 0)
        data = json.loads(out.getvalue())
        self.assertEqual([r["jitter"] for r in data["jitter"]], [0.0, 0.2])


if __name__ == "__main__":
    unittest.main()
