#!/usr/bin/env python3
"""Lab 07: seeded AtlasMart tracking data, loaded into BOTH stores so their answers can be compared.

Everything here is a lab assumption scaled down to laptop size (AtlasMart itself has 300,000
shipments in transit): 1,500 customers, 6,000 shipments created over the 7 days before the lab's
"today" (2026-11-27), one shipment per order, 12 carriers, and 3-6 scan events per shipment. One
carrier (carrier-c) has a higher delay rate so that the ad-hoc query in Step 3 has answers.

Timestamps are ISO-8601 strings in UTC ("2026-11-26T08:15:00Z"), so sorting the strings sorts the
times, which both the SQL index and the key-value sort key rely on.

Run:  python3 lab07_data.py            prints a summary of the generated data
"""
import random
import sys
from collections import Counter
from datetime import datetime, timedelta

CARRIERS = [f"carrier-{c}" for c in "abcdefghijkl"]          # 12 carriers (AtlasMart fact)
TODAY = datetime(2026, 11, 27)                               # lab clock: midnight UTC
YESTERDAY = (TODAY - timedelta(days=1)).strftime("%Y-%m-%d")
DAYS = 7

# Share of shipments per carrier. Normal days: the largest carrier has 20% (lab assumption).
NORMAL_SHARE = {c: (0.20 if c == "carrier-a" else 0.80 / 11) for c in CARRIERS}
# Sale day: a promotion ships with carrier-a's express service, which takes 40% (page assumption).
SALE_SHARE = {c: (0.40 if c == "carrier-a" else 0.60 / 11) for c in CARRIERS}
DELAY_RATE = {c: (0.25 if c == "carrier-c" else 0.05) for c in CARRIERS}

# (status, min hours after the previous event, max hours)
LIFECYCLE = [("PICKED_UP", 1, 6), ("IN_TRANSIT", 4, 16), ("DELAYED", 6, 20),
             ("OUT_FOR_DELIVERY", 8, 24), ("DELIVERED", 1, 8)]


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def generate(seed=7, customers=1500, shipments=6000):
    """Return {"customers", "orders", "shipments", "events"} as lists of dicts, fully determined by seed."""
    rng = random.Random(seed)
    cust_ids = [f"C{n:05d}" for n in range(1, customers + 1)]
    # A few customers order a lot, most order rarely (a Zipf-like skew).
    weights = [1 / (rank ** 0.8) for rank in range(1, customers + 1)]
    carriers, carrier_w = list(NORMAL_SHARE), list(NORMAL_SHARE.values())
    start = TODAY - timedelta(days=DAYS)
    orders, ships, events = [], [], []
    for n in range(1, shipments + 1):
        sid, oid = f"S{n:06d}", f"O{n:06d}"
        cid = rng.choices(cust_ids, weights)[0]
        carrier = rng.choices(carriers, carrier_w)[0]
        created = start + timedelta(seconds=rng.randrange(DAYS * 86400))
        orders.append({"order_id": oid, "customer_id": cid, "created_at": iso(created)})
        history, t = [("CREATED", created)], created
        for status, lo, hi in LIFECYCLE:
            if status == "DELAYED" and rng.random() >= DELAY_RATE[carrier]:
                continue
            t = t + timedelta(seconds=rng.randrange(lo * 3600, hi * 3600))
            if t >= TODAY:                       # not happened yet at the lab's "now"
                break
            history.append((status, t))
        for status, when in history:
            events.append({"event_id": f"E{len(events) + 1:07d}", "shipment_id": sid, "carrier": carrier,
                           "status": status, "occurred_at": iso(when)})
        ships.append({"shipment_id": sid, "order_id": oid, "customer_id": cid, "carrier": carrier,
                      "current_status": history[-1][0], "created_at": iso(created)})
    return {"customers": cust_ids, "orders": orders, "shipments": ships, "events": events}


def summary(data, out=sys.stdout):
    ships, events = data["shipments"], data["events"]
    per_customer = Counter(s["customer_id"] for s in ships)
    top_cid, top_n = per_customer.most_common(1)[0]
    print(f"customers {len(data['customers'])}  orders {len(data['orders'])}  shipments {len(ships)}  "
          f"scan events {len(events)}", file=out)
    print(f"customers with at least one shipment: {len(per_customer)}   busiest: {top_cid} "
          f"with {top_n} shipments", file=out)
    print("shipments per carrier:", dict(sorted(Counter(s['carrier'] for s in ships).items())), file=out)
    print("current status:", dict(sorted(Counter(s['current_status'] for s in ships).items())), file=out)
    delayed_y = [e for e in events if e["status"] == "DELAYED" and e["occurred_at"].startswith(YESTERDAY)]
    print(f"DELAYED events yesterday ({YESTERDAY}): {len(delayed_y)}, of which carrier-c: "
          f"{sum(e['carrier'] == 'carrier-c' for e in delayed_y)}", file=out)


if __name__ == "__main__":
    summary(generate())
