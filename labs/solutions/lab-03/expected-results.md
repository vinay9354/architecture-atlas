# Lab 03 — sample results

Runs on a laptop (macOS, Python 3.14) with the default seed 7. The simulation uses simulated time and
seeded random number generators, so the same command gives the same table on any machine with
Python 3.10 or newer.

## Step 2 — No jitter versus full jitter

```text
$ python3 queue_sim.py --jitter none full
messages=300 outage=2.0s failure_rate=0.05 poison=1 process=100ms slow_rate=0.01 backoff=1.0s..60.0s seed=7

 consumers |     jitter |    max rcv |      vis s |  processed |    retried |        DLQ | DLQ ok msg | duplicates |      p50 s |      p99 s |    drain s | retry peak
-----------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+-----------
         4 |       none |          5 |        5.0 |        299 |        616 |          1 |          0 |          3 |       6.71 |      17.63 |      37.52 |        300
         4 |       full |          5 |        5.0 |        298 |        742 |          2 |          1 |          3 |       5.64 |      14.09 |      23.23 |        234
```

## Step 3 — Maximum receive count 1 versus 5

```text
$ python3 queue_sim.py --max-receives 1 5
 consumers |     jitter |    max rcv |      vis s |  processed |    retried |        DLQ | DLQ ok msg | duplicates |      p50 s |      p99 s |    drain s | retry peak
-----------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+-----------
         4 |       full |          1 |        5.0 |          0 |        300 |        300 |        299 |          0 |        nan |        nan |       1.74 |        196
         4 |       full |          5 |        5.0 |        298 |        742 |          2 |          1 |          3 |       5.64 |      14.09 |      23.23 |        234

$ python3 queue_sim.py --max-receives 1 5 --outage-s 0
 consumers |     jitter |    max rcv |      vis s |  processed |    retried |        DLQ | DLQ ok msg | duplicates |      p50 s |      p99 s |    drain s | retry peak
-----------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+-----------
         4 |       full |          1 |        5.0 |        287 |         13 |         16 |         15 |          0 |       3.53 |      11.74 |      13.53 |          3
         4 |       full |          5 |        5.0 |        299 |         18 |          1 |          0 |          3 |       3.69 |      12.15 |      34.95 |          3

$ python3 queue_sim.py --max-receives 5 10
 consumers |     jitter |    max rcv |      vis s |  processed |    retried |        DLQ | DLQ ok msg | duplicates |      p50 s |      p99 s |    drain s | retry peak
-----------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+-----------
         4 |       full |          5 |        5.0 |        298 |        742 |          2 |          1 |          3 |       5.64 |      14.09 |      23.23 |        234
         4 |       full |         10 |        5.0 |        299 |        747 |          1 |          0 |          3 |        5.7 |      14.16 |      214.8 |        234
```

(The configuration line printed before each table is omitted after the first run.)

## Step 4 — One consumer versus four

```text
$ python3 queue_sim.py --consumers 1 4
 consumers |     jitter |    max rcv |      vis s |  processed |    retried |        DLQ | DLQ ok msg | duplicates |      p50 s |      p99 s |    drain s | retry peak
-----------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+-----------
         1 |       full |          5 |        5.0 |        299 |        217 |          1 |          0 |          0 |      16.52 |       52.4 |      55.13 |         91
         4 |       full |          5 |        5.0 |        298 |        742 |          2 |          1 |          3 |       5.64 |      14.09 |      23.23 |        234
```

## Step 5 — Visibility timeout shorter than processing time

```text
$ python3 queue_sim.py --consumers 16 --visibility-timeout 0.1 5
 consumers |     jitter |    max rcv |      vis s |  processed |    retried |        DLQ | DLQ ok msg | duplicates |      p50 s |      p99 s |    drain s | retry peak
-----------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+-----------
        16 |       full |          5 |        0.1 |        295 |        861 |         24 |         23 |         79 |       3.24 |       9.39 |      18.09 |        344
        16 |       full |          5 |        5.0 |        295 |        858 |          5 |          4 |          3 |       3.15 |       9.68 |      16.36 |        342
```

## What to notice

1. **No jitter keeps retries synchronized.** Four consumers fail the whole backlog during the outage
   in about 0.75 s (300 × 10 ms ÷ 4), and each failure comes back exactly 1 s later, so all 300 first
   retries become visible within one simulated second (`retry peak` 300). With full jitter the same
   retries spread over 0-1 s after each failure and the peak drops to 234; later retry rounds spread
   further because the ceiling doubles each time.
2. **Spreading retries finished the work sooner here.** Full jitter lowered p50 from 6.71 s to 5.64 s,
   p99 from 17.63 s to 14.09 s, and drain time from 37.52 s to 23.23 s.
3. **Full jitter is not free.** Its average delay is half the ceiling, so messages come back sooner,
   some of them while the dependency is still down: 742 retries against 616. One healthy message used
   up all five receives and landed in the DLQ. The receive limit and the backoff schedule together
   decide how long an outage a message can survive; size them as a pair.
4. **A receive limit of 1 means "no retries".** During the 2-second outage every message failed once
   and was parked: 299 healthy messages in the DLQ and nothing processed. Even without an outage, a 5%
   transient failure rate parked 15 healthy messages. Someone now has to redrive them by hand.
5. **A high receive limit keeps the poison message cycling.** With 5 receives and full jitter the
   poison message was parked at 34.95 s in the no-outage run; with 10 receives the queue was not fully
   settled until 214.8 s because the capped backoff keeps the poison message coming back for minutes.
   Classifying errors (retry only what can succeed later) beats raising the limit.
6. **More consumers finish sooner and push harder.** Four consumers cut p50 from 16.52 s to 5.64 s and
   drain time from 55.13 s to 23.23 s. They also made 742 failing calls during and after the outage
   against 217 for one consumer, because four consumers churn through the backlog four times as fast
   while the dependency is down. Scaling consumers out during a dependency incident amplifies load on
   it.
7. **A short visibility timeout causes duplicates.** With a 0.1 s lease and 50-150 ms processing,
   79 handler runs were duplicates, against 3 with a 5 s lease (those 3 come from the 1% of runs that
   are deliberately slower than 5 s). Redeliveries also count as receives, so 23 healthy messages hit
   the DLQ limit. Sixteen consumers, against four in Step 4, also burned more receives during the
   outage: 4 healthy messages in the DLQ even with the 5 s lease.
8. **Every message settles exactly once in the bookkeeping:** `processed + DLQ = 300` in every row,
   but `duplicates` shows that "processed exactly once" is not the same as "handler ran exactly once".

## Answers to the questions in the lab page

- **Why is the no-jitter retry peak equal to the backlog?** Because every failure during the outage
  happened within 0.75 s and was delayed by exactly the same amount, so the whole backlog returns
  together. Deterministic backoff preserves the synchronization the outage created.
- **Which configuration drains sooner?** Full jitter: 23.23 s against 37.52 s, with a lower p99.
- **Why did full jitter make more retries?** A uniform draw between 0 and the ceiling averages half
  the ceiling, so the expected wait before each retry is shorter and more retries land inside the
  outage.
- **How can a healthy message reach the DLQ under full jitter?** If its first four delays are all
  short draws, it can be received five times within the 2-second outage plus a transient failure or
  two afterwards, which exhausts the receive limit.
- **How many healthy messages with `--max-receives 1` during the outage?** All 299 that were not
  poison: every one failed its single permitted delivery.
- **How many more failing calls with four consumers?** 742 retries against 217. The outage lasts the
  same 2 s either way, but four consumers attempt four times as many messages in it.
