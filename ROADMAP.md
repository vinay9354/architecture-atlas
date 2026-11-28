# Roadmap

This roadmap lets a human contributor or an AI agent continue the work without losing context.
It follows the implementation phases in `MASTER_PROMPT.md` Section 16. Topic-level status lives in
`curriculum/coverage.yaml` (rendered at `docs/appendices/coverage-matrix.md`); this file tracks
batches.

Status legend: ✅ done · 🔄 in progress · ⬜ not started

## Phase 0 — Inspect and plan ✅ (2026-11-15)

- Empty repository with `origin` set, Python 3.14, uv, Node 26 available.
- Stack: MkDocs 1.6.1 + Material 9.8.1 (ADR-0001). Mermaid diagrams (ADR-0003).

## Phase 1 — Repository foundation ✅ (2026-11-15)

- README, MASTER_PROMPT, licenses (MIT + CC BY 4.0), attribution register, third-party notices,
  contributing, conduct, security, support, changelog, roadmap.
- `mkdocs.yml`, pinned requirements, editorconfig, markdownlint, lychee config, `.gitignore`.
- CI: docs-build (validate + strict build + lint + secret scan), link-check (weekly), pages deploy.
- Templates: topic, lab, case study, ADR. Six repository ADRs.
- Landing page, Start Here (how to use, learning paths, curriculum index, glossary).
- 33 section landing pages with injected topic tables; coverage matrix generator and validator; tests.
- Open: GitHub Pages must be enabled by the maintainer (Settings → Pages → GitHub Actions).

## Phase 2 — Core learning path ✅ (2026-11-15; human review carried into Phase 9)

| # | Page | Status |
|---|---|---|
| 1 | What does a Solutions Architect do? | ✅ Draft |
| 2 | Functional vs non-functional requirements | ✅ Draft |
| 3 | Architecture quality attributes and trade-offs | ✅ Draft |
| 4 | C4 model and architecture documentation | ✅ Draft |
| 5 | Estimate load, throughput, storage, and capacity | ✅ Draft |
| 6 | Networking fundamentals (D09-T01) and transport/application protocols (D09-T02), two pages | ✅ Draft |
| 7 | Relational databases and SQL internals (D06-T01) | ✅ Draft |
| 8 | API design (D05-T02) and integration architecture (D05-T03), two pages | ✅ Draft |
| 9 | Caching architecture (D06-T05) and message queues and brokers (D08-T01), two pages | ✅ Draft |
| 10 | Distributed systems fundamentals, time, and coordination (D04-T01) | ✅ Draft |
| 11 | High availability design (D13-T01) and performance fundamentals (D14-T01), two pages | ✅ Draft |
| 12 | SLAs, SLOs, SLIs, error budgets, and recovery objectives (D01-T06) | ✅ Draft |
| 13 | Trade-offs, principles, ADRs, and architecture governance (D01-T07) | ✅ Draft |
| 14 | Stakeholders and success metrics (D01-T02); constraints and scope (D01-T03); As-Is/To-Be and build vs buy (D01-T04), three pages | ✅ Draft |
| 15 | Second-person review of all Draft pages → promote to Reviewed | ➡️ moved to Phase 9 (needs a human reviewer) |

Also in this phase: Lab 01 (latency and throughput) ✅ Draft, with a CI smoke test; glossary growth ✅;
first domain quiz for D01 ✅ Draft.

## Phase 3 — Software and distributed architecture ✅ (2026-11-20; human review carried into Phase 9)

| Area | Pages | Status |
|---|---|---|
| D02 foundations | Computers, OS, and Linux (T01); data structures and algorithms (T02); paradigms and concurrency (T03); design principles and clean code (T04); testing types and strategies (T05) | Draft |
| D03 software architecture | Architecture styles (T01); microservices (T02); application design patterns (T03); distributed system patterns (T04) | Draft |
| D04 distributed systems | Consistency, CAP, and PACELC (T02); transactions, sagas, and delivery guarantees (T03); resilience mechanics (T04); scaling, partitioning, and replication (T05) | Draft |
| D30 design method | The twelve-step architecture design method (T01); AI design decisions at definition depth (T02) | Draft / Outline |
| D29 exercises | URL shortener, rate limiter, distributed cache, job scheduler (full); application and infrastructure exercise collections with briefs for the rest | Draft / Outline |
| Labs | 03 queue retries and DLQ; 04 idempotency; 05 race condition; 08 sharding and consistent hashing; 09 replication lag, each with a CI smoke test | Draft |

The design method page was scheduled for Phase 8; it moved here because the exercises are built on it.

## Phase 4 — Cloud and enterprise architecture ✅ (4A 2026-11-21, 4B 2026-11-27; human review carried into Phase 9)

Phase 4 is split into two batches because of its size (41 topics, 6 labs, 6 case studies, 3 exercises).

**Batch 4A — networking, cloud, containers, security** (written, Draft)

