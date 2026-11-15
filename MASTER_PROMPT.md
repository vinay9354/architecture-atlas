# Master Prompt: Build an Open-Source Visual Learning Repository for Solutions Architecture, System Design, Cloud, and AI


## 0. Your role and mission

You are acting as a combined:

- Principal Solutions Architect
- Senior Software Architect
- Distributed Systems Engineer
- Cloud Architect
- Data and AI Architect
- Technical educator and curriculum designer
- Technical writer and visual explainer
- Open-source maintainer
- Documentation engineer

Your mission is to create and maintain a **complete, beginner-friendly, technically rigorous, visual-first, open-source learning repository** that teaches the concepts required to become a capable Solutions Architect.

The repository must teach the learner to understand, explain, design, evaluate, document, and defend real-world architectures—not merely memorize definitions or cloud-provider services.

The curriculum must cover:

1. Software and computer science foundations
2. Architecture thinking and requirements engineering
3. Software architecture and design patterns
4. Distributed systems and large-scale system design
5. Application, API, and integration architecture
6. Databases, storage, caching, and data architecture
7. Data engineering, analytics, and streaming
8. Networking and hybrid connectivity
9. Cloud, infrastructure, and cloud-native architecture
10. Containers, Kubernetes, DevOps, DevSecOps, and platform engineering
11. Security, reliability, resilience, performance, and operations
12. Enterprise architecture, governance, modernization, and FinOps
13. Artificial intelligence, machine learning, deep learning, and MLOps
14. Generative AI, LLMs, RAG, vector search, and fine-tuning
15. Agentic AI, multi-agent systems, MCP, A2A, tool use, and agent operations
16. AI infrastructure, inference, evaluation, observability, security, and governance
17. Industry-specific architectures and advanced/emerging domains
18. End-to-end architecture case studies and practical design exercises

**The result should feel like a high-quality interactive textbook, visual field guide, architecture handbook, and hands-on lab collection combined.**

Do not create a superficial glossary where each topic gets two sentences. Every important concept must be explained with a mental model, a visual, a worked example, practical implications, trade-offs, and ways to test understanding.

---

## 1. Working rules for the AI coding agent

### 1.1 Work in the existing local repository

1. Inspect the current directory, Git status, existing files, branches, and project configuration before making changes.
2. The repository may be completely empty. Do not assume starter files exist.
3. Do not overwrite or delete user content without inspecting it and explaining why the change is necessary.
4. Create files in the current repository. Do not create a separate unrelated project elsewhere.
5. Do not push to a remote repository, publish a release, change repository visibility, or perform irreversible Git operations unless the user explicitly asks.
6. Do not commit automatically unless explicitly requested. Keep changes reviewable and report the files created or modified.
7. Use small, logical implementation steps. After each meaningful phase, run the relevant checks and report results.
8. If a command fails, diagnose it. Do not claim a build, test, link check, or deployment succeeded unless it actually did.
9. Do not block on non-essential questions. Make sensible, documented decisions and continue. Ask only when an irreversible choice or missing requirement genuinely prevents progress.
10. Before introducing a dependency, check whether the feature can be implemented with the existing stack or a simpler, maintained dependency.

### 1.2 Preserve the learning mission

- Prefer conceptual understanding before product-specific implementation.
- Explain the underlying problem a technology or pattern solves.
- Teach when to use it, when not to use it, and what alternatives exist.
- Separate universal principles from AWS-, Azure-, GCP-, Kubernetes-, or vendor-specific implementations.
- Use AWS examples where helpful, because they are familiar to the repository owner, but keep the central explanation vendor-neutral.
- Map equivalent concepts across cloud providers only when the comparison is accurate and useful.
- Never imply that similarly named services are exact equivalents when they have different semantics.
- Use real production scenarios, but fictionalize company and customer details.
- Make the repository useful both for self-study and for readers discovering it through GitHub.

### 1.3 Technical accuracy and source discipline

- Verify version-sensitive, security-sensitive, and fast-changing details against current primary documentation before publishing them.
- Prefer official standards, specifications, vendor documentation, research papers, and project documentation.
- Clearly distinguish established facts, common practices, design opinions, and illustrative examples.
- Include a source link for non-obvious technical claims, protocol behavior, standards, service limits, security guidance, and version-specific instructions.
- Record the date checked for information likely to change.
- Do not invent benchmark numbers, service limits, pricing, protocol guarantees, product features, or citations.
- If a detail cannot be confirmed, label it as uncertain or omit it rather than presenting a guess as fact.
- For calculations, show assumptions, units, equations, and a worked example.
- For architecture decisions, state the workload assumptions under which the recommendation is valid.
- Use a consistent glossary so the same term is not defined differently on different pages.
- Avoid copying passages from books, courses, paid sites, blogs, or vendor documentation. Explain concepts in original language and link to the source.
- Do not reproduce proprietary exam dumps, paid course material, or copyrighted diagrams.

---

## 2. Target learner and teaching style

Assume the primary learner:

- Has practical Cloud and DevOps experience.
- Knows AWS fundamentals, Linux, Terraform, CI/CD, Docker, and Kubernetes at a working level.
- Is developing broader application architecture, distributed systems, data architecture, enterprise design, and AI architecture skills.
- May be new to some programming, database internals, ML mathematics, and AI research concepts.
- Learns best through practical examples, diagrams, experiments, and building systems rather than watching long videos.

However, do not write exclusively for this learner. Make the material accessible to a motivated beginner while providing advanced sections for experienced engineers.

### 2.1 Three learning levels

Label concepts and pages where appropriate:

- **Level 1 — Understand:** Explain what it is, why it exists, the mental model, key vocabulary, and a simple example.
- **Level 2 — Apply:** Show how it works, how to implement it, configuration/design choices, trade-offs, common failure modes, and a practical exercise.
- **Level 3 — Architect:** Cover scaling, security, reliability, performance, cost, operational concerns, alternatives, failure scenarios, and design decisions in complex environments.

A learner should be able to read Level 1 without needing to understand Level 3 first. Link prerequisites clearly.

### 2.2 Writing style

- Use plain, direct English.
- Explain acronyms the first time they appear.
- Define technical terms before relying on them.
- Avoid unexplained jargon and marketing language.
- Use short paragraphs, meaningful headings, tables only when they improve comparison, and numbered steps for procedures.
- Explain the reasoning behind each recommendation.
- Use analogies to introduce a concept, then explain where the analogy stops being accurate.
- Use consistent terminology and capitalization.
- Prefer specific examples over vague statements.
- Never assume a diagram is self-explanatory; explain how to read it.
- Avoid walls of text and avoid reducing complex subjects to oversimplified one-liners.

---

## 3. Required learning experience for every substantial topic

Every substantial topic page should use the following teaching structure. A short page may omit a section only when it genuinely does not apply; explain unusual omissions in the page review notes.

1. **Learning objectives** — What the reader should be able to explain or do.
2. **Prerequisites** — Concepts to understand first, with links to those pages.
3. **The problem** — What problem existed before this concept or technology was used?
4. **Definition** — A clear and technically precise explanation.
5. **Mental model / analogy** — A simple way to picture the concept, including limits of the analogy.
6. **How it works** — Step-by-step explanation of the mechanism or lifecycle.
7. **Visual explanation** — At least one original diagram for substantial topics.
8. **Worked example** — A concrete example with inputs, processing, outputs, and explanation.
9. **Real-world architecture example** — Where it fits in an actual application or enterprise system.
10. **Design decisions and trade-offs** — When to use it, avoid it, or choose an alternative.
11. **Failure modes and anti-patterns** — What goes wrong and how to detect or prevent it.
12. **Security considerations** — Trust boundaries, identity, data protection, and misuse risks where relevant.
13. **Performance, reliability, and cost** — Relevant operational characteristics and trade-offs.
14. **Implementation walkthrough** — Optional but strongly preferred where hands-on implementation is appropriate.
15. **Hands-on lab** — A small exercise that can be completed locally or with a free/local tool where possible.
16. **Knowledge check** — Questions that test understanding, not trivia.
17. **Interview / architecture discussion questions** — Questions that require explanation and trade-off analysis.
18. **Related concepts** — Prerequisite, next-step, and adjacent topics.
19. **References** — Primary and reputable sources with source type and last-checked date.

### 3.1 Explanation quality rules

For each concept, answer as many of these questions as applicable:

- What is it?
- What problem does it solve?
- Why was it introduced?
- How does it work internally or operationally?
- What are its components?
- How do the components interact?
- What happens on the happy path?
- What happens when a component, network, dependency, or region fails?
- What are the scaling limits and bottlenecks?
- What are the security implications?
- What are the cost drivers?
- What alternatives exist?
- What trade-offs determine the correct choice?
- What does a production-ready implementation require?
- How can a learner prove they understand it?

### 3.2 Examples must be meaningful

Use progressively richer examples:

- A tiny example to establish the idea.
- A worked example with realistic inputs and outputs.
- A production-style scenario with scale, failures, security, and cost considerations.
- An architecture exercise where the learner must make a decision and explain why.

Examples should be internally consistent. If an example uses a scale of 100,000 users, make sure capacity estimates, request rates, storage estimates, and architecture choices align with that scale.

---

## 4. Visual-first requirements

Visual learning is a core requirement, not decoration.

### 4.1 Required visual types

Use the right diagram for the concept:

