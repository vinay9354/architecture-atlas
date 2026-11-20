---
title: Software architecture styles and design patterns
description: "Architecture styles (monolith, modular monolith, microservices, event-driven, serverless, hexagonal,."
---

# Software architecture styles and design patterns

Architecture styles (monolith, modular monolith, microservices, event-driven, serverless, hexagonal,
and others) are reusable shapes for a whole system. Design patterns are reusable shapes for a part of
it. This section teaches both, with the emphasis on *when each one is the wrong choice*.

The microservices material deserves special care: it is the most over-applied style of the last decade.
You will learn decomposition by domain boundaries, the costs of distribution, and how to recognize the
distributed monolith anti-pattern before it costs you a year.

## What you will learn here

- Compare architecture styles on coupling, deployability, scalability, and operational cost
- Decompose a system into bounded contexts and justify service boundaries
- Apply application patterns (Repository, Strategy, Observer, and more) where they reduce complexity
- Apply distributed patterns (CQRS, Saga, Outbox, Circuit Breaker, Strangler Fig) with their failure modes
- Recognize anti-patterns such as the distributed monolith and the shared database

**Prerequisites:** [Architecture fundamentals](../architecture-fundamentals/index.md) and the concurrency pages in [Foundations](../foundations/index.md).

## Topics in this section

Every topic from the master curriculum that belongs to this section is listed below with its
status. A link means the page exists; `planned:` shows where it will be created. Status meanings
are explained in the [coverage matrix](../appendices/coverage-matrix.md).

<!-- coverage:start -->
| ID | Topic | Status | Page |
|---|---|---|---|
| **D03** | **Software architecture styles and design patterns** | | |
| D03-T01 | Architecture styles | :material-circle-slice-5: Draft | [architecture-styles](architecture-styles.md) |
| D03-T02 | Microservices architecture | :material-circle-slice-5: Draft | [microservices-architecture](microservices-architecture.md) |
| D03-T03 | Application design patterns | :material-circle-slice-5: Draft | [application-design-patterns](application-design-patterns.md) |
| D03-T04 | Distributed system patterns | :material-circle-slice-5: Draft | [distributed-system-patterns](distributed-system-patterns.md) |
<!-- coverage:end -->

## How to continue

- Follow the [learning paths](../start-here/learning-path.md) for a recommended order.
- Look up unfamiliar terms in the [glossary](../start-here/glossary.md).
- Want to write one of the planned pages? See the
  [contribution guide](https://github.com/vinay9354/architecture-atlas/blob/main/CONTRIBUTING.md).
