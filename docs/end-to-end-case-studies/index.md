---
title: End-to-end case studies
description: "Complete architecture case studies with business narrative, progressive diagrams, decision records, alternatives, and learner challenges."
---

# End-to-end case studies

Each case study follows one fictional organization from business problem to running system:
context and requirements, capacity estimates, options considered, the chosen architecture in
progressive C4 diagrams, request and data flows, security boundaries, reliability and DR, operations,
cost model, risks, Architecture Decision Records, and at least one plausible alternative with the
conditions under which it would be the better choice. Every case ends with a challenge for you.

Case studies use the [case-study template](https://github.com/vinay9354/architecture-atlas/blob/main/templates/case-study-template.md)
and the twelve-step [design method](../system-design-exercises/index.md).

## Case studies

| # | Case study | Track | Status |
|---|---|---|---|
| 01 | [Highly available three-tier web application](cs-01-highly-available-three-tier-web-application.md) | Core | Draft |
| 02 | Monolith to modular monolith and then microservices modernization | Core | Planned |
| 03 | Multi-tenant SaaS platform with tenant isolation | Core | Planned |
| 04 | E-commerce application with flash-sale traffic | Core | Planned |
| 05 | Payment and order-processing workflow using Saga and idempotency | Core | Planned |
| 06 | Real-time notification and event-processing platform | Core | Planned |
| 07 | Centralized enterprise logging and security monitoring platform | Core | Planned |
| 08 | [Multi-account cloud landing zone and hub-and-spoke network](cs-08-multi-account-landing-zone-and-hub-and-spoke-network.md) | Core | Draft |
| 09 | Hybrid on-premises/cloud migration with private connectivity | Core | Planned |
| 10 | Multi-region active-passive and active-active disaster recovery | Core | Planned |
| 11 | Enterprise Kubernetes platform with GitOps and policy controls | Core | Planned |
| 12 | Data lakehouse with batch and streaming ingestion | Core | Planned |
| 13 | Real-time fraud detection pipeline | Core | Planned |
| 14 | Enterprise API platform with authentication, quotas, and developer onboarding | Core | Planned |
| 15 | [Zero-trust application architecture](cs-15-zero-trust-application-architecture.md) | Core | Draft |
| 16 | Enterprise document RAG assistant with document-level access control | AI | Planned |
| 17 | Customer-support assistant with human handoff and auditable actions | AI | Planned |
| 18 | Multi-model AI gateway with routing, fallback, quotas, and cost controls | AI | Planned |
| 19 | Secure MCP server exposing read-only enterprise tools | AI | Planned |
| 20 | Agent that performs approved cloud operations with least privilege and rollback | AI | Planned |
| 21 | Multi-agent research/workflow system with bounded autonomy | AI | Planned |
| 22 | Model-serving platform on Kubernetes with GPU scheduling and autoscaling | AI | Planned |
| 23 | LLM evaluation and observability platform | AI | Planned |
| 24 | Multimodal knowledge assistant using text, documents, and images | AI | Planned |
| 25 | Production AI platform with governance, security, tenant isolation, and audit trails | AI | Planned |

Case studies 01, 08, and 15 are written (Draft, awaiting review). The rest are scheduled in the
[roadmap](https://github.com/vinay9354/architecture-atlas/blob/main/ROADMAP.md) after the concept
pages they depend on: each case study links to the topic pages it applies.
