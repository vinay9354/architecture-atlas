---
title: Hands-on labs
description: "Local, free experiments that turn architecture theory into measurements and working code."
---

# Hands-on labs

Labs are small experiments you can finish in under an hour on your own machine. They favor free,
local, containerized, or simulated tools. Any lab that needs a cloud account, GPU, paid service, or
API key says so before you start and includes cleanup steps and cost safeguards.

Labs never ask you to expose credentials, grant broad cloud permissions, run destructive commands, or
upload private data. How labs are run and tested is recorded in
[ADR-0005](../appendices/adr/adr-0005-lab-execution-strategy.md) and
[ADR-0006](../appendices/adr/adr-0006-example-testing.md).

Each lab page uses the [lab template](https://github.com/vinay9354/architecture-atlas/blob/main/templates/lab-template.md);
code lives under `labs/` in the repository and solutions under `labs/solutions/`.

## Lab roadmap

| # | Lab | Requirements | Status |
|---|---|---|---|
| 01 | [Measure latency and throughput for a simple HTTP service](lab-01-latency-and-throughput.md) | Local, free | Draft |
| 02 | Add a cache and compare hit/miss behavior | Local, free | Planned |
| 03 | [Simulate a queue with multiple consumers, retries, and a dead-letter queue](lab-03-queue-retries-and-dead-letter.md) | Local, free | Draft |
| 04 | [Demonstrate idempotency and duplicate message handling](lab-04-idempotency-and-duplicates.md) | Local, free | Draft |
| 05 | [Reproduce a race condition and fix it with synchronization](lab-05-race-condition.md) | Local, free | Draft |
| 06 | Demonstrate database indexing and query plans | Local, free | Planned |
| 07 | Compare SQL and NoSQL access patterns with a concrete workload | Local, free | Planned |
| 08 | [Simulate sharding and consistent hashing](lab-08-sharding-and-consistent-hashing.md) | Local, free | Draft |
| 09 | [Demonstrate eventual consistency and replication lag](lab-09-replication-lag.md) | Local, free | Draft |
| 10 | [Build a small REST API with authentication and request validation](lab-10-rest-api-auth-and-validation.md) | Local, free | Draft |
| 11 | Add distributed tracing and structured logging to two services | Local, free | Planned |
| 12 | [Deploy a small application to local Kubernetes](lab-12-local-kubernetes-deployment.md) | Local, free (Docker and kind) | Draft |
| 13 | Implement a GitOps deployment locally | Local, free | Planned |
| 14 | [Demonstrate network segmentation with containers or a local lab](lab-14-network-segmentation.md) | Local, free | Draft |
| 15 | [Create an infrastructure module and run static checks](lab-15-infrastructure-module-and-static-checks.md) | Local, free (Terraform or OpenTofu) | Draft |
| 16 | Build a simple event-driven workflow | Local, free | Planned |
| 17 | Implement a basic RAG pipeline using local documents and a local or optional embedding/model endpoint | Local, free | Planned |
| 18 | Compare keyword, vector, and hybrid retrieval on a small dataset | Local, free | Planned |
| 19 | Visualize chunking and embedding similarity | Local, free | Planned |
| 20 | Add source citations and access filters to a RAG demo | Local, free | Planned |
| 21 | Create a tool-calling agent with read-only, simulated tools | Local, free | Planned |
| 22 | Add human approval before an agent performs a simulated write action | Local, free | Planned |
| 23 | Record agent traces, token use, latency, and estimated cost | Local, free | Planned |
| 24 | Test prompt injection and demonstrate layered defenses in a safe toy application | Local, free | Planned |
| 25 | Compare model outputs using a small, versioned evaluation dataset | Local, free | Planned |

## Mini-exercises already available

The first topic pages each include a small practical exercise you can do now:

- [Functional vs non-functional requirements](../architecture-fundamentals/functional-vs-non-functional-requirements.md#hands-on-lab-rewrite-vague-requirements) — rewrite vague requirements into testable ones.
- [Quality attributes and trade-offs](../architecture-fundamentals/quality-attributes-and-trade-offs.md#hands-on-lab-a-trade-off-matrix-for-a-real-decision) — build a trade-off matrix for a real decision.
- [The C4 model](../architecture-fundamentals/c4-model.md#hands-on-lab-draw-your-system) — draw context and container diagrams for a system you know.
- [Estimating load, throughput, storage, and capacity](../performance-and-scalability/capacity-estimation.md#hands-on-lab-size-a-system-in-a-spreadsheet) — size a system with a spreadsheet and check it with Little's Law.
