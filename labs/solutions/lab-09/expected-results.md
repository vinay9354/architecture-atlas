# Lab 09 — sample results

Runs on a laptop (macOS, Python 3.14) of `python3 replication_sim.py` with the defaults: 60 simulated
seconds, 50 client sessions, carrier writes at 70 per second, per-write apply lag drawn from a
lognormal distribution with a 40 ms median (sigma 0.8), seed 9. The simulation is deterministic, so
the same seed prints the same numbers on any machine.

## Run 1 — normal lag

```text
60 simulated s, 4556 writes (298 from clients), 6626 reads, seed 9

Apply lag per follower (lognormal, 40 ms; includes waiting behind earlier writes)
  follower |     p50 ms |     p99 ms |     max ms
-----------+------------+------------+-----------
follower-0 |       98.4 |      471.8 |      621.4
follower-1 |      101.1 |      648.8 |     1164.1

Read policies (staleness percentiles are over stale reads only)
            policy |    stale % |  stale p50 |  stale p99 |  RYW viol. | mono viol. |   leader % |   wait p99 |  fallbacks
-------------------+------------+------------+------------+------------+------------+------------+------------+-----------
      any-follower |       6.25 |       68.2 |      452.7 |        374 |         35 |        0.0 |        0.0 |          0
leader-after-write |       0.53 |       54.8 |      452.7 |          0 |          2 |      16.31 |        0.0 |          0
 wait-for-position |       0.66 |       54.2 |      452.7 |          0 |          4 |       0.08 |      131.6 |          5
   sticky-follower |       6.32 |       70.7 |      452.7 |        377 |          0 |        0.0 |        0.0 |          0
```

## Run 2 — lag spike on follower-1 (`--lag-spike`)

```text
60 simulated s, 4556 writes (298 from clients), 6626 reads, seed 9, lag spike on follower-1: +5000 ms for writes committed 20-30 s

Apply lag per follower (lognormal, 40 ms; includes waiting behind earlier writes)
  follower |     p50 ms |     p99 ms |     max ms
-----------+------------+------------+-----------
follower-0 |       98.4 |      471.8 |      621.4
follower-1 |      137.5 |     5272.5 |     5564.7

Read policies (staleness percentiles are over stale reads only)
            policy |    stale % |  stale p50 |  stale p99 |  RYW viol. | mono viol. |   leader % |   wait p99 |  fallbacks
-------------------+------------+------------+------------+------------+------------+------------+------------+-----------
      any-follower |      11.47 |      189.2 |     5099.1 |        630 |        340 |        0.0 |        0.0 |          0
leader-after-write |       4.92 |     2583.9 |     5150.3 |        189 |        269 |      16.31 |        0.0 |          0
 wait-for-position |       2.11 |     1411.9 |     5178.9 |          0 |         94 |       4.48 |      500.0 |        297
   sticky-follower |      11.68 |      211.6 |     5136.8 |        635 |          0 |        0.0 |        0.0 |          0
```

## Run 3 — tuning the knobs during the spike

`--lag-spike --pin-ms 3000` (only the policy rows):

```text
      any-follower |      11.47 |      189.2 |     5099.1 |        630 |        340 |        0.0 |        0.0 |          0
leader-after-write |       3.12 |     3218.0 |     5099.1 |         81 |        162 |      30.91 |        0.0 |          0
 wait-for-position |       2.11 |     1411.9 |     5178.9 |          0 |         94 |       4.48 |      500.0 |        297
   sticky-follower |      11.68 |      211.6 |     5136.8 |        635 |          0 |        0.0 |        0.0 |          0
```

`--lag-spike --wait-timeout-ms 100` (only the policy rows):

```text
      any-follower |      11.47 |      189.2 |     5099.1 |        630 |        340 |        0.0 |        0.0 |          0
leader-after-write |       4.92 |     2583.9 |     5150.3 |        189 |        269 |      16.31 |        0.0 |          0
 wait-for-position |       2.07 |     1492.1 |     5178.9 |          0 |         83 |       6.08 |      100.0 |        403
   sticky-follower |      11.68 |      211.6 |     5136.8 |        635 |          0 |        0.0 |        0.0 |          0
```

