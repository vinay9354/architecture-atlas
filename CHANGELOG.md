# Changelog

All material changes to content and tooling, newest first. Technical corrections to published pages
name the page, the correction, and the source that prompted it.

Format follows the spirit of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added — 2026-11-28, data architecture batch (Phase 5)

- Eleven topic pages (Draft): NoSQL databases; advanced database architecture; storage architecture;
  data modeling, metadata, and data governance; batch, streaming, ETL/ELT, and pipelines; warehouses,
  lakes, lakehouses, and data mesh; big data processing engines and table formats; OLTP vs OLAP,
  dimensional modeling, and BI; event-driven architecture; event streaming and log-based architecture;
  messaging technologies compared.
- Case studies (Draft): 12 data lakehouse with batch and streaming ingestion (Corvina Mobility), 13
  real-time fraud detection pipeline (Halvane Pay).
- Exercises (Draft): data lake, CDC pipeline, real-time analytics; the D29-T03 data platform exercise
  collection (Outline) with briefs for all ten listed exercises.
- Labs 02 (cache hit and miss), 06 (indexing and query plans in SQLite), 07 (SQL vs NoSQL access
  patterns), and 16 (event-driven workflow with an outbox, idempotent consumers, and a saga), each with
  results and a smoke test.
- Glossary: 97 new terms in three sections, 638 terms in total.
- Navigation, learning paths, quiz index, labs and case-study indexes, curriculum index, README, and
  roadmap updated; `curriculum/coverage.yaml` marks 84 topic entries Draft and 5 Outline.

### Changed — 2026-11-28

- Event Store partitioning: later-decision notes on the relational, scaling, and data security pages
  record the move to weekly partitions on `occurred_at` (advanced database architecture page).
- Consistency fixes across new pages: scan events reach the lakehouse through an outbox and a
  `scan-events` topic; the clickstream topic has 24 partitions, with 12 Bronze writer tasks; the
  event-driven page is framed as the step after the CDC pipeline exercise.

### Added — 2026-11-27, reliability, operations, delivery, cost, and enterprise batch (Phase 4B)

- Nineteen topic pages (Draft) covering twenty-one curriculum entries: reliability engineering;
  disaster recovery strategies; advanced resilience and failure containment; observability
  fundamentals (logs, metrics, traces); monitoring, alerting, and on-call; incident management and SRE
  practices; DevOps lifecycle and source control; CI/CD pipeline design and deployment strategies;
  Infrastructure as Code; DevSecOps and secure delivery; platform engineering; cloud cost models and
  FinOps; sustainable and carbon-aware architecture; enterprise architecture practice; enterprise
  architecture frameworks (also D28-T03 and D28-T04); legacy modernization and migration; hybrid and
  multi-cloud architecture; Well-Architected frameworks; cloud adoption frameworks.
