# Example tests

Tests for runnable examples under `examples/` and `labs/` live here, one module per example, discovered
by `python -m unittest discover -s tests`. See [ADR-0006](../../docs/appendices/adr/adr-0006-example-testing.md)
for the testing strategy.

| Module | Covers |
|---|---|
| `test_lab01.py` | Lab 01 server and load generator: compile check, percentile function, end-to-end run on an ephemeral port |
