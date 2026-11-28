# Lab 16 — sample results

Runs on a laptop (macOS, Python 3.14.7; the same output was also produced with Python 3.9.6) with the
default seed 16. Every block below is copied from a real run, trimmed only where noted. The bus,
the order generator, and the fault injection are driven by seeded random generators and the
workflow is single-threaded, so the same command prints the same numbers on any machine. Commands
were run from a copy of the lab directory so that `--keep data` wrote inside it.

## Step 1 — Happy path

```text
$ python3 lab16_workflow.py --experiment happy --trace AM-1001
seed=16 orders=10 skus=3 initial stock=50 per SKU duplicate_rate=0.3 reorder_rate=0.3 (faults apply to duplicates and payment-failure)

== happy
   orders by status   {'SHIPPED': 10}
   payments           {'AUTHORIZED': 10}   shipments 10
   stock on hand      {'SKU-A': 44, 'SKU-B': 41, 'SKU-C': 44}
   bus                published 40, deliveries 60, duplicates injected 0, reorders injected 0
   consumers          duplicates skipped 0, stale ignored 8, unknown order 0
   invariants         OK

-- deliveries for AM-1001 in 'happy'
 step  consumer   type                           event id    outcome
    1  inventory  atlasmart.order.placed         ord-0001    applied
    3  orders     atlasmart.inventory.reserved   inv-0001    applied
    5  payments   atlasmart.inventory.reserved   inv-0001    applied
    6  orders     atlasmart.payment.authorized   pay-0001    applied
   10  shipping   atlasmart.payment.authorized   pay-0001    applied
   13  orders     atlasmart.shipment.created     shp-0001    applied
```

Answers:

1. 40 events published = 10 orders × 4 events (`order.placed`, `inventory.reserved`,
   `payment.authorized`, `shipment.created`). 60 deliveries: `order.placed` has 1 subscriber,
   `inventory.reserved` 2 (Payments, Orders), `payment.authorized` 2 (Shipping, Orders),
   `shipment.created` 1 (Orders): 10 × (1 + 2 + 2 + 1) = 60. `payment.authorized` does not go to
   Inventory, because Inventory's subscription on `payments` filters to `payment.failed`.
2. "stale ignored 8" on a bus with no faults: Orders reads three topics, and the bus picks which
   subscription to serve next at random. Order is kept within each topic, never across topics, so
   eight times an `inventory.reserved` reached Orders after the same order's `payment.authorized` or
   `shipment.created`. Orders' state precedence (PENDING < RESERVED < PAID < SHIPPED) ignored it.
   In the AM-1001 trace the order happened to arrive in sequence.

## Step 2 — Crash between commit and publish

The moment of the crash, from the snippet on the lab page:

```text
crash: orders relay crashed before publishing ord-0003 (8 outbox rows unpublished)
orders committed: 10
outbox unpublished: 8 | published so far: 2
after restart: unpublished 0 | published 10
```

```text
$ python3 lab16_workflow.py --experiment crash --trace AM-1005
seed=16 orders=10 skus=3 initial stock=50 per SKU duplicate_rate=0.3 reorder_rate=0.3 (faults apply to duplicates and payment-failure)

== crash
   orders relay crashed before publishing ord-0003 (8 outbox rows unpublished); restarted on the next poll
   payments relay crashed after publishing pay-0005, before marking it published; restarted on the next poll
   orders by status   {'SHIPPED': 10}
   payments           {'AUTHORIZED': 10}   shipments 10
   stock on hand      {'SKU-A': 44, 'SKU-B': 41, 'SKU-C': 44}
   bus                published 41, deliveries 62, duplicates injected 0, reorders injected 0
   consumers          duplicates skipped 2, stale ignored 4, unknown order 0
   invariants         OK

-- deliveries for AM-1005 in 'crash'
 step  consumer   type                           event id    outcome
   15  inventory  atlasmart.order.placed         ord-0005    applied
   26  payments   atlasmart.inventory.reserved   inv-0005    applied
   30  orders     atlasmart.payment.authorized   pay-0005    applied
   34  orders     atlasmart.payment.authorized   pay-0005    duplicate skipped
   37  orders     atlasmart.inventory.reserved   inv-0005    stale ignored
   39  shipping   atlasmart.payment.authorized   pay-0005    applied
   40  shipping   atlasmart.payment.authorized   pay-0005    duplicate skipped
   45  orders     atlasmart.shipment.created     shp-0005    applied
```

Inspecting the kept databases (`--keep data`; output of `> /dev/null` omitted):

