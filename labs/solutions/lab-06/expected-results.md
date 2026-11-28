# Lab 06 — sample results

Runs on a laptop (macOS, Python 3.14.7, SQLite 3.53.4) with the default seed 6 and 37,500 shipments
(300,000 rows). Every block below is copied from a real run. The full run was one command,
`python3 lab06_plans.py`, split here by step; its first line was:

```text
SQLite 3.53.4; built 300,000 rows in 1.4 s (seed 6)

```

Plans, row counts, entries walked, and page counts are the same on every machine with the same seed
(SQLite has no statistics until `ANALYZE` runs, so the plans depend only on the indexes). Times are
from the author's machine; compare the ratios, not the numbers.

## Step 1 — Look at the data

```text
$ python3 lab06_data.py
built scan_events in 1.4 s
rows 300,000  shipments 37,500  carriers 12  received_at 2026-05-31 00:11:33 .. 2026-11-24 01:14:39
table size 6,285 pages (25.7 MB), no secondary indexes
   (8329, 1042, 10, 'C10-00000729', 'label_created', 'hub-10', '2026-10-27 09:52:46', '2026-10-27 09:54:43')
   (8330, 1042, 10, 'C10-00000730', 'picked_up', 'hub-28', '2026-10-27 11:05:44', '2026-10-27 11:06:19')
   (8331, 1042, 10, 'C10-00000731', 'in_transit', 'hub-16', '2026-10-28 00:59:00', '2026-10-28 00:59:55')
   (8332, 1042, 10, 'C10-00000732', 'in_transit', 'hub-10', '2026-10-28 06:42:23', '2026-10-28 06:42:56')
   (8333, 1042, 10, 'C10-00000733', 'in_transit', 'hub-19', '2026-10-28 19:04:23', '2026-10-28 19:04:37')
   (8334, 1042, 10, 'C10-00000734', 'in_transit', 'hub-25', '2026-10-28 21:40:20', '2026-10-28 21:40:42')
   (8335, 1042, 10, 'C10-00000735', 'out_for_delivery', 'hub-13', '2026-10-29 06:22:56', '2026-10-29 06:24:54')
   (8336, 1042, 10, 'C10-00000736', 'delivered', 'hub-14', '2026-10-29 19:55:39', '2026-10-29 19:55:50')
```

```text
$ python3 lab06_plans.py --step 1
== Step 1 - the table ==
  rows 300,000  shipments 37,500  carriers 12  received_at 2026-05-31 00:11:33 .. 2026-11-24 01:14:39
  6,285 pages (25.7 MB), no secondary indexes

```

Eight scans per shipment, 12 carriers, about 180 days of `received_at`. The table occupies 6,285
pages of 4,096 bytes; the only B-tree is the table itself, keyed by `event_id` (the rowid).

## Step 2 — Full scan versus index search

```text
$ python3 lab06_plans.py --step 2
== Step 2 - full scan versus index search ==

  [no index on shipment_id]
  SQL: SELECT * FROM scan_events WHERE shipment_id = ?   params (1042,)
    plan: SCAN scan_events
    rows 8   median 13.68 ms per query

  [after CREATE INDEX idx_ship ON scan_events (shipment_id)]
  SQL: SELECT * FROM scan_events WHERE shipment_id = ?   params (1042,)
    plan: SEARCH scan_events USING INDEX idx_ship (shipment_id=?)
    rows 8   median 15.6 us per query

  index search is 875x faster than the full scan on this machine

```

`SCAN` reads all 300,000 rows to find 8; `SEARCH ... USING INDEX` descends a B-tree of a few levels
and reads 8 index entries plus 8 table rows. The scan grows with the table and the search with the
logarithm of it, so the ratio grows with size. The same step on 40,000 rows (about 13% of the size):

```text
$ python3 lab06_plans.py --shipments 5000 --step 2
SQLite 3.53.4; built 40,000 rows in 0.2 s (seed 6)

== Step 2 - full scan versus index search ==

  [no index on shipment_id]
  SQL: SELECT * FROM scan_events WHERE shipment_id = ?   params (1042,)
    plan: SCAN scan_events
    rows 8   median 1.75 ms per query

  [after CREATE INDEX idx_ship ON scan_events (shipment_id)]
  SQL: SELECT * FROM scan_events WHERE shipment_id = ?   params (1042,)
    plan: SEARCH scan_events USING INDEX idx_ship (shipment_id=?)
    rows 8   median 15.6 us per query

  index search is 112x faster than the full scan on this machine
```

The search time stayed the same (15.6 µs); the scan shrank from about 13.7 ms to 1.75 ms with the
row count, and the ratio fell from 875× to 112×.

## Step 3 — Composite index column order