| Area | Pages | Status |
|---|---|---|
| D09 networking | Network security, load balancing, and traffic flow (T03); hybrid connectivity and VPNs (T04) | Draft |
| D10 cloud | Service and deployment models (T01); building blocks and landing zones (T02); compute options and sizing (T03); multi-account strategy and automation (T04); providers, principles before catalogs (T05) | Draft |
| D11 containers and Kubernetes | Containers and images (T01); Kubernetes architecture and workloads (T02); networking, storage, and service mesh (T03); ecosystem tools (T04) | Draft |
| D12 security | Principles and threat modeling; IAM; network; application; data and privacy; infrastructure and supply chain; security operations; compliance (T01-T08) | Draft |
| Case studies | 01 three-tier HA web app; 08 landing zone and hub-and-spoke; 15 zero-trust application | Draft |
| D29-T04 exercises | Multi-account landing zone and zero-trust enterprise (full); collection page with briefs for the other eleven | Draft / Outline |
| Labs | 10 REST API auth and validation; 12 local Kubernetes; 14 network segmentation; 15 infrastructure module and static checks | Draft |

**Batch 4B — reliability, operations, delivery, cost, enterprise, frameworks** (written, Draft)

| Area | Pages | Status |
|---|---|---|
| D13 reliability | Reliability engineering (T02); disaster recovery strategies (T03); advanced resilience and failure containment (T04) | Draft |
| D15 operations | Observability fundamentals (T01); monitoring, alerting, and on-call (T02); incident management and SRE (T03) | Draft |
| D16 delivery | DevOps lifecycle (T01); CI/CD and deployment strategies (T02); Infrastructure as Code (T03); DevSecOps (T04); platform engineering (T05) | Draft |
| D17 cost | Cloud cost models and FinOps (T01); sustainable and carbon-aware architecture (T02) | Draft |
| D18 enterprise | EA practice (T01); EA frameworks (T02, also D28-T03/T04); legacy modernization (T03); hybrid and multi-cloud (T04) | Draft |
| D28 frameworks | Well-Architected frameworks (T01); cloud adoption frameworks (T02) | Draft |
| Case studies | 09 hybrid migration; 10 multi-region DR; 11 enterprise Kubernetes with GitOps | Draft |
| Exercise | Multi-region disaster recovery (D29-T04) | Draft |
| Labs | 11 tracing and structured logging; 13 GitOps reconciliation | Draft |

## Phase 5 — Data architecture ✅ (2026-11-28; human review carried into Phase 9)

| Area | Pages | Status |
|---|---|---|
| D06 databases and storage | NoSQL (T02); advanced database architecture (T03); storage architecture (T04) | Draft |
| D07 data engineering | Modeling, metadata, governance (T01); pipelines (T02); warehouses, lakes, lakehouses, mesh (T03); engines and table formats (T04); OLTP vs OLAP and BI (T05) | Draft |
| D08 messaging and streaming | Event-driven architecture (T02); event streaming (T03); technologies compared (T04) | Draft |
| Case studies | 12 lakehouse with batch and streaming ingestion; 13 real-time fraud detection | Draft |
| D29-T03 exercises | Data lake, CDC pipeline, real-time analytics (full); collection with briefs for the rest | Draft / Outline |
| Labs | 02 cache hit and miss; 06 indexing and query plans; 07 SQL vs NoSQL; 16 event-driven workflow | Draft |

## Phase 6 — AI and ML foundations ⬜

D19, D20. Evaluation basics. Exercise: recommendation engine.

## Phase 7 — Generative AI and agentic AI ⬜

D21, D22, D23, D24, D25, D27-T07. Labs 17-25. Case studies 16-25. Exercises: enterprise RAG, AI
gateway, MCP server platform, GPU inference. Protocol pages (MCP, A2A) must record the specification
version and date checked.

## Phase 8 — Case studies and design studio ⬜

Remaining case studies (02-07, 14), D26 industry architectures, D27 emerging architectures, D29/D30
exercise library and design method page, interactive visualizations where they add understanding
(latency budget calculator, cache hit/miss explorer, consistency timeline, RAG pipeline explorer,
agent trace viewer), quizzes per domain.

## Phase 9 — Quality and public release readiness ⬜

- All checks green: strict build, lint, validator, tests, link check classified.
- License and attribution audit; dependency license inventory.
- Accessibility pass: keyboard, contrast, reduced motion, alt text, mobile.
- Headless Mermaid render check in CI (ADR-0003 follow-up); offline Mermaid bundle decision.
- Cross-check page front matter against coverage YAML (ADR-0004 follow-up).
- Second-person review of every Draft page; promote to `Reviewed` only after that review (carried from Phase 2).
- Release checklist; enable Pages; announce. No remote changes without maintainer approval.

## Known gaps and technical debt (as of 2026-11-28)

- Mermaid syntax is only type-checked by the validator; rendering was verified manually in a browser
  for every page written so far. CI does not render diagrams.
