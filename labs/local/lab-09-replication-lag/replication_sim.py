#!/usr/bin/env python3
"""Lab 09: replication lag, stale reads, and session guarantees in a discrete-event simulation.

Standard library only, deterministic for a given --seed, and no real sleeping: time is a simulated
clock in milliseconds. The model:

  * A leader commits writes (shipment status updates) in order and gives each one a log position
    (LSN 1, 2, 3, ...). Writes come from carriers (scan events) and from client sessions (for example
    a support agent changing a shipment's status).
  * Two asynchronous followers apply the leader's log in order. Each write reaches each follower after
    a random apply lag; a follower can never apply LSN n before LSN n-1, so one slow write delays
    every write behind it.
  * Client sessions read their own shipment: right after their own writes, and in page views of
    several reads a few milliseconds apart. A routing policy decides which replica serves each read.

Policies compared:
  1 any-follower      every read goes to a random follower
  2 leader-after-write a client's reads go to the leader for --pin-ms after that client's last write
  3 wait-for-position  a follower serves the read once it has applied the client's last write LSN,
                       waiting up to --wait-timeout-ms, then falling back to the leader
  4 sticky-follower    each client always reads from the same follower

Run:  python replication_sim.py --seed 9
      python replication_sim.py --seed 9 --lag-spike
"""
import argparse
import bisect
import json
import math
import random
import sys
from dataclasses import asdict, dataclass

POLICIES = ["any-follower", "leader-after-write", "wait-for-position", "sticky-follower"]
LEADER = "leader"


@dataclass
class Config:
    duration_s: float = 60.0          # simulated seconds
    clients: int = 50                 # client sessions; client i follows shipment i
    shipments: int = 1000             # carrier updates land on any of these
    carrier_rate: float = 70.0        # carrier writes per second (AtlasMart peak scan events)
    client_write_rate: float = 0.1    # writes per second per client
    view_rate: float = 1.0            # page views per second per client
    reads_per_view: int = 2           # reads in one page view (status widget, timeline, ...)
    view_gap_ms: float = 20.0         # gap between the reads of one page view
    raw_delay_ms: float = 200.0       # a client views its shipment 0..raw_delay_ms after writing
    lag_dist: str = "lognormal"       # lognormal | exponential | uniform | fixed
    lag_ms: float = 40.0              # median (lognormal), mean (exponential, uniform), or value (fixed)
    lag_sigma: float = 0.8            # shape of the lognormal
    pin_ms: float = 1000.0            # policy 2: read from the leader this long after a write
    wait_timeout_ms: float = 500.0    # policy 3: give up waiting and read from the leader
    lag_spike: bool = False           # make one follower fall far behind for a while
    spike_follower: int = 1
    spike_start_s: float = 20.0
    spike_duration_s: float = 10.0
    spike_ms: float = 5000.0          # extra apply lag for writes committed during the spike
    seed: int = 9


def percentile(sorted_values, p):
    """Nearest-rank percentile on an ascending list; p in 0..100 (same helper as Lab 01)."""
    if not sorted_values:
        return float("nan")
    k = max(0, min(len(sorted_values) - 1, math.ceil(p / 100.0 * len(sorted_values)) - 1))
    return sorted_values[k]


def draw_lag(cfg, rng):
    if cfg.lag_dist == "lognormal":
        return cfg.lag_ms * math.exp(rng.gauss(0.0, cfg.lag_sigma))
    if cfg.lag_dist == "exponential":
        return rng.expovariate(1.0 / cfg.lag_ms)
    if cfg.lag_dist == "uniform":
        return rng.uniform(0.0, 2.0 * cfg.lag_ms)
    if cfg.lag_dist == "fixed":
        return cfg.lag_ms
    raise ValueError(f"unknown lag distribution {cfg.lag_dist!r}")


def poisson_times(rate_per_s, duration_ms, rng):
    """Arrival times (ms) of a Poisson process."""
    times, t = [], 0.0
    if rate_per_s <= 0:
        return times
    while True:
        t += rng.expovariate(rate_per_s / 1000.0)
        if t >= duration_ms:
            return times
        times.append(t)