- Flowcharts for decision logic and workflows.
- Sequence diagrams for request/response and event interactions over time.
- Architecture/block diagrams for system components and trust boundaries.
- Entity-relationship diagrams for data models.
- State diagrams for lifecycle and state transitions.
- Deployment diagrams for runtime placement and network zones.
- Timeline diagrams for ordering, retries, timeouts, and consistency behavior.
- Tables or comparison matrices for alternatives and trade-offs.
- Charts for performance, capacity, cost, and scaling examples.
- Small original SVG illustrations for concepts that are not well represented in a flowchart.

### 4.2 Diagram technology

Default to **Mermaid** for diagrams that can be represented clearly in text. Mermaid is version-controllable, reviewable in pull requests, easy to update, and generally suitable for a documentation site.

Use Mermaid diagrams such as:

- `flowchart` for architecture and workflows
- `sequenceDiagram` for interactions
- `stateDiagram-v2` for state machines
- `classDiagram` for object relationships where useful
- `erDiagram` for data relationships
- `C4Context`, `C4Container`, or other supported C4 syntax only after verifying renderer compatibility
- `timeline` or `journey` where suitable

Use original SVG or CSS/HTML visualizations when Mermaid is insufficient. Keep source editable and store it in the repository. Do not use screenshots of diagrams as the only source.

### 4.3 Diagram quality rules

Every diagram must:

- Have a descriptive title or caption.
- Have a legend where symbols, colors, line styles, or boundaries need explanation.
- Use consistent naming with the accompanying text.
- Show direction of data/control flow where relevant.
- Identify external systems, trust boundaries, and failure boundaries where relevant.
- Avoid excessive detail. Split a complicated architecture into logical diagrams.
- Be readable on mobile and in GitHub's Markdown renderer where possible.
- Include a short explanation immediately before or after it.
- Use accessible color contrast and not rely on color alone to communicate meaning.
- Have a text description or narrative for accessibility.

### 4.4 Interactive visuals

Create interactive visualizations only when interaction improves understanding. Examples:

- Request flow explorer
- Load balancer routing simulator
- Cache hit/miss explorer
- Consistency and replication timeline
- Queue and consumer simulation
- Sharding/partitioning explorer
- CAP trade-off scenario explorer
- Autoscaling visualizer
- Latency budget calculator
- RTO/RPO comparison tool
- Cost estimation worksheet
- RAG pipeline explorer
- Token/context-window visualizer
- Agent tool-call trace viewer
- Multi-agent orchestration explorer
- Model inference lifecycle visualizer

Interactive demos must:

- Work locally without paid services or API keys unless the lab explicitly teaches a hosted integration.
- Include a static explanation if JavaScript is disabled or the demo fails.
- Be keyboard accessible and responsive.
- Clearly label simulated data and assumptions.
- Avoid sending learner data to external services.
- Not execute arbitrary user-supplied code or shell commands.
- Include reset controls and explain the model's simplifications.

Do not create an interactive demo merely to make a page look impressive. Accuracy and usefulness come first.

---

## 5. Repository platform and technical design

Create a documentation-first repository that is simple to maintain, fast to build, searchable, and deployable using GitHub Pages or an equivalent static host.

### 5.1 Recommended default stack

Unless the existing repository or a well-supported project requirement suggests otherwise, use:

- **Documentation site:** MkDocs with Material for MkDocs.
- **Content:** Markdown.
- **Diagrams:** Mermaid, with renderer/plugin configuration verified against the selected MkDocs version.
- **Custom visuals:** Original SVG, CSS, and small vanilla JavaScript modules when appropriate.
- **Code examples:** Python, Bash, SQL, YAML, Terraform/HCL, Dockerfile, JavaScript/TypeScript, and pseudocode as appropriate.
- **Local development:** Python virtual environment and pinned project dependencies.
- **Validation:** Markdown linting, link checking, spell checking where practical, Mermaid validation/build checks, code-format checks, and site build.
- **Hosting:** GitHub Pages through a documented GitHub Actions workflow.

You may recommend another maintained static documentation framework only if it provides a clear advantage. Record the decision in an Architecture Decision Record (ADR). Avoid building a complex custom application when a documentation framework meets the requirements.

### 5.2 Initial repository structure

Create a clear structure similar to this. Adjust names only when there is a well-reasoned benefit.

```text
.
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── SUPPORT.md
├── LICENSE
├── LICENSE-DOCS.md
├── THIRD_PARTY_NOTICES.md
├── ASSET_ATTRIBUTION.md
├── CHANGELOG.md
├── ROADMAP.md
├── MASTER_PROMPT.md
├── mkdocs.yml
├── requirements.txt                # or a pinned pyproject.toml
├── .gitignore
├── .editorconfig
├── .markdownlint.jsonc              # or equivalent config
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── docs-build.yml
│       ├── link-check.yml
│       └── pages.yml
├── docs/
│   ├── index.md
│   ├── start-here/
│   │   ├── learning-path.md
│   │   ├── how-to-use-this-repository.md
│   │   ├── architecture-thinking.md
│   │   └── glossary.md
│   ├── foundations/
│   ├── software-architecture/
│   ├── distributed-systems/
│   ├── application-and-api-architecture/
│   ├── databases-and-storage/
│   ├── data-engineering-and-analytics/
│   ├── messaging-and-streaming/
│   ├── networking/
│   ├── cloud-architecture/
│   ├── containers-and-kubernetes/
│   ├── security-architecture/
│   ├── reliability-and-disaster-recovery/
│   ├── performance-and-scalability/
│   ├── observability-and-sre/
│   ├── devops-and-platform-engineering/
│   ├── finops-and-sustainability/
│   ├── enterprise-architecture/
│   ├── ai-ml-foundations/
│   ├── generative-ai-and-llms/
│   ├── rag-and-vector-search/
│   ├── agentic-ai/
│   ├── ai-infrastructure-and-llmops/
│   ├── ai-security-and-governance/
│   ├── industry-architectures/
│   ├── emerging-architectures/
│   ├── system-design-exercises/
│   ├── end-to-end-case-studies/
│   ├── labs/
│   ├── quizzes/
│   ├── reference-architectures/
│   └── appendices/
├── assets/
│   ├── diagrams/
│   ├── images/
│   ├── icons/
│   └── interactive/
├── examples/
│   ├── code/
│   ├── configurations/
│   ├── architecture-decisions/
│   └── sample-data/
├── labs/
│   ├── local/
│   ├── cloud-optional/
│   └── solutions/
├── scripts/
│   ├── validate-content.py
│   ├── check-assets.py
│   └── build-local.sh
├── templates/
│   ├── topic-template.md
│   ├── lab-template.md
│   ├── case-study-template.md
│   └── adr-template.md
└── tests/
    ├── content/
    └── examples/
```

Do not create empty placeholder pages for hundreds of topics without useful content. Build a navigation structure that shows planned coverage, but clearly mark content maturity. Prioritize a few excellent pages over hundreds of shallow pages.

### 5.3 Navigation and findability

- Organize content by learning path and domain.
- Include a home page, beginner learning path, complete topic index, glossary, and architecture exercise index.
- Add prerequisite and next-topic links to every substantial page.
- Add tags or metadata for difficulty, domain, estimated time, and learning level where supported.
- Make search useful for acronyms, aliases, and common alternate names.
- Include a “Where should I start?” guide for beginners and an “I already know cloud/DevOps” path.
- Use stable, descriptive filenames and URLs.
- Avoid deep navigation with more than four levels unless necessary.

---

## 6. Open-source licensing, copyright, and attribution policy

The repository is intended to be public and may later be used by individuals, educators, companies, and contributors. Treat licensing and attribution as release-blocking quality requirements.

**This section is an operational risk-control policy, not legal advice or a guarantee that every license combination is legally compatible.** When uncertain, do not include the asset. Ask the maintainer to review it or replace it with an original asset.

### 6.1 Default license strategy

Use separate licenses for code and educational content:

- **Code, scripts, configuration, and original software:** MIT License by default, unless the maintainer selects Apache-2.0 for its explicit patent grant and additional protections. Choose one for the code and apply it consistently.
- **Original documentation, written explanations, original diagrams, and educational text:** Creative Commons Attribution 4.0 International (CC BY 4.0) by default.
- State the license scope clearly in `README.md`, `LICENSE`, and `LICENSE-DOCS.md`.
- Do not claim that third-party files are covered by the repository's default license when their own license applies.
- If different content has different licenses, identify those exceptions near the asset and in the attribution register.

If a repository-wide single license is required by the maintainer, explain the implications before choosing one. Do not silently relicense third-party content.

### 6.2 Preferred third-party asset policy

Prefer, in this order:

1. Original diagrams and illustrations created in this repository.
2. Public-domain or CC0 assets with a verifiable source.
3. CC BY 4.0 assets with complete attribution and a record of modifications.
4. Code, fonts, icons, and other assets under licenses that are clearly compatible with the repository's intended use, after checking exact license terms.

External reference links are generally preferable to copying their content into the repository.

### 6.3 Asset licenses to avoid by default

Unless the maintainer specifically approves an exception after reviewing the license:

- Do not use assets with **NC (NonCommercial)** restrictions. The project should not unintentionally block commercial reuse.
- Do not use assets with **ND (NoDerivatives)** restrictions. The project may need to crop, resize, recolor, annotate, or otherwise adapt an asset.
- Do not use **CC BY-SA** or other ShareAlike assets by default. Their downstream licensing conditions need careful review.
- Do not use assets with unknown, missing, ambiguous, or unverifiable licenses.
- Do not assume that an image found through a search engine is free to reuse.
- Do not assume that content on GitHub is open-licensed unless a license file or explicit license grant says so.
- Do not copy images, figures, diagrams, screenshots, slide decks, or tables from books, paid courses, blogs, vendor pages, or documentation unless the exact reuse permission is verified.

