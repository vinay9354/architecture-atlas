# Lab 02 — sample results

Runs on a laptop (macOS, Python 3.14.7, shown as `python3`) with the default seed (2). Every block
below is copied from a real run, trimmed only of trailing blank lines. The lab uses a simulated clock
and counts simulated milliseconds instead of sleeping, so every number here is reproducible: the same
seed gives the same output on any machine. The lab steps under the macOS system Python 3.9.6 produced
byte-identical output. The whole `python3 lab02_run.py all` took about 8.5 seconds of real time on
the author's machine. A second seed (3) is shown at the end to separate the lesson from the luck.

## Step 1 — The cache's rules: LRU eviction and lazy TTL expiry

```text
$ python3 lab02_cache.py
after inserting SHP-3 into a full 2-slot cache: ['SHP-1', 'SHP-3'] evictions 1
SHP-1 at t=29.9 s: True
SHP-1 at t=30.0 s: False expirations 1
```

`SHP-1` was read at t = 1 s, so when `SHP-3` arrived in a full two-slot cache, `SHP-2` (the least
recently used) was evicted, not `SHP-1` (which was inserted first; FIFO would have evicted it). The
entry written at t = 0 with a 30 s TTL is served at 29.9 s and treated as gone at exactly 30.0 s. The
expired entry was removed only because someone read it: until then it held a slot, which matters in
Step 3.

## Step 2 — The workload's skew

```text
$ python3 lab02_workload.py
top     10 of 50,000 shipments receive  25.7% of reads
top    100 of 50,000 shipments receive  45.5% of reads
top  1,000 of 50,000 shipments receive  65.7% of reads
top  5,000 of 50,000 shipments receive  79.8% of reads
top 20,000 of 50,000 shipments receive  92.0% of reads
60 s at 210 reads/s and 70 scans/s: 12,511 reads, 4,261 scans
```

With a Zipf exponent of 1.0, the top 100 of 50,000 shipments (0.2% of keys) receive 45.5% of reads,
and the top 5,000 (10%) receive 79.8%. One simulated minute has about 210 × 60 = 12,600 reads and
70 × 60 = 4,200 scans; the Poisson arrivals gave 12,511 and 4,261.

## Step 3 — Hit ratio versus cache size

```text
$ python3 lab02_run.py size
Experiment 1: hit ratio vs cache size (Zipf s=1.0 over 50,000 shipments, 210 reads/s, 70 scans/s, TTL 30 s, delete-on-write)
  slots    memory hit ratio backend calls  backend ms  avg ms evictions  stale
    100    0.4 MB     31.2%        86,914   1,738,280   14.77    86,321      0
    500    2.0 MB     47.2%        66,618   1,332,360   11.55    65,189      0
  1,000    4.0 MB     53.6%        58,612   1,172,240   10.28    55,401      1
  2,000    8.0 MB     58.6%        52,264   1,045,280    9.28    44,560      1
  5,000   20.0 MB     60.0%        50,500   1,010,000    9.00    27,746      3
 10,000   40.0 MB     60.0%        50,500   1,010,000    9.00    11,882      3
 50,000  200.0 MB     60.0%        50,500   1,010,000    9.00         0      3
reads: 126,259   scans: 41,832
```

Answers:

1. The hit ratio climbs from 31.2% (100 slots) to 58.6% (2,000) and stops at 60.0% from 5,000 slots
   upward. More memory beyond 5,000 entries (20 MB at 4 KB each) buys nothing.
2. The ceiling is set by the TTL and the invalidations, not by memory. Every shipment's first read in
   each 30-second window is a miss, and every scan deletes the entry. Within 30 seconds the workload
   touches only a few thousand distinct shipments, so about 5,000 slots hold all of them; the extra
   slots hold only expired entries.
3. Evictions at 5,000 and 10,000 slots are expired entries being pushed out by LRU. Expiry is lazy:
   an expired entry keeps its slot until it is read or evicted. Only at 50,000 slots (every shipment)
   do evictions reach zero.
4. The top 5,000 shipments get 79.8% of reads (Step 2), but the hit ratio is 60.0%, because the
   popularity curve only says which keys are read, not whether they are read twice within one TTL.
5. The "stale" column (0 to 3 reads) is the delete-on-write race: a load read the old version before a
   scan committed, finished after the scan deleted the entry, and stored the old value. Step 4
   returns to it.

## Step 4 — TTL, hit ratio, and stale reads

```text
$ python3 lab02_run.py ttl
Experiment 2: TTL vs hit ratio and staleness (cache holds all 50,000 shipments)
invalidation    TTL s hit ratio backend calls stale reads stale % mean stale s max stale s
TTL only            1     30.4%        87,921          32   0.03%          0.3         0.6
TTL only            5     44.6%        69,903         172   0.14%          1.5         4.6
TTL only           30     60.2%        50,250       1,468   1.16%          9.8        29.7
TTL only          120     71.6%        35,887       6,969   5.52%         40.4       118.3
TTL only          600     82.2%        22,435      33,408  26.46%        194.9       594.1
delete-on-write      1     30.4%        87,933           0   0.00%          0.0         0.0
delete-on-write      5     44.6%        69,940           0   0.00%          0.0         0.0
delete-on-write     30     60.0%        50,500           3   0.00%         21.7        29.7
delete-on-write    120     70.9%        36,752          13   0.01%         56.4       106.4
delete-on-write    600     79.2%        26,248           0   0.00%          0.0         0.0
```

