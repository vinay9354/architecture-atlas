---
title: Distributed systems
description: "Any system that spans more than one machine is a distributed system, and distributed systems fail in."
---

# Distributed systems

Any system that spans more than one machine is a distributed system, and distributed systems fail in
ways single machines never do: partial failure, network partitions, clocks that disagree, messages
delivered twice or not at all. This section teaches the theory that explains those failures and the
mechanisms that contain them.

The sequence matters. Consistency models and the CAP/PACELC trade-offs come first because every later
pattern (sagas, retries, leader election, replication) is a response to them.

## What you will learn here

- Explain partial failure, partitions, and why distributed time is hard
- Place a system on the consistency spectrum and justify the choice
- Design transactions across services with sagas, outboxes, and idempotent consumers
- Use timeouts, retries, backoff, circuit breakers, and backpressure without creating retry storms
- Scale with sharding, replication, and consistent hashing while managing hot keys

**Prerequisites:** [Networking fundamentals](../networking/index.md) and [Software architecture](../software-architecture/index.md).

## Topics in this section

Every topic from the master curriculum that belongs to this section is listed below with its
status. A link means the page exists; `planned:` shows where it will be created. Status meanings
are explained in the [coverage matrix](../appendices/coverage-matrix.md).

<!-- coverage:start -->
| ID | Topic | Status | Page |
|---|---|---|---|
| **D04** | **Distributed systems** | | |
| D04-T01 | Distributed systems fundamentals, time, and coordination | :material-circle-slice-5: Draft | [distributed-systems-fundamentals-time-and-coordination](distributed-systems-fundamentals-time-and-coordination.md) |
| D04-T02 | Consistency models, CAP, and PACELC | :material-circle-outline: Planned | planned: `distributed-systems/consistency-models-cap-and-pacelc.md` |
| D04-T03 | Transactions, sagas, and delivery guarantees | :material-circle-outline: Planned | planned: `distributed-systems/transactions-sagas-and-delivery-guarantees.md` |
| D04-T04 | Resilience mechanics: timeouts, retries, and backpressure | :material-circle-outline: Planned | planned: `distributed-systems/resilience-mechanics-timeouts-retries-and-backpressure.md` |
| D04-T05 | Scaling, partitioning, and replication | :material-circle-outline: Planned | planned: `distributed-systems/scaling-partitioning-and-replication.md` |
<!-- coverage:end -->

## How to continue

- Follow the [learning paths](../start-here/learning-path.md) for a recommended order.
- Look up unfamiliar terms in the [glossary](../start-here/glossary.md).
- Want to write one of the planned pages? See the
  [contribution guide](https://github.com/vinay9354/architecture-atlas/blob/main/CONTRIBUTING.md).
