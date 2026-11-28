#!/usr/bin/env python3
"""Lab 02: add a cache and compare hit/miss behavior. Runs the five experiments.

    python3 lab02_run.py size         # hit ratio vs cache size (TTL 30 s, delete-on-write)
    python3 lab02_run.py ttl          # hit ratio and stale reads vs TTL, with and without invalidation
    python3 lab02_run.py stampede     # one hot key expiring, without and with single-flight
    python3 lab02_run.py jitter       # many keys loaded together expiring together, fixed vs jittered TTL
    python3 lab02_run.py arithmetic   # hit ratio -> backend load and average latency, model vs simulation
    python3 lab02_run.py all

Options: --seed N (workload seed, default 2), --duration S (simulated seconds for size and ttl,
default 600), --json (machine-readable output). Simulated time only: the whole lab runs in seconds.
"""
import argparse
import json
import sys

from lab02_cache_aside import Settings, simulate
from lab02_workload import campaign_workload, hot_key_workload, tracking_workload

N_KEYS = 50_000                 # shipments in the lab (a sample of AtlasMart's 300,000 in transit)
ENTRY_KB = 4                    # cached status payload, from the capacity page
SIZES = [100, 500, 1_000, 2_000, 5_000, 10_000, 50_000]
TTLS = [1, 5, 30, 120, 600]


def run_size(seed=2, duration_s=600.0, sizes=SIZES):
    events = tracking_workload(n_keys=N_KEYS, duration_s=duration_s, seed=seed)
    return [dict(capacity=c, **simulate(events, N_KEYS, Settings(capacity=c))) for c in sizes]


def run_ttl(seed=2, duration_s=600.0, ttls=TTLS):
    events = tracking_workload(n_keys=N_KEYS, duration_s=duration_s, seed=seed)
    rows = []
    for invalidate in (False, True):
        for ttl in ttls:
            r = simulate(events, N_KEYS, Settings(ttl_s=ttl, invalidate=invalidate))
            rows.append(dict(ttl_s=ttl, invalidate=invalidate, **r))
    return rows


def run_stampede(seed=2, db_ms=200.0, read_rate=150.0, duration_s=300.0):
    events = hot_key_workload(read_rate=read_rate, duration_s=duration_s, seed=seed)
    return [dict(single_flight=sf, **simulate(events, 1, Settings(capacity=10, db_ms=db_ms, single_flight=sf)))
            for sf in (False, True)]


def run_jitter(seed=2, customers=2_000, duration_s=300.0, jitter=0.2):
    events = campaign_workload(customers=customers, duration_s=duration_s, seed=seed)
    rows = []
    for j in (0.0, jitter):
        r = simulate(events, customers, Settings(capacity=customers, jitter=j, seed=seed))
        after_warmup = {sec: n for sec, n in r["calls_per_s"].items() if sec >= 5}
        peak_sec = max(after_warmup, key=after_warmup.get)
        rows.append(dict(jitter=j, peak_s=peak_sec, peak_calls=after_warmup[peak_sec], **r))
    return rows


def model(hit_ratio, hit_ms=1.0, db_ms=20.0, read_rate=210.0):
    """The arithmetic: every read pays the cache lookup; misses also pay the database."""
    return {"backend_per_s": read_rate * (1 - hit_ratio), "avg_ms": hit_ms + (1 - hit_ratio) * db_ms}


def print_size(rows, out):
    print("Experiment 1: hit ratio vs cache size (Zipf s=1.0 over 50,000 shipments, 210 reads/s, "
          "70 scans/s, TTL 30 s, delete-on-write)", file=out)
    print(f"{'slots':>7} {'memory':>9} {'hit ratio':>9} {'backend calls':>13} {'backend ms':>11} "
          f"{'avg ms':>7} {'evictions':>9} {'stale':>6}", file=out)
    for r in rows:
        mem = r["capacity"] * ENTRY_KB / 1000
        print(f"{r['capacity']:>7,} {mem:>6.1f} MB {r['hit_ratio']:>9.1%} {r['backend_calls']:>13,} "
              f"{r['backend_ms']:>11,.0f} {r['avg_latency_ms']:>7.2f} {r['evictions']:>9,} "
              f"{r['stale_reads']:>6,}", file=out)
    print(f"reads: {rows[0]['reads']:,}   scans: {rows[0]['writes']:,}", file=out)


def print_ttl(rows, out):
    print("Experiment 2: TTL vs hit ratio and staleness (cache holds all 50,000 shipments)", file=out)
    print(f"{'invalidation':<14} {'TTL s':>6} {'hit ratio':>9} {'backend calls':>13} {'stale reads':>11} "
          f"{'stale %':>7} {'mean stale s':>12} {'max stale s':>11}", file=out)
    for r in rows:
        label = "delete-on-write" if r["invalidate"] else "TTL only"
        print(f"{label:<14} {r['ttl_s']:>6} {r['hit_ratio']:>9.1%} {r['backend_calls']:>13,} "
              f"{r['stale_reads']:>11,} {r['stale_share']:>7.2%} {r['mean_staleness_s']:>12.1f} "
              f"{r['max_staleness_s']:>11.1f}", file=out)