```text
$ sqlite3 data/crash/orders.db "SELECT seq, event_id, topic, published FROM outbox ORDER BY seq LIMIT 4;"
1|ord-0001|orders|1
2|ord-0002|orders|1
3|ord-0003|orders|1
4|ord-0004|orders|1
$ sqlite3 data/crash/orders.db "SELECT event FROM outbox WHERE seq = 3;"
{"data": {"amount_cents": 8209, "order_id": "AM-1003", "payment_method": "test-card-ok", "qty": 1, "schema_version": 1, "sku": "SKU-B"}, "datacontenttype": "application/json", "id": "ord-0003", "source": "/atlasmart/orders", "specversion": "1.0", "subject": "AM-1003", "type": "atlasmart.order.placed"}
$ sqlite3 data/crash/payments.db "SELECT * FROM processed_events LIMIT 3;"
/atlasmart/inventory|inv-0001
/atlasmart/inventory|inv-0002
/atlasmart/inventory|inv-0003
$ sqlite3 data/crash/shipping.db "SELECT * FROM processed_events WHERE event_id = 'pay-0005';"
/atlasmart/payments|pay-0005
$ sqlite3 data/crash/inventory.db "SELECT order_id, sku, qty, status FROM reservations LIMIT 3;"
AM-1001|SKU-B|2|RESERVED
AM-1002|SKU-B|2|RESERVED
AM-1003|SKU-B|1|RESERVED
```

Answers:

1. At the crash, all 10 orders were committed and 8 outbox rows (ord-0003 to ord-0010) were still
   `published = 0`. The relay's restart simply read them again; nothing was lost because the event
   was part of the same commit as the order.
2. The second crash is the opposite gap: `pay-0005` reached the bus but was not marked published, so
   the restarted relay sent it again (41 published instead of 40). Both of its subscribers, Orders
   (step 34) and Shipping (step 40), found `(/atlasmart/payments, pay-0005)` already in
   `processed_events` and skipped it: "duplicates skipped 2". The outbox gives at-least-once
   publishing; the consumers' processed-event table turns that into one effect.

## Steps 3 and 4 — Duplicate and out-of-order delivery, then replay

```text
$ python3 lab16_workflow.py --experiment duplicates
seed=16 orders=10 skus=3 initial stock=50 per SKU duplicate_rate=0.3 reorder_rate=0.3 (faults apply to duplicates and payment-failure)

== duplicates
   orders by status   {'SHIPPED': 10}
   payments           {'AUTHORIZED': 10}   shipments 10
   stock on hand      {'SKU-A': 44, 'SKU-B': 41, 'SKU-C': 44}
   bus                published 40, deliveries 88, duplicates injected 28, reorders injected 25
   consumers          duplicates skipped 28, stale ignored 1, unknown order 0
   replay             10 order.placed events replayed into Inventory: 13 skipped as duplicates, stock/payments/shipments unchanged
   invariants         OK

== duplicates (naive consumers, no processed_events check)
   orders by status   {'SHIPPED': 10}
   payments           {'AUTHORIZED': 19}   shipments 31
   stock on hand      {'SKU-A': 44, 'SKU-B': 32, 'SKU-C': 44}
   bus                published 74, deliveries 157, duplicates injected 50, reorders injected 45
   consumers          duplicates skipped 0, stale ignored 64, unknown order 0
   invariants         9 BROKEN
     - AM-1001: SHIPPED with 2 payment(s), 3 shipment(s), 2 reservation(s)
     - AM-1002: SHIPPED with 1 payment(s), 3 shipment(s), 1 reservation(s)
     - AM-1003: SHIPPED with 3 payment(s), 5 shipment(s), 2 reservation(s)
     - AM-1004: SHIPPED with 2 payment(s), 4 shipment(s), 1 reservation(s)
     - AM-1005: SHIPPED with 1 payment(s), 3 shipment(s), 1 reservation(s)
     - AM-1007: SHIPPED with 3 payment(s), 5 shipment(s), 3 reservation(s)
     - AM-1008: SHIPPED with 4 payment(s), 4 shipment(s), 1 reservation(s)
     - AM-1009: SHIPPED with 1 payment(s), 2 shipment(s), 1 reservation(s)
     - stock {'SKU-A': 44, 'SKU-B': 32, 'SKU-C': 44} != expected {'SKU-A': 44, 'SKU-B': 41, 'SKU-C': 44}
```

Answers:

1. Idempotent run: the final state is identical to the happy path, and "duplicates skipped" (28)
   equals "duplicates injected" (28). Every redelivered event hit a `processed_events` primary key
   in the same transaction as its effect.
