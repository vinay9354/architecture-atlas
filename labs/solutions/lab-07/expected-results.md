# Lab 07 — sample results

Runs on a laptop (macOS, Python 3.14.7 with its bundled SQLite 3.53.4) with the default data seed
7. Every block below is copied from a real run. Answers, item counts, partitions touched, and the
hot-partition table are deterministic: the generators are seeded and partition placement uses
CRC-32. SQLite VM step counts depend on the SQLite version (with Python 3.9.6 and SQLite 3.54.0 the
pattern averages were 29, 147, and 44 instead of 28, 139, and 46, and the ad-hoc plan scanned
`scan_events` through `events_by_shipment` instead of scanning `shipments`).

## Step 1 — Look at the data and both layouts

```text
$ python3 lab07_run.py data
customers 1500  orders 6000  shipments 6000  scan events 27422
customers with at least one shipment: 1244   busiest: C00001 with 356 shipments
shipments per carrier: {'carrier-a': 1169, 'carrier-b': 425, 'carrier-c': 449, 'carrier-d': 409, 'carrier-e': 402, 'carrier-f': 457, 'carrier-g': 462, 'carrier-h': 470, 'carrier-i': 419, 'carrier-j': 435, 'carrier-k': 479, 'carrier-l': 424}
current status: {'CREATED': 127, 'DELAYED': 41, 'DELIVERED': 4777, 'IN_TRANSIT': 588, 'OUT_FOR_DELIVERY': 144, 'PICKED_UP': 323}
DELAYED events yesterday (2026-11-26): 55, of which carrier-c: 23

relational model (SQLite 3.53.4):
  table carriers         12 rows
  table orders         6000 rows
  table shipments      6000 rows
  table scan_events   27422 rows
  index events_by_shipment on scan_events
  index orders_by_customer on orders
  index shipments_by_order on shipments

key-value model (simulated, 16 partitions):
  table tracking: 33422 items (shipment META items + EVT# items), items per partition min 2017 max 2153
  global index by_customer: 6000 items (one copy per shipment)

  item collection for SHP#S000042:
    sk=EVT#2026-11-22T07:43:19Z#E0000192          event    status=CREATED
    sk=EVT#2026-11-22T11:14:33Z#E0000193          event    status=PICKED_UP
    sk=EVT#2026-11-22T16:00:38Z#E0000194          event    status=IN_TRANSIT
    sk=EVT#2026-11-23T09:15:11Z#E0000195          event    status=OUT_FOR_DELIVERY
    sk=EVT#2026-11-23T14:22:07Z#E0000196          event    status=DELIVERED
    sk=META                                       shipment status=DELIVERED
```

Answers: the `EVT#` sort keys embed the ISO-8601 UTC timestamp, and ISO timestamps sort correctly as
text, so the item collection is already in time order; `META` sorts after `EVT#` because `M` comes
after `E`. The table holds 33,422 items: 27,422 event items plus 6,000 shipment `META` items. The
`by_customer` index adds a further 6,000 copies. Partitions hold between 2,017 and 2,153 items: the
shipment key spreads data evenly.

## Step 2 — Run the three designed access patterns on both stores

```text
$ python3 lab07_run.py patterns
Pattern 1: get shipment by id (200 different ids)
  example S001950: {'shipment_id': 'S001950', 'customer_id': 'C00001', 'carrier': 'carrier-g', 'status': 'DELAYED', 'created_at': '2026-11-25T15:19:52Z'}
  SQL  plan:
         SEARCH s USING INDEX sqlite_autoindex_shipments_1 (shipment_id=?)
         SEARCH o USING INDEX sqlite_autoindex_orders_1 (order_id=?)
         SEARCH c USING INTEGER PRIMARY KEY (rowid=?)
       rows returned per query 1.00, SQLite VM steps per query 28 (average)
  KV   items read per query 1.00, partitions touched (max) 1, requests (max) 1
  same answer from both stores: 200 of 200

Pattern 2: customer's 5 most recent shipments (200 different ids)
  example C00001: ['S003628', 'S001595', 'S004957', 'S003569', 'S005216']
  SQL  plan:
         SEARCH o USING INDEX orders_by_customer (customer_id=?)
         SEARCH s USING INDEX shipments_by_order (order_id=?)
         USE TEMP B-TREE FOR ORDER BY
       rows returned per query 2.72, SQLite VM steps per query 139 (average)
  KV   items read per query 2.72, partitions touched (max) 1, requests (max) 1
  same answer from both stores: 200 of 200

Pattern 3: events for a shipment, in order (200 different ids)
  example S001950: [('E0008900', 'CREATED', '2026-11-25T15:19:52Z'), ('E0008901', 'PICKED_UP', '2026-11-25T18:02:29Z'), ('E0008902', 'IN_TRANSIT', '2026-11-26T01:52:14Z'), ('E0008903', 'DELAYED', '2026-11-26T20:38:51Z')]
  SQL  plan:
         SEARCH scan_events USING INDEX events_by_shipment (shipment_id=?)
       rows returned per query 4.54, SQLite VM steps per query 46 (average)
  KV   items read per query 4.54, partitions touched (max) 1, requests (max) 1
  same answer from both stores: 200 of 200

```