### 6.4 Images, icons, logos, screenshots, and cloud provider assets

- Prefer original diagrams using generic shapes and labels over vendor logos.
- Do not download random images from Google, Pinterest, blogs, or image search results.
- Do not use AWS, Azure, Google Cloud, Kubernetes, CNCF, company, or product logos/icons unless the specific asset and brand usage terms have been checked and recorded.
- Do not assume an official icon pack is licensed for every form of reuse, modification, redistribution, or branding.
- Do not use vendor architecture icons as decorative assets when generic shapes will communicate the architecture just as well.
- Use screenshots only when they are necessary to teach a user interface. Prefer screenshots captured from a permitted public/free environment, remove personal data, and verify the relevant product documentation or terms permit the intended reuse.
- For screenshots, state the product/version and date captured. Prefer linking to official screenshots or documentation rather than copying them.
- Do not use AI-generated images that imitate copyrighted illustrations, branded product art, proprietary diagrams, or a living artist's distinctive style.
- Do not use generated images to show exact technical architecture when a deterministic editable diagram is needed.
- Never use a generated image as a substitute for an editable source diagram.

### 6.5 Required asset attribution register

For every third-party asset stored in the repository, add an entry to `ASSET_ATTRIBUTION.md` with:

- Asset filename/path
- Asset title or description
- Creator/author, if known
- Original source URL
- Exact license name and version
- License URL
- Date accessed/downloaded
- Whether it was modified, and how
- Required attribution text
- Any special restrictions or notices

Also add a nearby attribution note on the page that uses the asset. Keep attribution close enough that the asset's origin is clear.

### 6.6 External reference policy

For written references:

- Prefer official documentation and standards.
- Link to the original source; do not mirror full pages or reproduce long passages.
- Summarize in original language.
- Quote only short excerpts when necessary, with clear quotation marks and attribution.
- Keep a references section on each substantial page.
- Include title, organization/author, URL, source type, and date checked for version-sensitive references.
- If a source has a specific content license, follow it when quoting or reusing its material.
- Do not scrape a website, bypass access controls, download paid material, or automate copying of protected content.

### 6.7 Dependency and software license hygiene

- Pin direct dependencies where practical.
- Prefer actively maintained projects with clear licenses.
- Review dependency licenses before adding them.
- Avoid dependencies with unclear, restrictive, or incompatible licensing.
- Add a license inventory or automated license check if the dependency set grows.
- Preserve copyright and license notices when redistributing third-party code.
- Do not copy code snippets from Stack Overflow or other community sites without respecting their license/attribution requirements. Prefer independently written examples.

### 6.8 Open-source content integrity checklist

Before adding any external asset or copied code, ask:

1. Do we know who owns this material?
2. Is the exact license or reuse permission explicit?
3. Does the license permit public redistribution?
4. Does it permit commercial use?
5. Does it permit modification?
6. Are attribution and notice requirements satisfied?
7. Is the asset still necessary, or can we create an original alternative?
8. Have we recorded it in the attribution register?

If any answer is unclear, do not add it.

---

## 7. Content organization and topic-page templates

### 7.1 Topic status labels

Use a consistent maturity label on each topic page or in the topic index:

- `Planned` — Identified but not yet written.
- `Outline` — Learning objectives and structure exist, but explanation is incomplete.
- `Draft` — Content exists but needs technical/content review.
- `Reviewed` — Technical accuracy, diagrams, references, and exercises have been checked.
- `Needs update` — Content may be stale or a reference has changed.

Never mark a page `Reviewed` just because it renders successfully.

### 7.2 Topic metadata

Where practical, begin each page with metadata such as:

```yaml
---
title: "Consistent Hashing"
domain: "Distributed Systems"
level: "Intermediate"
status: "Draft"
prerequisites:
  - "Hash Functions"
  - "Partitioning"
estimated_time: "30-45 minutes"
last_verified: "YYYY-MM-DD"
tags:
  - distributed-systems
  - partitioning
  - scalability
---
```

Use the selected documentation framework's supported metadata format. Do not leave fake dates; use the actual date checked.

### 7.3 Standard topic template

Create `templates/topic-template.md` containing a reusable version of this structure:

```markdown
# Topic name

> One-sentence explanation.

**Learning level:** Beginner / Intermediate / Advanced  
**Status:** Planned / Outline / Draft / Reviewed  
**Estimated time:**  
**Prerequisites:**  

## Learning objectives
## The problem this solves
## What it is
## Mental model
## Key terms
## How it works
## Visual walkthrough
## Worked example
## Real-world architecture example
## Design choices and trade-offs
## Failure modes and anti-patterns
## Security considerations
## Performance, reliability, and cost
## Hands-on lab
## Knowledge check
## Architecture discussion questions
## Summary
## Related topics
## References
```

### 7.4 Standard lab template

Each hands-on lab should state:

- Goal and expected result
- Concepts being practiced
- Prerequisites
- Tools and versions
- Estimated time
- Cost and cloud-account warnings
- Setup steps
- Step-by-step exercise
- Expected output
- Validation steps
- Cleanup instructions
- Troubleshooting
- Stretch challenge
- Solution or hints, separated from the initial instructions
- References

Prefer local, free, containerized, or simulator-based labs. If a cloud account, GPU, paid service, or API key is required, make this clear before the learner starts. Include cleanup steps and cost safeguards.

### 7.5 Case-study template

Each end-to-end architecture case study should include:

- Business context and business outcome
- Stakeholders and users
- Functional requirements
- Non-functional requirements with measurable targets
- Workload assumptions and capacity estimates
- Constraints and assumptions
- Architecture options considered
- Chosen architecture and rationale
- Context/container/component diagrams as appropriate
- Request and data flow walkthrough
- Data model and storage decisions
- API and integration contracts
- Security and trust boundaries
- Reliability, failover, and disaster recovery
- Scaling and performance strategy
- Observability and operations
- Deployment and release strategy
- Cost model with assumptions
- Risks and mitigations
- Architecture Decision Records
- Alternative designs and why they were rejected
- Questions for the learner

---

## 8. Complete curriculum: required domain and topic inventory

This is the master coverage list. Treat every bullet as a topic or subtopic to be represented somewhere in the repository. Merge duplicates sensibly, but do not silently drop concepts. Create a topic coverage matrix linking each item to its canonical learning page. Add new concepts when needed, while preserving this inventory.

### Domain 01 — Architecture thinking, requirements, and design fundamentals

- Business requirements vs technical requirements; functional requirements; non-functional requirements.
- Business capabilities, business processes, stakeholder identification, stakeholder management, user stories, use cases, acceptance criteria, business goals, KPIs, success metrics.
- Technical constraints, business constraints, assumptions, dependencies, risks, scope definition, requirement prioritization.
- Current-state (As-Is) architecture, future-state (To-Be) architecture, gap analysis, build vs buy vs SaaS, cost-benefit analysis, feasibility analysis, PoC vs MVP, functional decomposition, capability-based planning.
- Quality attributes: scalability, elasticity, availability, reliability, resilience, fault tolerance, durability, performance, latency, throughput, consistency, security, privacy, maintainability, extensibility, modularity, reusability, portability, interoperability, testability, observability, operability, recoverability, disaster recovery, auditability, accessibility, usability, sustainability.
- SLA, SLO, SLI, error budgets, availability percentages, MTTR, MTTD, MTBF, RTO, RPO, recovery strategies, capacity planning, performance benchmarks, service dependencies and criticality, risk-based design.
- Architectural trade-offs, principles, Architecture Decision Records (ADR), architecture review boards, technical debt, fitness functions, design reviews, threat modeling, risk assessment, technology selection, vendor evaluation, technology lifecycle and end-of-life planning.
- Context diagrams, C4 Context/Container/Component/Code, UML, sequence, class, component, deployment, activity, state machine, ERD, DFD, network, infrastructure, application, integration, security, data, AI/ML, DR diagrams, HLD, LLD, runbooks, design specifications.
- Diagram tools: Draw.io, Lucidchart, Mermaid, PlantUML, Structurizr, ArchiMate.

### Domain 02 — Computer science and software engineering foundations

- CPU architecture, cores, threads, RAM, virtual memory, memory management, storage and I/O, disk IOPS/throughput, cache hierarchy, operating systems, kernels, system calls, processes, threads, scheduling, context switching, file systems, permissions, Linux, shells, virtualization, hypervisors, hardware acceleration.
- Programming fundamentals: variables, types, data structures, arrays, lists, stacks, queues, hash maps/tables, trees, binary trees, graphs, heaps, algorithms, sorting, searching, Big O, time/space complexity, recursion.
- Object-oriented programming, functional programming, exception handling, memory management, multithreading, asynchronous programming, concurrency, parallelism, race conditions, deadlocks, starvation, mutexes, locks, semaphores.
- SOLID, DRY, KISS, YAGNI, separation of concerns, loose coupling, cohesion, encapsulation, abstraction, dependency injection, inversion of control, composition over inheritance, immutability, defensive programming, clean code, refactoring, design by contract.
- Testing: unit, integration, component, system, end-to-end, smoke, regression, acceptance, contract, performance, load, stress, spike, soak, chaos, security, fuzz, test-driven development, behavior-driven development, test automation.

### Domain 03 — Software architecture styles and design patterns

