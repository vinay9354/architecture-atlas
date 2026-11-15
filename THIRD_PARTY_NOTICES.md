# Third-party notices

This file lists third-party software and content redistributed with, or depended on by, this
repository. Dependencies are **not vendored**; they are installed at build time from their
official package registries. Their license texts are shipped with the packages.

Last reviewed: 2026-11-15.

## Documentation toolchain (Python, installed via `requirements.txt`)

| Package | Version pinned | License | Homepage |
|---|---|---|---|
| mkdocs | 1.6.1 | BSD-2-Clause | <https://www.mkdocs.org/> |
| mkdocs-material | 9.8.1 | MIT | <https://squidfunk.github.io/mkdocs-material/> |
| pymdown-extensions | 13.1 | MIT | <https://facelessuser.github.io/pymdown-extensions/> |
| PyYAML | 6.0.3 | MIT | <https://pyyaml.org/> |

Transitive dependencies (Markdown, Jinja2, Pygments, Babel, and others) are pulled in by the
packages above and carry their own permissive licenses; run `pip-licenses` in the virtual
environment to list them.

## Runtime assets loaded by the built site

| Asset | How it is used | License | Notes |
|---|---|---|---|
| Mermaid (JavaScript library) | Loaded by Material for MkDocs at page view time to render `mermaid` code fences | MIT | Fetched from a public CDN by the theme; not stored in this repository. See [ADR-0003](docs/appendices/adr/adr-0003-diagram-format.md). |
| Material Design Icons / FontAwesome / Octicons | Icon sets bundled inside mkdocs-material | Apache-2.0 / CC BY 4.0 (FontAwesome icons) / MIT | Bundled by the theme; not copied here. |

## CI tooling (GitHub Actions)

| Tool | License |
|---|---|
| markdownlint-cli2 | MIT |
| lychee / lychee-action | Apache-2.0 / MIT |
| gitleaks-action | MIT (gitleaks itself: MIT; commercial use terms apply to organizations, see its repository) |

## Content

No third-party text, images, or diagrams are included at this time. Any future inclusion must be
recorded in [`ASSET_ATTRIBUTION.md`](ASSET_ATTRIBUTION.md).
