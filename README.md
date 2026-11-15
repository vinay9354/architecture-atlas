# Architecture Atlas

**A free, open-source, visual-first learning repository for Solutions Architecture, system design,
cloud, data, and AI architecture.**

Site: <https://vinay9354.github.io/architecture-atlas/> (deploys from `main` via GitHub Pages once
Pages is enabled in the repository settings).

## What it is

A curriculum that teaches you to understand, explain, design, evaluate, document, and defend real
architectures, not to memorize product names. Thirty domains cover software and computer science
foundations, architecture thinking and requirements, software and distributed architecture, APIs and
integration, databases and data engineering, messaging and streaming, networking, cloud and
Kubernetes, security, reliability, performance, observability, DevOps and platform engineering,
FinOps, enterprise architecture, and the full AI stack: ML foundations, LLMs, RAG, agents, MCP and
A2A, model serving, and AI governance. It ends in design exercises, labs, and end-to-end case studies.

Every substantial page has learning objectives, a mental model, an original diagram (Mermaid), a
worked example, trade-offs, failure modes, a small exercise, a knowledge check, and dated references.
Explanations are vendor-neutral; AWS examples appear where they help.

## Who it is for

Primarily engineers with working cloud and DevOps experience who want to grow into broader
architecture roles. Written to stay readable for motivated beginners, with advanced (Level 3) sections
marked for experienced engineers.

## Status (2026-11-15)

Foundation batch complete:

- Repository structure, MkDocs Material site, CI (build, validation, link check, Pages deploy).
- Complete 30-domain curriculum index and a machine-readable coverage matrix with 140 topic entries,
  each mapped to a page or a planned destination (`curriculum/coverage.yaml`).
- Five learning pages in **Draft** status: the Solutions Architect role, functional vs non-functional
  requirements, quality attributes and trade-offs, the C4 model, and capacity estimation.
- Six Architecture Decision Records for the repository itself.

Everything else is `Planned`. See [`ROADMAP.md`](ROADMAP.md) and the
[coverage matrix](docs/appendices/coverage-matrix.md). No page is marked `Reviewed` yet.

## Quick start

```bash
git clone https://github.com/vinay9354/architecture-atlas.git
cd architecture-atlas
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve        # open http://127.0.0.1:8000/
```

Validate before a pull request:

```bash
python scripts/validate-content.py && python scripts/build-coverage.py --check && mkdocs build --strict
```

Or `scripts/build-local.sh check`. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full workflow.

## Repository layout

```text
docs/            Site content (Markdown). One directory per curriculum section; docs/assets for served files.
curriculum/      coverage.yaml - the machine-readable coverage matrix (source of truth for topic status).
scripts/         validate-content.py, build-coverage.py, check-assets.py, build-local.sh
templates/       topic, lab, case-study, and ADR templates
labs/            Lab code (local/, cloud-optional/, solutions/)
examples/        Runnable examples, configurations, sample data, example ADRs
tests/           unittest suites for tooling and examples
.github/         Workflows (docs-build, link-check, pages), issue and PR templates
MASTER_PROMPT.md The full project specification this repository is built from
```

## Licenses

- **Code, scripts, configuration, demos:** [MIT](LICENSE).
- **Educational text and original diagrams:** [CC BY 4.0](LICENSE-DOCS.md).
- **Third-party material:** its own license, listed in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)
  and [`ASSET_ATTRIBUTION.md`](ASSET_ATTRIBUTION.md).

Product names and logos are the property of their owners; mention does not imply endorsement.

## Contributing and support

- Corrections, new topics, broken links, lab bugs, accessibility: use the issue templates
  (see [`SUPPORT.md`](SUPPORT.md)).
- Security problems: private reporting, see [`SECURITY.md`](SECURITY.md).
- Writing pages, diagrams, and labs: [`CONTRIBUTING.md`](CONTRIBUTING.md).
- Community standards: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