2. Naive run: duplicates multiply down the chain. A duplicate `order.placed` makes Inventory reserve
   twice and publish a *second, different* `inventory.reserved` (a new event id), so Payments charges
   twice even if its own delivery was clean, and each payment triggers a shipment. That is why the
   bus published 74 events instead of 40, and why shipments (31) outgrow payments (19). Stock of
   SKU-B is 9 units too low.
3. Orders stays correct even in the naive run (all 10 SHIPPED, "stale ignored 64"): its state
   machine is naturally idempotent, so a duplicate status change is a no-op. Inventory, Payments, and
   Shipping insert rows, which is not idempotent without the processed-event record.
4. Replay: all 10 `order.placed` events were re-delivered to Inventory; the faulty bus duplicated 3
   of those deliveries, so 13 were skipped and nothing changed.

## Step 5 — Payment failure and compensation

```text
$ python3 lab16_workflow.py --experiment payment-failure --trace AM-1004
seed=16 orders=10 skus=3 initial stock=50 per SKU duplicate_rate=0.3 reorder_rate=0.3 (faults apply to duplicates and payment-failure)

== payment-failure
   orders by status   {'CANCELLED': 2, 'SHIPPED': 8}
   payments           {'AUTHORIZED': 8, 'DECLINED': 2}   shipments 8
   stock on hand      {'SKU-A': 44, 'SKU-B': 41, 'SKU-C': 50}
   bus                published 40, deliveries 87, duplicates injected 29, reorders injected 20
   consumers          duplicates skipped 29, stale ignored 3, unknown order 0
   invariants         OK

-- deliveries for AM-1004 in 'payment-failure'
 step  consumer   type                           event id    outcome
    7  inventory  atlasmart.order.placed         ord-0004    applied
   36  payments   atlasmart.inventory.reserved   inv-0005    applied
   37  inventory  atlasmart.payment.failed       pay-0006    applied
   54  orders     atlasmart.payment.failed       pay-0006    applied
   55  orders     atlasmart.inventory.reserved   inv-0005    stale ignored
   56  payments   atlasmart.inventory.reserved   inv-0005    duplicate skipped
   65  orders     atlasmart.inventory.reserved   inv-0005    duplicate skipped
   66  payments   atlasmart.inventory.reserved   inv-0005    duplicate skipped
   69  orders     atlasmart.payment.failed       pay-0006    duplicate skipped
   81  orders     atlasmart.inventory.reserved   inv-0005    duplicate skipped
```

Answers:

1. AM-1004 and AM-1008 are declined. Each produces `payment.failed`, consumed by Inventory (the
   compensation: release the reservation and add the stock back, step 37) and by Orders (mark
   CANCELLED, step 54). Both declined orders were for SKU-C, whose stock is back at 50.
2. 40 events again: 8 × 4 for shipped orders plus 2 × 4 for cancelled ones (`order.placed`,
   `inventory.reserved`, `payment.failed`, `inventory.released`). `inventory.released` has no
   subscriber in this lab; it is published for anyone who needs it later.
3. Ordering: `payment.failed` reached Orders (step 54) before `inventory.reserved` (step 55).
   Without state precedence, the late event would have moved the order from CANCELLED back to
   RESERVED. The duplicate `payment.failed` (step 69) would have released the stock a second time
   in a naive Inventory.

## Step 6 — Naive dual write

```text
$ python3 lab16_workflow.py --experiment dual-write --trace AM-1006
seed=16 orders=10 skus=3 initial stock=50 per SKU duplicate_rate=0.3 reorder_rate=0.3 (faults apply to duplicates and payment-failure)

== dual-write
   AM-1003: committed, crashed before publishing
   AM-1006: published, then rolled back
   orders by status   {'PENDING': 1, 'SHIPPED': 8}
   payments           {'AUTHORIZED': 9}   shipments 9
   stock on hand      {'SKU-A': 44, 'SKU-B': 42, 'SKU-C': 44}
   bus                published 36, deliveries 54, duplicates injected 0, reorders injected 0
   consumers          duplicates skipped 0, stale ignored 6, unknown order 3
   invariants         3 BROKEN
     - AM-1003: stuck in PENDING (0 reservation(s), 0 payment(s))
     - AM-1006: not in Orders, yet 1 reservation(s), 1 payment(s), 1 shipment(s) (ghost order)
     - stock {'SKU-A': 44, 'SKU-B': 42, 'SKU-C': 44} != expected {'SKU-A': 46, 'SKU-B': 42, 'SKU-C': 44}

-- deliveries for AM-1006 in 'dual-write'
 step  consumer   type                           event id    outcome
   15  inventory  atlasmart.order.placed         ord-dw-0006 applied
   25  payments   atlasmart.inventory.reserved   inv-0005    applied
   32  orders     atlasmart.inventory.reserved   inv-0005    unknown order
   33  shipping   atlasmart.payment.authorized   pay-0005    applied
   37  orders     atlasmart.payment.authorized   pay-0005    unknown order
   39  orders     atlasmart.shipment.created     shp-0005    unknown order
```

