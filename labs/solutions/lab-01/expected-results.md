# Lab 01 — sample results

One run on a laptop (macOS, Python 3.14, server started with `--service-ms 20 --max-workers 8`,
load generator with `--duration 3`). Your absolute numbers will differ; the shape should not.

```text
   clients |   requests |     errors |      req/s |    mean ms |     p50 ms |     p95 ms |     p99 ms |     max ms | rps x mean
-----------+------------+------------+------------+------------+------------+------------+------------+------------+-----------
         1 |        139 |          0 |       39.5 |       25.3 |       25.9 |       26.5 |       27.7 |       27.7 |        1.0
         2 |        286 |          0 |       81.2 |       24.6 |       25.3 |       26.5 |       26.8 |       27.2 |        2.0
         4 |        572 |          0 |      162.7 |       24.6 |       25.0 |       26.6 |       27.1 |       27.9 |        4.0
         8 |       1147 |          0 |      325.5 |       24.5 |       25.0 |       26.5 |       27.4 |       37.4 |       7.96
        16 |       1160 |          1 |      328.1 |       48.5 |       48.9 |       70.8 |       75.4 |      100.2 |      15.92
        32 |       1187 |          0 |      329.8 |       95.5 |       96.7 |       154.1 |      174.0 |      245.1 |      31.51
```

## What to notice

1. **Below saturation (1-8 clients)** latency stays flat at about 25 ms (20 ms of simulated work plus
   roughly 5 ms of Python and HTTP overhead on this machine) and throughput grows linearly with the
   number of clients: each extra client adds about 40 requests per second.
2. **Capacity** is reached at 8 clients, equal to `--max-workers`. The ceiling is workers ÷ service
   time: 8 ÷ 0.025 s ≈ 320 requests per second, which matches the measured plateau of about 330.
3. **Above saturation (16, 32 clients)** throughput does not increase at all. Every extra client only
   adds queueing: mean latency doubles from 8 to 16 clients and doubles again at 32, because each
   request now waits behind others for a free worker.
4. **Tail latency** grows faster than the median once queueing starts: at 32 clients p99 is 174 ms
   against a p50 of 97 ms, while below saturation p99 and p50 were within 2 ms of each other.
5. **Little's Law holds** in every row: throughput × mean latency ≈ number of clients (the last
   column). A closed-loop load generator cannot violate it, which makes it a useful self-check that
   the measurements are consistent.
6. The single error at 16 clients was a connection reset during the warm-up window; occasional
   resets from the load generator reconnecting are expected and are reported, not hidden.

## Answers to the questions in the lab page

- **Why does latency stay flat until 8 clients?** Because every request immediately finds a free
  worker; there is no queue. Latency equals service time plus fixed overhead.
- **What sets the plateau?** The worker count divided by the service time. Doubling the workers
  (`--max-workers 16`) roughly doubles the plateau; halving the service time (`--service-ms 10`) does
  the same. Try both and compare.
- **What would an open-loop load generator show?** With arrivals at a fixed rate above capacity, the
  queue would grow without bound and latency would climb for as long as the test ran; the closed
  loop here caps the queue at the number of clients, which is why latency stabilizes at each level.
