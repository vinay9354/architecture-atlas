---
title: Architecture Atlas
description: "A free, visual-first learning repository for Solutions Architecture, system design, cloud, data, and AI architecture."
hide:
  - navigation
---

# Architecture Atlas

**A free, open-source, visual-first guide to thinking like a Solutions Architect.**
Concepts first, vendors second; diagrams on every substantial page; trade-offs instead of dogma.

!!! info "Project status: data architecture complete (November 2026)"
    The structure, curriculum index, and tooling are complete. **Eighty-three topic pages, sixteen labs,
    ten design exercises, eight end-to-end case studies, and one domain quiz are written (Draft).**
    The remaining topics are indexed with planned destinations in the
    [coverage matrix](appendices/coverage-matrix.md). Pages carry an honest status; nothing here is
    marked "Reviewed" until a second person has checked it.

## What this is

A curriculum that takes you from "what does an architect actually do?" to designing, defending, and
operating real systems: distributed systems, APIs, databases, cloud platforms, Kubernetes, security,
reliability, data platforms, and the full AI stack from machine learning basics to RAG, agents, MCP,
and model serving. Thirty domains, one coherent glossary, one design method used throughout.

It is written for someone with working cloud and DevOps experience who wants to grow into broader
architecture, and it stays readable for a motivated beginner. Advanced sections are marked so you can
skip them the first time through.

## How to learn with it

<div class="grid cards" markdown>

-   :material-compass-outline: **Start here**

    ---

    New to architecture? Take the beginner path. Already run cloud infrastructure? Take the
    "I know cloud/DevOps" path.

    [:octicons-arrow-right-24: Learning paths](start-here/learning-path.md)

-   :material-book-open-page-variant-outline: **Read a page end to end**

    ---

    Every substantial page has objectives, a mental model, a diagram, a worked example, trade-offs,
    failure modes, a small exercise, and a knowledge check.

    [:octicons-arrow-right-24: What does a Solutions Architect do?](architecture-fundamentals/what-does-a-solutions-architect-do.md)

-   :material-map-search-outline: **Browse the whole curriculum**

    ---

    All thirty domains, from computer science foundations to agentic AI, with the status of
    every topic.

    [:octicons-arrow-right-24: Curriculum index](start-here/curriculum-index.md)

-   :material-flask-outline: **Do, don't just read**

    ---

    Labs run locally with free tools. Design exercises make you decide and explain why.

    [:octicons-arrow-right-24: Labs](labs/index.md) · [:octicons-arrow-right-24: Design exercises](system-design-exercises/index.md)

</div>

## Start with these five pages

| Page | You will be able to... | Time |
|---|---|---|
| [What does a Solutions Architect do?](architecture-fundamentals/what-does-a-solutions-architect-do.md) | Describe the role, its outputs, and how it differs from adjacent roles | 25-35 min |
| [Functional vs non-functional requirements](architecture-fundamentals/functional-vs-non-functional-requirements.md) | Write requirements that can be tested and turn vague asks into measurable targets | 30-45 min |
| [Quality attributes and trade-offs](architecture-fundamentals/quality-attributes-and-trade-offs.md) | Name the quality attributes, see where they conflict, and make trade-offs explicit | 40-60 min |
| [The C4 model](architecture-fundamentals/c4-model.md) | Draw context, container, and component diagrams others can read | 40-60 min |
| [Estimating load, throughput, storage, and capacity](performance-and-scalability/capacity-estimation.md) | Turn a user count into request rates, storage, bandwidth, and instance counts | 45-60 min |

## Principles behind every page

- **Explain the problem before the solution.** Every technology exists because something was hard.
- **Vendor-neutral core, concrete examples.** AWS examples appear often because they are familiar to
  the maintainer; the explanation never depends on them.
- **Trade-offs, not slogans.** You will not read "always use microservices" or "NoSQL is faster".
  You will read under which workload assumptions a choice is right.
- **No invented numbers.** Limits, benchmarks, and prices come with a source and a date, or they are
  not here.
- **Visual and accessible.** Diagrams are text (Mermaid) with captions, legends, and prose
  descriptions. Color never carries meaning alone.
- **Open.** Text and diagrams are CC BY 4.0; code is MIT. See the
  [license notes](https://github.com/vinay9354/architecture-atlas/blob/main/LICENSE-DOCS.md).

## Contribute or report a problem

Found a mistake, a stale reference, or a confusing diagram? Open a
[content correction](https://github.com/vinay9354/architecture-atlas/issues/new?template=content-correction.yml).
Want to write a planned page? Read the
[contribution guide](https://github.com/vinay9354/architecture-atlas/blob/main/CONTRIBUTING.md)
and pick a topic from the [coverage matrix](appendices/coverage-matrix.md).
