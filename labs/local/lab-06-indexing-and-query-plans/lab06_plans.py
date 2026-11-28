#!/usr/bin/env python3
"""Lab 06: read SQLite query plans and measure what indexes change (standard library only).

Builds the seeded scan_events table from lab06_data.py in memory, then runs seven steps:

  1. The table: rows, shipments, date range, size.
  2. Full scan versus index search for one shipment's events.
  3. Composite index column order: equality column first versus range column first.
  4. Covering index: the query is answered from the index without visiting the table.
  5. Indexes the planner cannot use: a function on the column and a leading wildcard, with fixes.
  6. ORDER BY satisfied by an index versus a temporary B-tree.
  7. The write cost of extra indexes (insert time and pages, relative to no secondary index).

Each step prints the SQL, the EXPLAIN QUERY PLAN lines, the rows returned, and the median time per
query on this machine. Times vary by machine; compare the ratios, not the absolute numbers.

Run:  python3 lab06_plans.py                    (all steps, 37,500 shipments = 300,000 rows)
      python3 lab06_plans.py --step 3           (build the data, then run one step)
      python3 lab06_plans.py --shipments 5000   (smaller and faster)
"""
import argparse
import itertools
import statistics
import time

import lab06_data

_plan_ids = itertools.count()
SHIPMENT = 1042                                 # the shipment the lookups use
CARRIER = 7
WEEK_START = "2026-11-17 00:00:00"              # the last seven days of the sample
DAY = ("2026-11-20 00:00:00", "2026-11-21 00:00:00")

WRITE_INDEXES = [
    ("idx_ship_time", "scan_events (shipment_id, occurred_at)"),
    ("idx_carrier_event", "scan_events (carrier_id, carrier_event_id)"),
    ("idx_carrier_recv", "scan_events (carrier_id, received_at)"),
    ("idx_recv", "scan_events (received_at)"),
    ("idx_status_loc", "scan_events (status, location_text)"),
]


def plan(conn, sql, params=()):
    """The EXPLAIN QUERY PLAN detail lines, indented by depth.

    Python's sqlite3 caches prepared statements per connection, and a cached EXPLAIN statement keeps
    reporting the plan it was prepared with even after an index is created or dropped. A unique
    trailing comment makes every call prepare a fresh statement.
    """
    rows = conn.execute(f"EXPLAIN QUERY PLAN {sql} -- plan {next(_plan_ids)}", params).fetchall()
    depth = {0: -1}
    out = []
    for node_id, parent, _, detail in rows:
        depth[node_id] = depth.get(parent, -1) + 1
        out.append("  " * depth[node_id] + detail)
    return out


def bench(conn, sql, params=(), budget=0.3, max_runs=2_000):
    """Median seconds per execution (fetching all rows), and the row count."""
    rows = conn.execute(sql, params).fetchall()          # warm-up, also gives the row count
    times = []
    deadline = time.perf_counter() + budget
    while len(times) < max_runs and (len(times) < 5 or time.perf_counter() < deadline):
        t0 = time.perf_counter()
        conn.execute(sql, params).fetchall()
        times.append(time.perf_counter() - t0)
    return statistics.median(times), len(rows)


def drop_secondary_indexes(conn):
    names = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'index' AND name NOT LIKE 'sqlite_autoindex%'")]
    for name in names:
        conn.execute(f"DROP INDEX {name}")


def case(conn, label, sql, params=(), budget=0.3):
    seconds, nrows = bench(conn, sql, params, budget)
    return {"label": label, "sql": sql, "params": params, "plan": plan(conn, sql, params),
            "us": seconds * 1e6, "rows": nrows}


def count(conn, where, params):
    return conn.execute(f"SELECT count(*) FROM scan_events WHERE {where}", params).fetchone()[0]


# --- the steps -----------------------------------------------------------------------------------

def step_scan_vs_search(conn, budget=0.3):
    drop_secondary_indexes(conn)
    sql = "SELECT * FROM scan_events WHERE shipment_id = ?"
    before = case(conn, "no index on shipment_id", sql, (SHIPMENT,), budget)
    conn.execute("CREATE INDEX idx_ship ON scan_events (shipment_id)")
    after = case(conn, "after CREATE INDEX idx_ship ON scan_events (shipment_id)", sql, (SHIPMENT,), budget)
    return {"cases": [before, after], "speedup": before["us"] / after["us"]}