```text
$ python3 lab06_plans.py --step 3
== Step 3 - composite index column order ==

  [only index idx_recv_carrier (received_at, carrier_id)]
  SQL: SELECT count(*) FROM scan_events WHERE carrier_id = ? AND received_at >= ?   params (7, '2026-11-17 00:00:00')
    plan: SEARCH scan_events USING COVERING INDEX idx_recv_carrier (received_at>?)
    rows 1   median 491.2 us per query

  [only index idx_carrier_recv (carrier_id, received_at)]
  SQL: SELECT count(*) FROM scan_events WHERE carrier_id = ? AND received_at >= ?   params (7, '2026-11-17 00:00:00')
    plan: SEARCH scan_events USING COVERING INDEX idx_carrier_recv (carrier_id=? AND received_at>?)
    rows 1   median 27.0 us per query

  index entries walked: range column first 8,794, equality column first 863
  equality-first is 18.2x faster on this machine

```

Both indexes cover `count(*)`, so the only difference is the order. With the range column first the
bracket shows only `(received_at>?)`: the search walks every scan of the week (8,794 entries, all
carriers) and checks `carrier_id` on each. With the equality column first it walks only carrier 7's
863 entries for the week. The time ratio (18× on this machine) points the same way as the entries
ratio (about 10×); the exact factor depends on per-entry and per-query costs, so the entries walked
are the number to reason with.

## Step 4 — Covering index

```text
$ python3 lab06_plans.py --step 4
== Step 4 - covering index ==

  [index (carrier_id, received_at): status read from the table]
  SQL: SELECT received_at, status FROM scan_events WHERE carrier_id = ? AND received_at >= ?   params (7, '2026-11-17 00:00:00')
    plan: SEARCH scan_events USING INDEX idx_carrier_recv (carrier_id=? AND received_at>?)
    rows 863   median 840.8 us per query

  [index (carrier_id, received_at, status): covering]
  SQL: SELECT received_at, status FROM scan_events WHERE carrier_id = ? AND received_at >= ?   params (7, '2026-11-17 00:00:00')
    plan: SEARCH scan_events USING COVERING INDEX idx_carrier_recv_status (carrier_id=? AND received_at>?)
    rows 863   median 536.8 us per query

  the covering index is 1.6x faster on this machine

```

Without `status` in the index, each of the 863 matches costs a lookup in the table B-tree by rowid.
The covering index avoids them, about 1.6× faster here. The price is a wider index that is updated
on every insert and whenever `status` changes. In PostgreSQL the equivalent is an `INCLUDE` column
and an `Index Only Scan`.

## Step 5 — Indexes the planner cannot use, and the fixes

```text
$ python3 lab06_plans.py --step 5
== Step 5 - indexes the planner cannot use, and the fixes ==

  [function on the column (index idx_recv exists)]
  SQL: SELECT * FROM scan_events WHERE date(received_at) = ?   params ('2026-11-20',)
    plan: SCAN scan_events
    rows 1,701   median 46.71 ms per query

  [rewritten as a range on the bare column]
  SQL: SELECT * FROM scan_events WHERE received_at >= ? AND received_at < ?   params ('2026-11-20 00:00:00', '2026-11-21 00:00:00')
    plan: SEARCH scan_events USING INDEX idx_recv (received_at>? AND received_at<?)
    rows 1,701   median 3.52 ms per query

  [leading wildcard (index idx_carrier_event exists)]
  SQL: SELECT * FROM scan_events WHERE carrier_event_id LIKE ?   params ('%00000420',)
    plan: SCAN scan_events
    rows 12   median 52.78 ms per query

  [prefix LIKE: still a scan in SQLite (LIKE is case-insensitive, the index is not)]
  SQL: SELECT * FROM scan_events WHERE carrier_event_id LIKE ?   params ('C07-0000042%',)
    plan: SCAN scan_events
    rows 10   median 23.74 ms per query

  [prefix GLOB (case-sensitive): an index range]
  SQL: SELECT * FROM scan_events WHERE carrier_event_id GLOB ?   params ('C07-0000042*',)
    plan: SEARCH scan_events USING INDEX idx_carrier_event (carrier_event_id>? AND carrier_event_id<?)
    rows 10   median 32.7 us per query

  [same function query after CREATE INDEX idx_recv_day ON scan_events (date(received_at))]
  SQL: SELECT * FROM scan_events WHERE date(received_at) = ?   params ('2026-11-20',)
    plan: SEARCH scan_events USING INDEX idx_recv_day (<expr>=?)
    rows 1,701   median 3.15 ms per query

```

- `date(received_at) = ?`: the index is sorted by `received_at`, not by `date(received_at)`, so the
  planner cannot descend it; it scans and calls `date()` 300,000 times (slower than Step 2's plain
  scan). Rewriting as a half-open range on the bare column gives the same 1,701 rows from an index
  range, about 13× faster; an index on the expression also works (`(<expr>=?)`).
