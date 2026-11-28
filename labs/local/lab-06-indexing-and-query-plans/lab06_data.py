#!/usr/bin/env python3
"""Lab 06 data: a seeded, AtlasMart-like scan-events table in SQLite (standard library only).

Each shipment gets 8 carrier scans (label created, picked up, four hub scans, out for delivery,
delivered) spread over hours, inside a 180-day window that ends on 2026-11-27. There are no
addresses or customer data (AtlasMart's NFR-6). The volume is a scaled-down sample, not AtlasMart's
real traffic: the default 37,500 shipments give 300,000 rows.

Run on its own to print a summary:  python3 lab06_data.py --shipments 37500 --seed 6
"""
import argparse
import random
import sqlite3
import time
from datetime import datetime, timedelta

WINDOW_END = datetime(2026, 11, 27)
WINDOW_DAYS = 180
CARRIERS = 12
EVENTS_PER_SHIPMENT = 8
STATUSES = ("label_created", "picked_up", "in_transit", "in_transit", "in_transit", "in_transit",
            "out_for_delivery", "delivered")
HUBS = tuple(f"hub-{i:02d}" for i in range(1, 31))

SCHEMA = """
CREATE TABLE scan_events (
    event_id          INTEGER PRIMARY KEY,  -- SQLite's rowid: the table is a B-tree keyed by it
    shipment_id       INTEGER NOT NULL,
    carrier_id        INTEGER NOT NULL,
    carrier_event_id  TEXT    NOT NULL,     -- the carrier's own id, for example C07-00000042
    status            TEXT    NOT NULL,
    location_text     TEXT    NOT NULL,
    occurred_at       TEXT    NOT NULL,     -- ISO 8601 text, so string order is time order
    received_at       TEXT    NOT NULL
)"""

INSERT = ("INSERT INTO scan_events (shipment_id, carrier_id, carrier_event_id, status, location_text, "
          "occurred_at, received_at) VALUES (?, ?, ?, ?, ?, ?, ?)")


def generate(shipments, seed):
    """Yield one tuple per scan event, deterministically for a given seed."""
    rng = random.Random(seed)
    start = WINDOW_END - timedelta(days=WINDOW_DAYS)
    days = [(start + timedelta(days=d)).strftime("%Y-%m-%d") for d in range(WINDOW_DAYS + 1)]

    def fmt(s):  # seconds since the window start -> 'YYYY-MM-DD HH:MM:SS' (much faster than strftime)
        d, rest = divmod(s, 86_400)
        h, rest = divmod(rest, 3_600)
        m, sec = divmod(rest, 60)
        return f"{days[d]} {h:02d}:{m:02d}:{sec:02d}"

    span_s = (WINDOW_DAYS - 6) * 86_400          # leave room for the last shipment's later scans
    per_carrier = [0] * (CARRIERS + 1)
    for shipment_id in range(1, shipments + 1):
        carrier = rng.randint(1, CARRIERS)
        t = rng.randrange(span_s)
        for status in STATUSES:
            per_carrier[carrier] += 1
            yield (shipment_id, carrier, f"C{carrier:02d}-{per_carrier[carrier]:08d}", status,
                   rng.choice(HUBS), fmt(t), fmt(t + rng.randint(1, 120)))
            t += rng.randint(1_800, 54_000)       # 30 minutes to 15 hours to the next scan


def connect(path=":memory:"):
    return sqlite3.connect(path)


def build(conn, shipments=37_500, seed=6):
    """Create scan_events with no secondary index and load it. Returns the number of rows."""
    conn.execute("DROP TABLE IF EXISTS scan_events")
    conn.execute(SCHEMA)
    with conn:
        conn.executemany(INSERT, generate(shipments, seed))
    return conn.execute("SELECT count(*) FROM scan_events").fetchone()[0]


def summary(conn):
    row = conn.execute("SELECT count(*), count(DISTINCT shipment_id), min(received_at), max(received_at), "
                       "count(DISTINCT carrier_id) FROM scan_events").fetchone()
    pages = conn.execute("PRAGMA page_count").fetchone()[0]
    page_size = conn.execute("PRAGMA page_size").fetchone()[0]
    return {"rows": row[0], "shipments": row[1], "first": row[2], "last": row[3], "carriers": row[4],
            "pages": pages, "mb": round(pages * page_size / 1_000_000, 1)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shipments", type=int, default=37_500)
    ap.add_argument("--seed", type=int, default=6)
    args = ap.parse_args()
    conn = connect()
    t0 = time.perf_counter()
    build(conn, args.shipments, args.seed)
    s = summary(conn)
    print(f"built scan_events in {time.perf_counter() - t0:.1f} s")
    print(f"rows {s['rows']:,}  shipments {s['shipments']:,}  carriers {s['carriers']}  "
          f"received_at {s['first']} .. {s['last']}")
    print(f"table size {s['pages']:,} pages ({s['mb']} MB), no secondary indexes")
    for r in conn.execute("SELECT * FROM scan_events WHERE shipment_id = 1042 ORDER BY occurred_at"):
        print("  ", r)


if __name__ == "__main__":
    main()
