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

## Phase 2 — Core learning path 🔄

| # | Page | Status |
|---|---|---|
| 1 | What does a Solutions Architect do? | ✅ Draft |
| 2 | Functional vs non-functional requirements | ✅ Draft |
| 3 | Architecture quality attributes and trade-offs | ✅ Draft |
| 4 | C4 model and architecture documentation | ✅ Draft |
| 5 | Estimate load, throughput, storage, and capacity | ✅ Draft |
| 6 | Networking fundamentals for architects (D09-T01, T02) | ⬜ |
| 7 | Database fundamentals and data modeling (D06-T01) | ⬜ |
| 8 | API architecture and integration (D05-T02, T03) | ⬜ |
| 9 | Caching and messaging (D06-T05, D08-T01) | ⬜ |
| 10 | Distributed systems fundamentals (D04-T01) | ⬜ |
| 11 | Scalability, availability, and reliability (D13-T01, D14-T01) | ⬜ |
| 12 | SLAs, SLOs, SLIs, error budgets (D01-T06) | ⬜ |
| 13 | ADRs and architecture governance (D01-T07) | ⬜ |
| 14 | Stakeholders, capabilities, success metrics (D01-T02); constraints and scope (D01-T03); As-Is/To-Be and build vs buy (D01-T04) | ⬜ |
| 15 | Second-person review of pages 1-5 → promote to Reviewed | ⬜ |

Also in this phase: Lab 01 (latency and throughput) as the reference lab; glossary growth; first
domain quiz for D01.

## Phase 3 — Software and distributed architecture ⬜

D03 (styles, microservices, application patterns, distributed patterns), D04 (consistency,
transactions and sagas, resilience mechanics, scaling and partitioning), D02 (foundations).
Labs 03-05, 08, 09. Design exercises: URL shortener, rate limiter, distributed cache, job scheduler.

## Phase 4 — Cloud and enterprise architecture ⬜

D09, D10, D11, D12, D13, D15, D16, D17, D18, D28 (Well-Architected and adoption frameworks).
Labs 10-15. Case studies 01, 08, 09, 10, 11, 15. Exercises: landing zone, multi-region, zero trust.

## Phase 5 — Data architecture ⬜

D06 (remaining), D07, D08. Labs 02, 06, 07, 16. Case studies 12, 13. Exercises: data lake, CDC
pipeline, real-time analytics.

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
- Release checklist; enable Pages; announce. No remote changes without maintainer approval.

## Known gaps and technical debt (as of 2026-11-15)

- Mermaid syntax is only type-checked by the validator; rendering was verified manually in a browser
  for the five pages. CI does not render diagrams.
- Page `status` is recorded in both front matter and `coverage.yaml`; no automated cross-check yet.
- `docs/appendices/tags.md` depends on the Material tags plugin's index marker; verify after theme upgrades.
- External link checking runs weekly, not on pull requests, to avoid flaky failures. On 2026-11-15 all
  39 reference URLs were checked: 38 resolve; the Little's Law DOI link returns 403 to automated
  clients (publisher bot-blocking, classified as "blocked by the checker", not broken).
- The Contributor Covenant is adopted by reference with original wording; if its full text is adopted
  later, its CC BY 4.0 attribution must be added.
- No interactive demos yet.
