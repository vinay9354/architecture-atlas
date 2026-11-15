#!/usr/bin/env python3
"""Lab 01 load generator: closed-loop clients, latency percentiles, and a Little's Law check.

Standard library only. Each client thread sends one request, waits for the response, and
immediately sends the next (a "closed loop"), so the number of requests in flight equals the
number of clients. For each concurrency level it reports throughput, mean and percentile latency,
and the Little's Law product throughput x mean latency, which should be close to the concurrency.

Run:  python loadgen.py --url http://127.0.0.1:8080/status/42 --concurrency 1 4 8 16 32 --duration 5
"""
import argparse
import http.client
import json
import math
import statistics
import sys
import threading
import time
from urllib.parse import urlsplit


def percentile(sorted_values, p):
    """Nearest-rank percentile on an ascending list; p in 0..100."""
    if not sorted_values:
        return float("nan")
    k = max(0, min(len(sorted_values) - 1, math.ceil(p / 100.0 * len(sorted_values)) - 1))
    return sorted_values[k]


def worker(host, port, path, stop_at, latencies, errors, lock):
    conn = http.client.HTTPConnection(host, port, timeout=30)
    local = []
    local_errors = 0
    try:
        while time.perf_counter() < stop_at:
            t0 = time.perf_counter()
            try:
                conn.request("GET", path)
                resp = conn.getresponse()
                resp.read()
                if resp.status != 200:
                    local_errors += 1
            except (OSError, http.client.HTTPException):
                local_errors += 1
                conn.close()
                conn = http.client.HTTPConnection(host, port, timeout=30)
                continue
            local.append(time.perf_counter() - t0)
    finally:
        conn.close()
    with lock:
        latencies.extend(local)
        errors[0] += local_errors


def run_level(url, concurrency, duration_s, warmup_s=0.5):
    parts = urlsplit(url)
    host, port = parts.hostname, parts.port or 80
    path = parts.path or "/"
    latencies, errors, lock = [], [0], threading.Lock()
    # Warm-up: open connections and let the server settle before the measured window.
    stop_at = time.perf_counter() + warmup_s + duration_s
    threads = [threading.Thread(target=worker, args=(host, port, path, stop_at, latencies, errors, lock),
                                daemon=True) for _ in range(concurrency)]
    t_start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - t_start
    if not latencies:
        return {"concurrency": concurrency, "requests": 0, "errors": errors[0], "elapsed_s": elapsed}
    lat = sorted(latencies)
    n = len(lat)
    mean = statistics.fmean(lat)
    rps = n / elapsed
    return {
        "concurrency": concurrency,
        "requests": n,
        "errors": errors[0],
        "elapsed_s": round(elapsed, 2),
        "throughput_rps": round(rps, 1),
        "mean_ms": round(mean * 1000, 1),
        "p50_ms": round(percentile(lat, 50) * 1000, 1),
        "p95_ms": round(percentile(lat, 95) * 1000, 1),
        "p99_ms": round(percentile(lat, 99) * 1000, 1),
        "max_ms": round(lat[-1] * 1000, 1),
        "littles_law_L": round(rps * mean, 2),  # should be close to concurrency (closed loop)
    }


def print_table(rows):
    cols = ["concurrency", "requests", "errors", "throughput_rps", "mean_ms", "p50_ms", "p95_ms", "p99_ms",
            "max_ms", "littles_law_L"]
    head = ["clients", "requests", "errors", "req/s", "mean ms", "p50 ms", "p95 ms", "p99 ms", "max ms", "rps x mean"]
    print(" | ".join(f"{h:>10}" for h in head))
    print("-+-".join("-" * 10 for _ in head))
    for r in rows:
        print(" | ".join(f"{str(r.get(c, '')):>10}" for c in cols))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://127.0.0.1:8080/status/42")
    ap.add_argument("--concurrency", type=int, nargs="+", default=[1, 2, 4, 8, 16, 32])
    ap.add_argument("--duration", type=float, default=5.0, help="measured seconds per level")
    ap.add_argument("--json", help="also write results to this file")
    args = ap.parse_args()
    rows = []
    for c in args.concurrency:
        r = run_level(args.url, c, args.duration)
        rows.append(r)
        print(f"clients={c:<4} req/s={r.get('throughput_rps', 0):<8} p50={r.get('p50_ms', '-')} ms "
              f"p95={r.get('p95_ms', '-')} ms p99={r.get('p99_ms', '-')} ms errors={r['errors']}", flush=True)
    print()
    print_table(rows)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)
        print(f"\nwrote {args.json}")
    return 0 if all(r["errors"] == 0 for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
