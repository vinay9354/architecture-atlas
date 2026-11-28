#!/usr/bin/env python3
"""Lab 07: run the same AtlasMart tracking access patterns on a relational model (SQLite) and on a
simulated partitioned key-value / document store, and compare answers and work done.

  python3 lab07_run.py data          the seeded data and how each store lays it out
  python3 lab07_run.py patterns      the three designed access patterns on both stores
  python3 lab07_run.py adhoc         a question the key-value design did not plan for
  python3 lab07_run.py index-lag     a global secondary index is eventually consistent
  python3 lab07_run.py hot           a sale-day burst: hot partition, then write sharding
  python3 lab07_run.py all           everything above

Work is reported as items read, partitions touched, query plans, and SQLite VM steps. Nothing here
measures or claims the speed of any database product.
"""
import argparse
import random
import sys
from collections import Counter

import lab07_data
import lab07_hot
import lab07_sql
import lab07_tracking_kv as kv


def setup(seed):
    data = lab07_data.generate(seed)
    conn = lab07_sql.build(data)
    table, by_customer = kv.build(data)
    return data, conn, table, by_customer


def cmd_data(ctx, out):
    data, conn, table, by_customer = ctx
    lab07_data.summary(data, out)
    print(f"\nrelational model (SQLite {lab07_sql.sqlite3.sqlite_version}):", file=out)
    for name in ("carriers", "orders", "shipments", "scan_events"):
        print(f"  table {name:<12} {conn.execute(f'SELECT count(*) FROM {name}').fetchone()[0]:>6} rows", file=out)
    for (name, tbl) in conn.execute("SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' "
                                    "AND sql IS NOT NULL ORDER BY name"):
        print(f"  index {name} on {tbl}", file=out)
    print("\nkey-value model (simulated, 16 partitions):", file=out)
    print(f"  table tracking: {table.item_count()} items (shipment META items + EVT# items), "
          f"items per partition min {min(table.partition_item_counts())} "
          f"max {max(table.partition_item_counts())}", file=out)
    print(f"  global index by_customer: {by_customer.item_count()} items (one copy per shipment)", file=out)
    sid = data["shipments"][41]["shipment_id"]
    print(f"\n  item collection for {kv.shipment_pk(sid)}:", file=out)
    for item in table.query(kv.shipment_pk(sid)):
        sk = kv.META if item["type"] == "shipment" else kv.event_sk(item)
        print(f"    sk={sk:<42} {item['type']:<8} status={item['status']}", file=out)
    table.meter.reset()


def _sample(data, seed):
    rng = random.Random(seed)
    sids = rng.sample([s["shipment_id"] for s in data["shipments"]], 200)
    cids = sorted({s["customer_id"] for s in data["shipments"]})
    return sids, rng.sample(cids, 200)


def _kv_cost(meter_list, fn):
    for m in meter_list:
        m.reset()
    result = fn()
    snap = [m.snapshot() for m in meter_list]
    return result, {k: sum(s[k] for s in snap) for k in snap[0]}


def run_patterns(ctx, seed):
    """Run all three patterns on both stores. Returns a dict of per-pattern results."""
    data, conn, table, by_customer = ctx
    sids, cids = _sample(data, seed)
    busiest = Counter(s["customer_id"] for s in data["shipments"]).most_common(1)[0][0]
    cids = [busiest] + [c for c in cids if c != busiest][:199]
    patterns = {
        "get shipment by id": (sids, lambda x: lab07_sql.get_shipment(conn, x),
                               lambda x: kv.get_shipment(table, x), [table.meter],
                               lab07_sql.GET_SHIPMENT, lambda x: (x,)),
        "customer's 5 most recent shipments": (cids, lambda x: lab07_sql.customer_recent(conn, x),
                                               lambda x: kv.customer_recent(by_customer, x),
                                               [by_customer.meter], lab07_sql.CUSTOMER_RECENT,
                                               lambda x: (x, 5)),
        "events for a shipment, in order": (sids, lambda x: lab07_sql.shipment_events(conn, x),
                                            lambda x: kv.shipment_events(table, x), [table.meter],
                                            lab07_sql.SHIPMENT_EVENTS, lambda x: (x,)),
    }
    results = {}
    for name, (ids, sql_fn, kv_fn, meters, sql_text, params) in patterns.items():
        same, steps, costs, rows = 0, [], [], 0
        for x in ids:
            sql_ans, n_steps = sql_fn(x)
            kv_ans, cost = _kv_cost(meters, lambda: kv_fn(x))
            same += sql_ans == kv_ans
            steps.append(n_steps)
            costs.append(cost)
            rows += 1 if isinstance(sql_ans, dict) else len(sql_ans)
        results[name] = {
            "n": len(ids), "same": same, "example_id": ids[0], "example": sql_fn(ids[0])[0],
            "plan": lab07_sql.plan(conn, sql_text, params(ids[0])),
            "sql_steps_avg": sum(steps) / len(steps), "rows_avg": rows / len(ids),
            "kv_items_read_avg": sum(c["items_read"] for c in costs) / len(costs),
            "kv_partitions_max": max(c["partitions_touched"] for c in costs),
            "kv_requests_max": max(c["requests"] for c in costs),
        }
    return results


