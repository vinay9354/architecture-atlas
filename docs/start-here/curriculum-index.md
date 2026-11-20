---
title: Curriculum index
description: "All thirty curriculum domains, what each covers, where it lives, and how much of it is written."
---

# Curriculum index

The curriculum has thirty domains. Each row links to the section that hosts the domain, where every
topic is listed with its status. Counts come from the
[coverage matrix](../appendices/coverage-matrix.md), which is generated from
`curriculum/coverage.yaml` and checked in CI, so this index cannot drift from reality.

**Legend:** Written = at least one topic entry in the domain has a page in `Outline`, `Draft`, or
`Reviewed` status.

## Part I — Architecture thinking and software foundations

| Domain | Covers | Section | Written |
|---|---|---|---|
| D01 Architecture thinking, requirements, and design fundamentals | Requirements, stakeholders, constraints, quality attributes, SLOs, trade-offs, ADRs, diagrams | [Architecture fundamentals](../architecture-fundamentals/index.md) | 3 of 9 topics (Draft) |
| D02 Computer science and software engineering foundations | Hardware, OS, Linux, data structures, algorithms, paradigms, concurrency, design principles, testing | [Foundations](../foundations/index.md) | 0 of 5 |
| D03 Software architecture styles and design patterns | Styles, microservices, application patterns, distributed patterns | [Software architecture](../software-architecture/index.md) | 0 of 4 |
| D04 Distributed systems | Partial failure, time, consistency, CAP/PACELC, transactions, resilience, scaling | [Distributed systems](../distributed-systems/index.md) | 0 of 5 |
| D05 Application, API, and integration architecture | Web/mobile/SaaS apps, API design, integration styles | [Application, API, and integration](../application-and-api-architecture/index.md) | 0 of 3 |

## Part II — Data

| Domain | Covers | Section | Written |
|---|---|---|---|
| D06 Database, storage, and caching architecture | Relational internals, NoSQL, advanced databases, storage, caching | [Databases, storage, and caching](../databases-and-storage/index.md) | 0 of 5 |
| D07 Data engineering, analytics, and big data | Modeling, pipelines, warehouse/lake/lakehouse/mesh, engines and table formats, OLAP and BI | [Data engineering and analytics](../data-engineering-and-analytics/index.md) | 0 of 5 |
| D08 Messaging, event-driven systems, and streaming | Queues, events, streaming, broker technologies | [Messaging and streaming](../messaging-and-streaming/index.md) | 0 of 4 |

## Part III — Cloud, platform, and operations

| Domain | Covers | Section | Written |
|---|---|---|---|
| D09 Networking and hybrid connectivity | IP/CIDR/DNS, protocols, security and load balancing, VPN and private links | [Networking](../networking/index.md) | 0 of 4 |
| D10 Cloud and infrastructure architecture | Service models, building blocks, compute, multi-account, providers | [Cloud architecture](../cloud-architecture/index.md) | 0 of 5 |
| D11 Containers, Kubernetes, and cloud-native | Containers, Kubernetes, networking/storage/mesh, ecosystem | [Containers and Kubernetes](../containers-and-kubernetes/index.md) | 0 of 4 |
| D12 Security architecture and cybersecurity | Principles, IAM, network, application, data, supply chain, SecOps, compliance | [Security architecture](../security-architecture/index.md) | 0 of 8 |
| D13 High availability, reliability, resilience, and DR | HA design, reliability engineering, DR, advanced resilience | [Reliability and disaster recovery](../reliability-and-disaster-recovery/index.md) | 0 of 4 |
| D14 Performance engineering and scalability | Latency/throughput, scaling techniques, capacity planning | [Performance and scalability](../performance-and-scalability/index.md) | 1 of 3 (Draft) |
| D15 Observability, monitoring, SRE, and operations | Telemetry, monitoring and alerting, incident management | [Observability and SRE](../observability-and-sre/index.md) | 0 of 3 |
| D16 DevOps, DevSecOps, CI/CD, IaC, platform engineering | Delivery lifecycle, pipelines, IaC, DevSecOps, platforms | [DevOps and platform engineering](../devops-and-platform-engineering/index.md) | 0 of 5 |
| D17 FinOps, cost architecture, and sustainability | Cost models, unit economics, carbon-aware design | [FinOps and sustainability](../finops-and-sustainability/index.md) | 0 of 2 |
| D18 Enterprise architecture, governance, hybrid, modernization | EA practice, frameworks, modernization, hybrid/multi-cloud | [Enterprise architecture](../enterprise-architecture/index.md) | 0 of 4 |

