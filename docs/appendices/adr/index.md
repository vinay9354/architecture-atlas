---
title: Architecture Decision Records
description: "Decisions about how this repository is built, in the ADR format the curriculum teaches."
---

# Architecture Decision Records (ADRs)

An ADR captures one significant decision: the context that forced it, the options weighed, what was
chosen, and the consequences. ADRs are short, numbered, immutable once accepted (a new ADR supersedes
an old one), and live next to the thing they describe. The repository uses them for its own design so
that readers see the format in use before they meet it in the curriculum.

| ADR | Decision | Status |
|---|---|---|
| [ADR-0001](adr-0001-documentation-stack.md) | Use MkDocs with Material, hosted on GitHub Pages | Accepted |
| [ADR-0002](adr-0002-license-strategy.md) | MIT for code, CC BY 4.0 for content | Accepted |
| [ADR-0003](adr-0003-diagram-format.md) | Mermaid by default, original SVG when needed | Accepted |
| [ADR-0004](adr-0004-content-metadata-and-taxonomy.md) | Front-matter metadata and a YAML coverage matrix | Accepted |
| [ADR-0005](adr-0005-lab-execution-strategy.md) | Local-first labs with explicit cloud/GPU opt-in | Accepted |
| [ADR-0006](adr-0006-example-testing.md) | Examples and scripts are tested with unittest in CI | Accepted |

The template is at
[`templates/adr-template.md`](https://github.com/vinay9354/architecture-atlas/blob/main/templates/adr-template.md).
The curriculum page on ADRs and architecture governance is planned under
[Architecture fundamentals](../../architecture-fundamentals/index.md).
