# Example tests

Tests for runnable examples under `examples/` and `labs/` live here, one module per example, discovered
by `python -m unittest discover -s tests`. See [ADR-0006](../../docs/appendices/adr/adr-0006-example-testing.md)
for the testing strategy.

| Module | Covers |
|---|---|
| `test_lab01.py` | Lab 01 server and load generator: compile check, percentile function, end-to-end run on an ephemeral port |
| `test_lab03.py` | Lab 03 queue simulation: retries with backoff and jitter, poison message to the dead-letter queue |
| `test_lab04.py` | Lab 04 idempotency: double charges without a key, none with a key, inbox deduplication |
| `test_lab05.py` | Lab 05 race condition: lost updates in the racy mode, exact results with a lock and with optimistic concurrency |
| `test_lab08.py` | Lab 08 hashing: keys moved by mod-N versus the ring and rendezvous hashing, spread versus virtual nodes |
| `test_lab09.py` | Lab 09 replication lag: read-your-writes and monotonic-read guarantees per routing policy |
