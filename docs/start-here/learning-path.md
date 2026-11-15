---
title: Learning paths
description: "Where to start: a beginner path, a faster path for cloud/DevOps engineers, and an AI-architecture path, each in recommended order."
---

# Learning paths

Three paths, each a recommended order through the same material. Written pages are linked; planned
pages are named so you can see the whole journey. Each path ends with design exercises because
architecture is learned by deciding, not by reading.

## Where should I start? (beginner path)

You are new to architecture, possibly new to parts of software engineering, and want a solid base.

**Stage 1 — Think like an architect** (available now)

1. [What does a Solutions Architect do?](../architecture-fundamentals/what-does-a-solutions-architect-do.md)
2. [Functional vs non-functional requirements](../architecture-fundamentals/functional-vs-non-functional-requirements.md)
3. [Architecture quality attributes and trade-offs](../architecture-fundamentals/quality-attributes-and-trade-offs.md)
4. [The C4 model: how to communicate software architecture](../architecture-fundamentals/c4-model.md)
5. [How to estimate load, throughput, storage, and capacity](../performance-and-scalability/capacity-estimation.md)

**Stage 2 — Foundations** (planned; see [Foundations](../foundations/index.md))

6. Computers, operating systems, and Linux for architects
7. Programming fundamentals, data structures, and algorithms
8. Programming paradigms and concurrency
9. Networking fundamentals: IP, CIDR, routing, and DNS
10. Relational databases and SQL internals

**Stage 3 — Core application architecture** (planned)

11. Architecture styles · 12. API design · 13. Caching architecture · 14. Message queues and brokers ·
15. Distributed systems fundamentals · 16. Consistency models, CAP, and PACELC ·
17. High availability design · 18. Security principles and threat modeling

**Stage 4 — Practice**

19. Design exercises: URL shortener, rate limiter, notification service
20. Case study 01: Highly available three-tier web application

## I already know cloud and DevOps (accelerated path)

You run AWS (or another cloud), Terraform, CI/CD, Docker, and Kubernetes. You want application,
distributed-systems, data, enterprise, and AI architecture depth, and the vocabulary to defend designs.

**Stage 1 — Sharpen the architect's toolkit** (available now, 3-4 hours)

Read the same five pages as the beginner path, but focus on the Level 3 sections, the trade-off
tables, and the discussion questions. Do the capacity-estimation lab with a system you operate.

**Stage 2 — Distributed systems and data** (planned)

- Consistency models, CAP, and PACELC → Transactions, sagas, and delivery guarantees →
  Resilience mechanics → Scaling, partitioning, and replication
- Relational internals → NoSQL by access pattern → Advanced database architecture → Caching
- Event-driven architecture → Event streaming → Messaging technologies compared

**Stage 3 — Application and enterprise** (planned)

- Architecture styles → Microservices (and when not) → Distributed system patterns
- API design → Integration architecture
- Enterprise architecture practice → Legacy modernization → Hybrid and multi-cloud

**Stage 4 — Operate at scale** (planned)

- Performance fundamentals → Observability → Incident management and SRE → Disaster recovery strategies
- FinOps → Platform engineering

**Stage 5 — Practice**

- Design exercises: multi-region application, multi-tenant SaaS, landing zone, secure CI/CD
- Case studies 02, 03, 08, 10, 11

## AI architecture path

For engineers who need to design AI systems responsibly. Assumes the accelerated path's Stage 1.

1. AI, ML, and learning paradigms → Math for machine learning → Neural networks and transformers
2. ML lifecycle → MLOps
3. LLM fundamentals → LLM architecture decisions → Prompt and context engineering
4. RAG fundamentals → Ingestion and chunking → Embeddings and vector indexes → Retrieval and reranking → Advanced RAG
5. Agent fundamentals → Components and runtime → Patterns → Memory → Tools → MCP and A2A → Long-running agents
6. GPU infrastructure → Model serving and inference → AI platform and LLMOps
7. AI evaluation → AI observability → AI safety and security → NIST AI RMF and OWASP guidance
8. Design exercises: enterprise RAG, AI gateway, MCP server platform; case studies 16-25

All AI pages are planned; the sections exist with their topic lists:
[AI and ML foundations](../ai-ml-foundations/index.md),
[Generative AI and LLMs](../generative-ai-and-llms/index.md),
[RAG and vector search](../rag-and-vector-search/index.md),
[Agentic AI](../agentic-ai/index.md),
[AI infrastructure and LLMOps](../ai-infrastructure-and-llmops/index.md),
[AI evaluation, security, and governance](../ai-security-and-governance/index.md).

## How the paths map to the design method

Every path ends in the twelve-step [design method](../system-design-exercises/index.md). The
Stage 1 pages cover steps 1-3 (understand the problem, gather requirements, estimate load) and the
communication skill (C4) you need for every later step.

## Visual overview

**Figure 1 — The three paths share a common first stage and converge on practice.**

```mermaid
flowchart TB
    S1[Stage 1: Think like an architect<br/>5 pages, available now]
    S1 --> B[Beginner path<br/>Foundations → Core architecture]
    S1 --> A[Accelerated path<br/>Distributed systems → Data → Enterprise → Operations]
    S1 --> AI[AI path<br/>ML → LLMs → RAG → Agents → Serving → Governance]
    B --> P[Practice: design exercises and case studies]
    A --> P
    AI --> P
```

Read it top to bottom: everyone starts with the same five pages, branches by background, and ends by
designing systems and defending the decisions.