Answers:

1. AM-1003 was committed and its event never published: the order is stuck in PENDING with nothing
   downstream. No retry can fix it, because nothing remembers that an event was owed.
2. AM-1006 was published and then rolled back: the order does not exist, yet 2 units of SKU-A were
   reserved, a card was authorized, and a shipment was created. Orders logged the three status events
   as "unknown order". Expected SKU-A stock is 46; the ghost took it to 44.
3. Only 9 orders exist (8 SHIPPED, 1 PENDING) and 36 events were published instead of 40 (AM-1003's
   four events never existed). With the outbox, the same two failures are impossible: the order and
   its event commit together or not at all.

## Step 7 — More duplicates, another seed

```text
$ python3 lab16_workflow.py --duplicate-rate 0.6 --experiment duplicates
seed=16 orders=10 skus=3 initial stock=50 per SKU duplicate_rate=0.6 reorder_rate=0.3 (faults apply to duplicates and payment-failure)

== duplicates
   orders by status   {'SHIPPED': 10}
   payments           {'AUTHORIZED': 10}   shipments 10
   stock on hand      {'SKU-A': 44, 'SKU-B': 41, 'SKU-C': 44}
   bus                published 40, deliveries 133, duplicates injected 73, reorders injected 35
   consumers          duplicates skipped 73, stale ignored 1, unknown order 0
   replay             10 order.placed events replayed into Inventory: 28 skipped as duplicates, stock/payments/shipments unchanged
   invariants         OK

== duplicates (naive consumers, no processed_events check)
   orders by status   {'SHIPPED': 10}
   payments           {'AUTHORIZED': 43}   shipments 104
   stock on hand      {'SKU-A': 42, 'SKU-B': 27, 'SKU-C': 44}
   bus                published 178, deliveries 616, duplicates injected 374, reorders injected 160
   consumers          duplicates skipped 0, stale ignored 419, unknown order 0
   invariants         9 BROKEN
```

(The nine broken-invariant lines are trimmed.) Doubling the duplicate rate leaves the idempotent
run's final state unchanged, while the naive run grows from 19 to 43 payments and from 31 to 104
shipments, because each extra effect also publishes extra events that are themselves duplicated. With `--seed 7` (full run, not
shown) all four outbox-based experiments again report `invariants OK`, the naive duplicates run
reports 11 broken invariants, and the dual-write run reports the same three kinds of breakage.

## Full default run

`python3 lab16_workflow.py` prints the six result blocks above (without traces) in the order happy,
crash, duplicates, duplicates (naive), payment-failure, dual-write, and exits with status 0, meaning
every experiment broke exactly the invariants it was designed to break and no others.

## Smoke test

```text
$ python3 -m unittest tests.examples.test_lab16 -v
test_bus_filtering_duplicates_and_replay (tests.examples.test_lab16.Lab16Tests.test_bus_filtering_duplicates_and_replay) ... ok
test_cli_runs_all_experiments (tests.examples.test_lab16.Lab16Tests.test_cli_runs_all_experiments) ... ok
test_crash_between_commit_and_publish_is_saved_by_the_outbox (tests.examples.test_lab16.Lab16Tests.test_crash_between_commit_and_publish_is_saved_by_the_outbox) ... ok
test_duplicates_are_harmless_only_with_idempotent_consumers (tests.examples.test_lab16.Lab16Tests.test_duplicates_are_harmless_only_with_idempotent_consumers) ... ok
test_event_envelope (tests.examples.test_lab16.Lab16Tests.test_event_envelope) ... ok
test_happy_path (tests.examples.test_lab16.Lab16Tests.test_happy_path) ... ok
test_naive_dual_write_loses_an_event_and_creates_a_ghost (tests.examples.test_lab16.Lab16Tests.test_naive_dual_write_loses_an_event_and_creates_a_ghost) ... ok
test_outbox_row_commits_with_the_order_or_not_at_all (tests.examples.test_lab16.Lab16Tests.test_outbox_row_commits_with_the_order_or_not_at_all) ... ok
test_payment_failure_runs_the_compensation (tests.examples.test_lab16.Lab16Tests.test_payment_failure_runs_the_compensation) ... ok
test_sources_compile (tests.examples.test_lab16.Lab16Tests.test_sources_compile) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.835s

OK
```