Answers:

1. The relational answer is spread over three normalized tables (the carrier code lives in
   `carriers`, the customer id in `orders`), so it takes three primary-key searches joined
   together. The key-value item was written with the customer id and carrier copied onto it, so one
   read returns everything. That is denormalization paying off on reads; the cost is that a change
   to a copied value must be written to every copy.
2. SQLite finds the customer's orders through `orders_by_customer`, joins each to its shipment, and
   then sorts by the shipment's `created_at` (the index on `orders` is not the sort the query asks
   for after the join). The key-value index stores each shipment under `CUST#<id>` with sort key
   `<created_at>#<shipment_id>`, so reading the collection backwards is already newest first. The
   busiest customer, `C00001`, has 356 shipments; the key-value query still reads only 5 items.
3. Each key-value query names one partition key and reads a contiguous sort-key range, so it reads
   exactly the items it returns: no filter discards anything. Every pattern touches one partition
   with one request.

## Step 3 — Ask a question the key-value design did not plan for

```text
$ python3 lab07_run.py adhoc
Ad-hoc: shipments with a DELAYED event at carrier-c on 2026-11-26 (yesterday)
  SQL, schema as designed (no index for this question):
         SEARCH c USING COVERING INDEX sqlite_autoindex_carriers_1 (code=?)
         SCAN s
         SEARCH e USING INDEX events_by_shipment (shipment_id=? AND occurred_at>? AND occurred_at<?)
         USE TEMP B-TREE FOR DISTINCT
       23 shipments, SQLite VM steps 30783
  SQL, after CREATE INDEX events_by_status_time ON scan_events(status, occurred_at):
         SEARCH c USING COVERING INDEX sqlite_autoindex_carriers_1 (code=?)
         SEARCH e USING INDEX events_by_status_time (status=? AND occurred_at>? AND occurred_at<?)
         SEARCH s USING INDEX sqlite_autoindex_shipments_1 (shipment_id=?)
         USE TEMP B-TREE FOR DISTINCT
       23 shipments, SQLite VM steps 1064
  KV, no key serves this question: full scan
       23 shipments, items read 33422 of 33422, partitions touched 16 of 16
  KV, add global index CAR#<carrier>#<day> / <status>#<time>#<event> and backfill it:
       backfill read 33422 base items and wrote 27422 index items
       query: 23 shipments, items read 23, partitions touched 1
  same answer from all four: True   shipments: S000007, S000417, S000556, S000603, S000754, S000800 ...
```

Answers: SQL answers the unplanned question exactly as written; the planner picks the best path it
has (here a scan of `shipments` with an index search per shipment), and one `CREATE INDEX` cuts the
work by about 29 times (30,783 to 1,064 VM steps). The key-value store has no key that names a
carrier or a day, so the only way is to read all 33,422 items in all 16 partitions to find 23
shipments. Building a global index fixes the query (23 items read, 1 partition) but the backfill
itself is a full scan plus 27,422 index writes, and from then on every event write costs two
writes. On a production-sized table that backfill is a capacity and cost event to plan, not a quick
statement.

## Step 4 — Watch a global index lag behind the base table

```text
$ python3 lab07_run.py index-lag
New shipment S900001 for customer C00032, written to both stores
  SQL recent shipments (same transaction view):  ['S900001', 'S002701', 'S000519', 'S005938', 'S004298']
  KV base-table get SHP#S900001 / META found:     True
  KV by_customer index, before propagation:       ['S002701', 'S000519', 'S005938', 'S004298', 'S000949']   (pending index updates: 1)
  KV by_customer index, after propagation of 1:   ['S900001', 'S002701', 'S000519', 'S005938', 'S004298']
```

Answers: SQLite (one database, one transaction view) and the key-value base-table get see the new
shipment at once. The global index still has its update queued, so the customer's list misses it
until propagation. For read-your-writes on "my shipments", the Tracking API can read the new item by
key from the base table (it has the id from the write response) and merge it into the list, or
show the confirmation page's data until the index catches up.

## Step 5 — A sale-day burst: hot partition, then write sharding

