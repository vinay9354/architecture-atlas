# Example tests

Tests for runnable examples under `examples/` and `labs/` live here, one module per example, discovered
by `python -m unittest discover -s tests`. See [ADR-0006](../../docs/appendices/adr/adr-0006-example-testing.md)
for the testing strategy.

| Module | Covers |
|---|---|
| `test_lab01.py` | Lab 01 server and load generator: compile check, percentile function, end-to-end run on an ephemeral port |
| `test_lab02.py` | Lab 02 cache: hit ratio rises with cache size, stale reads rise with TTL, single-flight cuts stampede loads, jittered TTL flattens expiry peaks |
| `test_lab03.py` | Lab 03 queue simulation: retries with backoff and jitter, poison message to the dead-letter queue |
| `test_lab04.py` | Lab 04 idempotency: double charges without a key, none with a key, inbox deduplication |
| `test_lab05.py` | Lab 05 race condition: lost updates in the racy mode, exact results with a lock and with optimistic concurrency |
| `test_lab06.py` | Lab 06 indexing: SQLite plans switch from SCAN to SEARCH or COVERING INDEX, composite column order, ignored indexes, write cost of extra indexes |
| `test_lab07.py` | Lab 07 SQL vs NoSQL: same answers from both stores, partitions touched per access pattern, hot-partition ratio before and after write sharding |
| `test_lab08.py` | Lab 08 hashing: keys moved by mod-N versus the ring and rendezvous hashing, spread versus virtual nodes |
| `test_lab09.py` | Lab 09 replication lag: read-your-writes and monotonic-read guarantees per routing policy |
| `test_lab10.py` | Lab 10 REST API: every authentication failure returns 401, owner-only reads, scope checks, request validation with problem details |
| `test_lab11.py` | Lab 11 tracing: W3C traceparent rules, one trace id across both services' structured logs, parent/child spans, broken propagation |
| `test_lab12.py` | Lab 12 local Kubernetes: manifest invariants (spread, probes, limits, security context, PDB, NetworkPolicy) and the stub service's endpoints |
| `test_lab13.py` | Lab 13 GitOps: a reconciler on a temporary Git repo converges, detects and heals drift, rolls back by revert, prunes only when enabled |
| `test_lab14.py` | Lab 14 network segmentation: flat versus segmented flows, the stateless ACL return-traffic trap, CIDR versus group references |
| `test_lab15.py` | Lab 15 infrastructure module: static file checks always; `fmt`, `validate`, and `test` when Terraform or OpenTofu is installed |
| `test_lab16.py` | Lab 16 event-driven workflow: outbox survives relay crashes, idempotent consumers absorb duplicates, compensation on payment failure, dual write loses events |