def step_composite_order(conn, budget=0.3):
    drop_secondary_indexes(conn)
    # count(*) needs only indexed columns, so both indexes cover the query and the only difference
    # between the two runs is the column order (Step 4 looks at covering on its own).
    sql = "SELECT count(*) FROM scan_events WHERE carrier_id = ? AND received_at >= ?"
    params = (CARRIER, WEEK_START)
    cases = []
    for name, cols in (("idx_recv_carrier", "received_at, carrier_id"),
                       ("idx_carrier_recv", "carrier_id, received_at")):
        drop_secondary_indexes(conn)
        conn.execute(f"CREATE INDEX {name} ON scan_events ({cols})")
        cases.append(case(conn, f"only index {name} ({cols})", sql, params, budget))
    # Index entries the search walks: the whole time range (range first) or one carrier's slice of it.
    walked = {"range_first": count(conn, "received_at >= ?", (WEEK_START,)),
              "equality_first": count(conn, "carrier_id = ? AND received_at >= ?", params)}
    return {"cases": cases, "walked": walked, "speedup": cases[0]["us"] / cases[1]["us"]}


def step_covering(conn, budget=0.3):
    drop_secondary_indexes(conn)
    sql = "SELECT received_at, status FROM scan_events WHERE carrier_id = ? AND received_at >= ?"
    params = (CARRIER, WEEK_START)
    conn.execute("CREATE INDEX idx_carrier_recv ON scan_events (carrier_id, received_at)")
    plain = case(conn, "index (carrier_id, received_at): status read from the table", sql, params, budget)
    drop_secondary_indexes(conn)
    conn.execute("CREATE INDEX idx_carrier_recv_status ON scan_events (carrier_id, received_at, status)")
    covering = case(conn, "index (carrier_id, received_at, status): covering", sql, params, budget)
    return {"cases": [plain, covering], "speedup": plain["us"] / covering["us"]}


def step_unusable(conn, budget=0.3):
    drop_secondary_indexes(conn)
    conn.execute("CREATE INDEX idx_recv ON scan_events (received_at)")
    conn.execute("CREATE INDEX idx_carrier_event ON scan_events (carrier_event_id)")
    cases = [
        case(conn, "function on the column (index idx_recv exists)",
             "SELECT * FROM scan_events WHERE date(received_at) = ?", (DAY[0][:10],), budget),
        case(conn, "rewritten as a range on the bare column",
             "SELECT * FROM scan_events WHERE received_at >= ? AND received_at < ?", DAY, budget),
        case(conn, "leading wildcard (index idx_carrier_event exists)",
             "SELECT * FROM scan_events WHERE carrier_event_id LIKE ?", ("%00000420",), budget),
        case(conn, "prefix LIKE: still a scan in SQLite (LIKE is case-insensitive, the index is not)",
             "SELECT * FROM scan_events WHERE carrier_event_id LIKE ?", ("C07-0000042%",), budget),
        case(conn, "prefix GLOB (case-sensitive): an index range",
             "SELECT * FROM scan_events WHERE carrier_event_id GLOB ?", ("C07-0000042*",), budget),
    ]
    conn.execute("CREATE INDEX idx_recv_day ON scan_events (date(received_at))")
    cases.append(case(conn, "same function query after CREATE INDEX idx_recv_day ON scan_events "
                      "(date(received_at))",
                      "SELECT * FROM scan_events WHERE date(received_at) = ?", (DAY[0][:10],), budget))
    return {"cases": cases}


def step_order_by(conn, budget=0.3):
    drop_secondary_indexes(conn)
    timeline = "SELECT occurred_at, status FROM scan_events WHERE shipment_id = ? ORDER BY occurred_at"
    latest = "SELECT * FROM scan_events ORDER BY received_at DESC LIMIT 20"
    cases = [case(conn, "latest 20 events, no index on received_at", latest, (), budget)]
    conn.execute("CREATE INDEX idx_recv ON scan_events (received_at)")
    cases.append(case(conn, "latest 20 events, index on received_at", latest, (), budget))
    conn.execute("CREATE INDEX idx_ship ON scan_events (shipment_id)")
    cases.append(case(conn, "one shipment's timeline, index (shipment_id)", timeline, (SHIPMENT,), budget))
    drop_secondary_indexes(conn)
    conn.execute("CREATE INDEX idx_ship_time ON scan_events (shipment_id, occurred_at)")
    cases.append(case(conn, "one shipment's timeline, index (shipment_id, occurred_at)", timeline,
                      (SHIPMENT,), budget))
    return {"cases": cases, "latest_speedup": cases[0]["us"] / cases[1]["us"]}