- `LIKE '%00000420'`: a leading wildcard has no starting point in a sorted index, so it scans. Fixes
  are a different access path: store and index the reversed string, or use a text-search index.
- `LIKE 'C07-0000042%'`: still a scan, because SQLite's `LIKE` ignores case by default and the index
  uses binary (case-sensitive) order. `GLOB` is case-sensitive, so the same prefix becomes the range
  `(carrier_event_id>? AND carrier_event_id<?)` and returns the same 10 rows about 700× faster. An index
  declared `COLLATE NOCASE` would let `LIKE` use it instead.

## Step 6 — ORDER BY from an index versus a temporary B-tree

```text
$ python3 lab06_plans.py --step 6
== Step 6 - ORDER BY from an index versus a temporary B-tree ==

  [latest 20 events, no index on received_at]
  SQL: SELECT * FROM scan_events ORDER BY received_at DESC LIMIT 20
    plan: SCAN scan_events
    plan: USE TEMP B-TREE FOR ORDER BY
    rows 20   median 26.61 ms per query

  [latest 20 events, index on received_at]
  SQL: SELECT * FROM scan_events ORDER BY received_at DESC LIMIT 20
    plan: SCAN scan_events USING INDEX idx_recv
    rows 20   median 39.7 us per query

  [one shipment's timeline, index (shipment_id)]
  SQL: SELECT occurred_at, status FROM scan_events WHERE shipment_id = ? ORDER BY occurred_at   params (1042,)
    plan: SEARCH scan_events USING INDEX idx_ship (shipment_id=?)
    plan: USE TEMP B-TREE FOR ORDER BY
    rows 8   median 9.6 us per query

  [one shipment's timeline, index (shipment_id, occurred_at)]
  SQL: SELECT occurred_at, status FROM scan_events WHERE shipment_id = ? ORDER BY occurred_at   params (1042,)
    plan: SEARCH scan_events USING INDEX idx_ship_time (shipment_id=?)
    rows 8   median 7.1 us per query

  latest-20 with the index is 669x faster on this machine

```

Without an index, "latest 20" must read and sort every row into a temporary B-tree before it can
return the first one. With the index on `received_at`, the plan scans the index backwards and stops
after 20 entries, about 670× faster. The timeline query only ever sorts 8 rows, so removing its
temporary B-tree saves a few microseconds; the index order matters most when the sort input is large
or a `LIMIT` lets the engine stop early.

## Step 7 — The write cost of extra indexes

```text
$ python3 lab06_plans.py --step 7
== Step 7 - write cost of extra indexes (300,000 rows inserted per run, best of 3) ==
  secondary indexes   insert time  vs none    pages  vs none
  0                        0.35 s    1.00x    6,285    1.00x
  1                        0.50 s    1.43x    8,896    1.42x
  3                        1.04 s    2.95x   13,192    2.10x
  5                        1.77 s    5.04x   17,705    2.82x
  indexes, in order added: idx_ship_time, idx_carrier_event, idx_carrier_recv, idx_recv, idx_status_loc
```

Each secondary index is another B-tree updated on every insert, so both time and pages rise with
the index count; time rose faster than pages (5.0× against 2.8× with five indexes). Rows are
generated shipment by shipment, so `shipment_id` keys arrive in order and append to the end of
their index, while keys for the carrier, time, and status indexes land throughout their trees, which
costs more page work per insert. The first candidate to drop is `idx_status_loc`: no query in this
lab needs it.

## Smoke test

```text
$ python3 -m unittest tests.examples.test_lab06 -v
test_covering_index_skips_the_table (tests.examples.test_lab06.Lab06Tests.test_covering_index_skips_the_table) ... ok
test_data_is_seeded_and_shaped (tests.examples.test_lab06.Lab06Tests.test_data_is_seeded_and_shaped) ... ok
test_equality_column_first (tests.examples.test_lab06.Lab06Tests.test_equality_column_first) ... ok
test_more_indexes_cost_more_writes (tests.examples.test_lab06.Lab06Tests.test_more_indexes_cost_more_writes) ... ok
test_order_by_from_index_or_temp_btree (tests.examples.test_lab06.Lab06Tests.test_order_by_from_index_or_temp_btree) ... ok
test_plan_helper_is_not_fooled_by_the_statement_cache (tests.examples.test_lab06.Lab06Tests.test_plan_helper_is_not_fooled_by_the_statement_cache) ... ok
test_scan_then_index_search (tests.examples.test_lab06.Lab06Tests.test_scan_then_index_search) ... ok
test_sources_compile (tests.examples.test_lab06.Lab06Tests.test_sources_compile) ... ok
test_unusable_predicates_and_fixes (tests.examples.test_lab06.Lab06Tests.test_unusable_predicates_and_fixes) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.880s

OK
```

Run from the repository root (the author used the repository's virtual environment interpreter in
place of `python3`). It builds 20,000 rows and asserts plan text and relationships only.
