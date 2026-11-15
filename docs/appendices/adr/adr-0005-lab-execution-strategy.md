---
title: "ADR-0005: Lab execution strategy"
description: "Labs run locally with free tools by default; cloud, GPU, or API-key requirements are explicit opt-ins with cleanup and cost safeguards."
---

# ADR-0005: Local-first labs with explicit cloud/GPU opt-in

**Status:** Accepted  
**Date:** 2026-11-15  
**Deciders:** Repository maintainer, initial AI build agent  
**Related:** [ADR-0006](adr-0006-example-testing.md), `templates/lab-template.md`

## Context

Labs turn theory into experiments, but learners have different budgets, machines, and permissions.
Labs must never require exposing credentials, granting broad cloud permissions, running destructive
commands, or uploading private data. AI labs additionally face GPU and API cost barriers.

## Decision drivers

- Accessibility: most labs should run on a laptop with free tools.
- Safety: no credential exposure, no destructive commands, cleanup always documented.
- Honesty: say what costs money before the learner starts.
- Reproducibility: pinned tool versions and tested instructions.

## Options considered

### Option 1 — Cloud-first labs on AWS

Realistic, but cost and permission barriers exclude many learners and risk surprise bills.

### Option 2 — Local-first with containers and simulators; cloud and GPU as labelled opt-ins (chosen)

Docker/Podman, kind or k3d for Kubernetes, local databases and brokers in containers, Python scripts
for simulations, small local embedding models or a mock model endpoint for RAG and agent labs. Cloud
labs live under `labs/cloud-optional/` with cost estimates, least-privilege policies, and cleanup.

### Option 3 — Hosted sandbox environments

Attractive but requires infrastructure and funding the project does not have.

## Decision

- Default: labs under `labs/local/` run with free, local, containerized, or simulated tools.
- `labs/cloud-optional/` holds labs that need a cloud account; each states required permissions
  (least privilege), expected cost, and cleanup commands, and uses tagging so resources are findable.
- AI labs prefer local or mock model endpoints; any hosted model usage is optional and keyed by an
  environment variable that the learner supplies, never committed.
- Every lab includes: goal, concepts, prerequisites, tool versions, cost warning, setup, steps,
  expected output, validation, cleanup, troubleshooting, stretch challenge, and a separated solution.
- Simulations (queues, sharding, replication lag, autoscaling) are small Python programs with clearly
  labelled simplifications and seeded randomness for reproducible output.

## Consequences

**Positive**

- Any learner with a laptop can complete the core lab path for free.
- Reduced risk of accidental cloud spend or credential leakage.

**Negative**

- Local simulations simplify real cloud behavior; each lab states its simplifications.
- Kubernetes and GPU labs need capable machines; minimum requirements are stated per lab.

## Follow-up actions

- [ ] Write Lab 01 (latency and throughput) as the reference implementation of this strategy.
- [ ] Provide a dev container definition so tool versions are consistent across machines.