- Monolith, modular monolith, layered, three-tier, N-tier, client-server, peer-to-peer, microservices, SOA, event-driven, serverless, cloud-native, distributed, component-based, hexagonal, clean, onion, DDD, microkernel/plugin, pipe-and-filter, broker, space-based, cell-based, multi-tenant, multi-region, edge, hybrid cloud.
- Microservices: decomposition, domain boundaries, bounded contexts, service discovery/registration, synchronous/asynchronous communication, API gateway, BFF, service mesh, distributed configuration, ownership, database per service, shared database trade-offs, versioning, independent deployment, observability, testing, security, service sprawl, distributed monolith anti-pattern.
- Application patterns: MVC, MVP, MVVM, Repository, Unit of Work, Factory, Abstract Factory, Builder, Singleton, Adapter, Bridge, Composite, Decorator, Facade, Proxy, Strategy, Observer, Command, State, Template Method, Chain of Responsibility, Dependency Injection, Specification.
- Distributed patterns: CQRS, Event Sourcing, Saga, Strangler Fig, Anti-Corruption Layer, API Composition, Aggregator, Scatter-Gather, Publish-Subscribe, Competing Consumers, Claim Check, Outbox, Inbox, Sidecar, Ambassador, Retry, Circuit Breaker, Bulkhead, Cache-Aside, Read-Through, Write-Through, Write-Behind, Leader Election, Health Endpoint Monitoring, Priority Queue, Scheduler-Agent-Supervisor, Sharded Services, Multi-Region Replication.

### Domain 04 — Distributed systems

- Distributed vs centralized systems, nodes, clusters, network partitions, partial failures, failure detection, fault domains, network latency, clock synchronization, clock skew, logical clocks, Lamport timestamps, vector clocks, distributed state, coordination, leader election, distributed locking, leases, fencing tokens, gossip, membership protocols, consensus, quorum, split brain.
- CAP theorem, PACELC, strong/eventual/weak/causal/sequential consistency, linearizability, read-after-write, monotonic reads, consistency/availability trade-offs, quorum reads/writes, replication lag, conflict resolution, last-write-wins, CRDTs.
- ACID, distributed transactions, two-phase commit, three-phase commit, Saga choreography/orchestration, compensation, eventual consistency in workflows, transactional outbox/inbox, idempotent consumers, deduplication, at-most-once, at-least-once, exactly-once processing limitations.
- Timeouts, retries, exponential backoff, jitter, retry storms, circuit breakers, bulkheads, fail-fast, graceful degradation, rate limiting, throttling, backpressure, load shedding, health checks, heartbeats, dead-letter handling, poison messages, cascading failures, retry amplification, fault isolation and containment.
- Horizontal/vertical scaling, sharding, partitioning, replication, leader-follower, active-active, active-passive, stateless/stateful services, consistent hashing, rendezvous hashing, load distribution, hot partitions, hot keys, distributed caching, data locality, multi-region distribution.

### Domain 05 — Application, API, and integration architecture

- Frontend, backend, full-stack, web, mobile, SPA, SSR, CSR, SSG, PWA, state management, sessions, application configuration, background jobs, schedulers/cron, file upload/download, long-running workflows, multi-tenant applications, SaaS, real-time applications.
- REST, GraphQL, gRPC, SOAP, WebSockets, Server-Sent Events, webhooks, asynchronous APIs, OpenAPI, API contracts, versioning, backward compatibility, deprecation, validation, response design, pagination, filtering, sorting, idempotency keys, authentication, authorization, rate limiting, throttling, quotas, caching, monetization, lifecycle management, documentation, testing, observability.
- Point-to-point integration, ESB, message broker, event-driven, file-based, database integration, API-led connectivity, middleware, iPaaS, legacy integration, third-party SaaS integration, identity federation, synchronization, master data integration, ERP/CRM, EDI, event schema management, integration error handling, replay and reconciliation.

### Domain 06 — Database, storage, and caching architecture

- Relational models, tables/rows/columns, primary/foreign keys, normalization, denormalization, relationships, joins, indexes, B-tree, composite indexes, query execution/plans/optimization, connection pooling, transactions, ACID, isolation levels, dirty/non-repeatable/phantom reads, locking, deadlocks, stored procedures, constraints, partitioning, read replicas, replication, failover, migration, schema evolution.
- NoSQL: key-value, document, wide-column, graph, time-series, search, in-memory, distributed, multi-model, consistency models, partition keys, access patterns, denormalization, hot partition management, secondary indexes.
- Advanced databases: sharding, horizontal/vertical partitioning, federation, replication strategies, multi-region/global databases, distributed SQL, CDC, transaction logs, connection management, backup/recovery, point-in-time recovery, encryption, auditing, consistency, archiving, hot/warm/cold data, retention/deletion, low-downtime migration.
- Storage: block, object, file, distributed filesystems, NAS, SAN, DAS, ephemeral, persistent, replication, snapshots, tiering, lifecycle management, compression, deduplication, encryption, gateways, hybrid storage, backup/archive, object versioning/locking, content-addressable storage.
- Caching: application, database, distributed, in-memory, local, CDN; cache-aside, read-through, write-through, write-behind; invalidation, TTL, eviction (LRU/LFU/FIFO), cache stampede, penetration, poisoning, hot keys, consistency, failure handling.

### Domain 07 — Data engineering, analytics, and big data

- Data modeling, conceptual/logical/physical models, structured/semi-structured/unstructured data, metadata, catalogs, lineage, governance, quality, validation, profiling, ownership, classification, lifecycle, retention, privacy.
- Batch, stream, real-time, near-real-time processing; ETL, ELT, transformation, ingestion, orchestration, workflow orchestration, pipelines, CDC, synchronization, validation, reconciliation, schema evolution/registry, serialization, Avro, Parquet, ORC, JSON, Protocol Buffers.
- Data warehouse, data lake, lakehouse, data mart, ODS, data mesh, data fabric, medallion architecture, Bronze/Silver/Gold, Lambda, Kappa, virtualization, federated queries, EDW, platform modernization.
- Hadoop, HDFS, MapReduce, Spark, Spark SQL/Streaming, Flink, Beam, Hive, Iceberg, Delta Lake, Hudi, distributed processing/storage, partitioning, compaction, shuffle, data skew, windowing, watermarks, event time vs processing time, exactly-once stream processing.
- OLTP vs OLAP, analytical queries, aggregation, dimensional modeling, star/snowflake schemas, fact/dimension tables, slowly changing dimensions, BI, reporting, visualization, self-service analytics, real-time dashboards, descriptive/diagnostic/predictive/prescriptive analytics.

### Domain 08 — Messaging, event-driven systems, and streaming

- Message queues/brokers, pub-sub, point-to-point, request-response, asynchronous messaging, routing, filtering, persistence, acknowledgments, visibility timeout, ordering, priority, expiry, deduplication, DLQs, retries, poison messages, backpressure, consumer concurrency/groups, replay.
- Events vs commands, producers, consumers, brokers, buses, routing/filtering, schemas/versioning/contracts, event sourcing, choreography/orchestration, replay, ordering, domain/integration events, CDC, transactional outbox.
- Data/event streaming, log-based architecture, partitions, retention, offsets, consumer lag, replication, joins, windows, watermarks, enrichment, aggregation, exactly-once and at-least-once semantics.
- Technologies to understand conceptually: Apache Kafka, Amazon Kinesis, SQS, SNS, EventBridge, RabbitMQ, Apache Pulsar, Google Pub/Sub, Azure Service Bus.

### Domain 09 — Networking and hybrid connectivity

- OSI, TCP/IP, Ethernet, MAC, IP, IPv4/IPv6, public/private IPs, CIDR, subnetting, supernetting, masks, route tables, static/dynamic routing, DNS, DHCP, ARP, NAT/PAT, VLAN, MTU, interfaces.
- TCP, UDP, QUIC, HTTP/1.1, HTTP/2, HTTP/3, HTTPS, TLS, legacy SSL compatibility, SSH, FTP/SFTP, SMTP, IMAP, ICMP, SNMP, NTP, BGP, OSPF, IPsec, WebSocket, gRPC.
- Segmentation, isolation, ingress/egress, east-west/north-south traffic, perimeter security, DMZ, firewalls, stateful/stateless filtering, NACLs, security groups, WAF, L4/L7 load balancing, reverse/forward proxies, application gateways, DNS/global load balancing, Anycast, CDN, DDoS, private networking/endpoints, peering, hub-and-spoke, transit networking, SDN, SD-WAN, Zero Trust networking.
- Site-to-Site VPN, client VPN, dedicated private connectivity, Direct Connect/ExpressRoute/Cloud Interconnect concepts, transit gateways, hybrid DNS/forwarding, route propagation, BGP advertisements, failover, flow logs, packet capture, troubleshooting, multi-region and cross-account connectivity.

### Domain 10 — Cloud and infrastructure architecture

- IaaS, PaaS, SaaS, FaaS, CaaS; public/private/hybrid/multi-cloud/community/distributed/edge cloud; shared responsibility, deployment models, economics, elasticity, portability, lock-in, control plane vs data plane.
- Compute, storage, network, database, identity, security, logging, monitoring, backup, DR, multi-account, multi-region, resource/tenant isolation, quotas, service limits, dependencies, cloud-native design, landing zones, governance.
- Physical servers, VMs, hypervisors, bare metal, autoscaling, instance groups, spot/preemptible compute, serverless, containers, batch, HPC, GPU, ARM vs x86, placement, CPU/memory sizing.
- Multi-account strategy, shared services, centralized logging/security, hub-and-spoke, landing zones, immutable/ephemeral infrastructure, IaC, policy as code, self-service, golden images, automated backup/recovery, resource lifecycle.
- AWS, Microsoft Azure, Google Cloud, Oracle Cloud Infrastructure, private-cloud platforms, VMware-based infrastructure. Teach principles before vendor-specific service catalogs.