def cmd_patterns(ctx, out, seed=3):
    for n, (name, r) in enumerate(run_patterns(ctx, seed).items(), start=1):
        print(f"Pattern {n}: {name} ({r['n']} different ids)", file=out)
        print(f"  example {r['example_id']}: {r['example']}", file=out)
        print("  SQL  plan:", file=out)
        for line in r["plan"]:
            print(f"         {line}", file=out)
        print(f"       rows returned per query {r['rows_avg']:.2f}, SQLite VM steps per query "
              f"{r['sql_steps_avg']:.0f} (average)", file=out)
        print(f"  KV   items read per query {r['kv_items_read_avg']:.2f}, partitions touched (max) "
              f"{r['kv_partitions_max']}, requests (max) {r['kv_requests_max']}", file=out)
        print(f"  same answer from both stores: {r['same']} of {r['n']}\n", file=out)


def run_adhoc(ctx, carrier="carrier-c", day=lab07_data.YESTERDAY):
    data, conn, table, _ = ctx
    res = {"carrier": carrier, "day": day}
    ans, steps, params = lab07_sql.delayed_at_carrier(conn, carrier, day)
    res["sql_before"] = {"answer": ans, "steps": steps, "plan": lab07_sql.plan(conn, lab07_sql.DELAYED_AT_CARRIER, params)}
    conn.execute(lab07_sql.ADHOC_INDEX)
    conn.execute("ANALYZE")
    ans2, steps2, _ = lab07_sql.delayed_at_carrier(conn, carrier, day)
    res["sql_after"] = {"answer": ans2, "steps": steps2, "plan": lab07_sql.plan(conn, lab07_sql.DELAYED_AT_CARRIER, params)}
    conn.execute("DROP INDEX events_by_status_time")             # leave the database as built
    table.meter.reset()
    scan_ans = kv.delayed_by_scan(table, carrier, day)
    res["kv_scan"] = {"answer": scan_ans, **table.meter.snapshot(), "total_items": table.item_count(),
                      "partitions": len(table.parts)}
    table.meter.reset()
    index = kv.add_carrier_day_index(table)
    res["kv_backfill"] = {"base_items_read": table.meter.items_read, "index_items_written": index.item_count()}
    index.meter.reset()
    idx_ans = kv.delayed_by_index(index, carrier, day)
    res["kv_index"] = {"answer": idx_ans, **index.meter.snapshot()}
    table.indexes.remove(index)                                   # leave the table as built
    table.meter.reset()
    return res


