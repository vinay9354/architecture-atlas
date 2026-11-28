#!/usr/bin/env python3
"""Lab 11: load script for tracking-api. Standard library only.

First it sends five probe requests that carry a client-made `traceparent` (one valid, four invalid in
different ways), so you can see in the logs which ones tracking-api continued and which it restarted.
Then it sends --requests plain requests (no traceparent) for shipments picked with a seeded random
generator, one at a time, and prints client-side latency percentiles.

  python3 load.py --url http://127.0.0.1:8011 --requests 200
"""
import argparse
import math
import random
import sys
import time
import urllib.error
import urllib.request

import traceparent

SHIPMENT_IDS = [f"SHP-{1000 + i}" for i in range(50)]


def probe_headers(seed):
    """(label, header) pairs. The valid one uses ids from a client-side generator."""
    ids = traceparent.IdGenerator(seed)
    good_trace, good_span = ids.trace_id(), ids.span_id()
    return [
        ("valid, sampled", traceparent.format_traceparent(good_trace, good_span, True)),
        ("uppercase hex", f"00-{good_trace.upper()}-{good_span.upper()}-01"),
        ("all-zero trace-id", f"00-{'0' * 32}-{good_span}-01"),
        ("version ff", f"ff-{good_trace}-{good_span}-01"),
        ("version 00 plus extra field", f"00-{good_trace}-{good_span}-01-extra"),
    ]


def send(base_url, shipment_id, header=None, timeout=5.0):
    """Return (status, seconds)."""
    headers = {"traceparent": header} if header else {}
    req = urllib.request.Request(f"{base_url.rstrip('/')}/track/{shipment_id}", headers=headers)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
            status = resp.status
    except urllib.error.HTTPError as e:
        e.close()
        status = e.code
    return status, time.perf_counter() - started


def percentile(sorted_values, p):
    """Nearest-rank percentile: the smallest value with at least p% of values at or below it."""
    rank = max(1, math.ceil(p / 100 * len(sorted_values)))
    return sorted_values[rank - 1]


def run(base_url, requests, seed=11, out=sys.stdout):
    print("probes (client-made traceparent headers):", file=out)
    for label, header in probe_headers(seed - 1):
        status, _ = send(base_url, "SHP-1000", header)
        print(f"  {label:<28} {header:<62} -> HTTP {status}", file=out)
    rng = random.Random(seed)
    statuses, latencies = {}, []
    for _ in range(requests):
        status, secs = send(base_url, rng.choice(SHIPMENT_IDS))
        statuses[status] = statuses.get(status, 0) + 1
        latencies.append(secs * 1000)
    latencies.sort()
    summary = {"requests": requests, "statuses": dict(sorted(statuses.items()))}
    if latencies:
        summary.update({f"p{p}": round(percentile(latencies, p), 1) for p in (50, 95, 99)})
        summary["max"] = round(latencies[-1], 1)
    print(f"sent {requests} requests, statuses {summary['statuses']}", file=out)
    if latencies:
        print(f"client-side latency ms: p50 {summary['p50']}  p95 {summary['p95']}  "
              f"p99 {summary['p99']}  max {summary['max']}", file=out)
    return summary


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--url", default="http://127.0.0.1:8011")
    p.add_argument("--requests", type=int, default=200)
    p.add_argument("--seed", type=int, default=11)
    args = p.parse_args(argv)
    run(args.url, args.requests, args.seed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