def print_stampede(rows, out):
    print("Experiment 3: one viral shipment, 150 reads/s for 300 s, TTL 30 s, 200 ms database read", file=out)
    print(f"{'single-flight':<14} {'reads':>6} {'hits':>6} {'coalesced':>9} {'backend calls':>13} "
          f"{'peak in flight':>14} {'avg ms':>7} {'max ms':>7}", file=out)
    for r in rows:
        print(f"{'on' if r['single_flight'] else 'off':<14} {r['reads']:>6,} {r['hits']:>6,} "
              f"{r['coalesced']:>9,} {r['backend_calls']:>13,} {r['peak_inflight']:>14} "
              f"{r['avg_latency_ms']:>7.2f} {r['max_latency_ms']:>7.1f}", file=out)
    off = rows[0]
    expiries = off["expirations"] + 1    # the cold start plus every expiry
    print(f"loads per expiry without single-flight: {off['backend_calls']} / {expiries} "
          f"= {off['backend_calls'] / expiries:.1f}", file=out)


def print_jitter(rows, out):
    print("Experiment 4: 2,000 customers sent to their pages in one second, refreshing every ~5 s, "
          "TTL 30 s", file=out)
    print(f"{'TTL jitter':<11} {'backend calls':>13} {'hit ratio':>9} {'peak calls in 1 s (after 5 s)':>30}",
          file=out)
    for r in rows:
        label = "none" if r["jitter"] == 0 else f"+/-{r['jitter']:.0%}"
        print(f"{label:<11} {r['backend_calls']:>13,} {r['hit_ratio']:>9.1%} "
              f"{r['peak_calls']:>12} at second {r['peak_s']}", file=out)
    for r in rows:
        label = "none" if r["jitter"] == 0 else f"+/-{r['jitter']:.0%}"
        window = " ".join(f"{r['calls_per_s'].get(sec, 0):>3}" for sec in range(28, 41))
        print(f"calls per second 28..40, jitter {label:<7} {window}", file=out)


def print_arithmetic(rows, out):
    print("Experiment 5: from hit ratio to backend load and latency (hit 1 ms, miss 1 + 20 ms)", file=out)
    print(f"{'slots':>7} {'hit ratio':>9} {'model avg ms':>12} {'simulated avg ms':>16} "
          f"{'model calls':>11} {'simulated calls':>15}", file=out)
    for r in rows:
        m = model(r["hit_ratio"])
        print(f"{r['capacity']:>7,} {r['hit_ratio']:>9.1%} {m['avg_ms']:>12.2f} {r['avg_latency_ms']:>16.2f} "
              f"{r['reads'] * (1 - r['hit_ratio']):>11,.0f} {r['backend_calls']:>15,}", file=out)
    print("AtlasMart sale-day peak, 210 tracking reads/s:", file=out)
    print(f"{'hit ratio':>9} {'database reads/s':>16} {'avg latency ms':>14}", file=out)
    for h in (0.0, 0.5, 0.8, 0.9, 0.95, 0.99):
        m = model(h)
        print(f"{h:>9.0%} {m['backend_per_s']:>16.1f} {m['avg_ms']:>14.2f}", file=out)


def main(argv=None, out=None):
    out = out or sys.stdout
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("experiment", choices=["size", "ttl", "stampede", "jitter", "arithmetic", "all"])
    p.add_argument("--seed", type=int, default=2)
    p.add_argument("--duration", type=float, default=600.0)
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    results = {}
    if a.experiment in ("size", "arithmetic", "all"):
        results["size"] = run_size(a.seed, a.duration)
    if a.experiment in ("ttl", "all"):
        results["ttl"] = run_ttl(a.seed, a.duration)
    if a.experiment in ("stampede", "all"):
        results["stampede"] = run_stampede(a.seed)
    if a.experiment in ("jitter", "all"):
        results["jitter"] = run_jitter(a.seed)
    if a.json:
        for rows in results.values():
            for r in rows:
                r["calls_per_s"] = {str(k): v for k, v in r["calls_per_s"].items()}
        json.dump(results, out, indent=2)
        print(file=out)
        return 0
    printers = [("size", print_size), ("ttl", print_ttl), ("stampede", print_stampede), ("jitter", print_jitter)]
    first = True
    for name, printer in printers:
        if name in results and (a.experiment != "arithmetic"):
            if not first:
                print(file=out)
            printer(results[name], out)
            first = False
    if a.experiment in ("arithmetic", "all"):
        if not first:
            print(file=out)
        print_arithmetic(results["size"], out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