- Page `status` is recorded in both front matter and `coverage.yaml`; no automated cross-check yet.
- `docs/appendices/tags.md` depends on the Material tags plugin's index marker; verify after theme upgrades.
- External link checking runs weekly, not on pull requests, to avoid flaky failures. On 2026-11-15 all
  39 reference URLs were checked: 38 resolve; the Little's Law DOI link returns 403 to automated
  clients (publisher bot-blocking, classified as "blocked by the checker", not broken). After the
  Phase 2 batch, 134 distinct reference URLs were checked: 130 resolve; doi.org and cacm.acm.org
  return 403 to scripts (both open in a browser); the repository's own GitHub link to
  `labs/solutions/lab-01/expected-results.md` returns 404 until the branch is pushed.
- The Contributor Covenant is adopted by reference with original wording; if its full text is adopted
  later, its CC BY 4.0 attribution must be added.
- No interactive demos yet.
- Lab 01 runs client and server on one machine, so its absolute numbers include load-generator
  overhead; the page says to compare ratios. An open-loop load generator is left as a stretch task.
- Page 15 of Phase 2 (promotion to Reviewed) cannot be done by the build agent; it needs a second
  person.
- On 2026-11-20 the history was rewritten so every commit is authored by `vinay9354`. The force-push
  made one CI run fail in the gitleaks step (it scans from the parent of the first pushed commit, and
  the root commit has none). The checkout now fetches full history; the one-off failure needs no fix.
- Until 2026-11-20 `tests/examples/` had no `__init__.py`, so `unittest discover` (locally and in
  CI) silently skipped every lab smoke test, including Lab 01's. The package marker is now in place
  and discovery runs 49 tests (8 content, 41 lab).
- Two code samples in Phase 3 exercises are illustrative and were not executed against the real
  system: the Lua token-bucket script in the rate limiter exercise (no Redis available) and the
  `SKIP LOCKED` claim query in the job scheduler exercise (no PostgreSQL available). Both pages say
  so in their review notes.
- Five Phase 3 pages run longer than the 650-line target (up to 725 lines); they were kept whole
  rather than cut.
- Batch 4A steps that were not executed because no container runtime or cluster was available to the
  build agent: Lab 12's cluster steps (create, load, apply, drain, NetworkPolicy test), the Docker
  Compose appendix of Lab 14, the Dockerfiles on the containers page, and the Kubernetes YAML on the D11
  pages (parsed, never applied). OpenTofu commands in Lab 15 were not run (Terraform 1.15.6 was). A
  reviewer with Docker and kind should run Lab 12 end to end; three behaviours need confirmation
  (replacement Pod placement after a zone drain with `nodeTaintsPolicy: Honor`, the drain sequence, and
  kubelet probes under default-deny NetworkPolicies).
- Facts in batch 4A that rest on secondary sources and need a reviewer: the mapping of NIST SP 800-61
  Rev. 3 to CSF functions; SP 800-86 phase names; the claim that Microsoft moved away from DREAD; PCI DSS
  requirement titles (the official PDF is behind a licence page). iso.org and hhs.gov return 403 to
  scripts; their links were kept.
- Several batch 4A pages run past the 650-line target (up to about 720 lines).
- docs.aws.amazon.com answers HTTP 200 even for pages that do not exist, so a status check cannot
  prove an AWS link is real. On 2026-11-21 all 68 AWS documentation URLs in batch 4A were checked by
  page title instead (a missing page returns only the generic service name); all were real.
- Batch 4B steps not executed: the optional OpenTelemetry SDK appendix of Lab 11, the optional kind plus
  Argo CD appendix of Lab 13, and the Kyverno policies in case study 11 (not run against a cluster or the
  Kyverno CLI). Lab 11 and Lab 13 themselves run in CI.
- Kyverno's `ClusterPolicy`, `Policy`, `CleanupPolicy`, and legacy `PolicyException` are deprecated as of
  v1.19 and due for removal in v1.20 (kyverno.io, checked 2026-11-27); case study 11 uses the CEL-based
  kinds. Re-check when v1.20 ships.
- Facts in batch 4B from secondary or partial sources, for a reviewer: SPACE dimension names (abstract
  only; the ACM Queue paper blocks scripts); the four green-software principle names (the GSF learning
  site blocks scripts); TOGAF method phase names (pubs.opengroup.org now needs a sign-in); the Google
  Cloud Well-Architected review tooling, which is likely to change.
- The scratchpad used by the build agent was cleared between sessions on 2026-11-27, which removed the
  pre-rewrite history backup bundle. The rewrite was verified and pushed earlier, so nothing depends on it.
- Phase 5 items for a reviewer: the advanced database page's PostgreSQL mini-lab was not run (no
  PostgreSQL available); the storage page costs the event store by provisioned volume (2 × 600 GB) while
  the FinOps page costs stored data (430 GB), which is deliberate but should be cross-referenced; Lab 07
  generates about 4.5 scan events per shipment while the AtlasMart figure is 8 (480,000 ÷ 60,000); the
  data fabric definition has no vendor-neutral primary source; recent messaging features (Kafka share
  groups, Kinesis queue consumers, the new EventBridge custom event bus, Event Hubs Kafka transactions in
  preview) should be re-checked against owner docs.
- Earlier pages cite a 13-month event-store retention (relational page) that predates the 180-day rule
  on the data security page; a note now points to the later decision, but the original example text is
  unchanged.
