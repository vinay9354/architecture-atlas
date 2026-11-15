---
title: "ADR-0004: Content metadata and taxonomy"
description: "YAML front matter on every page plus a machine-readable coverage matrix keyed by stable topic IDs."
---

# ADR-0004: Front-matter metadata and a YAML coverage matrix

**Status:** Accepted  
**Date:** 2026-11-15  
**Deciders:** Repository maintainer, initial AI build agent  
**Related:** [ADR-0001](adr-0001-documentation-stack.md), `curriculum/coverage.yaml`, `scripts/build-coverage.py`

## Context

The curriculum inventory has 30 domains and 140 topic entries. The repository must show planned
coverage without creating hundreds of empty pages, let another contributor or AI agent continue the
work without losing context, and make the status of every page honest and visible. Pages also need
difficulty, domain, time, and freshness metadata for navigation and maintenance.

## Decision drivers

- One source of truth for "what exists, what is planned, where it will live".
- Stable identifiers usable in issues and pull requests.
- Validation in CI so status claims cannot silently drift from reality.
- Framework-native metadata where possible (MkDocs reads YAML front matter).

## Options considered

### Option 1 — Metadata only in page front matter, matrix maintained by hand

Simple, but a hand-maintained matrix drifts immediately and planned topics have no page to hold metadata.

### Option 2 — Machine-readable coverage file + page front matter + generator (chosen)

`curriculum/coverage.yaml` holds every topic with ID, title, status, destination path, and the
verbatim inventory text. `scripts/build-coverage.py` renders the matrix page and injects per-section
topic tables; `--check` mode fails CI if outputs are stale. `scripts/validate-content.py` checks that
every non-Planned topic points to an existing page and that page front matter is complete.

### Option 3 — Database or external tracker

Overkill for a static repository and invisible to readers.

## Decision

**Page metadata** (front matter, validated):

| Key | Values |
|---|---|
| `title`, `description` | Free text; used by the theme and search |
| `domain` | Domain title from the coverage file |
| `level` | `Beginner`, `Intermediate`, `Advanced`, `Mixed` |
| `status` | `Planned`, `Outline`, `Draft`, `Reviewed`, `Needs update` |
| `estimated_time` | Free text, e.g. "30-45 minutes" |
| `last_verified` | ISO date actually checked; never a placeholder |
| `coverage_ids` | Topic IDs the page is canonical for |
| `prerequisites` | Page titles, linked in the page body |
| `tags` | Domain, concept, and level tags (rendered by the Material tags plugin) |

**Taxonomy:** `D<nn>` domain IDs and `D<nn>-T<nn>` topic IDs mirror the order of the master
inventory. Topics are never deleted from the file; they are merged by pointing two IDs at one
destination (for example D21-T03 and D21-T04 both map to the prompt-and-context-engineering page).

**Learning levels** on pages follow the specification: Level 1 Understand, Level 2 Apply, Level 3
Architect. A page's `level` is its overall pitch; sections inside a page may be labelled individually.

## Consequences

**Positive**

- The coverage matrix is always accurate or CI fails.
- A newcomer can pick any `Planned` topic, see its destination path, and start writing.
- Status honesty is enforced structurally: `Draft` pages must exist; `Reviewed` is a human judgement
  recorded in both the page and the YAML.

**Negative**

- Two places carry status (page front matter and YAML). A future check can cross-validate them; for now
  reviewers compare them in pull requests.

## Follow-up actions

- [ ] Add a cross-check between page `status`/`coverage_ids` and the YAML.
- [ ] Add a "Report an issue" link to each page footer that pre-fills the coverage ID.
