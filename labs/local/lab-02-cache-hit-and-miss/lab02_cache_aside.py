"""Lab 02: the cache-aside read path, replayed on a simulated clock.

For each tracking read at time t:

1. Loads that finished by t write their result into the cache (with a TTL, optionally jittered).
2. Look up the cache. A live entry is a **hit** (cost `hit_ms`). If its version is older than the
   database's current version, the read is **stale**; staleness is t minus the commit time of the
   first version the reader missed.
3. On a miss, without single-flight: query the database (cost `hit_ms + db_ms`); the result reaches
   the cache only when the query finishes, `db_ms` later. Every read of the same key that arrives in
   that window also misses and sends its own query: that is the **stampede**.
4. On a miss with single-flight (request coalescing): if a load for this key is already in flight,
   wait for it instead of querying (cost `hit_ms` plus the remaining wait). Only the first miss
   queries the database.

A carrier scan (write) updates the database. With `invalidate=True` it also deletes the cache entry
(delete-on-write). A load that read the old version before the write and finishes after it still
stores the old value: the race the caching page describes, counted here as stale reads.
"""
import heapq
import random
from collections import Counter
from dataclasses import dataclass

from lab02_backend import SimulatedDatabase
from lab02_cache import LRUCache
from lab02_workload import READ


@dataclass
class Settings:
    capacity: int = 50_000          # cache slots (entries)
    ttl_s: float = 30.0             # AtlasMart Status Cache TTL
    jitter: float = 0.0             # 0.2 means each TTL is drawn from 0.8 x ttl .. 1.2 x ttl
    invalidate: bool = True         # delete-on-write from the Event Processor
    single_flight: bool = False     # request coalescing per key
    hit_ms: float = 1.0             # cache round trip (lab assumption)
    db_ms: float = 20.0             # database query (lab assumption)
    seed: int = 2                   # for the TTL jitter


def percentile(sorted_values, p):
    """Nearest-rank percentile of an already sorted list."""
    if not sorted_values:
        return 0.0
    rank = max(1, -(-len(sorted_values) * p // 100))
    return sorted_values[int(rank) - 1]


def simulate(events, n_keys, settings):
    """Replay events through cache-aside and return a dictionary of measurements."""
    s = settings
    rng = random.Random(s.seed)
    db = SimulatedDatabase(n_keys, read_ms=s.db_ms)
    cache = LRUCache(s.capacity)
    db_s = s.db_ms / 1000.0
    pending = []                 # heap of (finish_time, seq, key, status, version)
    inflight = {}                # key -> finish time of its single-flight load
    seq = 0
    reads = hits = coalesced = stale = 0
    staleness = []
    latencies = []
    calls_per_s = Counter()
    peak_inflight = 0

    def finish_loads(now):
        while pending and pending[0][0] <= now:
            done, _, key, status, version = heapq.heappop(pending)
            ttl = s.ttl_s * (1.0 + rng.uniform(-s.jitter, s.jitter)) if s.jitter else s.ttl_s
            cache.set(key, status, version, ttl, done)
            if inflight.get(key) == done:
                del inflight[key]

    def check_stale(key, version, now):
        nonlocal stale
        if version < db.version(key):
            stale += 1
            staleness.append(now - db.committed_at(key, version + 1))

    for t, kind, key in events:
        finish_loads(t)
        if kind != READ:
            db.write(key, t)
            if s.invalidate:
                cache.delete(key)
            continue
        reads += 1
        entry = cache.get(key, t)
        if entry is not None:
            hits += 1
            latencies.append(s.hit_ms)
            check_stale(key, entry.version, t)
            continue
        if s.single_flight and key in inflight:
            coalesced += 1
            latencies.append(s.hit_ms + (inflight[key] - t) * 1000.0)
            continue
        status, version = db.read(key, t)
        calls_per_s[int(t)] += 1
        seq += 1
        heapq.heappush(pending, (t + db_s, seq, key, status, version))
        if s.single_flight:
            inflight[key] = t + db_s
        peak_inflight = max(peak_inflight, len(pending))
        latencies.append(s.hit_ms + s.db_ms)

    latencies.sort()
    staleness.sort()
    return {
        "reads": reads,
        "hits": hits,
        "coalesced": coalesced,
        "backend_calls": db.calls,
        "writes": db.writes,
        "hit_ratio": hits / reads if reads else 0.0,
        "backend_ms": db.busy_ms,
        "avg_latency_ms": sum(latencies) / reads if reads else 0.0,
        "p99_latency_ms": percentile(latencies, 99),
        "max_latency_ms": latencies[-1] if latencies else 0.0,
        "stale_reads": stale,
        "stale_share": stale / reads if reads else 0.0,
        "mean_staleness_s": sum(staleness) / len(staleness) if staleness else 0.0,
        "max_staleness_s": staleness[-1] if staleness else 0.0,
        "evictions": cache.evictions,
        "expirations": cache.expirations,
        "peak_inflight": peak_inflight,
        "calls_per_s": dict(sorted(calls_per_s.items())),
    }