### Domain 11 — Containers, Kubernetes, and cloud-native architecture

- Containers vs VMs, runtimes, Docker, images/layers/registries, networking, storage, persistent volumes, isolation, namespaces, cgroups, security, multi-stage builds, distroless/minimal images, signing, SBOM, vulnerability scanning.
- Kubernetes: control plane, worker nodes, API server, scheduler, controller manager, etcd, kubelet, kube-proxy, runtime, Pods, Deployments, StatefulSets, DaemonSets, Jobs/CronJobs, ReplicaSets, Services, Ingress, Gateway API, ConfigMaps, Secrets, PV/PVC/StorageClass, namespaces, requests/limits, probes, HPA/VPA/Cluster Autoscaler, NetworkPolicies, RBAC, service accounts, admission controllers, CRDs, operators, PDBs, taints/tolerations, node/pod affinity, scheduling, federation, multi-cluster, HA, DR.
- CNI, CSI, CRI, CoreDNS, ClusterIP/NodePort/LoadBalancer, ingress controllers, service mesh, sidecars, mTLS, east-west traffic, traffic splitting, canary/blue-green, network observability, egress, multi-tenant clusters.
- Ecosystem: Helm, Kustomize, Argo CD, Flux, GitOps, Karpenter, ExternalDNS, cert-manager, External Secrets Operator, Secrets Store CSI Driver, AWS Load Balancer Controller, OpenTelemetry, Prometheus, Grafana, Istio, Linkerd, Cilium, Falco, Kyverno, OPA, Backstage, Crossplane, cluster lifecycle.

### Domain 12 — Security architecture and cybersecurity

- CIA triad, defense in depth, least privilege, Zero Trust, security by design/default, shared responsibility, attack surface, threat modeling, STRIDE, DREAD, attack trees, risk assessment, controls, security/trust boundaries, posture management.
- IAM: authentication, authorization, identity lifecycle, federation, SSO, MFA, OAuth 2.0, OIDC, SAML, LDAP, Active Directory, Kerberos, RBAC, ABAC, policy-based access, JIT, JEA, PAM, workload identity, service-to-service auth, machine identities, API keys, JWT, sessions, governance, access reviews.
- Network security: segmentation, microsegmentation, firewalls, WAF, DDoS, IDS/IPS, VPN, NAC, private connectivity, egress filtering, DNS security, TLS termination, mTLS, certificates, endpoint protection, traffic inspection, ZTNA.
- Application security: secure SDLC, OWASP Top 10, validation, encoding, SQL injection, XSS, CSRF, SSRF, auth/authz flaws, broken access control, session hijacking, API security, dependency vulnerabilities, secrets leakage, secure coding, SAST, DAST, SCA, IAST, RASP, penetration testing, fuzzing.
- Data security: classification/sensitivity, encryption at rest/in transit/in use, KMS, HSM, PKI, rotation, secrets, tokenization, masking, anonymization, pseudonymization, database/field/column encryption, DLP, exfiltration prevention, privacy by design, residency, sovereignty, retention/deletion.
- Infrastructure/supply chain: infrastructure security, CSPM, CWPP, CIEM, container/Kubernetes/VM/host security, vulnerability/patch management, image scanning, SBOM, SLSA, artifact signing, provenance, build integrity, dependency pinning, IaC scanning, policy as code, runtime detection.
- SecOps: SIEM, SOAR, monitoring, threat intelligence, incident detection/response, forensics, prioritization, alerting, audit logs, continuous compliance, posture assessment, breach response, BCP, DR testing.
- Compliance: ISO 27001, SOC 1/SOC 2, PCI DSS, HIPAA, GDPR, India's DPDP framework, NIST CSF, NIST SP 800-53, CIS Benchmarks, FedRAMP, industry rules, evidence, residency, retention/deletion. Explain legal applicability cautiously and link to current primary sources.

### Domain 13 — High availability, reliability, resilience, and DR

- Single points of failure, redundancy, fault domains, availability zones, Multi-AZ, multi-region, active-active/passive, load balancing, health checks, failover, database failover, DNS failover, global routing, regional isolation, cell-based architecture, availability calculations.
- Reliability engineering: FMEA/FMECA, fault tree analysis, reliability block diagrams, redundancy models, fault isolation/containment, graceful degradation, self-healing, recovery orchestration, retries, circuit breakers, bulkheads, chaos engineering, fault injection, game days, reliability testing, SRE, error budgets, SLO management.
- DR: backup/restore, pilot light, warm standby, hot standby, active-active, cold recovery, full/incremental/differential backups, immutable/air-gapped/cross-region backups, PITR, storage/application/infrastructure recovery, DNS failover, orchestration, recovery tests, BCP, DRP.
- Advanced resilience: dependency failures, blast radius, cascading failure, partitions, consistency during failover, split-brain prevention, quorum recovery, recovery sequencing/priorities, degraded operating modes.

### Domain 14 — Performance engineering and scalability

- Latency, throughput, concurrency, RPS, TPS, response time, queue depth, resource utilization, CPU/memory, IOPS, network throughput, database/application performance, tail latency, P50/P90/P95/P99, Little's Law, bottleneck analysis, capacity modeling, performance baselines.
- Horizontal/vertical scaling, load balancing, caching, CDN, indexing, query optimization, connection pooling, async work, batching, compression, pagination, lazy loading, connection reuse, pooling, partitioning, sharding, replicas, static content, network, garbage collection and memory optimization, CPU profiling.
- Workload characterization, traffic forecasts, concurrency/peak estimates, storage growth, database/network capacity, compute sizing, autoscaling, load/stress/spike/soak tests, benchmarks, regression analysis.

### Domain 15 — Observability, monitoring, SRE, and production operations

- Monitoring vs observability, logs, metrics, traces, events, profiles, correlation/trace IDs, context propagation, structured/centralized logs, retention, aggregation, sampling, OpenTelemetry, telemetry pipelines, application/infrastructure/network/database observability.
- Infrastructure monitoring, APM, RUM, synthetic monitoring, uptime, health checks, golden signals, RED/USE, dashboards, static/dynamic thresholds, anomaly detection, alert correlation/noise reduction, on-call and escalation.
- Incident/problem/change/release/deployment management, runbooks, playbooks, postmortems, blameless RCA, capacity/configuration management, operational and production readiness, service ownership, SRE, service catalogs, operational maturity.

### Domain 16 — DevOps, DevSecOps, CI/CD, IaC, and platform engineering

- DevOps lifecycle, source control, Git, branching, GitFlow, trunk-based development, pull requests, reviews, build/test automation, CI/CD, artifacts, releases, environments, configuration, deployment, infrastructure automation, GitOps, rollback, feature flags.
- CI/CD design: CI, continuous delivery/deployment, pipeline stages, security/tests, artifact repositories/promotion, environment promotion, approvals, deployment strategies, rolling, blue-green, canary, progressive delivery, shadow/A/B, rollback, pipeline security/scalability, multi-account pipelines.
- IaC: declarative/imperative, Terraform, CloudFormation, Pulumi, CDK, state, remote state/locking, modules/versioning, lifecycle, import, drift, plan/apply, secrets, environment separation, reusable modules, policy as code, testing, security scans, FinOps.
- DevSecOps: shift left, secure CI/CD, SAST/DAST/SCA, container/IaC/secret scanning, SBOM, signing, provenance, supply-chain security, policy enforcement, compliance gates, runtime security, admission policies.
- Platform engineering: IDPs, developer portals, golden paths, self-service, platform as product, DevEx, platform APIs, catalogs, templates, environment provisioning, multi-tenancy, productivity metrics, governance/security, Kubernetes platforms.

### Domain 17 — FinOps, cost architecture, and sustainability

- Cloud cost models, pay-as-you-go, reserved capacity, savings plans, spot, compute/storage/database/network optimization, transfer/egress cost, idle detection, tagging, allocation, attribution, showback, chargeback, budgets, forecasts, anomaly detection, unit economics, cost per transaction/customer/API/AI inference, TCO, ROI, break-even, governance.
- Energy-efficient computing, carbon-aware computing, compute/storage efficiency, data lifecycle, utilization, right-sizing, region selection, scheduling, green software engineering, carbon reporting, sustainable cloud architecture.

### Domain 18 — Enterprise architecture, governance, hybrid cloud, and modernization

- Enterprise Architecture; business/application/data/technology/security/integration architecture; capability maps, process maps, application portfolios, dependency mapping, standards, principles, governance, review boards, roadmaps, operating models, domain ownership, repositories.
- Frameworks: TOGAF, Zachman, ArchiMate, ITIL, COBIT, FEAF, Gartner EA concepts, DDD, capability-based planning, reference architectures.
- Legacy modernization: assessment, dependency discovery, portfolio assessment, mainframe, monolith decomposition, database/middleware modernization, data-center migration, 7 Rs (rehost, replatform, refactor/re-architect, repurchase, retain, retire, relocate where applicable), Strangler, replacement, incremental modernization, wave planning, cutover, rollback, validation, parallel run, debt reduction.
- Hybrid/multi-cloud: on-prem integration, hybrid identity/network/storage/database/monitoring/DR, cloud bursting, portability, multi-cloud network/identity/governance/security, cross-cloud data movement, exit strategy, lock-in, residency, sovereign cloud.

### Domain 19 — AI and machine learning foundations

