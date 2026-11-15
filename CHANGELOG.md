# Changelog

All material changes to content and tooling, newest first. Technical corrections to published pages
name the page, the correction, and the source that prompted it.

Format follows the spirit of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
