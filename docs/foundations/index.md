---
title: Computer science and software engineering foundations
description: "Architecture decisions rest on how computers actually work: how a CPU schedules threads, why a."
---

# Computer science and software engineering foundations

Architecture decisions rest on how computers actually work: how a CPU schedules threads, why a
disk's IOPS limit shows up as application latency, what a hash map costs, and how concurrency bugs
appear under load. This section fills those gaps for readers who came to architecture from operations
or cloud work rather than from a computer science degree.

Nothing here is academic for its own sake. Each page connects a foundation concept to an architecture
consequence: Big O to capacity planning, virtual memory to container limits, race conditions to
distributed locking, testing types to deployment confidence.

## What you will learn here

- Reason about CPU, memory, storage, and I/O limits when sizing systems
- Choose data structures and recognize their complexity trade-offs in real services
- Explain concurrency hazards (races, deadlocks, starvation) and the primitives that prevent them
- Apply SOLID, cohesion, and coupling to service boundaries, not just classes
- Pick the right kind of test for the risk being reduced

**Prerequisites:** [Architecture fundamentals](../architecture-fundamentals/index.md) helps but is not required.

## Topics in this section

Every topic from the master curriculum that belongs to this section is listed below with its
status. A link means the page exists; `planned:` shows where it will be created. Status meanings
are explained in the [coverage matrix](../appendices/coverage-matrix.md).

<!-- coverage:start -->
| ID | Topic | Status | Page |
|---|---|---|---|
| **D02** | **Computer science and software engineering foundations** | | |
| D02-T01 | Computers, operating systems, and Linux for architects | :material-circle-outline: Planned | planned: `foundations/computers-operating-systems-and-linux-for-architects.md` |
| D02-T02 | Programming fundamentals, data structures, and algorithms | :material-circle-outline: Planned | planned: `foundations/programming-fundamentals-data-structures-and-algorithms.md` |
| D02-T03 | Programming paradigms and concurrency | :material-circle-outline: Planned | planned: `foundations/programming-paradigms-and-concurrency.md` |
| D02-T04 | Software design principles and clean code | :material-circle-outline: Planned | planned: `foundations/software-design-principles-and-clean-code.md` |
| D02-T05 | Software testing types and strategies | :material-circle-outline: Planned | planned: `foundations/software-testing-types-and-strategies.md` |
<!-- coverage:end -->

## How to continue

- Follow the [learning paths](../start-here/learning-path.md) for a recommended order.
- Look up unfamiliar terms in the [glossary](../start-here/glossary.md).
- Want to write one of the planned pages? See the
  [contribution guide](https://github.com/vinay9354/architecture-atlas/blob/main/CONTRIBUTING.md).
