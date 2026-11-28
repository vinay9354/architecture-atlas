#!/usr/bin/env python3
"""Lab 16: run the choreographed order saga under five experiments and check the final state.

  python3 lab16_workflow.py                                   all experiments
  python3 lab16_workflow.py --experiment crash                one experiment
  python3 lab16_workflow.py --experiment payment-failure --trace AM-1004
  python3 lab16_workflow.py --experiment happy --keep data    keep the SQLite files in ./data/happy/

Experiments:
  happy            clean bus, every card accepted
  crash            the Orders relay dies after the commit but before publishing; the Payments relay
                   dies after publishing but before marking the row (a duplicate publish)
  duplicates       the bus duplicates and reorders deliveries; idempotent vs naive consumers, then a
                   full replay of the "orders" topic into Inventory
  payment-failure  two cards are declined; the compensation releases stock and cancels the order,
                   with duplicates and reordering still switched on
  dual-write       Orders writes to its database and publishes to the bus as two separate steps;
                   one crash between them loses an event, one rollback after publishing creates a ghost
"""
import argparse
import os
import random
import sys
import tempfile

from lab16_bus import EventBus
from lab16_services import (DECLINING_METHOD, InventoryService, OrdersService, OutboxRelay, PaymentsService,
                            ShippingService, SimulatedCrash)

SKUS = ("SKU-A", "SKU-B", "SKU-C")
INITIAL_STOCK = 50
SUBSCRIPTIONS = [  # (topic, consuming service, event types it handles)
    ("orders", "inventory", ["order.placed"]),
    ("payments", "inventory", ["payment.failed"]),                 # compensation trigger
    ("inventory", "payments", ["inventory.reserved"]),
    ("payments", "shipping", ["payment.authorized"]),
    ("inventory", "orders", ["inventory.reserved"]),
    ("payments", "orders", ["payment.authorized", "payment.failed"]),
    ("shipping", "orders", ["shipment.created"]),
]
EXPERIMENTS = ("happy", "crash", "duplicates", "payment-failure", "dual-write")


def make_orders(seed, count=10, declined=()):
    """Ten fictional orders AM-1001..AM-1010 with seeded SKU, quantity, and amount."""
    rng = random.Random(seed)
    orders = []
    for i in range(count):
        order_id = f"AM-{1001 + i}"
        method = DECLINING_METHOD if order_id in declined else "test-card-ok"
        orders.append((order_id, rng.choice(SKUS), rng.randint(1, 3), rng.randint(1500, 12000), method))
    return orders


def build(data_dir, bus, idempotent=True, crash_before=(), crash_after=()):
    """Create the four services on separate SQLite files, wire subscriptions, and make the relays."""
    svc = {
        "orders": OrdersService(os.path.join(data_dir, "orders.db"), idempotent),
        "inventory": InventoryService(os.path.join(data_dir, "inventory.db"), idempotent),
        "payments": PaymentsService(os.path.join(data_dir, "payments.db"), idempotent),
        "shipping": ShippingService(os.path.join(data_dir, "shipping.db"), idempotent),
    }
    svc["inventory"].load_stock({sku: INITIAL_STOCK for sku in SKUS})
    # Routing: each consumer subscribes to a topic and filters to the event types it handles.
    for topic, consumer, types in SUBSCRIPTIONS:
        bus.subscribe(topic, consumer, svc[consumer].handle, ["atlasmart." + t for t in types])
    relays = [OutboxRelay(svc[name], bus,
                          crash_before_publish=[e for e in crash_before if e.startswith(svc[name].prefix)],
                          crash_after_publish=[e for e in crash_after if e.startswith(svc[name].prefix)])
              for name in ("orders", "inventory", "payments", "shipping")]
    return svc, relays


def drain(bus, relays, max_steps=20000):
    """Alternate relay polls and single deliveries until nothing is unpublished or pending.

    A relay that crashes is simply polled again on the next round: that is the restart.
    """
    for _ in range(max_steps):
        for relay in relays:
            try:
                relay.run_once()
            except SimulatedCrash:
                pass
        if not bus.deliver_one() and not any(r.service.unpublished() for r in relays):
            return
    raise RuntimeError("the workflow did not settle")