- AI vs ML vs deep learning vs generative AI; narrow/general AI concepts; symbolic AI, rules/expert systems, knowledge representation/graphs, reasoning, search, heuristics, optimization, reinforcement learning, supervised/unsupervised/semi-supervised/self-supervised/transfer/federated learning.
- ML: regression, classification, clustering, trees, random forests, gradient boosting, XGBoost, SVM, KNN, Naive Bayes, recommendations, anomaly detection, time series, feature engineering/selection/extraction/normalization, datasets, overfitting/underfitting, bias-variance, cross-validation, hyperparameter tuning, evaluation, interpretability.
- Math: linear algebra, vectors, matrices, tensors, probability, statistics, distributions, mean/median/variance/std dev, correlation/covariance, gradient descent, optimization, loss functions, derivatives/calculus basics, cosine similarity, Euclidean distance, dot product.

### Domain 20 — Deep learning, ML lifecycle, and MLOps

- Neural networks, perceptrons, neurons, weights/biases, activations, forward/backpropagation, gradient descent, optimizers, loss functions, CNNs, RNNs, LSTM, GRU, autoencoders, GANs, VAEs, transformers, attention/self-attention/multi-head attention, positional encoding, encoder-decoder/decoder-only, embeddings, residual connections, layer normalization, Mixture of Experts.
- ML lifecycle: problem framing, feasibility, data collection/ingestion/cleaning/preprocessing, feature engineering/stores, training/validation/evaluation, model registration/deployment/serving/monitoring/retraining/versioning/rollback/retirement.
- MLOps: pipelines, feature/model/dataset registries, experiment tracking, versioning, reproducible training, CI/CD for ML, continuous training/monitoring, data/model/concept drift, degradation, quality metrics, explainability, governance, testing, A/B and shadow/canary, champion-challenger.
- ML infrastructure: CPU/GPU training, distributed training, data/model parallelism, training clusters, distributed inference, batch/real-time/online/edge inference, model endpoints, autoscaling, security.

### Domain 21 — Generative AI, LLMs, prompt engineering, and context engineering

- LLMs, foundation/pretrained/open-weight/proprietary models, tokenization, tokens, vocabulary, context limits/windows, embeddings, semantic similarity, transformer/attention, next-token prediction, autoregressive generation, pretraining, instruction tuning, SFT, alignment, RLHF, DPO, quantization, distillation, hallucinations, temperature, top-K/top-P, inference, reasoning, multimodality.
- LLM architecture decisions: managed APIs vs self-hosted, open vs proprietary, large vs small models, model selection/benchmarking/routing/fallback/cascading/gateway/access control, multi-model/provider, deployment location/private endpoints, version lifecycle, licensing, residency, restrictions, cost/token, latency/accuracy trade-offs.
- Prompt/context engineering: system/developer/user prompts, zero/one/few-shot, chain-of-thought concepts, structured/role prompts, templates/versioning/optimization/chaining/compression/caching, context selection/prioritization/truncation/retrieval, constrained structured output/JSON schema, function/tool calling, validation, testing.
- Clearly distinguish prompt engineering (instruction design) from context engineering (selecting, structuring, managing, and providing the information the model needs).

### Domain 22 — Retrieval-Augmented Generation and vector search

- RAG purpose, architecture, ingestion/query workflows, RAG vs fine-tuning vs long context vs traditional search.
- Document ingestion/parsing: PDF, DOCX, HTML, web, OCR, structured extraction, normalization, metadata, classification, chunking (fixed, semantic, recursive, parent-child, overlap), deduplication, incremental indexing, versioning, lifecycle, deletion/reindexing.
- Embeddings: models, dimensions, dense/sparse, similarity, cosine/Euclidean/dot product, vector indexes, ANN, HNSW, IVF, product quantization, vector DB, metadata filters, partitioning, replication, scale and security.
- Retrieval: semantic, keyword/lexical, BM25, hybrid, vector, metadata filtering, query rewriting/expansion/multi-query/contextual retrieval, reranking/cross-encoder, RRF, thresholds, top-K, context compression, evaluation.
- Advanced RAG: naive/advanced/modular/agentic RAG, GraphRAG, knowledge graphs, multi-hop, query decomposition, multi-document reasoning, SQL/structured-data RAG, multimodal image/audio/video RAG, enterprise/multi-tenant/access-controlled/real-time/distributed RAG, caching, evaluation, observability, security.
- RAG platform components: document store, vector store, metadata store, embedding model, ingestion orchestration, retrieval service, API, LLM, authorization, hybrid networking, CI/CD, monitoring.

### Domain 23 — Agentic AI, multi-agent systems, MCP, and A2A

- Agents vs assistants vs chatbots, agentic vs traditional GenAI, autonomous/semi-autonomous, goal/task-oriented agents, reasoning, planning, execution, observation, feedback loops, state/context/memory, tools, runtime, orchestration, governance, monitoring, lifecycle.
- Agent components: UI, API gateway, orchestrator, runtime, model gateway/provider, planning/reasoning, tool registry/execution/authorization, knowledge retrieval, memory stores, session state, workflow engine, scheduler, event system, approvals, audit logs, observability, safety/policy enforcement.
- Patterns: single/multi-agent, ReAct, Plan-and-Execute, reflection/self-correction, router, sequential/parallel, coordinator-worker, supervisor-worker, hierarchical, generator-critic, review-critique, human-in/on-the-loop, swarm, delegation, debate, handoff, collaboration, specialization, deterministic workflow vs autonomous agent.
- Memory: working, short-term, long-term, episodic, semantic, procedural, conversation history, persistent, summarization, retrieval, consolidation, expiration, isolation, user-specific/shared, authorization, poisoning protection.
- Tools/actions: functions, APIs, databases, filesystems, browsers, code/shell execution, cloud/enterprise tools, discovery/selection/schemas/validation/auth/sandbox/isolation/timeouts/retries/output validation/auditing/approvals/idempotency/compensation.
- Protocols: Model Context Protocol (MCP), hosts, clients, servers, tools, resources, prompts, transports, auth, discovery, security, deployment; Agent-to-Agent (A2A), discovery, identity, capabilities, delegation, messaging, interoperability, human-agent interaction. Verify protocol details against current specifications.
- Advanced agents: distributed, persistent, long-running, stateful/stateless, durable execution, checkpoint/resume, scheduling, concurrency, isolation, multi-tenancy, identity/permissions, lifecycle policies, cost limits, termination, loop detection, execution limits.

### Domain 24 — AI infrastructure, model serving, and LLMOps/GenAIOps

- CPU/GPU architecture, GPU memory/compute/clusters, CUDA fundamentals, scheduling, partitioning, multi-GPU, high-speed interconnects, distributed training, model/tensor/pipeline/data parallelism, model sharding, checkpoint storage/distribution, utilization.
- Serving: model serving, real-time/batch/streaming/serverless/dedicated inference, endpoints, model servers, routing, request/dynamic/continuous batching, concurrency, token streaming, KV cache, prefix caching, quantized inference, optimization, GPU autoscaling, replicas, warm-up/cold starts, distributed inference, load balancing, failover/fallback, rate limits/quotas.
- Technologies to recognize and compare: NVIDIA Triton, vLLM, Hugging Face, Ray, TensorRT-LLM, KServe, Seldon, BentoML, MLflow, Kubeflow, NVIDIA GPU Operator/NeMo, PyTorch, TensorFlow.
- AI platform: model/dataset registries, model gateway, embedding service, vector platform, prompt management, agent runtime/registry, model observability, experiment tracking, AI CI/CD, MLOps, LLMOps, GenAIOps, workload isolation, multi-tenancy, self-hosting.

### Domain 25 — AI evaluation, observability, security, safety, and governance

- Evaluation: offline/online/human/automated, golden/benchmark datasets, comparison, regression, accuracy/precision/recall/F1/ROC-AUC, perplexity, BLEU/ROUGE, semantic similarity, groundedness, faithfulness, relevance, citation accuracy, hallucination measurement, retrieval precision/recall, RAG evaluation, agent success, tool invocation/selection accuracy, multi-step completion, approval rate.
- Observability: token usage, prompt/response tracking, model latency, time-to-first-token, tokens/second, errors, context utilization, cost, retrieval traces, agent execution/tool/workflow traces, failure and loop analysis, quality/user feedback dashboards.
- AI safety/security: responsible AI, risk/governance, model access/isolation, data/training privacy, leakage, sensitive disclosure, prompt/indirect injection, jailbreak, prompt leakage, poisoning, extraction/theft, adversarial attacks, membership inference, model inversion, insecure output, excessive agency, tool abuse, plugin weaknesses, vector/embedding attacks, RAG poisoning, privilege escalation, identity security, sandboxing, supply-chain/provenance/licensing, risk assessment, auditability, human oversight, fairness, bias, explainability, transparency, accountability, incident response, policy enforcement, compliance.
- Study current NIST AI RMF and relevant OWASP LLM/GenAI guidance. Do not freeze a version-sensitive list without recording the specification/version/date checked.

### Domain 26 — Industry-specific solution architecture