def cmd_adhoc(ctx, out):
    r = run_adhoc(ctx)
    print(f"Ad-hoc: shipments with a DELAYED event at {r['carrier']} on {r['day']} (yesterday)", file=out)
    b, a = r["sql_before"], r["sql_after"]
    print("  SQL, schema as designed (no index for this question):", file=out)
    for line in b["plan"]:
        print(f"         {line}", file=out)
    print(f"       {len(b['answer'])} shipments, SQLite VM steps {b['steps']}", file=out)
    print("  SQL, after CREATE INDEX events_by_status_time ON scan_events(status, occurred_at):", file=out)
    for line in a["plan"]:
        print(f"         {line}", file=out)
    print(f"       {len(a['answer'])} shipments, SQLite VM steps {a['steps']}", file=out)
    s = r["kv_scan"]
    print("  KV, no key serves this question: full scan", file=out)
    print(f"       {len(s['answer'])} shipments, items read {s['items_read']} of {s['total_items']}, "
          f"partitions touched {s['partitions_touched']} of {s['partitions']}", file=out)
    f = r["kv_backfill"]
    print("  KV, add global index CAR#<carrier>#<day> / <status>#<time>#<event> and backfill it:", file=out)
    print(f"       backfill read {f['base_items_read']} base items and wrote {f['index_items_written']} "
          f"index items", file=out)
    i = r["kv_index"]
    print(f"       query: {len(i['answer'])} shipments, items read {i['items_read']}, partitions touched "
          f"{i['partitions_touched']}", file=out)
    same = b["answer"] == a["answer"] == s["answer"] == i["answer"]
    print(f"  same answer from all four: {same}   shipments: {', '.join(b['answer'][:6])}"
          f"{' ...' if len(b['answer']) > 6 else ''}", file=out)


def run_index_lag(ctx):
    data, conn, table, by_customer = ctx
    cid = data["shipments"][0]["customer_id"]
    new = {"type": "shipment", "shipment_id": "S900001", "order_id": "O900001", "customer_id": cid,
           "carrier": "carrier-b", "status": "CREATED", "created_at": "2026-11-27T09:00:00Z"}
    conn.execute("INSERT INTO orders VALUES ('O900001', ?, '2026-11-27T09:00:00Z')", (cid,))
    conn.execute("INSERT INTO shipments VALUES ('S900001', 'O900001', 2, 'CREATED', '2026-11-27T09:00:00Z')")
    table.put(kv.shipment_pk("S900001"), kv.META, new)
    res = {"customer": cid,
           "sql_recent": lab07_sql.customer_recent(conn, cid)[0],
           "kv_base_get": kv.get_shipment(table, "S900001") is not None,
           "pending": len(by_customer.pending),
           "kv_index_before": kv.customer_recent(by_customer, cid)}
    res["applied"] = by_customer.propagate()
    res["kv_index_after"] = kv.customer_recent(by_customer, cid)
    conn.rollback()                                               # leave both stores as built
    table.delete(kv.shipment_pk("S900001"), kv.META)
    by_customer.delete(f"CUST#{cid}", "2026-11-27T09:00:00Z#S900001")
    return res


def cmd_index_lag(ctx, out):
    r = run_index_lag(ctx)
    print(f"New shipment S900001 for customer {r['customer']}, written to both stores", file=out)
    print(f"  SQL recent shipments (same transaction view):  {r['sql_recent']}", file=out)
    print(f"  KV base-table get SHP#S900001 / META found:     {r['kv_base_get']}", file=out)
    print(f"  KV by_customer index, before propagation:       {r['kv_index_before']}   "
          f"(pending index updates: {r['pending']})", file=out)
    print(f"  KV by_customer index, after propagation of {r['applied']}:   {r['kv_index_after']}", file=out)


def cmd_hot(out, shards_list=(1, 8)):
    results = [lab07_hot.simulate(shards=k) for k in shards_list]
    lab07_hot.report(results, out)
    return results


def main(argv=None, out=sys.stdout):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("command", choices=["data", "patterns", "adhoc", "index-lag", "hot", "all"])
    p.add_argument("--seed", type=int, default=7, help="data seed (default 7)")
    p.add_argument("--shards", type=int, nargs="+", default=[1, 8], help="write-shard counts for 'hot'")
    args = p.parse_args(argv)
    if args.command == "hot":
        cmd_hot(out, args.shards)
        return 0
    ctx = setup(args.seed)
    try:
        _run_steps(args, ctx, out)
    finally:
        ctx[1].close()
    return 0


def _run_steps(args, ctx, out):
    steps = {"data": cmd_data, "patterns": cmd_patterns, "adhoc": cmd_adhoc, "index-lag": cmd_index_lag}
    for name, fn in steps.items():
        if args.command in (name, "all"):
            if args.command == "all":
                print(f"===== {name} =====", file=out)
            fn(ctx, out)
            if args.command == "all":
                print(file=out)
    if args.command == "all":
        print("===== hot =====", file=out)
        cmd_hot(out, args.shards)


if __name__ == "__main__":
    sys.exit(main())