def check(svc, orders):
    """Return a list of broken business invariants (empty when the final state is correct)."""
    problems = []
    status = dict(svc["orders"].db.execute("SELECT order_id, status FROM orders"))
    pay, shp, inv = svc["payments"], svc["shipping"], svc["inventory"]
    for order_id, sku, qty, _amount, _method in orders:
        st = status.get(order_id)
        auth = pay.count("SELECT COUNT(*) FROM payments WHERE order_id = ? AND status = 'AUTHORIZED'", order_id)
        ships = shp.count("SELECT COUNT(*) FROM shipments WHERE order_id = ?", order_id)
        res = inv.count("SELECT COUNT(*) FROM reservations WHERE order_id = ?", order_id)
        held = inv.count("SELECT COUNT(*) FROM reservations WHERE order_id = ? AND status = 'RESERVED'", order_id)
        if st is None:
            if auth or ships or res:
                problems.append(f"{order_id}: not in Orders, yet {res} reservation(s), {auth} payment(s), "
                                f"{ships} shipment(s) (ghost order)")
        elif st == "SHIPPED":
            if (auth, ships, res, held) != (1, 1, 1, 1):
                problems.append(f"{order_id}: SHIPPED with {auth} payment(s), {ships} shipment(s), "
                                f"{res} reservation(s)")
        elif st == "CANCELLED":
            if auth or ships or held or res != 1:
                problems.append(f"{order_id}: CANCELLED with {auth} payment(s), {ships} shipment(s), "
                                f"{held} reservation(s) still held")
        else:
            problems.append(f"{order_id}: stuck in {st} ({res} reservation(s), {auth} payment(s))")
    expected = {sku: INITIAL_STOCK for sku in SKUS}
    for order_id, sku, qty, _amount, _method in orders:
        if status.get(order_id) == "SHIPPED":
            expected[sku] -= qty
    actual = inv.stock()
    if actual != expected:
        problems.append(f"stock {actual} != expected {expected}")
    return problems


def summarize(svc, bus, relays):
    pay, shp = svc["payments"], svc["shipping"]
    return {
        "orders": svc["orders"].by_status(),
        "payments": dict(pay.db.execute("SELECT status, COUNT(*) FROM payments GROUP BY status ORDER BY status")),
        "shipments": shp.count("SELECT COUNT(*) FROM shipments"),
        "stock": svc["inventory"].stock(),
        "duplicates_skipped": sum(s.stats["duplicates_skipped"] for s in svc.values()),
        "stale_ignored": sum(s.stats["stale_ignored"] for s in svc.values()),
        "unknown_order": sum(s.stats["unknown_order"] for s in svc.values()),
        "bus": dict(bus.stats),
        "relay_crashes": [c for r in relays for c in r.crashes],
    }


def run_experiment(name, seed=16, keep=None, duplicate_rate=0.3, reorder_rate=0.3, idempotent=True):
    """Run one experiment in a fresh set of databases. Returns a dict with everything the test needs."""
    if name not in EXPERIMENTS:
        raise ValueError(f"unknown experiment {name!r}; choose from {', '.join(EXPERIMENTS)}")
    faulty = name in ("duplicates", "payment-failure")
    bus = EventBus(seed=seed, duplicate_rate=duplicate_rate if faulty else 0.0,
                   reorder_rate=reorder_rate if faulty else 0.0)
    declined = ("AM-1004", "AM-1008") if name == "payment-failure" else ()
    orders = make_orders(seed, declined=declined)
    tmp = None
    if keep:
        data_dir = os.path.join(keep, name + ("" if idempotent else "-naive"))
        os.makedirs(data_dir, exist_ok=True)
        for f in os.listdir(data_dir):
            if f.endswith(".db"):
                os.remove(os.path.join(data_dir, f))
    else:
        tmp = tempfile.TemporaryDirectory()
        data_dir = tmp.name
    try:
        crash_before = ("ord-0003",) if name == "crash" else ()
        crash_after = ("pay-0005",) if name == "crash" else ()
        svc, relays = build(data_dir, bus, idempotent, crash_before, crash_after)
        notes = []
        for order_id, sku, qty, amount, method in orders:
            if name == "dual-write":
                fault = {"AM-1003": "crash-after-commit", "AM-1006": "rollback-after-publish"}.get(order_id)
                result = svc["orders"].place_order_dual_write(bus, order_id, sku, qty, amount, method, fault)
                if fault:
                    notes.append(f"{order_id}: {result}")
            else:
                svc["orders"].place_order(order_id, sku, qty, amount, method)
        drain(bus, relays)
        result = {"name": name, "idempotent": idempotent, "orders": orders, "notes": notes,
                  "summary": summarize(svc, bus, relays), "problems": check(svc, orders),
                  "delivery_log": list(bus.delivery_log)}
        if name == "duplicates" and idempotent:
            before = (svc["inventory"].stock(), result["summary"]["payments"], result["summary"]["shipments"])
            skipped_before = svc["inventory"].stats["duplicates_skipped"]
            replayed = bus.replay("orders", "inventory")
            drain(bus, relays)
            after = (svc["inventory"].stock(), summarize(svc, bus, relays)["payments"],
                     summarize(svc, bus, relays)["shipments"])
            result["replay"] = {"replayed": replayed, "unchanged": before == after,
                                "duplicates_skipped": svc["inventory"].stats["duplicates_skipped"] - skipped_before}
        for s in svc.values():
            s.db.close()
        return result
    finally:
        if tmp is not None:
            tmp.cleanup()


