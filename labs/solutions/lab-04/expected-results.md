# Lab 04 — sample results

Runs on a laptop (macOS, Python 3.14) with the default seed 11. Separate seeded random number
generators drive amounts, lost responses, keys, and redeliveries, so the same command gives the same
tables on any machine with Python 3.10 or newer, and the `no-key` and `key` rows see exactly the same
lost responses.

## Steps 1, 2, and 4 — Default run

```text
$ python3 idempotency_sim.py
orders=1000 loss_rate=0.2 max_attempts=4 redelivery_rate=0.1 seed=11

Payment capture API (client retries on timeout)
        mode |     requests |    lost resp |      gave up |      charges |  double chgd |  overcharged |      replays |   retried ok |    identical
-------------+--------------+--------------+--------------+--------------+--------------+--------------+--------------+--------------+-------------
      no-key |         1238 |          240 |            2 |         1238 |          194 |     25041.73 |            0 |          192 |            0
         key |         1238 |          240 |            2 |         1000 |            0 |          0.0 |          238 |          192 |          192

same key, different amount -> HTTP 422 (refused, not replayed)

PaymentCaptured consumer (at-least-once delivery)
    consumer |       events |   deliveries |      applied |  dup dropped |  double appl | ledger total |     expected
-------------+--------------+--------------+--------------+--------------+--------------+--------------+-------------
       naive |         1000 |         1105 |         1105 |            0 |           97 |    116760.81 |    105671.04
       inbox |         1000 |         1105 |         1000 |          105 |            0 |    105671.04 |    105671.04
```

## Step 5 — Changing the failure rates

```text
$ python3 idempotency_sim.py --mode no-key key --max-attempts 1
        mode |     requests |    lost resp |      gave up |      charges |  double chgd |  overcharged |      replays |   retried ok |    identical
-------------+--------------+--------------+--------------+--------------+--------------+--------------+--------------+--------------+-------------
      no-key |         1000 |          197 |          197 |         1000 |            0 |          0.0 |            0 |            0 |            0
         key |         1000 |          197 |          197 |         1000 |            0 |          0.0 |            0 |            0 |            0

$ python3 idempotency_sim.py --mode no-key key --loss-rate 0.5
        mode |     requests |    lost resp |      gave up |      charges |  double chgd |  overcharged |      replays |   retried ok |    identical
-------------+--------------+--------------+--------------+--------------+--------------+--------------+--------------+--------------+-------------
      no-key |         1885 |          947 |           62 |         1885 |          496 |     92159.11 |            0 |          434 |            0
         key |         1885 |          947 |           62 |         1000 |            0 |          0.0 |          885 |          434 |          434

$ python3 idempotency_sim.py --mode inbox --redelivery-rate 0.3
    consumer |       events |   deliveries |      applied |  dup dropped |  double appl | ledger total |     expected
-------------+--------------+--------------+--------------+--------------+--------------+--------------+-------------
       naive |         1000 |         1393 |         1393 |            0 |          277 |    148296.56 |    105671.04
       inbox |         1000 |         1393 |         1000 |          393 |            0 |    105671.04 |    105671.04
```

(The configuration line and table titles are omitted from the Step 5 runs.)

## What to notice

1. **Every request charged.** Without a key, `charges` equals `requests` (1,238). The server cannot
   tell a retry from a new purchase, so 238 retries became 238 extra charges spread over 194 orders,
   25,041.73 currency units that would have to be refunded.
2. **The retry count follows from the loss rate.** 240 responses were lost; 238 of them were followed
   by a retry (the other 2 were the last attempts of the 2 orders that gave up). About one order in
   five (194 + 2 of 1,000) lost its first response, matching the 20% loss rate.
3. **The key turns retries into replays.** With the same lost responses, the key mode created exactly
   1,000 charges. The 238 retries were answered from the `idempotency_keys` table, and all 192 clients
   that eventually got an answer after a retry received byte-for-byte the response that had been lost
   (`identical` = `retried ok`): same charge ID, same capture sequence number.
4. **A key is bound to its request.** Reusing a key with a different amount returned 422. Replaying
   the stored response there would have told the client that 0.01 was captured when a different amount
   was.
5. **Not retrying is not a fix.** With one attempt, nobody is double-charged, but 197 clients (the
   lost responses) do not know whether payment went through, although every one of those orders was
   charged. Retries are needed for a definite answer; keys make them safe.
6. **Keys keep working as loss gets worse.** At a 50% loss rate the no-key client double-charged 496
   orders; the key mode still created exactly 1,000 charges and served 885 replays. 62 orders gave up
   after 4 lost responses in a row (1,000 × 0.5^4 ≈ 62.5, as expected).
7. **The inbox catches every redelivery.** With 10% redelivery the naive consumer applied 1,105
   deliveries for 1,000 events and over-recorded 11,089.77 currency units (116,760.81 − 105,671.04)
   across 97 orders. The inbox consumer applied each event once and dropped exactly the 105 extra
   deliveries. At a 30% redelivery rate the naive error grew to 42,625.52 across 277 orders; the inbox
   result did not change.
8. **The constraint does the work.** In both fixed modes the decision "have I seen this before?" is a
   failed `INSERT` against a primary key, made inside the same transaction as the side effect. There is
   no window between checking and acting.

## Answers to the questions in the lab page

- **How does `charges` compare with `requests`?** Equal, in no-key mode: every request that reaches
  the server is a new charge.
- **How many orders were charged more than once?** 194, roughly the 20% of orders whose first
  response was lost (some of them lost two or three responses and were charged three or four times).
- **Was a `gave up` customer charged?** Yes: the server processed every attempt. The client does not
  know; it needs a way to look up the outcome (stretch challenge 3) rather than guess.
- **Why insert the key first, in one transaction with the charge?** A `SELECT` followed by an
  `INSERT` leaves a window in which two requests with the same key both see "not found" and both
  charge. The `INSERT` against a primary key is atomic: exactly one request wins. Keeping the key, the
  charge, and the stored response in one transaction means a crash cannot leave a charge without its
  key (which would allow a second charge) or a key without its charge (which would replay a response
  for money never taken).
- **What is the cost of not retrying?** Unknown outcomes: 197 orders charged but unconfirmed.
- **Does the key mode hold at 50% loss?** Yes: 0 double charges and 885 replays.
- **How does the naive ledger error grow with redelivery?** Roughly in proportion: 105 extra
  deliveries at 10% and 393 at 30%, and the over-recorded total grows with them.
