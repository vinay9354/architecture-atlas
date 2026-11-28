#!/usr/bin/env python3
"""Lab 07: the relational model of AtlasMart tracking data in SQLite (standard library sqlite3).

Normalized tables (carriers, orders, shipments, scan_events) with foreign keys and one index per
known access pattern. Work is reported two ways, neither of which is a timing:

- the query plan from EXPLAIN QUERY PLAN ("SEARCH ... USING INDEX" or "SCAN ..."), and
- SQLite virtual-machine steps, counted with a progress handler called on every VM instruction.
  It is a deterministic proxy for "how much work did the engine do" for one SQLite version.
"""
import sqlite3
from datetime import date, timedelta

SCHEMA = """
CREATE TABLE carriers (
    carrier_id INTEGER PRIMARY KEY,
    code       TEXT NOT NULL UNIQUE
);
CREATE TABLE orders (
    order_id    TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
CREATE TABLE shipments (
    shipment_id    TEXT PRIMARY KEY,
    order_id       TEXT NOT NULL REFERENCES orders(order_id),
    carrier_id     INTEGER NOT NULL REFERENCES carriers(carrier_id),
    current_status TEXT NOT NULL,
    created_at     TEXT NOT NULL
);
CREATE TABLE scan_events (
    event_id    TEXT PRIMARY KEY,
    shipment_id TEXT NOT NULL REFERENCES shipments(shipment_id),
    status      TEXT NOT NULL,
    occurred_at TEXT NOT NULL
);
CREATE INDEX orders_by_customer ON orders(customer_id, created_at);
CREATE INDEX shipments_by_order ON shipments(order_id);
CREATE INDEX events_by_shipment ON scan_events(shipment_id, occurred_at, event_id);
"""

# The index an analyst would add for the ad-hoc query in Step 3 (not created by build()).
ADHOC_INDEX = "CREATE INDEX events_by_status_time ON scan_events(status, occurred_at)"

GET_SHIPMENT = """
SELECT s.shipment_id, o.customer_id, c.code, s.current_status, s.created_at
FROM shipments s
JOIN orders o   ON o.order_id = s.order_id
JOIN carriers c ON c.carrier_id = s.carrier_id
WHERE s.shipment_id = ?"""

CUSTOMER_RECENT = """
SELECT s.shipment_id
FROM orders o
JOIN shipments s ON s.order_id = o.order_id
WHERE o.customer_id = ?
ORDER BY s.created_at DESC, s.shipment_id DESC
LIMIT ?"""

SHIPMENT_EVENTS = """
SELECT event_id, status, occurred_at
FROM scan_events
WHERE shipment_id = ?
ORDER BY occurred_at, event_id"""

DELAYED_AT_CARRIER = """
SELECT DISTINCT e.shipment_id
FROM scan_events e
JOIN shipments s ON s.shipment_id = e.shipment_id
JOIN carriers c  ON c.carrier_id = s.carrier_id
WHERE c.code = ? AND e.status = 'DELAYED'
  AND e.occurred_at >= ? AND e.occurred_at < ?
ORDER BY e.shipment_id"""


class Steps:
    """Counts SQLite virtual-machine instructions executed while active."""

    def __init__(self, conn):
        self.conn, self.count = conn, 0

    def _tick(self):
        self.count += 1
        return 0                                  # non-zero would abort the query

    def __enter__(self):
        self.count = 0
        self.conn.set_progress_handler(self._tick, 1)
        return self

    def __exit__(self, *exc):
        self.conn.set_progress_handler(None, 1)


def build(data):
    """Create an in-memory database, load the data, and gather planner statistics."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    ids = {code: n for n, code in enumerate(sorted({s["carrier"] for s in data["shipments"]}), start=1)}
    conn.executemany("INSERT INTO carriers VALUES (?, ?)", [(n, code) for code, n in ids.items()])
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?)",
                     [(o["order_id"], o["customer_id"], o["created_at"]) for o in data["orders"]])
    conn.executemany("INSERT INTO shipments VALUES (?, ?, ?, ?, ?)",
                     [(s["shipment_id"], s["order_id"], ids[s["carrier"]], s["current_status"], s["created_at"])
                      for s in data["shipments"]])
    conn.executemany("INSERT INTO scan_events VALUES (?, ?, ?, ?)",
                     [(e["event_id"], e["shipment_id"], e["status"], e["occurred_at"]) for e in data["events"]])
    conn.commit()
    conn.execute("ANALYZE")
    return conn


def plan(conn, sql, params):
    """The plan's detail lines, for example 'SEARCH s USING INDEX shipments_by_order (order_id=?)'."""
    return [row[3] for row in conn.execute("EXPLAIN QUERY PLAN " + sql, params)]


def run(conn, sql, params):
    """Return (rows, vm_steps)."""
    with Steps(conn) as steps:
        rows = conn.execute(sql, params).fetchall()
    return rows, steps.count


def get_shipment(conn, sid):
    rows, steps = run(conn, GET_SHIPMENT, (sid,))
    if not rows:
        return None, steps
    s, cid, carrier, status, created = rows[0]
    return {"shipment_id": s, "customer_id": cid, "carrier": carrier, "status": status,
            "created_at": created}, steps


def customer_recent(conn, cid, limit=5):
    rows, steps = run(conn, CUSTOMER_RECENT, (cid, limit))
    return [r[0] for r in rows], steps


def shipment_events(conn, sid):
    rows, steps = run(conn, SHIPMENT_EVENTS, (sid,))
    return [tuple(r) for r in rows], steps


def delayed_at_carrier(conn, carrier, day):
    nxt = (date.fromisoformat(day) + timedelta(days=1)).isoformat()
    params = (carrier, f"{day}T00:00:00Z", f"{nxt}T00:00:00Z")     # [day 00:00, next day 00:00)
    rows, steps = run(conn, DELAYED_AT_CARRIER, params)
    return [r[0] for r in rows], steps, params