def step_write_cost(shipments, seed, index_counts=(0, 1, 3, 5), repeats=3):
    """Insert the same rows into a fresh table carrying 0, 1, 3, or 5 secondary indexes."""
    rows = list(lab06_data.generate(shipments, seed))
    results = []
    for k in index_counts:
        times = []
        for _ in range(repeats):
            conn = lab06_data.connect()
            conn.execute(lab06_data.SCHEMA)
            for name, target in WRITE_INDEXES[:k]:
                conn.execute(f"CREATE INDEX {name} ON {target}")
            t0 = time.perf_counter()
            with conn:
                conn.executemany(lab06_data.INSERT, rows)
            times.append(time.perf_counter() - t0)
            pages = conn.execute("PRAGMA page_count").fetchone()[0]
            conn.close()
        results.append({"indexes": k, "names": [n for n, _ in WRITE_INDEXES[:k]],
                        "seconds": min(times), "pages": pages})
    base = results[0]
    for r in results:
        r["time_x"] = r["seconds"] / base["seconds"]
        r["pages_x"] = r["pages"] / base["pages"]
    return {"rows": len(rows), "results": results}


# --- printing ------------------------------------------------------------------------------------

def fmt_us(us):
    return f"{us / 1000:,.2f} ms" if us >= 1000 else f"{us:,.1f} us"


def print_cases(cases):
    for c in cases:
        params = f"   params {c['params']}" if c["params"] else ""
        print(f"\n  [{c['label']}]")
        print(f"  SQL: {c['sql']}{params}")
        for line in c["plan"]:
            print(f"    plan: {line}")
        print(f"    rows {c['rows']:,}   median {fmt_us(c['us'])} per query")


def run(conn, step, shipments, seed, budget):
    if step in (0, 1):
        s = lab06_data.summary(conn)
        print("\n== Step 1 - the table ==")
        print(f"  rows {s['rows']:,}  shipments {s['shipments']:,}  carriers {s['carriers']}  "
              f"received_at {s['first']} .. {s['last']}")
        print(f"  {s['pages']:,} pages ({s['mb']} MB), no secondary indexes")
    if step in (0, 2):
        r = step_scan_vs_search(conn, budget)
        print("\n== Step 2 - full scan versus index search ==")
        print_cases(r["cases"])
        print(f"\n  index search is {r['speedup']:,.0f}x faster than the full scan on this machine")
    if step in (0, 3):
        r = step_composite_order(conn, budget)
        print("\n== Step 3 - composite index column order ==")
        print_cases(r["cases"])
        w = r["walked"]
        print(f"\n  index entries walked: range column first {w['range_first']:,}, "
              f"equality column first {w['equality_first']:,}")
        print(f"  equality-first is {r['speedup']:,.1f}x faster on this machine")
    if step in (0, 4):
        r = step_covering(conn, budget)
        print("\n== Step 4 - covering index ==")
        print_cases(r["cases"])
        print(f"\n  the covering index is {r['speedup']:,.1f}x faster on this machine")
    if step in (0, 5):
        r = step_unusable(conn, budget)
        print("\n== Step 5 - indexes the planner cannot use, and the fixes ==")
        print_cases(r["cases"])
    if step in (0, 6):
        r = step_order_by(conn, budget)
        print("\n== Step 6 - ORDER BY from an index versus a temporary B-tree ==")
        print_cases(r["cases"])
        print(f"\n  latest-20 with the index is {r['latest_speedup']:,.0f}x faster on this machine")
    if step in (0, 7):
        r = step_write_cost(shipments, seed)
        print(f"\n== Step 7 - write cost of extra indexes ({r['rows']:,} rows inserted per run, best of 3) ==")
        print(f"  {'secondary indexes':<18} {'insert time':>12} {'vs none':>8} {'pages':>8} {'vs none':>8}")
        for x in r["results"]:
            print(f"  {x['indexes']:<18} {x['seconds']:>10.2f} s {x['time_x']:>7.2f}x {x['pages']:>8,} "
                  f"{x['pages_x']:>7.2f}x")
        print("  indexes, in order added: " + ", ".join(n for n, _ in WRITE_INDEXES))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shipments", type=int, default=37_500, help="8 rows per shipment (default 37,500)")
    ap.add_argument("--seed", type=int, default=6)
    ap.add_argument("--step", type=int, default=0, choices=range(0, 8), help="0 = all steps")
    ap.add_argument("--budget", type=float, default=0.3, help="seconds of repeated runs per timed query")
    args = ap.parse_args()
    conn = lab06_data.connect()
    t0 = time.perf_counter()
    lab06_data.build(conn, args.shipments, args.seed)
    print(f"SQLite {lab06_data.sqlite3.sqlite_version}; built {args.shipments * 8:,} rows "
          f"in {time.perf_counter() - t0:.1f} s (seed {args.seed})")
    run(conn, args.step, args.shipments, args.seed, args.budget)


if __name__ == "__main__":
    main()
