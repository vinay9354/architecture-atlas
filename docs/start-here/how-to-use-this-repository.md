---
title: How to use this repository
description: "The anatomy of a topic page, learning levels, status labels, diagrams, labs, and how to report problems."
---

# How to use this repository

## The anatomy of a topic page

Every substantial page follows the same order so you always know where you are:

| Section | Why it is there |
|---|---|
| Page facts box | Level, status, time, last-verified date at a glance |
| Learning objectives | What you should be able to explain or do afterwards |
| Prerequisites | Linked pages to read first |
| The problem this solves | Why the concept exists at all |
| What it is / Mental model / Key terms | Precise definition, an analogy, and where the analogy breaks |
| How it works / Visual walkthrough | Mechanism, with at least one original diagram and its explanation |
| Worked example | Real inputs, processing, outputs, with numbers and units |
| Real-world architecture example | Where it sits in an actual system |
| Design choices and trade-offs | When to use it, when not to, alternatives, and the assumptions behind the advice |
| Failure modes, security, performance/reliability/cost | What breaks, what an attacker sees, what it costs |
| Hands-on lab | A small exercise you can do now |
| Knowledge check / Discussion questions | Test yourself; practise defending a design |
| Summary / Related topics / References | What to remember, where to go next, where the claims come from |

You do not have to read every section. A beginner can stop after the worked example; an experienced
engineer can jump straight to trade-offs and failure modes.

## Learning levels

Pages and sections are labelled with three levels. Read Level 1 without needing Level 3 first.

- **Level 1 — Understand:** what it is, why it exists, the mental model, vocabulary, a simple example.
- **Level 2 — Apply:** how it works, how to implement or configure it, trade-offs, failure modes, an exercise.
- **Level 3 — Architect:** scaling, security, reliability, performance, cost, operations, alternatives,
  and decisions in complex environments.

## Status labels

Status is an honest statement about review, not about whether the page renders.

| Status | Meaning |
|---|---|
| Planned | Identified in the curriculum; not written. The coverage matrix shows where it will live. |
| Outline | Objectives and structure exist; the explanation is incomplete. |
| Draft | Content exists; needs technical and teaching review. |
| Reviewed | A second person checked accuracy, diagrams, references, and exercises. |
| Needs update | May be stale or a referenced source changed. |

The `last_verified` date tells you when version-sensitive claims were last checked. Foundational
theory ages slowly; cloud services, Kubernetes, and AI protocols age quickly. Treat anything about a
product, API, limit, or price as a snapshot.

## Diagrams

Diagrams are written in [Mermaid](https://mermaid.js.org/) and rendered in your browser. Each one has
a caption, a legend when shapes or line styles mean something, and a prose explanation next to it, so
the page still makes sense if the diagram does not render or you use a screen reader. Diagrams never
rely on color alone. If a diagram looks too small on a phone, rotate the device or open the page on a
larger screen; the source is also readable on GitHub.

## Labs and exercises

Labs run locally with free tools unless a page says otherwise. Mini-exercises inside pages need only a
text editor or spreadsheet. Solutions are hidden behind a click so you can attempt them first.

## Searching

The search box understands acronyms and alternative names (for example "RPO" and "recovery point
objective" both find the same page). The [glossary](glossary.md) is the fastest way to resolve an
unfamiliar term.

## Reporting a problem

Each page has an "edit" icon that opens the Markdown source on GitHub. For corrections, broken links,
lab bugs, or accessibility barriers, use the issue templates linked from
[`SUPPORT.md`](https://github.com/vinay9354/architecture-atlas/blob/main/SUPPORT.md). Security
problems go through private reporting described in
[`SECURITY.md`](https://github.com/vinay9354/architecture-atlas/blob/main/SECURITY.md).

## Using the material elsewhere

Text and diagrams are CC BY 4.0, code is MIT. You can reuse them, including commercially, with
attribution. Details in
[`LICENSE-DOCS.md`](https://github.com/vinay9354/architecture-atlas/blob/main/LICENSE-DOCS.md).