class Cluster:
    """The write log and, for each follower, the time at which it applied each LSN."""

    def __init__(self, cfg):
        rng = random.Random(cfg.seed)
        duration_ms = cfg.duration_s * 1000.0
        writes = [(t, rng.randrange(cfg.shipments), None) for t in poisson_times(cfg.carrier_rate, duration_ms, rng)]
        reads = []
        for c in range(cfg.clients):
            for t in poisson_times(cfg.client_write_rate, duration_ms, rng):
                writes.append((t, c, c))
                reads.extend(self._view(cfg, c, t + rng.uniform(0.0, cfg.raw_delay_ms)))
            for t in poisson_times(cfg.view_rate, duration_ms, rng):
                reads.extend(self._view(cfg, c, t))
        writes.sort()
        self.commit_ms = [t for t, _, _ in writes]            # index i holds LSN i+1
        self.write_key = [k for _, k, _ in writes]
        self.write_client = [c for _, _, c in writes]
        self.versions = {}                                    # key -> ascending LSNs that wrote it
        for i, k in enumerate(self.write_key):
            self.versions.setdefault(k, []).append(i + 1)
        self.reads = sorted(r for r in reads if r[0] < duration_ms)

        lag_rng = random.Random(cfg.seed + 1)
        spike_lo, spike_hi = cfg.spike_start_s * 1000.0, (cfg.spike_start_s + cfg.spike_duration_s) * 1000.0
        self.applied_ms, self.lags_ms = [], []
        for f in range(2):
            applied, lags, last = [], [], 0.0
            for t in self.commit_ms:
                lag = draw_lag(cfg, lag_rng)
                if cfg.lag_spike and f == cfg.spike_follower and spike_lo <= t < spike_hi:
                    lag += cfg.spike_ms
                last = max(last, t + lag)                     # in-order apply
                applied.append(last)
                lags.append(last - t)
            self.applied_ms.append(applied)
            self.lags_ms.append(lags)

    @staticmethod
    def _view(cfg, client, t):
        return [(t + i * cfg.view_gap_ms, client, client) for i in range(cfg.reads_per_view)]

    def position(self, replica, t):
        """Highest LSN the replica has at time t (leader: committed, follower: applied)."""
        times = self.commit_ms if replica == LEADER else self.applied_ms[replica]
        return bisect.bisect_right(times, t)

    def version(self, key, position):
        """Newest LSN that wrote `key` and is at or below `position` (0 means never written)."""
        lsns = self.versions.get(key, [])
        i = bisect.bisect_right(lsns, position)
        return lsns[i - 1] if i else 0

    def next_version(self, key, position):
        lsns = self.versions.get(key, [])
        i = bisect.bisect_right(lsns, position)
        return lsns[i] if i < len(lsns) else None


def simulate(cluster, cfg, policy):
    """Replay every write and read in time order under one routing policy and collect the metrics."""
    rng = random.Random(cfg.seed * 7919 + POLICIES.index(policy))
    events = [(t, 0, i) for i, t in enumerate(cluster.commit_ms) if cluster.write_client[i] is not None]
    events += [(t, 1, j) for j, (t, _, _) in enumerate(cluster.reads)]
    events.sort()
    last_lsn, last_write_ms, seen = {}, {}, {}
    staleness, waits = [], []
    ryw = mono = leader_reads = fallbacks = 0
    for t, kind, idx in events:
        if kind == 0:                                         # a client's own write commits
            client = cluster.write_client[idx]
            last_lsn[client], last_write_ms[client] = idx + 1, t
            continue
        _, client, key = cluster.reads[idx]
        serve_ms, replica = t, rng.randrange(2)
        if policy == "leader-after-write":
            if client in last_write_ms and t - last_write_ms[client] < cfg.pin_ms:
                replica = LEADER
        elif policy == "wait-for-position":
            target = last_lsn.get(client, 0)
            ready_ms = cluster.applied_ms[replica][target - 1] if target else t
            wait = max(0.0, ready_ms - t)
            if wait <= cfg.wait_timeout_ms:
                serve_ms = t + wait
            else:
                serve_ms, replica = t + cfg.wait_timeout_ms, LEADER
                fallbacks += 1
            waits.append(serve_ms - t)
        elif policy == "sticky-follower":
            replica = client % 2
        if replica == LEADER:
            leader_reads += 1

        got = cluster.version(key, cluster.position(replica, serve_ms))
        latest = cluster.version(key, cluster.position(LEADER, serve_ms))
        if got < latest:                                      # stale: a newer committed version exists
            missing = cluster.next_version(key, got)
            staleness.append(serve_ms - cluster.commit_ms[missing - 1])
        if got < last_lsn.get(client, 0) and cluster.write_key[last_lsn[client] - 1] == key:
            ryw += 1                                          # the client's own write is not visible
        if got < seen.get((client, key), 0):
            mono += 1                                         # older than something already shown
        seen[(client, key)] = max(seen.get((client, key), 0), got)

    n = len(cluster.reads)
    staleness.sort()
    waits.sort()
    return {
        "policy": policy,
        "reads": n,
        "stale_pct": round(100.0 * len(staleness) / n, 2),
        "stale_p50_ms": round(percentile(staleness, 50), 1) if staleness else 0.0,
        "stale_p99_ms": round(percentile(staleness, 99), 1) if staleness else 0.0,
        "stale_max_ms": round(staleness[-1], 1) if staleness else 0.0,
        "ryw_violations": ryw,
        "monotonic_violations": mono,
        "leader_pct": round(100.0 * leader_reads / n, 2),
        "wait_p99_ms": round(percentile(waits, 99), 1) if waits else 0.0,
        "fallbacks": fallbacks,
    }