```text
$ python3 lab07_run.py hot --shards 1 2 4 8 16
sale-day burst: 3,500 writes/s for 10 s, carrier-a 40%, 16 partitions, budget 500 writes/s per partition
design                    hottest key                   key/s  hottest part/s  mean part/s  hot ratio  throttled  read fan-out
base table (SHP#id)       (one per shipment)                -             228          219       1.04          0             1
index CAR#carrier#day     CAR#carrier-a#2026-11-27       1413            1996          219       9.13      16356             1
index CAR#carrier#day x2  CAR#carrier-a#2026-11-27#0      710            1086          219       4.97      15000             2
index CAR#carrier#day x4  CAR#carrier-a#2026-11-27#0      356             548          219       2.51       1702             4
index CAR#carrier#day x8  CAR#carrier-a#2026-11-27#0      182             276          219       1.26          0             8
index CAR#carrier#day x16 CAR#carrier-a#2026-11-27#7       94             354          219       1.62          0            16
index x1: 12 partition keys in use; the hottest partition holds 4 of them: carrier-a#2026-11-27, carrier-b#2026-11-27, carrier-d#2026-11-27, carrier-g#2026-11-27
index x2: 24 partition keys in use; the hottest partition holds 5 of them: carrier-a#2026-11-27#0, carrier-f#2026-11-27#0, carrier-g#2026-11-27#1, carrier-h#2026-11-27#0, carrier-i#2026-11-27#1
index x4: 48 partition keys in use; the hottest partition holds 5 of them: carrier-a#2026-11-27#0, carrier-f#2026-11-27#0, carrier-g#2026-11-27#1, carrier-h#2026-11-27#0, carrier-i#2026-11-27#1
index x8: 96 partition keys in use; the hottest partition holds 5 of them: carrier-a#2026-11-27#4, carrier-f#2026-11-27#4, carrier-g#2026-11-27#5, carrier-h#2026-11-27#4, carrier-i#2026-11-27#5
index x16: 192 partition keys in use; the hottest partition holds 17 of them: carrier-a#2026-11-27#12, carrier-a#2026-11-27#5, carrier-b#2026-11-27#9, carrier-c#2026-11-27#8, carrier-d#2026-11-27#8, carrier-e#2026-11-27#15, carrier-e#2026-11-27#9, carrier-f#2026-11-27#11, carrier-f#2026-11-27#5, carrier-g#2026-11-27#4, carrier-h#2026-11-27#5, carrier-i#2026-11-27#4, carrier-j#2026-11-27#8, carrier-k#2026-11-27#13, carrier-k#2026-11-27#9, carrier-l#2026-11-27#10, carrier-l#2026-11-27#9
```

The default `python3 lab07_run.py hot` prints the same base, x1, and x8 rows.

Answers:

- **Base table:** keyed by shipment id over 300,000 shipments, the 35,000 writes spread almost
  perfectly: hottest partition 228 writes/s against a mean of 219 (ratio 1.04), nothing throttled.
- **Unsharded carrier-day index:** carrier-a's key alone carries 1,413 writes/s (40% of 3,500 is
  1,400; the seeded draw gave 1,413). Its partition also holds the keys of carrier-b, carrier-d, and
  carrier-g, about 190 writes/s each, for 1,996 writes/s: 9.13 times the mean and four times the
  budget. 16,356 writes were throttled, including writes for the three carriers that merely share
  the partition.
- **2 and 4 shards:** carrier-a's suffixes drop to 710 and 356 writes/s, but each still shares a
  partition with other keys (1,086 and 548 writes/s), so writes are still throttled. The arithmetic
  "1,400 ÷ 500 = 2.8, so 3 or 4 suffixes" ignores collisions.
- **8 shards:** the hottest partition carries 276 writes/s (ratio 1.26) and nothing is throttled. A
  support query for "carrier-a yesterday" now issues 8 queries and merges them.
- **16 shards:** the ratio rises again to 1.62 because 192 keys on 16 partitions collide in a
  different way (one partition holds 17 keys). More shards is not automatically better: past the
  point where the hot key is split enough, the spread is set by how keys land on partitions, and
  every extra suffix doubles the read fan-out again. Eight is the choice here.

## Smoke test

```text
$ python3 -m unittest tests.examples.test_lab07 -v
test_adhoc_query_scan_versus_index ... ok
test_cli_all_runs ... ok
test_data_is_seeded ... ok
test_designed_patterns_same_answers_one_partition ... ok
test_global_index_is_eventually_consistent ... ok
test_hot_partition_and_write_sharding ... ok
test_sources_compile ... ok

----------------------------------------------------------------------
Ran 7 tests in 5.350s

OK
```

The test asserts relationships, not timings: identical answers from both stores for all three
patterns; one partition and one request per key-value pattern, with items read equal to rows
returned; a `SCAN` in the SQL plan before the ad-hoc index and none after, with at least 5 times
fewer VM steps; a key-value full scan that reads every item in every partition and an index query
that reads one partition; the global index missing a new shipment until propagation; and, on a
4-second burst, an even base table, an unsharded index with a hot ratio above 5 and throttled
writes, and an 8-shard index with a ratio under a third of that, no throttling, and a read fan-out
of 8.
