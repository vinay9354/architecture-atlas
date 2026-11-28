#!/usr/bin/env python3
"""Lab 07: a sale-day write burst against the tracking table and its carrier-day index.

Assumptions (all labelled on the lab page):
- The burst is the 50x growth scenario from the scaling page: 3,500 scan events per second, here
  for 10 simulated seconds (35,000 writes).
- Sale-day carrier mix: carrier-a carries 40% of events, the other 11 carriers share 60%.
- Shipment ids are drawn from 300,000 shipments in transit (AtlasMart fact).
- Each table and index has 16 partitions and a budget of 500 writes per partition per second
  (the team's per-partition design budget, not any product's limit).

The base table is keyed by shipment, so the burst spreads evenly. The carrier-day index puts every
event of one carrier and day under one partition key; write sharding appends #0..#k-1 (a stable
hash of the shipment id) to spread that key over k partition keys.
"""
import random

from lab07_data import SALE_SHARE, TODAY
from lab07_kvstore import Table
from lab07_tracking_kv import carrier_day_keys, event_sk, shipment_pk


def sale_day_events(seed=11, rate=3500, seconds=10, in_transit=300_000):
    rng = random.Random(seed)
    carriers, weights = list(SALE_SHARE), list(SALE_SHARE.values())
    day = TODAY.strftime("%Y-%m-%d")
    n = 0
    for second in range(seconds):
        for _ in range(rate):
            n += 1
            yield second, {"type": "event", "event_id": f"E{n:07d}",
                           "shipment_id": f"S{rng.randrange(in_transit):06d}",
                           "carrier": rng.choices(carriers, weights)[0], "status": "IN_TRANSIT",
                           "occurred_at": f"{day}T10:00:{second:02d}Z"}


def simulate(shards=1, seed=11, rate=3500, seconds=10, partitions=16, budget=500):
    base = Table("tracking", partitions, budget)
    index = base.add_global_index(f"by_carrier_day_x{shards}", carrier_day_keys(shards), partitions,
                                  budget, sync=True)
    per_key = {}
    for second, ev in sale_day_events(seed, rate, seconds):
        base.put(shipment_pk(ev["shipment_id"]), event_sk(ev), ev, second)
        ipk = carrier_day_keys(shards)(ev)[0]
        per_key[ipk] = per_key.get(ipk, 0) + 1
    hot_pk, hot_n = max(per_key.items(), key=lambda kv: kv[1])
    total = rate * seconds
    load = {}
    for pk, n in per_key.items():
        part = index.partition_of(pk)
        load[part] = load.get(part, 0) + n
    hot_part = max(load, key=load.get)
    sharing = sorted(pk for pk in per_key if index.partition_of(pk) == hot_part)
    return {"shards": shards, "writes": total, "base": base.load_stats(seconds),
            "index": index.load_stats(seconds), "index_partition_keys": len(per_key),
            "hottest_key": hot_pk, "hottest_key_share": hot_n / total,
            "hottest_key_per_s": hot_n / seconds, "read_fanout": shards,
            "hottest_partition_keys": sharing}


def report(results, out):
    print("sale-day burst: 3,500 writes/s for 10 s, carrier-a 40%, 16 partitions, budget 500 writes/s "
          "per partition", file=out)
    print(f"{'design':<26}{'hottest key':<28}{'key/s':>7}{'hottest part/s':>16}{'mean part/s':>13}"
          f"{'hot ratio':>11}{'throttled':>11}{'read fan-out':>14}", file=out)
    first = results[0]
    b = first["base"]
    print(f"{'base table (SHP#id)':<26}{'(one per shipment)':<28}{'-':>7}{b['hottest_per_s']:>16.0f}"
          f"{b['mean_per_s']:>13.0f}{b['hot_ratio']:>11.2f}{b['throttled']:>11}{1:>14}", file=out)
    for r in results:
        i = r["index"]
        label = "index CAR#carrier#day" + ("" if r["shards"] == 1 else f" x{r['shards']}")
        print(f"{label:<26}{r['hottest_key']:<28}{r['hottest_key_per_s']:>7.0f}{i['hottest_per_s']:>16.0f}"
              f"{i['mean_per_s']:>13.0f}{i['hot_ratio']:>11.2f}{i['throttled']:>11}{r['read_fanout']:>14}",
              file=out)
    for r in results:
        keys = r["hottest_partition_keys"]
        print(f"index x{r['shards']}: {r['index_partition_keys']} partition keys in use; the hottest partition holds "
              f"{len(keys)} of them: {', '.join(k.split('#', 1)[1] for k in keys)}", file=out)
