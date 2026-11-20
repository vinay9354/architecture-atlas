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

## Phase 3 — Software and distributed architecture 🔄 (written 2026-11-20)

| Area | Pages | Status |
|---|---|---|
| D02 foundations | Computers, OS, and Linux (T01); data structures and algorithms (T02); paradigms and concurrency (T03); design principles and clean code (T04); testing types and strategies (T05) | Draft |
| D03 software architecture | Architecture styles (T01); microservices (T02); application design patterns (T03); distributed system patterns (T04) | Draft |
| D04 distributed systems | Consistency, CAP, and PACELC (T02); transactions, sagas, and delivery guarantees (T03); resilience mechanics (T04); scaling, partitioning, and replication (T05) | Draft |
| D30 design method | The twelve-step architecture design method (T01); AI design decisions at definition depth (T02) | Draft / Outline |
| D29 exercises | URL shortener, rate limiter, distributed cache, job scheduler (full); application and infrastructure exercise collections with briefs for the rest | Draft / Outline |
| Labs | 03 queue retries and DLQ; 04 idempotency; 05 race condition; 08 sharding and consistent hashing; 09 replication lag, each with a CI smoke test | Draft |

The design method page was scheduled for Phase 8; it moved here because the exercises are built on it.

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
- Second-person review of every Draft page; promote to `Reviewed` only after that review (carried from Phase 2).
- Release checklist; enable Pages; announce. No remote changes without maintainer approval.

## Known gaps and technical debt (as of 2026-11-20)

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