def report(result, out):
    s, b = result["summary"], result["summary"]["bus"]
    label = result["name"] + ("" if result["idempotent"] else " (naive consumers, no processed_events check)")
    print(f"== {label}", file=out)
    for note in result["notes"]:
        print(f"   {note}", file=out)
    for crash in s["relay_crashes"]:
        print(f"   {crash}; restarted on the next poll", file=out)
    print(f"   orders by status   {s['orders']}", file=out)
    print(f"   payments           {s['payments']}   shipments {s['shipments']}", file=out)
    print(f"   stock on hand      {s['stock']}", file=out)
    print(f"   bus                published {b['published']}, deliveries {b['deliveries']}, "
          f"duplicates injected {b['duplicates_injected']}, reorders injected {b['reorders_injected']}",
          file=out)
    print(f"   consumers          duplicates skipped {s['duplicates_skipped']}, "
          f"stale ignored {s['stale_ignored']}, unknown order {s['unknown_order']}", file=out)
    if "replay" in result:
        r = result["replay"]
        print(f"   replay             {r['replayed']} order.placed events replayed into Inventory: "
              f"{r['duplicates_skipped']} skipped as duplicates, "
              f"stock/payments/shipments {'unchanged' if r['unchanged'] else 'CHANGED'}", file=out)
    if result["problems"]:
        print(f"   invariants         {len(result['problems'])} BROKEN", file=out)
        for p in result["problems"]:
            print(f"     - {p}", file=out)
    else:
        print("   invariants         OK", file=out)
    print(file=out)


def trace(result, order_id, out):
    print(f"-- deliveries for {order_id} in '{result['name']}'", file=out)
    print(f"{'step':>5}  {'consumer':<10} {'type':<30} {'event id':<11} outcome", file=out)
    for step, consumer, _topic, etype, eid, subject, outcome in result["delivery_log"]:
        if subject == order_id:
            print(f"{step:>5}  {consumer:<10} {etype:<30} {eid:<11} {outcome}", file=out)
    print(file=out)


def main(argv=None, out=sys.stdout):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--experiment", choices=EXPERIMENTS + ("all",), default="all")
    p.add_argument("--seed", type=int, default=16)
    p.add_argument("--duplicate-rate", type=float, default=0.3)
    p.add_argument("--reorder-rate", type=float, default=0.3)
    p.add_argument("--trace", metavar="ORDER_ID", help="print every delivery for one order")
    p.add_argument("--keep", metavar="DIR", help="keep the SQLite files under DIR/<experiment>/")
    args = p.parse_args(argv)
    names = EXPERIMENTS if args.experiment == "all" else (args.experiment,)
    print(f"seed={args.seed} orders=10 skus={len(SKUS)} initial stock={INITIAL_STOCK} per SKU "
          f"duplicate_rate={args.duplicate_rate} reorder_rate={args.reorder_rate} "
          "(faults apply to duplicates and payment-failure)\n", file=out)
    broken = 0
    for name in names:
        variants = (True, False) if name == "duplicates" else (True,)
        for idempotent in variants:
            result = run_experiment(name, args.seed, args.keep, args.duplicate_rate, args.reorder_rate, idempotent)
            report(result, out)
            if args.trace and idempotent:
                trace(result, args.trace, out)
            expected_broken = name == "dual-write" or not idempotent
            broken += bool(result["problems"]) != expected_broken
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
