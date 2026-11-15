---
title: "ADR-0001: Documentation stack and hosting"
description: "Use MkDocs with the Material theme, Markdown content, and GitHub Pages via GitHub Actions."
---

# ADR-0001: Use MkDocs with Material, hosted on GitHub Pages

**Status:** Accepted  
**Date:** 2026-11-15  
**Deciders:** Repository maintainer, initial AI build agent  
**Related:** [ADR-0003](adr-0003-diagram-format.md), [ADR-0004](adr-0004-content-metadata-and-taxonomy.md)

## Context

The repository must hold hundreds of Markdown pages with diagrams, be searchable, build quickly from a
clean checkout, deploy as a static site, and be maintainable by contributors who are not front-end
developers. The master specification recommends MkDocs with Material by default and asks for an ADR if
anything else is chosen. The local environment had Python 3.14, `uv`, and Node.js 26 available.

## Decision drivers

- Zero-cost static hosting (GitHub Pages) with a documented CI deployment.
- Diagrams as text in version control (see ADR-0003).
- Fast builds, strict link validation, offline-friendly local preview.
- Minimal dependency surface with clear licenses.
- A contributor only needs Python and Git.

## Options considered

### Option 1 — MkDocs + Material for MkDocs (chosen)

Python-based, single `mkdocs.yml`, built-in search, tags, admonitions, tabs, Mermaid integration via
`pymdownx.superfences`, strict mode that fails on broken links and missing anchors. Mature and widely
used for technical documentation. Licenses: BSD-2 (MkDocs), MIT (Material).

### Option 2 — Docusaurus

React/Node based. Excellent for versioned product docs and MDX interactivity, but adds a JavaScript
build toolchain, larger dependency tree, and a steeper path for contributors editing only Markdown.

### Option 3 — Astro Starlight

Modern, fast, good defaults. Younger ecosystem and again a Node toolchain; no clear advantage over
Option 1 for a Markdown-first curriculum.

### Option 4 — Custom static generator

Full control, but a maintenance burden that distracts from the learning mission. Rejected outright.

## Decision

Use **MkDocs 1.6.1 with mkdocs-material 9.8.1**, pinned in `requirements.txt`. Content is Markdown
under `docs/`. GitHub Actions builds with `mkdocs build --strict` on every push and deploys to GitHub
Pages from `main`. The Material theme's `font: false` setting avoids external font requests, so the
site makes no third-party calls other than the Mermaid script (ADR-0003).

Structure deviations from the specification's suggested tree, with reasons:

- Served assets live under `docs/assets/` rather than a top-level `assets/`, because MkDocs only serves
  files inside `docs_dir`. Non-served sources (lab code, examples) stay at the top level.
- A `curriculum/` directory holds the machine-readable coverage file (ADR-0004).
- Domain 01 pages live in `docs/architecture-fundamentals/` and Domain 02 in `docs/foundations/`, so
  "foundations" is not ambiguous between architecture thinking and computer science.

## Consequences

**Positive**

- Clean checkout to running site in two commands.
- Strict builds catch broken internal links, nav mistakes, and missing anchors in CI.
- Material's search handles acronyms and camel-case via a tuned separator.

**Negative**

- Interactive demos must be plain HTML/JS embedded in pages; there is no component framework. This is
  acceptable because demos are deliberately small (specification Section 4.4).
- Mermaid diagrams render client-side, so the strict build does not validate diagram syntax (mitigated
  in ADR-0003 and `scripts/validate-content.py`).

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Theme or plugin breaking changes | Versions are pinned; upgrades are deliberate and recorded in `CHANGELOG.md`. |
| GitHub Pages not enabled on the repository | `pages.yml` documents the one-time setting; the build workflow still verifies the site on every push. |
| Python version drift | CI uses 3.12; local verified on 3.14; both recorded in `requirements.txt`. |

## Follow-up actions

- [ ] Enable GitHub Pages (Settings → Pages → Source: GitHub Actions) — maintainer, requires repository settings access.
- [ ] Add an offline Mermaid bundle if offline use becomes a requirement.
