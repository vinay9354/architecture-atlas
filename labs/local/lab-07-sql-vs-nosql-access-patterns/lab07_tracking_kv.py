#!/usr/bin/env python3
"""Lab 07: AtlasMart tracking data in the simulated key-value / document store, designed
access-pattern first (single-table design).

Base table "tracking", partition key = the shipment:

    pk                 sk                                   item
    SHP#<shipment_id>  META                                 shipment: customer, carrier, status, created_at
    SHP#<shipment_id>  EVT#<occurred_at>#<event_id>         one scan event (carrier copied onto it)

So "shipment by id" is one get, and "events for a shipment in order" is one query on one partition
(the EVT# items sort by time because the timestamps are ISO strings).

Global index "by_customer" (pk = CUST#<customer_id>, sk = <created_at>#<shipment_id>) holds a copy of
each shipment item, so "a customer's recent shipments" is one query read newest first.

The ad-hoc question "shipments delayed at carrier X yesterday" has no key. Without a new index it
is a full scan; add_carrier_day_index() builds the index an analyst would ask for
(pk = CAR#<carrier>#<day>[#<shard>], sk = <status>#<occurred_at>#<event_id>).
"""
from lab07_kvstore import Table, stable_hash

META = "META"


def shipment_pk(sid):
    return f"SHP#{sid}"


def event_sk(event):
    return f"EVT#{event['occurred_at']}#{event['event_id']}"


def by_customer_keys(item):
    if item["type"] != "shipment":
        return None
    return f"CUST#{item['customer_id']}", f"{item['created_at']}#{item['shipment_id']}"


def carrier_day_keys(shards=1):
    """Index keys for events by carrier and day; with shards > 1 the day is write-sharded."""
    def keyfn(item):
        if item["type"] != "event":
            return None
        pk = f"CAR#{item['carrier']}#{item['occurred_at'][:10]}"
        if shards > 1:
            pk += f"#{stable_hash(item['shipment_id']) % shards}"
        return pk, f"{item['status']}#{item['occurred_at']}#{item['event_id']}"
    return keyfn


def build(data, partitions=16):
    table = Table("tracking", partitions)
    by_customer = table.add_global_index("by_customer", by_customer_keys, partitions)
    for s in data["shipments"]:
        table.put(shipment_pk(s["shipment_id"]), META,
                  {"type": "shipment", "shipment_id": s["shipment_id"], "order_id": s["order_id"],
                   "customer_id": s["customer_id"], "carrier": s["carrier"], "status": s["current_status"],
                   "created_at": s["created_at"]})
    for e in data["events"]:
        table.put(shipment_pk(e["shipment_id"]), event_sk(e), {"type": "event", **e})
    by_customer.propagate()
    table.meter.reset()
    by_customer.meter.reset()
    return table, by_customer


# ---- the three designed access patterns ---------------------------------------------------------
def get_shipment(table, sid):
    item = table.get(shipment_pk(sid), META)
    if item is None:
        return None
    return {k: item[k] for k in ("shipment_id", "customer_id", "carrier", "status", "created_at")}


def customer_recent(by_customer, cid, limit=5):
    return [it["shipment_id"] for it in by_customer.query(f"CUST#{cid}", limit=limit, newest_first=True)]


def shipment_events(table, sid):
    return [(it["event_id"], it["status"], it["occurred_at"])
            for it in table.query(shipment_pk(sid), prefix="EVT#")]


# ---- the ad-hoc question ------------------------------------------------------------------------
def delayed_by_scan(table, carrier, day):
    hits = table.scan(lambda it: it["type"] == "event" and it["carrier"] == carrier
                      and it["status"] == "DELAYED" and it["occurred_at"].startswith(day))
    return sorted({it["shipment_id"] for it in hits})


def add_carrier_day_index(table, shards=1, partitions=16):
    index = table.add_global_index(f"by_carrier_day_x{shards}", carrier_day_keys(shards), partitions)
    index.backfill(table)
    return index


def delayed_by_index(index, carrier, day, shards=1):
    pks = [f"CAR#{carrier}#{day}"] if shards == 1 else [f"CAR#{carrier}#{day}#{n}" for n in range(shards)]
    hits = []
    for pk in pks:                                    # with write sharding: one query per shard
        hits.extend(index.query(pk, prefix="DELAYED#"))
    return sorted({it["shipment_id"] for it in hits})