## Part IV — AI

| Domain | Covers | Section | Written |
|---|---|---|---|
| D19 AI and machine learning foundations | Paradigms, classical ML, math | [AI and ML foundations](../ai-ml-foundations/index.md) | 0 of 3 |
| D20 Deep learning, ML lifecycle, and MLOps | Neural networks, transformers, lifecycle, MLOps, ML infrastructure | [AI and ML foundations](../ai-ml-foundations/index.md) | 0 of 4 |
| D21 Generative AI, LLMs, prompt and context engineering | LLM fundamentals, architecture decisions, prompt/context engineering | [Generative AI and LLMs](../generative-ai-and-llms/index.md) | 0 of 4 |
| D22 Retrieval-Augmented Generation and vector search | RAG, ingestion, embeddings, retrieval, advanced RAG, platform | [RAG and vector search](../rag-and-vector-search/index.md) | 0 of 6 |
| D23 Agentic AI, multi-agent systems, MCP, and A2A | Agents, components, patterns, memory, tools, protocols, durability | [Agentic AI](../agentic-ai/index.md) | 0 of 7 |
| D24 AI infrastructure, model serving, and LLMOps | GPUs, serving, technologies, platform | [AI infrastructure and LLMOps](../ai-infrastructure-and-llmops/index.md) | 0 of 4 |
| D25 AI evaluation, observability, security, safety, governance | Evaluation, observability, safety/security, NIST/OWASP | [AI evaluation, security, and governance](../ai-security-and-governance/index.md) | 0 of 4 |

## Part V — Practice

| Domain | Covers | Section | Written |
|---|---|---|---|
| D26 Industry-specific solution architecture | E-commerce, finance, healthcare, media, IoT, logistics, enterprise, others | [Industry architectures](../industry-architectures/index.md) | 0 of 8 |
| D27 Advanced and emerging architecture | Edge, real-time, search, blockchain, privacy-preserving, cyber resilience, advanced AI | [Emerging architectures](../emerging-architectures/index.md) | 0 of 7 |
| D28 Architecture frameworks and reference models | Well-Architected, adoption frameworks, TOGAF/Zachman/C4/DDD/NIST/OWASP/FinOps/SRE/CNCF | [Reference architectures and frameworks](../reference-architectures/index.md) | 0 of 4 |
| D29 Architecture problem-solving exercises | Graded design exercises from URL shortener to AI platforms | [System design exercises](../system-design-exercises/index.md) | 0 of 5 |
| D30 Architecture design method | The twelve-step method and AI-specific decisions | [System design exercises](../system-design-exercises/index.md) | 0 of 2 |

Beyond the thirty domains, the repository also plans twenty-five
[end-to-end case studies](../end-to-end-case-studies/index.md) and twenty-five
[hands-on labs](../labs/index.md).

## Reading the status honestly

As of 2026-11-20, 33 topic entries are written in `Draft` status and 3 in `Outline`, across D01-D06,
D08, D09, D13, D14, D29, and D30. Alongside them are the Solutions Architect role page, six labs, four
full design exercises, and one domain quiz. The other 104 topic entries are `Planned` with a
destination path each. Nothing is `Reviewed` yet; the
[roadmap](https://github.com/vinay9354/architecture-atlas/blob/main/ROADMAP.md) lists what comes next.
