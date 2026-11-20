# Lab 05 — sample results

Runs on a laptop (macOS, Python 3.14 with the GIL, SQLite 3.53.4). Steps 1, 2, 4, and 5 use real
threads, so your numbers will differ from run to run; what should not differ is that the racy modes
lose updates and the fixed modes never do. Step 3 uses the seeded `sim` engine and is deterministic.

## Step 1 — Lost updates with threads

```text
$ python3 counter_race.py
engine=threads threads=4 increments/thread=2000

    engine |       mode |    threads |   expected |      final |       lost
-----------+------------+------------+------------+------------+-----------
   threads |       racy |          4 |       8000 |       2014 |       5986
   threads |     locked |          4 |       8000 |       8000 |          0
```

Two earlier runs of the same command lost 5,937 and 5,986 updates in the racy mode.

## Step 2 — Without the forced yield

```text
$ python3 counter_race.py --mode racy --no-yield --increments 200000
engine=threads threads=4 increments/thread=200000 yield=off

    engine |       mode |    threads |   expected |      final |       lost
-----------+------------+------------+------------+------------+-----------
   threads |       racy |          4 |     800000 |     800000 |          0
```

## Step 3 — Deterministic replay

```text
$ python3 counter_race.py --engine sim
engine=sim threads=4 increments/thread=2000 seed=3

    engine |       mode |    threads |   expected |      final |       lost
-----------+------------+------------+------------+------------+-----------
       sim |       racy |          4 |       8000 |       3011 |       4989
       sim |     locked |          4 |       8000 |       8000 |          0

First lost update (racy), last steps before it:
  T1 writes 1
  T2 reads 1
  T3 reads 1
  T0 reads 1
  T0 writes 2
  T3 writes 2  <- 1 update(s) lost

$ python3 counter_race.py --engine sim --threads 2 --mode racy --seed 1
engine=sim threads=2 increments/thread=2000 seed=1

    engine |       mode |    threads |   expected |      final |       lost
-----------+------------+------------+------------+------------+-----------
       sim |       racy |          2 |       4000 |       2524 |       1476

First lost update (racy), last steps before it:
  T0 reads 1
  T1 writes 2
  T1 reads 2
  T1 writes 3
  T1 reads 3
  T0 writes 2  <- 2 update(s) lost
```

## Steps 4 and 5 — Lost updates in a database row

```text
$ python3 shipment_race.py
workers=2 scans/worker=300 sqlite=3.53.4 seed=5

      mode |    workers |   expected | scan_count |       lost |    retries | elapsed ms
-----------+------------+------------+------------+------------+------------+-----------
      racy |          2 |        600 |        300 |        300 |          0 |       56.5
optimistic |          2 |        600 |        600 |          0 |          1 |       53.4
    atomic |          2 |        600 |        600 |          0 |          0 |       55.0

$ python3 shipment_race.py --workers 4
workers=4 scans/worker=300 sqlite=3.53.4 seed=5

      mode |    workers |   expected | scan_count |       lost |    retries | elapsed ms
-----------+------------+------------+------------+------------+------------+-----------
      racy |          4 |       1200 |        300 |        900 |          0 |      131.9
optimistic |          4 |       1200 |       1200 |          0 |          5 |      104.6
    atomic |          4 |       1200 |       1200 |          0 |          0 |      128.5
```

Six repeated two-worker runs with `--scans 100` lost 100, 100, 86, 100, 100, and 100 of 200 updates
in the racy mode. Six repeated four-worker optimistic runs needed between 4 and 6 retries; every one
ended with exactly 1,200.

## What to notice

1. **The racy counter loses most of its updates** when the yield sits inside the read-modify-write:
   5,986 of 8,000 in the run above, and a different number each run. A race does not produce a
   consistent wrong answer, which is part of why it survives testing.
2. **The lock makes the result exact** (8,000 every time) because the read, the yield, and the write
   form one critical section. Another thread can be scheduled during the yield, but it waits at the
   lock instead of reading a value that is about to become stale.
3. **Removing the yield hid the race on this machine.** 800,000 racy increments, zero lost. The code is
   exactly as wrong as before: nothing prevents a thread switch between the read and the write, it is
   just unlikely under CPython's GIL with this tiny window. A test that runs racy code once and checks
   the total proves very little.
4. **The deterministic trace shows the anatomy of a lost update.** In the seed 3 trace, T3 read 1, T0
   read 1, T0 wrote 2, and T3 then wrote 2 as well, erasing T0's increment. In the seed 1 trace, T0
   read 1 and was not scheduled again until T1 had completed two increments (to 3); T0's write of 2
   erased both. The `sim` engine loses fewer updates than the real threads (4,989 of 8,000) because
   its random scheduler does not fall into the lockstep pattern described next.
5. **The database race is the same bug.** Two autocommit statements (`SELECT`, then `UPDATE` with a
   value computed in Python) leave a gap. With two workers the racy mode lost 300 of 600 scans, exactly
   half; with four it lost 900 of 1,200, exactly three quarters. That precision means the workers ran
   in lockstep: every worker read the same count, then every worker wrote count + 1, so each round of
   *n* scans raised the count by one.
6. **Optimistic concurrency is exact and cheap at low contention.** The version check turned every
   overlap into a detected conflict (1 retry with two workers, 4 to 6 with four) and every scan was
   applied. Few retries were needed because the first conflict shifts the workers out of lockstep and
   they rarely overlap again. Under heavier, more random contention, retries grow and a bounded retry
   budget becomes necessary (stretch challenge 2).
7. **The atomic update needs no retries at all**, because `scan_count = scan_count + 1` is computed by
   the database inside one statement. Prefer it whenever the new value can be expressed in SQL; use the
   version check when the new value needs application logic (for example, validating a status
   transition) between the read and the write.
8. **Elapsed time is noise at this size.** All three modes finished in 50-130 ms; the differences
   between runs are larger than the differences between modes.

## Answers to the questions in the lab page

- **How many updates were lost, and is the number stable?** Thousands (5,937 and 5,986 in two runs
  of 8,000), and no, it changes from run to run.
- **What does the locked mode do differently, and what does it cost?** It holds a mutex across the
  read, yield, and write, so only one thread is ever inside the critical section. The cost is that
  increments are serialized; threads wait for each other instead of running in parallel.
- **Did you lose updates without the yield? Is the code correct?** No updates were lost in 800,000
  increments on the test machine, and no, the code is not correct; the race is still there.
- **Which write was overwritten in the trace?** Seed 3: T0's write of 2 was overwritten by T3's write
  of 2. Seed 1: T1's writes of 2 and 3 were overwritten by T0's write of 2.
- **What is the racy `scan_count` with four workers?** Predicted 300 (one increment per round of four
  scans, 300 rounds) if the workers stay in lockstep, which is what the run showed.
- **How do optimistic retries change from two to four workers?** They rise (1 to about 5 here),
  because more workers means more chances that a row changed between a worker's read and its write.
