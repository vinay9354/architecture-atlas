---
title: Application, API, and integration architecture
description: "Most of the value in an enterprise system flows through its APIs and integrations. This section covers."
---

# Application, API, and integration architecture

Most of the value in an enterprise system flows through its APIs and integrations. This section covers
how applications are structured (web, mobile, SaaS, multi-tenant), how to design APIs that survive
versioning and abuse (REST, GraphQL, gRPC, WebSockets, webhooks, asynchronous APIs), and how systems
are connected (point-to-point, brokers, ESBs, iPaaS, API-led connectivity, EDI).

Integration is where legacy systems meet new ones, so error handling, replay, and reconciliation get
as much attention as the happy path.

## What you will learn here

- Choose between REST, GraphQL, gRPC, and event-based APIs for a given consumer and workload
- Design pagination, filtering, idempotency keys, versioning, and deprecation into an API from day one
- Secure and rate-limit an API and explain the trade-offs of each quota model
- Select an integration style and explain its failure handling, replay, and reconciliation story
- Structure a multi-tenant SaaS application and its background work

**Prerequisites:** [Architecture fundamentals](../architecture-fundamentals/index.md); [Networking](../networking/index.md) for protocols.

## Topics in this section

Every topic from the master curriculum that belongs to this section is listed below with its
status. A link means the page exists; `planned:` shows where it will be created. Status meanings
are explained in the [coverage matrix](../appendices/coverage-matrix.md).

<!-- coverage:start -->
| ID | Topic | Status | Page |
|---|---|---|---|
| **D05** | **Application, API, and integration architecture** | | |
| D05-T01 | Application architecture for web, mobile, and SaaS | :material-circle-outline: Planned | planned: `application-and-api-architecture/application-architecture-for-web-mobile-and-saas.md` |
| D05-T02 | API design: REST, GraphQL, gRPC, and async APIs | :material-circle-slice-5: Draft | [api-design-rest-graphql-grpc-and-async-apis](api-design-rest-graphql-grpc-and-async-apis.md) |
| D05-T03 | Integration architecture | :material-circle-slice-5: Draft | [integration-architecture](integration-architecture.md) |
<!-- coverage:end -->

## How to continue

- Follow the [learning paths](../start-here/learning-path.md) for a recommended order.
- Look up unfamiliar terms in the [glossary](../start-here/glossary.md).
- Want to write one of the planned pages? See the
  [contribution guide](https://github.com/vinay9354/architecture-atlas/blob/main/CONTRIBUTING.md).