def lag_summary(cluster):
    rows = []
    for f, lags in enumerate(cluster.lags_ms):
        s = sorted(lags)
        rows.append({"follower": f"follower-{f}", "p50_ms": round(percentile(s, 50), 1),
                     "p99_ms": round(percentile(s, 99), 1), "max_ms": round(s[-1], 1)})
    return rows


def run(cfg):
    cluster = Cluster(cfg)
    return {
        "config": asdict(cfg),
        "writes": len(cluster.commit_ms),
        "client_writes": sum(1 for c in cluster.write_client if c is not None),
        "lag": lag_summary(cluster),
        "policies": [simulate(cluster, cfg, p) for p in POLICIES],
    }


def print_table(rows, cols, head, width=10):
    widths = [max(width, len(h)) for h in head]
    widths[0] = max(widths[0], *(len(str(r[cols[0]])) for r in rows))
    print(" | ".join(f"{h:>{w}}" for h, w in zip(head, widths)))
    print("-+-".join("-" * w for w in widths))
    for r in rows:
        print(" | ".join(f"{str(r[c]):>{w}}" for c, w in zip(cols, widths)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    d = Config()
    ap.add_argument("--duration-s", type=float, default=d.duration_s, help="simulated seconds")
    ap.add_argument("--clients", type=int, default=d.clients)
    ap.add_argument("--carrier-rate", type=float, default=d.carrier_rate, help="carrier writes per second")
    ap.add_argument("--client-write-rate", type=float, default=d.client_write_rate, help="writes/s per client")
    ap.add_argument("--view-rate", type=float, default=d.view_rate, help="page views/s per client")
    ap.add_argument("--lag-dist", choices=["lognormal", "exponential", "uniform", "fixed"], default=d.lag_dist)
    ap.add_argument("--lag-ms", type=float, default=d.lag_ms, help="median, mean, or fixed lag (see --help)")
    ap.add_argument("--lag-sigma", type=float, default=d.lag_sigma, help="lognormal shape")
    ap.add_argument("--pin-ms", type=float, default=d.pin_ms, help="policy 2 leader window after a write")
    ap.add_argument("--wait-timeout-ms", type=float, default=d.wait_timeout_ms, help="policy 3 wait limit")
    ap.add_argument("--lag-spike", action="store_true", help="make follower-1 fall far behind for a while")
    ap.add_argument("--spike-ms", type=float, default=d.spike_ms, help="extra lag during the spike")
    ap.add_argument("--spike-start-s", type=float, default=d.spike_start_s)
    ap.add_argument("--spike-duration-s", type=float, default=d.spike_duration_s)
    ap.add_argument("--seed", type=int, default=d.seed)
    ap.add_argument("--json", help="also write results to this file")
    args = ap.parse_args()
    cfg = Config(duration_s=args.duration_s, clients=args.clients, carrier_rate=args.carrier_rate,
                 client_write_rate=args.client_write_rate, view_rate=args.view_rate, lag_dist=args.lag_dist,
                 lag_ms=args.lag_ms, lag_sigma=args.lag_sigma, pin_ms=args.pin_ms,
                 wait_timeout_ms=args.wait_timeout_ms, lag_spike=args.lag_spike, spike_ms=args.spike_ms,
                 spike_start_s=args.spike_start_s, spike_duration_s=args.spike_duration_s, seed=args.seed)
    res = run(cfg)
    spike = (f", lag spike on follower-{cfg.spike_follower}: +{cfg.spike_ms:.0f} ms for writes committed "
             f"{cfg.spike_start_s:.0f}-{cfg.spike_start_s + cfg.spike_duration_s:.0f} s") if cfg.lag_spike else ""
    print(f"{cfg.duration_s:.0f} simulated s, {res['writes']} writes ({res['client_writes']} from clients), "
          f"{res['policies'][0]['reads']} reads, seed {cfg.seed}{spike}\n")
    print(f"Apply lag per follower ({cfg.lag_dist}, {cfg.lag_ms:.0f} ms; includes waiting behind earlier writes)")
    print_table(res["lag"], ["follower", "p50_ms", "p99_ms", "max_ms"], ["follower", "p50 ms", "p99 ms", "max ms"])
    print("\nRead policies (staleness percentiles are over stale reads only)")
    print_table(res["policies"],
                ["policy", "stale_pct", "stale_p50_ms", "stale_p99_ms", "ryw_violations", "monotonic_violations",
                 "leader_pct", "wait_p99_ms", "fallbacks"],
                ["policy", "stale %", "stale p50", "stale p99", "RYW viol.", "mono viol.", "leader %",
                 "wait p99", "fallbacks"])
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