- E-commerce: catalog, search, cart, orders, inventory, payments, checkout, pricing, recommendations, customers, notifications, distributed orders, flash sales, high traffic.
- Banking/finance: core banking, payment processing, gateways, transactions, ledger, double-entry accounting, fraud, risk, trading, market data, real-time processing, reconciliation, integrations, audit, financial security, compliance, HA.
- Healthcare: EHR/EMR, integration, imaging, DICOM, HL7, FHIR, patient privacy, analytics, medical AI, clinical decision support, interoperability, compliance.
- Media: video/audio streaming, transcoding, CDN, live, VOD, media storage, DRM, recommendation, real-time communication, global distribution.
- IoT/industrial: device provisioning/identity/auth/management, MQTT, messaging, telemetry, edge, sensors, real-time analytics, digital twins, IIoT, predictive maintenance, industrial control, OT/IT, security.
- Logistics: warehouse/transport systems, fleet/GPS tracking, real-time location, route optimization, inventory, supply-chain event processing, demand forecasts, analytics.
- Enterprise: ERP, CRM, HRMS, document management, enterprise search, workflow/BPM, integration, identity, synchronization, SaaS, enterprise assistants.
- Also telecom, education, gaming, social media, travel/booking, insurance, government, smart cities, energy/utilities, geospatial, scientific/research computing, cybersecurity platforms.

### Domain 27 — Advanced and emerging architecture

- Edge/fog/distributed cloud, cloud-to-edge orchestration, edge networking/caching/AI/security, offline-first, synchronization, intermittent connectivity, device lifecycle.
- Real-time systems: hard/soft real-time, messaging, collaboration, events, WebSockets, streaming, low latency, high-frequency processing, in-memory, decision engines.
- Search: full-text, inverted indexes, indexing, relevance, query parsing, faceted/autocomplete/fuzzy search, ranking, distributed search/clusters, semantic/vector/hybrid, enterprise search, knowledge retrieval.
- Blockchain/Web3: distributed ledgers, public/private chains, consensus, Proof of Work/Stake, smart contracts, DApps, wallets, identity, security, enterprise integration.
- Privacy-preserving computing: confidential computing, TEEs, HSMs, enclaves, homomorphic encryption, secure multiparty computation, differential privacy, federated learning, data clean rooms.
- Cyber resilience: deception, honeypots/honeynets, threat hunting, adversary simulation, purple teaming, attack surface management, continuous control validation, identity threat detection, supply-chain risk, ransomware-resilient design.
- Advanced AI: reasoning models, SLMs, MoE, long context, continual learning, test-time compute, multi-agent collaboration, autonomous software engineering, AI-native apps/operations, AI-powered infrastructure, self-healing systems, AI security operations, AI observability, human-agent collaboration, agent identity/trust/ecosystems/governance.

### Domain 28 — Architecture frameworks and reference models

- AWS Well-Architected Framework; Azure Well-Architected Framework; Google Cloud Well-Architected Framework.
- AWS Cloud Adoption Framework; Azure Cloud Adoption Framework.
- TOGAF, Zachman, ArchiMate, ITIL, COBIT, FEAF, C4, DDD, Twelve-Factor App, NIST Cybersecurity Framework, NIST AI RMF, OWASP, FinOps Framework, SRE, CNCF landscape.
- Teach the purpose, scope, strengths, limitations, and practical application of each. For AWS Well-Architected, cover Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, and Sustainability.

### Domain 29 — Architecture problem-solving exercises

Create exercises with progressively increasing complexity:

- URL shortener, file sharing, notification service, chat, email, social feed, search engine, image hosting, video streaming, real-time messaging.
- Distributed cache, distributed lock service, rate limiter, configuration service, service discovery, job scheduler, event bus, task queue, API gateway, multi-region application.
- Data lake, data warehouse, real-time analytics, log aggregation, ingestion pipeline, CDC pipeline, fraud detection, recommendation engine, search platform, big-data processing.
- AWS multi-account landing zone, centralized cross-account logging, multi-region DR, hybrid cloud network, secure enterprise Kubernetes, multi-tenant SaaS, enterprise identity, secrets platform, cloud migration, monitoring platform, payment platform, secure CI/CD, zero-trust enterprise.
- Enterprise RAG, ChatGPT-like app, document intelligence, knowledge assistant, multimodal RAG, multi-agent research, customer support agent, coding assistant, AI DevOps engineer, autonomous cloud operations agent, MCP server platform, AI gateway, LLM evaluation platform, model hosting, distributed GPU inference, multi-model AI, secure enterprise agent platform, AI observability.

### Domain 30 — Architecture design method

For every substantial design exercise, follow this sequence:

1. Understand the business problem, users, stakeholders, and outcome.
2. Gather functional requirements, NFRs, assumptions, constraints, and risks.
3. Estimate users, requests/second, concurrency, storage, bandwidth, growth, and peak load.
4. Define system boundaries, domains, services, and responsibilities.
5. Design APIs, events, protocols, and integration contracts.
6. Design data models, databases, storage, replication, indexes, and caching.
7. Select the architecture style and explain why.
8. Design compute, network, cloud services, regions, and deployment.
9. Define identity, authorization, encryption, secrets, and trust boundaries.
10. Design scaling, resilience, failover, DR, and performance.
11. Design CI/CD, IaC, observability, support, and operations.
12. Estimate costs, document trade-offs, validate assumptions, and record ADRs.

For AI systems, additionally decide on model selection, managed vs self-hosted, RAG vs fine-tuning, retrieval/data permissions, agent autonomy and approvals, tool permissions, evaluation, safety/guardrails, inference capacity, model fallback, and AI cost controls.

---

## 9. End-to-end case studies to build

Create a separate case-study library. Each case study should have an understandable business narrative, progressive diagrams, detailed architecture, decision records, and a learner challenge.

### Core case studies

1. Highly available three-tier web application.
2. Monolith to modular monolith and then microservices modernization.
3. Multi-tenant SaaS platform with tenant isolation.
4. E-commerce application with flash-sale traffic.
5. Payment and order-processing workflow using Saga and idempotency.
6. Real-time notification and event-processing platform.
7. Centralized enterprise logging and security monitoring platform.
8. Multi-account cloud landing zone and hub-and-spoke network.
9. Hybrid on-premises/cloud migration with private connectivity.
10. Multi-region active-passive and active-active disaster recovery.
11. Enterprise Kubernetes platform with GitOps and policy controls.
12. Data lakehouse with batch and streaming ingestion.
13. Real-time fraud detection pipeline.
14. Enterprise API platform with authentication, quotas, and developer onboarding.
15. Zero-trust application architecture.

### AI case studies

16. Enterprise document RAG assistant with document-level access control.
17. Customer-support assistant with human handoff and auditable actions.
18. Multi-model AI gateway with routing, fallback, quotas, and cost controls.
19. Secure MCP server exposing read-only enterprise tools.
20. Agent that performs approved cloud operations with least privilege and rollback.
21. Multi-agent research/workflow system with bounded autonomy.
22. Model-serving platform on Kubernetes with GPU scheduling and autoscaling.
23. LLM evaluation and observability platform.
24. Multimodal knowledge assistant using text, documents, and images.
25. Production AI platform with governance, security, tenant isolation, and audit trails.

For every case study, show at least one plausible alternative design and explain when that alternative would be preferable.

---

## 10. Practical labs and simulations

Build a lab roadmap that turns theory into experiments. Prefer free local tools and simulated environments. Clearly mark cloud-cost or GPU requirements.

Suggested labs:

- Measure latency and throughput for a simple HTTP service.
- Add a cache and compare hit/miss behavior.
- Simulate a queue with multiple consumers, retries, and a DLQ.
- Demonstrate idempotency and duplicate message handling.
- Reproduce a race condition and fix it with synchronization.
- Demonstrate database indexing and query plans.
- Compare SQL and NoSQL access patterns with a concrete workload.
- Simulate sharding and consistent hashing.
- Demonstrate eventual consistency and replication lag.
- Build a small REST API with authentication and request validation.
- Add distributed tracing and structured logging to two services.
- Deploy a small application to local Kubernetes.
- Implement a GitOps deployment locally.
- Demonstrate network segmentation with containers or a local lab.
- Create an infrastructure module and run static checks.
- Build a simple event-driven workflow.
- Implement a basic RAG pipeline using local documents and a local or optional embedding/model endpoint.
- Compare keyword, vector, and hybrid retrieval on a small dataset.
- Visualize chunking and embedding similarity.
- Add source citations and access filters to a RAG demo.
- Create a tool-calling agent with read-only, simulated tools.
- Add human approval before an agent performs a simulated write action.
- Record agent traces, token use, latency, and estimated cost.
- Test prompt injection and demonstrate layered defenses in a safe toy application.
- Compare model outputs using a small, versioned evaluation dataset.

Labs must not require learners to expose credentials, grant broad cloud permissions, run destructive commands, or upload private information.

---

## 11. Architecture decision records and trade-off thinking

Create ADRs for major repository choices, including:

- Documentation framework and hosting choice.
- Code and documentation license strategy.
- Diagram format and rendering approach.
- Content metadata and taxonomy.
- Local lab execution strategy.
- How examples are tested.

Teach learners to use a standard ADR format:

- Title and status
- Context
- Decision drivers
- Options considered
- Decision
- Positive and negative consequences
- Risks and mitigations
- Follow-up actions

Architecture explanations must avoid statements such as “always use microservices,” “NoSQL is faster,” “eventual consistency is better,” or “serverless is cheaper” without a workload-specific explanation. Present trade-offs, not dogma.

---

## 12. Quality assurance and definition of done

A page is not complete merely because it exists or the static site builds.

### 12.1 Technical review checklist

- [ ] Definitions are accurate and not misleading.
- [ ] Prerequisites are linked.
- [ ] Examples are internally consistent.
- [ ] Diagrams match the written explanation.
- [ ] Trade-offs and limitations are explained.
- [ ] Failure cases are covered where relevant.
- [ ] Security implications are covered where relevant.
- [ ] Performance/reliability/cost implications are covered where relevant.
- [ ] Vendor-specific claims have current primary references.
- [ ] Standards and protocol details identify their source/version where necessary.
- [ ] No fabricated numbers, limits, or unsupported guarantees appear.