Answers:

1. TTL only: as the TTL grows from 1 s to 600 s, the hit ratio rises from 30.4% to 82.2%, and stale
   reads rise from 32 (0.03%) to 33,408 (26.46%). The maximum staleness is just under the TTL each
   time (0.6, 4.6, 29.7, 118.3, 594.1 s): the TTL is the bound on staleness when nothing invalidates.
2. Against NFR-1 (status visible within 60 s): TTL only at 120 s or 600 s breaks it outright (a
   reader saw a status 118 s old). TTL only at 30 s keeps the cache's share of the delay under 30 s
   and leaves the other 30 s for the queue and the Event Processor, which is exactly the budget split
   on the caching page.
3. Delete-on-write removes almost all staleness at every TTL (0 to 13 stale reads out of 126,259)
   and costs a little hit ratio at long TTLs (79.2% against 82.2% at 600 s), because every scan
   throws away a copy that would otherwise have been served (stale).
4. The few stale reads that remain with delete-on-write are the race between a slow load and a
   write. The counts (3, 13, 0) are small and do not grow steadily with the TTL, because they depend
   on whether a scan happens to land inside one of the 20 ms loads, not on how long entries live.
   With a 600 s TTL none happened to; with a 120 s TTL thirteen reads saw a value stored by a racing
   load, one of them 106.4 s after the newer version committed. The TTL is still what bounds such a
   race's damage, which is why the AtlasMart design keeps both.

## Step 5 — A stampede on one hot key, and single-flight

```text
$ python3 lab02_run.py stampede
Experiment 3: one viral shipment, 150 reads/s for 300 s, TTL 30 s, 200 ms database read
single-flight   reads   hits coalesced backend calls peak in flight  avg ms  max ms
off            45,010 44,716         0           294             36    2.31   201.0
on             45,010 44,708       292            10              1    1.68   201.0
loads per expiry without single-flight: 294 / 10 = 29.4
```

Answers:

1. Without single-flight, each of the 10 cold loads (the first read plus 9 expiries) brought on
   about 29 database queries for the same row: 150 reads/s × 0.2 s = 30 reads arrive while the first
   load is still running, and each of them misses. Peak concurrent queries: 36. With single-flight:
   exactly 10 queries, never more than 1 in flight, and 292 readers waited for a load already
   running.
2. Average latency is lower with single-flight (1.68 ms against 2.31 ms) even though no read got
   faster than a hit: a coalesced reader waits only for the rest of a load already in progress,
   while without coalescing each of the ~29 extra readers paid a full 201 ms. The worst read is
   201 ms in both cases: someone still waits for the first load.
3. The simulation charges every query a fixed 200 ms. A real database receiving 36 identical
   queries at once would slow down for everyone, so the real damage of a stampede is larger than
   these numbers. Serving the stale value while one reader refreshes would remove even the 201 ms
   wait (Stretch challenge 2).

## Step 6 — Many keys expiring together, and jittered TTL

```text
$ python3 lab02_run.py jitter
Experiment 4: 2,000 customers sent to their pages in one second, refreshing every ~5 s, TTL 30 s
TTL jitter  backend calls hit ratio  peak calls in 1 s (after 5 s)
none               18,164     85.1%          317 at second 31
+/-20%             18,220     85.0%          162 at second 34
calls per second 28..40, jitter none      0   0 154 317 260 239 192 148 140  83  94  67  60
calls per second 28..40, jitter +/-20%   96  87  98 119 134 159 162 148 155 104 110  71  72
```

Answers:

1. All 2,000 entries were loaded inside the first second, so with a fixed 30 s TTL they expire
   inside one second too; the reloads arrive as soon as each customer's page refreshes (every 5 s on
   average). The peak is 317 database reads in second 31, against 0 in seconds 28 and 29.
2. With a TTL drawn from 24 to 36 s (±20%), the same reloads are spread over twelve seconds: the peak
   falls to 162 (about half), and seconds 28 and 29 already carry 96 and 87.
3. Total backend calls barely change (18,164 against 18,220) and neither does the hit ratio (85.1%
   against 85.0%). Jitter does not save work; it moves it so that the database sees a slope instead
   of a cliff. Single-flight would not help here at all: these are 2,000 different keys with one
   miss each.

## Step 7 — From hit ratio to backend load and latency