- Case studies (Draft): 09 hybrid migration with private connectivity (AtlasMart's warehouse system),
  10 multi-region disaster recovery, 11 enterprise Kubernetes platform with GitOps.
- Exercise (Draft): multi-region disaster recovery for AtlasMart's 40-service retail platform.
- Labs 11 (distributed tracing and structured logging, W3C Trace Context in the standard library) and
  13 (GitOps reconciliation against a local Git repository), each with results and a smoke test.
- Glossary: 139 new terms in six sections, 541 terms in total.
- Navigation, learning paths, quiz index, labs and case-study indexes, curriculum index, README, and
  roadmap updated; `curriculum/coverage.yaml` marks 73 topic entries Draft and 4 Outline.

### Changed — 2026-11-27

- SLA page: a note records that NFR-7 was later extended to region loss (disaster recovery page).
- Cloud-native ecosystem page: a note records the later addition of Argo Rollouts as a sixth add-on.
- Landing-zone page: "application landing zones" renamed "workload landing zones", following
  Microsoft's October 2026 rename.
- Two TOGAF references now point to the public overview page; pubs.opengroup.org requires a sign-in.
- High-availability page: `domain` front matter aligned with the curriculum's domain title.

### Added — 2026-11-21, cloud, platform, and security batch (Phase 4A)

- Nineteen topic pages (Draft): network security, load balancing, and traffic flow; hybrid
  connectivity and VPNs; cloud service and deployment models; cloud building blocks and landing zones;
  compute options and sizing; multi-account strategy and infrastructure automation; cloud providers
  (principles before catalogs); containers and images; Kubernetes architecture and workloads;
  Kubernetes networking, storage, and service mesh; cloud-native ecosystem tools; and the whole
  security architecture domain (principles and threat modeling, identity and access management,
  network security, application security, data security and privacy, infrastructure and supply-chain
  security, security operations, compliance and regulatory frameworks).
- The first end-to-end case studies (Draft): 01 highly available three-tier web application, 08
  multi-account landing zone and hub-and-spoke network, 15 zero-trust application architecture.
- Design exercises (Draft): multi-account landing zone and zero-trust enterprise; the D29-T04 cloud and
  enterprise platform exercise collection (Outline) with briefs for all thirteen listed exercises.
- Labs 10 (REST API authentication and validation), 12 (local Kubernetes deployment), 14 (network
  segmentation), and 15 (infrastructure module and static checks), each with code, results, and a
  smoke test. Lab 12's cluster steps and the Docker parts of Labs 14 and D11-T01 were not executed by
  the author (no container runtime available); their pages say so.
- Glossary: 149 new terms in six sections (cloud foundations; containers and Kubernetes; network
  security and hybrid connectivity; security principles, identity, and data protection; security
  operations, supply chain, and compliance; deployment and data recovery), 402 terms in total.
- Navigation, learning paths, quiz index, labs and case-study indexes, curriculum index, README, and
  roadmap updated; `curriculum/coverage.yaml` marks 52 topic entries Draft and 4 Outline.

### Changed — 2026-11-21

- CI installs Terraform 1.15.6 (`hashicorp/setup-terraform` v4) so Lab 15's `fmt`, `validate`, and
  `test` checks run instead of being skipped. The module has no providers, so nothing is downloaded.
- `.gitignore` excludes Terraform and OpenTofu working directories and state files.
- Curriculum index: the "Written" column is now generated from `curriculum/coverage.yaml` for every
  domain (it had not been updated for D02-D04 in Phase 3).

### Fixed — 2026-11-21

- Six new diagrams that rendered as unreadable strips were re-laid out: two side-by-side stacks
  (hypervisors, containers versus VMs) now stack vertically, a zone figure stacks its nodes, and three
  organizational-unit trees run left to right.

- Networking fundamentals: the address-plan step claimed `10.10.0.0/12` could summarize all AtlasMart
  prod networks. A `/12` must start on a multiple of 16 in the second octet, so that prefix is really
  `10.0.0.0/12` and overlaps other workloads. The text now uses `10.10.0.0/15` for two prod regions and
  explains the boundary rule.

### Added — 2026-11-20, software and distributed architecture batch (Phase 3)

- Thirteen topic pages (Draft): computers, operating systems, and Linux; data structures and
  algorithms; programming paradigms and concurrency; software design principles and clean code;
  software testing types and strategies; architecture styles; microservices architecture; application
  design patterns; distributed system patterns; consistency models, CAP, and PACELC; transactions,
  sagas, and delivery guarantees; resilience mechanics (timeouts, retries, backpressure); scaling,
  partitioning, and replication.
- The twelve-step architecture design method (D30-T01 Draft, D30-T02 Outline).
- Design exercises (Draft): URL shortener, rate limiter, distributed cache, job scheduler; exercise
  collection pages for D29-T01 and D29-T02 (Outline) with briefs for every listed exercise.
- Labs 03 (queue retries and dead-letter queue), 04 (idempotency and duplicates), 05 (race
  condition), 08 (sharding and consistent hashing), and 09 (replication lag), each with code under
  `labs/local/`, sample results under `labs/solutions/`, and a smoke test under `tests/examples/`.
- Glossary, navigation, learning paths, labs and quiz indexes, curriculum index, README, and roadmap
  updated; `curriculum/coverage.yaml` marks 33 topic entries Draft and 3 Outline.

### Changed — 2026-11-20

- Repository history rewritten so every commit is authored and committed by `vinay9354`; content
  unchanged.
- CI checkout fetches full history so the gitleaks secret scan can resolve the pushed commit range.

### Fixed — 2026-11-20

- `tests/examples/__init__.py` added: lab smoke tests were never discovered by
  `python -m unittest discover -s tests`, so CI did not run them. Discovery now runs 49 tests.
- Two exercise-collection diagrams switched to left-to-right layout (they rendered as thin strips);
  the circuit breaker state diagram's overlapping labels shortened.

### Added — 2026-11-15, core learning path batch (Phase 2)

- Fifteen topic pages (Draft): stakeholders, business capabilities, and success metrics; constraints,
  assumptions, dependencies, risks, and scope; As-Is and To-Be architecture, gap analysis, and build
  vs buy; SLAs, SLOs, SLIs, error budgets, and recovery objectives; trade-offs, principles, ADRs, and
  architecture governance; networking fundamentals (IP, CIDR, routing, DNS); transport and
  application protocols; relational databases and SQL internals; caching architecture; message
  queues and brokers; API design (REST, GraphQL, gRPC, async); integration architecture; distributed
  systems fundamentals, time, and coordination; high availability design; performance fundamentals
  and Little's Law.
- Lab 01: measure latency and throughput for a simple HTTP service (`labs/local/lab-01-latency-and-throughput/`,
  standard-library Python server and closed-loop load generator), sample results under
  `labs/solutions/lab-01/`, smoke test `tests/examples/test_lab01.py`.
- Quiz: architecture fundamentals (D01), 15 questions in three levels.
- Glossary: new terms for networking, databases, caching, messaging, distributed systems,
  availability, and governance.
- Navigation, learning paths, quiz index, labs index, curriculum index, README, and roadmap updated;
  `curriculum/coverage.yaml` marks 19 topic entries Draft.

### Added — 2026-11-15, foundation batch

- Repository structure and documentation stack: MkDocs 1.6.1, Material 9.8.1, pinned in
  `requirements.txt`.
- Community and license files: `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `SECURITY.md`, `SUPPORT.md`, `LICENSE` (MIT), `LICENSE-DOCS.md` (CC BY 4.0),
  `THIRD_PARTY_NOTICES.md`, `ASSET_ATTRIBUTION.md`, `ROADMAP.md`, `MASTER_PROMPT.md`.
- CI: `docs-build.yml` (validation, tests, strict build, markdownlint, gitleaks), `link-check.yml`
  (weekly lychee), `pages.yml` (GitHub Pages deploy). Issue templates (content correction, new topic,
  broken link, lab bug, accessibility, security hardening) and a pull request template.
- Tooling: `scripts/validate-content.py`, `scripts/build-coverage.py`, `scripts/check-assets.py`,
  `scripts/build-local.sh`, `Makefile`, `tests/content/test_coverage.py`.
- Curriculum: `curriculum/coverage.yaml` with all 30 domains and 140 topic entries from the master
  inventory; generated coverage matrix; curriculum index; learning paths; glossary.
- 33 section landing pages, each with an injected topic table.
- Templates: topic, lab, case study, ADR. ADR-0001 to ADR-0006.
- Learning pages (Draft): What does a Solutions Architect do?; Functional vs non-functional
  requirements; Architecture quality attributes and trade-offs; The C4 model; Estimating load,
  throughput, storage, and capacity.
