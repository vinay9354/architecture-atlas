---
title: "ADR-0006: How examples are tested"
description: "Scripts, examples, and interactive demos get smoke tests with Python's unittest, run in CI; content validation is itself tested."
---

# ADR-0006: Examples and scripts are tested with unittest in CI

**Status:** Accepted  
**Date:** 2026-11-15  
**Deciders:** Repository maintainer, initial AI build agent  
**Related:** [ADR-0005](adr-0005-lab-execution-strategy.md), `tests/`, `.github/workflows/docs-build.yml`

## Context

A learning repository that ships broken examples teaches the wrong lesson. Code under `examples/`,
`labs/`, `scripts/`, and `docs/assets/interactive/` must keep working as dependencies and content
change. The test approach must be light enough that contributors actually run it.

## Decision drivers

- No additional test dependency for the common case.
- Tests run in the same CI job as the build so failures are visible on every pull request.
- Examples that need Docker, Kubernetes, or GPUs are tested differently from pure-Python ones.

## Options considered

### Option 1 — No automated tests, manual verification

Fast now, unreliable later. Rejected.

### Option 2 — pytest with plugins

Excellent tooling but one more dependency and configuration surface. Deferred until needed.

### Option 3 — Python standard-library `unittest`, discovered from `tests/` (chosen)

Zero extra dependencies. Sufficient for smoke tests of scripts, simulations, and the content
validator. Can migrate to pytest later without rewriting tests (pytest runs unittest cases).

## Decision

- `tests/content/` tests the repository's own tooling: the coverage file, validator, coverage
  generator, and asset check. These run in CI on every push.
- `tests/examples/` holds one test module per runnable example or lab simulation. Pure-Python
  examples are executed directly; examples that need containers are tested by a lightweight syntax or
  static check in CI and a documented manual run (recorded in the lab page's "Validated on" note).
- Interactive demos (vanilla JS) get a smoke test that loads the HTML and checks for a static
  fallback block; behavioural tests may be added with a headless browser later.
- Code examples embedded in Markdown pages are illustrative and are not executed; anything that
  must run lives in `examples/` or `labs/` and is linked from the page.
- Formatting and syntax checks for example languages (Python, YAML, HCL, Dockerfile) are added per
  language as examples appear; Python is checked first with `python -m py_compile` inside the tests.

## Consequences

**Positive**

- One command (`python -m unittest discover -s tests`) runs everything locally and in CI.
- Content validation is tested like code, so the validator cannot silently stop working.

**Negative**

- Container- and cloud-dependent labs are only partly covered by automation; their pages must state
  when and on what versions they were last run by a human.

## Follow-up actions

- [ ] Add `py_compile` coverage for `labs/` as the first labs land.
- [ ] Add a Terraform `fmt`/`validate` check when the first HCL example is added.