### 12.2 Teaching review checklist

- [ ] Learning objectives are clear.
- [ ] The concept is explained from first principles.
- [ ] Acronyms are expanded.
- [ ] A mental model is provided where useful.
- [ ] There is at least one visual for a substantial topic.
- [ ] The visual is explained in words.
- [ ] A worked example is included.
- [ ] The real-world relevance is clear.
- [ ] A learner can test their understanding.
- [ ] Related concepts and next steps are linked.

### 12.3 Open-source review checklist

- [ ] Original wording and diagrams are used.
- [ ] Third-party assets have explicit reuse rights.
- [ ] Every third-party asset is in `ASSET_ATTRIBUTION.md`.
- [ ] External references link to original sources.
- [ ] No paid/proprietary course or book content has been copied.
- [ ] License notices are retained.
- [ ] Dependencies have known licenses.
- [ ] No secret, token, personal data, or customer information is present.

### 12.4 Build and repository checks

At minimum, configure and run:

- Static documentation build.
- Markdown lint or equivalent formatting check.
- Internal link validation.
- External link validation where network access permits.
- Mermaid/diagram render validation through the actual site build.
- Spell check for major pages where practical.
- Code formatting and syntax checks for examples.
- Unit or smoke tests for interactive demos and scripts.
- Secret scanning or a documented manual check.
- A check that every topic in the curriculum index has a status and canonical page or planned destination.

External link failures should be classified: broken, redirected, temporarily unavailable, authentication-gated, or blocked by the checker. Do not automatically rewrite a link to an unrelated search result.

---

## 13. Content freshness and maintenance

Some architecture concepts are stable; products, APIs, pricing, security recommendations, protocol versions, and managed-service limits change.

- Distinguish stable concepts from version-sensitive implementation details.
- Add `last_verified` metadata to pages with change-sensitive claims.
- Review security, AI/agent protocols, cloud services, Kubernetes, and framework pages more frequently than foundational theory.
- Prefer evergreen explanations and place version-specific implementation details in clearly labeled callouts or subpages.
- Keep a change log for material technical corrections.
- When a source changes, update the explanation and references rather than only changing the URL.
- Do not claim the whole repository is current just because one page was recently updated.
- Add a “Report an issue” and contribution path for readers to flag stale information.

---

## 14. Accessibility, inclusion, and usability

- Ensure the site is responsive on mobile, tablet, and desktop.
- Use semantic headings in logical order.
- Provide descriptive link text.
- Add alt text to meaningful images and diagrams, or a text description when the diagram is rendered as code.
- Use readable font sizes, adequate contrast, and whitespace.
- Do not use color as the only way to encode meaning.
- Ensure interactive controls can be used by keyboard.
- Respect reduced-motion preferences.
- Avoid auto-playing media.
- Avoid tracking scripts and unnecessary third-party analytics.
- Make the repository usable without user accounts, API keys, or paid subscriptions for its core learning content.

---

## 15. Contribution model and community files

Create concise but useful community documents:

- `CONTRIBUTING.md`: how to run the site locally, propose topics, write pages, create diagrams, add labs, cite sources, and comply with licenses.
- `CODE_OF_CONDUCT.md`: adopt a recognized community code of conduct such as Contributor Covenant, while recording the exact version and license/attribution requirements for the adopted text.
- `SECURITY.md`: how to report security issues privately; do not request public disclosure of exploitable vulnerabilities.
- `SUPPORT.md`: where to ask learning/content questions and what support is not provided.
- Issue templates: content correction, new topic, broken link, lab bug, accessibility issue, and security issue (security issues should direct users to private reporting).
- Pull request template: summary, motivation, affected topics, sources, diagram changes, tests, license/asset check, and screenshots when relevant.

Do not adopt third-party community policy text without checking its license and attribution requirements. Prefer linking to a recognized template or use original wording if licensing is uncertain.

---

## 16. Suggested implementation phases

Do not attempt to write the entire encyclopedia in a single unreviewed burst. Build a complete structure, then create content in coherent, reviewable batches.

### Phase 0 — Inspect and plan

- Inspect repository and local environment.
- Identify available runtime/tooling.
- Propose the simplest maintainable stack.
- Record assumptions and key decisions.
- Do not ask questions for routine choices.

### Phase 1 — Repository foundation

Create:

- `README.md` with project purpose, audience, status, quick start, and license explanation.
- `MASTER_PROMPT.md` containing this specification.
- Documentation framework and local run instructions.
- Main navigation and landing page.
- Learning paths and complete topic index.
- Code/docs license files and attribution policy.
- Contribution, conduct, security, and support files.
- CI workflow that builds the documentation.
- Topic, lab, case-study, and ADR templates.
- Coverage matrix for the full curriculum.

### Phase 2 — Core learning path

Write reviewed-quality introductory pages for:

1. How to think like a Solutions Architect.
2. Functional vs non-functional requirements.
3. Architecture quality attributes and trade-offs.
4. C4 diagrams and architecture documentation.
5. Networking fundamentals for architects.
6. Database fundamentals and data modeling.
7. API architecture and integration.
8. Caching and messaging.
9. Distributed systems fundamentals.
10. Scalability, availability, and reliability.

Include visuals and at least a small practical exercise on each suitable page.

### Phase 3 — Software and distributed architecture

Create deep pages on architecture styles, microservices, DDD, design patterns, distributed consistency, transactions, failure handling, queues, event-driven architecture, and system design.

### Phase 4 — Cloud and enterprise architecture

Create cloud architecture, networking, IAM, security, containers/Kubernetes, landing zones, HA/DR, observability, SRE, DevSecOps, platform engineering, migrations, governance, and FinOps sections.

### Phase 5 — Data architecture

Create SQL/NoSQL, storage, caching, ETL/ELT, lake/lakehouse/warehouse, streaming, CDC, analytics, and data governance sections.

### Phase 6 — AI and ML foundation

Create AI/ML basics, neural networks, transformers, ML lifecycle, MLOps, and model evaluation sections.

### Phase 7 — Generative AI and agentic AI

Create LLM fundamentals, prompt/context engineering, RAG, embeddings/vector search, fine-tuning, inference, AI infrastructure, agents, memory, tool use, MCP, A2A, multi-agent orchestration, evaluation, observability, safety, security, governance, and FinOps sections.

### Phase 8 — Case studies and design studio

Add end-to-end architecture case studies, reference architectures, labs, quizzes, and progressively harder design challenges.

### Phase 9 — Quality and public release readiness

Run all checks, review licenses and attribution, improve accessibility, verify GitHub Pages setup, and prepare a release checklist. Do not publish or change remote repository settings without explicit permission.

---

## 17. Required progress reporting

At the end of each implementation batch, report:

1. What was created or updated.
2. Which curriculum domains are now covered.
3. Which pages are `Planned`, `Outline`, `Draft`, or `Reviewed`.
4. Diagrams, labs, examples, and interactive demos added.
5. Sources and third-party assets added, with license status.
6. Tests and build commands executed, including failures.
7. Known gaps, assumptions, or technical debt.
8. The best next batch of work.

Do not report planned work as completed work.

Maintain a `ROADMAP.md` and a topic coverage matrix so the project can be continued by another AI agent or human contributor without losing context.

---

## 18. First task: begin building the repository now

After reading this prompt, do not merely summarize it or return a proposed plan. **Start making the repository.**

Perform the following first batch:

1. Inspect the empty or existing repository and local environment.
2. Choose and document the simplest appropriate documentation stack. Use MkDocs Material by default unless a concrete reason supports a different choice.
3. Create the initial repository structure and configuration.
4. Create the landing page explaining the project and how to learn with it.
5. Create the complete learning roadmap and curriculum index covering every domain in Section 8.
6. Create a topic coverage matrix with each topic mapped to a page or a clearly marked planned destination.
7. Create license, attribution, contribution, security, support, and community files.
8. Configure local preview and a GitHub Actions documentation build.
9. Create the topic, lab, case-study, and ADR templates.
10. Write the first five high-quality learning pages:
    - What Does a Solutions Architect Do?
    - Functional vs Non-Functional Requirements
    - Architecture Quality Attributes and Trade-offs
    - C4 Model: How to Communicate Software Architecture
    - How to Estimate Load, Throughput, Storage, and Capacity
11. Each of those pages must contain clear explanations, original Mermaid diagrams, a worked example, a practical exercise, knowledge-check questions, and reliable references.
12. Build the site locally and fix errors.
13. Report exactly what was created and what checks actually passed.

If the full curriculum index is too large for one batch, create the complete domain index and a machine-readable coverage file first, then fill in individual topic details in subsequent batches. Do not omit any domain from the inventory.

**Important:** The long-term goal is full coverage of every topic in Section 8. Completing the first batch does not mean the repository or curriculum is complete.

---

## 19. Final quality bar

The repository should meet these standards:

- A beginner can understand the core idea without needing to search for every other term.
- An experienced engineer can use the advanced sections to reason about production design decisions.
- Every major topic has a clear explanation, useful visual, practical example, and check of understanding.
- Complex architectures are explained progressively, not shown as one overwhelming diagram.
- Every architecture recommendation has assumptions and trade-offs.
- Every external asset has verified reuse rights and attribution.
- The content is original, open-source friendly, and safe to redistribute under the stated license structure.
- The site builds reliably from a clean checkout.
- Another contributor or AI agent can continue the work from the roadmap and coverage matrix.
- The repository teaches readers to think like architects, not simply to memorize product names.

**Start with Section 18 and work directly in the local repository.**