`--lag-dist exponential` (a 40 ms mean, no spike; only the policy rows):

```text
      any-follower |       4.15 |       50.6 |      231.7 |        249 |         15 |        0.0 |        0.0 |          0
leader-after-write |       0.29 |       43.6 |      239.7 |          0 |          4 |      16.31 |        0.0 |          0
 wait-for-position |       0.36 |       34.8 |      148.0 |          0 |          3 |        0.0 |       71.7 |          0
   sticky-follower |       4.29 |       52.6 |      191.8 |        259 |          0 |        0.0 |        0.0 |          0
```

## What to notice

1. **Effective lag is more than per-write lag.** Each write's own delay has a 40 ms median, yet the
   followers' median lag is about 100 ms. Followers apply in log order, so every write waits behind
   the slowest write ahead of it; at about 76 writes per second there is usually a slow one in
   front.
2. **Reading any follower gives eventual consistency and nothing more.** 6.25% of reads were stale,
   374 reads did not show the reader's own write, and 35 reads went backwards (for example, a page view showed
   a newer status in one widget and an older one in the next widget 20 ms later).
3. **Both read-your-writes policies removed the RYW violations** under normal lag, at different
   costs. Routing to the leader for 1 s after a write sent 16.31% of all reads to the leader.
   Waiting for the log position sent only 0.08% there (5 timeouts), and instead added latency to the
   reads that follow a write: p99 added wait 131.6 ms across all reads.
4. **Neither read-your-writes policy gives monotonic reads** (2 and 4 violations), because both still
   pick a random follower for most reads. The sticky policy has zero monotonic violations, because one
   follower's applied position never goes down, but it does nothing for read-your-writes (377).
   Session guarantees are separate properties; a product that needs both has to combine mechanisms.
5. **The lag spike separates guesses from guarantees.** With follower-1 about 5 s behind:
   - Leader-after-write is a guess that lag stays under 1 s, and it failed 189 times. Stretching the
     window to 3 s still failed 81 times and nearly doubled leader reads to 30.91%.
   - Wait-for-position still had zero RYW violations: 297 reads waited the full 500 ms and then fell
     back to the leader. A shorter 100 ms timeout made 403 reads fall back sooner, raising leader
     reads to 6.08% and cutting the worst added wait to 100 ms.
   - Sticky-follower kept monotonic reads at zero, but the half of the clients pinned to follower-1
     saw multi-second staleness for the whole spike, because the policy never moves them.
6. **The staleness numbers are small next to AtlasMart's NFR-1** (99% of events visible within 60 s):
   even the spike's worst stale read was about 5.2 s old. Replica lag matters here for the person who
   just made a change, not for freshness in general, which is why the fix is a session guarantee
   rather than leader reads for everyone.

## Answers to the questions in the lab page

- **Why is the RYW violation count not zero for the sticky policy?** Sticking to a follower keeps the
  client's view moving forward, but the client's own write still has to reach that follower; a read
  0-200 ms after the write often arrives first.
- **Why does leader-after-write still show stale reads under normal lag?** Its guarantee covers only
  the client's own write and only for the pin window. After the window, reads go to a follower that
  may be missing a carrier update for the same shipment; that is stale but not a RYW violation.
- **What does wait-for-position need from the database?** The leader must return the log position of
  each write (for example the WAL position after commit in PostgreSQL), and each follower must
  expose its applied position (`pg_last_wal_replay_lsn()` on a PostgreSQL standby). The client or
  API stores the position in the session and compares.
- **Which policy would you choose for AtlasMart's agent console?** Wait-for-position with a short
  timeout, or leader reads for agent sessions only while agent traffic is small. Customers who never
  write need monotonic reads (sticky routing, or a per-shipment version number the UI refuses to go
  backwards from) and bounded staleness, not read-your-writes.
- **With an exponential lag distribution** (`--lag-ms 40` is then the mean; for the default
  lognormal it is the median, and that lognormal's mean is about 40 × e^(0.8²/2) ≈ 55 ms with a
  longer tail), stale reads fell from 6.25% to 4.15% and the stale p99 from 452.7 ms to 231.7 ms; the guarantees
  held exactly as before. Policies 2 and 3 do not depend on the lag distribution; their cost does.
