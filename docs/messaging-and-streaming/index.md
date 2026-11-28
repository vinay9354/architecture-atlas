---
title: Messaging, event-driven systems, and streaming
description: "Queues and event streams decouple producers from consumers in time and in failure. This section."
---

# Messaging, event-driven systems, and streaming

Queues and event streams decouple producers from consumers in time and in failure. This section
explains brokers and their delivery semantics, event-driven architecture (events versus commands,
choreography versus orchestration, event sourcing), and log-based streaming (partitions, offsets,
consumer lag, windows, watermarks). Technologies such as Kafka, Kinesis, SQS/SNS, EventBridge,
RabbitMQ, Pulsar, Pub/Sub, and Service Bus are compared conceptually, not as feature lists.

## What you will learn here

- Choose between queues, pub-sub, and streams for a workload
- Explain at-most-once, at-least-once, and why exactly-once has limits
- Design event schemas, versioning, dead-letter handling, and replay
- Reason about ordering, partitions, consumer groups, and lag
- Map a requirement to a broker technology without confusing similarly named services

**Prerequisites:** [Distributed systems](../distributed-systems/index.md), especially delivery guarantees and idempotency.

## Topics in this section

Every topic from the master curriculum that belongs to this section is listed below with its
status. A link means the page exists; `planned:` shows where it will be created. Status meanings
are explained in the [coverage matrix](../appendices/coverage-matrix.md).

<!-- coverage:start -->
| ID | Topic | Status | Page |
|---|---|---|---|
| **D08** | **Messaging, event-driven systems, and streaming** | | |
| D08-T01 | Message queues and brokers | :material-circle-slice-5: Draft | [message-queues-and-brokers](message-queues-and-brokers.md) |
| D08-T02 | Event-driven architecture | :material-circle-slice-5: Draft | [event-driven-architecture](event-driven-architecture.md) |
| D08-T03 | Event streaming and log-based architecture | :material-circle-slice-5: Draft | [event-streaming-and-log-based-architecture](event-streaming-and-log-based-architecture.md) |
| D08-T04 | Messaging technologies compared | :material-circle-slice-5: Draft | [messaging-technologies-compared](messaging-technologies-compared.md) |
<!-- coverage:end -->

## How to continue

- Follow the [learning paths](../start-here/learning-path.md) for a recommended order.
- Look up unfamiliar terms in the [glossary](../start-here/glossary.md).
- Want to write one of the planned pages? See the
  [contribution guide](https://github.com/vinay9354/architecture-atlas/blob/main/CONTRIBUTING.md).