```text
$ python3 lab02_run.py arithmetic
Experiment 5: from hit ratio to backend load and latency (hit 1 ms, miss 1 + 20 ms)
  slots hit ratio model avg ms simulated avg ms model calls simulated calls
    100     31.2%        14.77            14.77      86,914          86,914
    500     47.2%        11.55            11.55      66,618          66,618
  1,000     53.6%        10.28            10.28      58,612          58,612
  2,000     58.6%         9.28             9.28      52,264          52,264
  5,000     60.0%         9.00             9.00      50,500          50,500
 10,000     60.0%         9.00             9.00      50,500          50,500
 50,000     60.0%         9.00             9.00      50,500          50,500
AtlasMart sale-day peak, 210 tracking reads/s:
hit ratio database reads/s avg latency ms
       0%            210.0          21.00
      50%            105.0          11.00
      80%             42.0           5.00
      90%             21.0           3.00
      95%             10.5           2.00
      99%              2.1           1.20
```

Answers:

1. The model is: backend reads = reads × (1 − hit ratio); average latency = 1 ms + (1 − hit ratio) ×
   20 ms. It matches the simulation to the hundredth of a millisecond because the simulation charges
   exactly those costs (no coalescing in this experiment). The point is that a measured hit ratio is
   enough to predict database load and mean latency; you do not need a load test for that part.
2. At AtlasMart's sale-day design peak of 210 reads/s, a 90% hit ratio leaves 21 database reads per
   second and an average of 3 ms; 99% leaves 2.1 reads per second. Going from 90% to 99% cuts
   database load by a factor of 10, which is why hit ratio is discussed in "nines".
3. Caution from the caching page: AtlasMart's real tracking reads are about four per shipment per
   day, hours apart, so the real per-shipment hit ratio with a 30 s TTL is low. The Zipf workload in
   this lab models the skewed bursts (campaigns, sale days, a viral parcel) that the Status Cache
   exists to absorb; the database is sized to serve the average read rate without the cache.

## A second seed

```text
$ python3 lab02_run.py size --seed 3
Experiment 1: hit ratio vs cache size (Zipf s=1.0 over 50,000 shipments, 210 reads/s, 70 scans/s, TTL 30 s, delete-on-write)
  slots    memory hit ratio backend calls  backend ms  avg ms evictions  stale
    100    0.4 MB     31.1%        86,960   1,739,200   14.79    86,361      0
    500    2.0 MB     47.0%        66,881   1,337,620   11.60    65,447      0
  1,000    4.0 MB     53.4%        58,827   1,176,540   10.33    55,636      0
  2,000    8.0 MB     58.4%        52,523   1,050,460    9.33    44,917      1
  5,000   20.0 MB     59.8%        50,684   1,013,680    9.04    27,975      1
 10,000   40.0 MB     59.8%        50,684   1,013,680    9.04    12,037      1
 50,000  200.0 MB     59.8%        50,684   1,013,680    9.04         0      1
reads: 126,136   scans: 42,212
```

```text
$ python3 lab02_run.py stampede --seed 3
Experiment 3: one viral shipment, 150 reads/s for 300 s, TTL 30 s, 200 ms database read
single-flight   reads   hits coalesced backend calls peak in flight  avg ms  max ms
off            44,884 44,571         0           313             37    2.39   201.0
on             44,884 44,543       331            10              1    1.80   201.0
loads per expiry without single-flight: 313 / 10 = 31.3
```

Different random events, same shape: the hit ratio plateaus near 60% from 5,000 slots, and
single-flight turns about 31 loads per expiry into 1.

## Smoke test

```text
$ python3 -m unittest tests.examples.test_lab02 -v
test_cli_prints_tables_and_json (tests.examples.test_lab02.Lab02Tests.test_cli_prints_tables_and_json) ... ok
test_hit_ratio_matches_the_arithmetic (tests.examples.test_lab02.Lab02Tests.test_hit_ratio_matches_the_arithmetic) ... ok
test_hit_ratio_rises_with_cache_size (tests.examples.test_lab02.Lab02Tests.test_hit_ratio_rises_with_cache_size) ... ok
test_jitter_flattens_the_expiry_wave (tests.examples.test_lab02.Lab02Tests.test_jitter_flattens_the_expiry_wave) ... ok
test_longer_ttl_more_hits_and_more_stale_reads (tests.examples.test_lab02.Lab02Tests.test_longer_ttl_more_hits_and_more_stale_reads) ... ok
test_lru_eviction_and_lazy_ttl_expiry (tests.examples.test_lab02.Lab02Tests.test_lru_eviction_and_lazy_ttl_expiry) ... ok
test_single_flight_stops_the_stampede (tests.examples.test_lab02.Lab02Tests.test_single_flight_stops_the_stampede) ... ok
test_sources_compile (tests.examples.test_lab02.Lab02Tests.test_sources_compile) ... ok
test_workload_is_seeded_and_skewed (tests.examples.test_lab02.Lab02Tests.test_workload_is_seeded_and_skewed) ... ok

----------------------------------------------------------------------
Ran 9 tests in 1.125s

OK
```
