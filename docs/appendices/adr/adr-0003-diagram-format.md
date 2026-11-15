---
title: "ADR-0003: Diagram format and rendering"
description: "Mermaid in Markdown by default; original SVG when Mermaid cannot express the visual; no screenshots as the only source."
---

# ADR-0003: Mermaid by default, original SVG when needed

**Status:** Accepted  
**Date:** 2026-11-15  
**Deciders:** Repository maintainer, initial AI build agent  
**Related:** [ADR-0001](adr-0001-documentation-stack.md), `CONTRIBUTING.md` section 4

## Context

Visual explanation is a core requirement: every substantial topic needs at least one original diagram.
Diagrams must be reviewable in pull requests, editable by contributors without special tools, render on
GitHub and on the documentation site, and remain accessible.

## Decision drivers

- Text-based source that diffs cleanly.
- Renders on GitHub.com (Mermaid fences are rendered natively there) and in the MkDocs site.
- No proprietary tools; no binary-only diagram sources.
- Accessibility: every diagram needs a prose description regardless of format.

## Options considered

### Option 1 — Mermaid fences in Markdown (chosen as default)

Supported by Material for MkDocs through `pymdownx.superfences` and rendered natively by GitHub.
Covers flowcharts, sequence, state, class, ER, journey, timeline, and more. Limitations: layout control
is limited, large diagrams become unreadable, and rendering happens client-side (the Mermaid library is
fetched from a CDN by the theme at page view time).

### Option 2 — PlantUML

Richer layouts, but needs a Java renderer or an external server in the build and does not render on
GitHub without plugins.

### Option 3 — Draw.io / diagrams.net XML with exported SVG

Good for complex diagrams, but XML sources are hard to review and the tool is a dependency for every
edit.

### Option 4 — Hand-written SVG

Full control and accessibility, but slow to write; reserved for cases Mermaid cannot express (custom
illustrations, charts with exact geometry).

## Decision

1. **Mermaid is the default.** Every diagram has a caption, a legend where symbols or styles carry
   meaning, flow direction, trust/failure boundaries where relevant, and a prose explanation next to it.
2. **Original SVG** under `docs/assets/diagrams/` when Mermaid is insufficient; the SVG source is the
   committed artifact, listed in `ASSET_ATTRIBUTION.md` as an original asset, with alt text.
3. **Interactive visuals** are small vanilla HTML/JS modules under `docs/assets/interactive/`, embedded
   only when interaction improves understanding, with a static explanation fallback.
4. **Screenshots are never the only source** of a diagram.
5. **C4 diagrams** are drawn with Mermaid `flowchart` syntax styled as C4 (nested subgraphs for
   boundaries) because Mermaid's dedicated C4 syntax is experimental and its rendering was not verified
   as stable at the time of this decision. It may be adopted later after verification.
6. **Color is never the only carrier of meaning**; shapes, labels, and line styles are used as well.

## Validation

- `scripts/validate-content.py` checks that every Mermaid fence starts with a known diagram type.
- Full rendering is verified by viewing pages in `mkdocs serve` (or the built site) before marking a
  page `Draft` or higher. A headless render check (for example `@mermaid-js/mermaid-cli`) may be added
  to CI later; it was not added now because it requires a browser download in CI.

## Consequences

**Positive**

- Diagrams are reviewable as text and render both on GitHub and the site.
- Contributors need no diagram tooling beyond a text editor.

**Negative**

- Client-side rendering means the strict build does not catch Mermaid syntax errors; the manual render
  check is part of the definition of done.
- The site fetches the Mermaid script from a CDN; offline viewers see the diagram source instead of the
  rendered figure. The prose description next to each diagram keeps the page usable.

## Follow-up actions

- [ ] Evaluate bundling Mermaid locally via `extra_javascript` for offline use.
- [ ] Evaluate a headless Mermaid render check in CI once the page count justifies it.
