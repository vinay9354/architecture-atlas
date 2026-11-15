---
title: "ADR-0002: License strategy"
description: "MIT for code and configuration, CC BY 4.0 for educational content and original diagrams."
---

# ADR-0002: MIT for code, CC BY 4.0 for content

**Status:** Accepted  
**Date:** 2026-11-15  
**Deciders:** Repository maintainer, initial AI build agent  
**Related:** `LICENSE`, `LICENSE-DOCS.md`, `ASSET_ATTRIBUTION.md`, `THIRD_PARTY_NOTICES.md`

## Context

The repository will be public and may be reused by individuals, educators, and companies. It contains
two kinds of material with different reuse norms: software (scripts, configuration, demos, lab code)
and educational content (prose, diagrams, exercises). The specification requires licensing and
attribution to be treated as release-blocking, and it must be impossible to accidentally relicense
third-party material.

## Decision drivers

- Maximize reuse, including commercial reuse, so that companies can use the material for training.
- Keep attribution to the project for the educational content.
- Use licenses contributors and lawyers already recognize.
- Avoid ShareAlike or NonCommercial terms, which the specification explicitly excludes by default.

## Options considered

### Option 1 — Single MIT license for everything

Simple, but MIT is written for software; applying it to prose and diagrams is unusual and its
"software" wording creates ambiguity for text reuse.

### Option 2 — Single CC BY 4.0 for everything

Clear for text, but CC licenses are not recommended by Creative Commons for software, and package
ecosystems expect a software license on code.

### Option 3 — MIT for code, CC BY 4.0 for content (chosen)

Conventional pairing used by many documentation projects. Each license is applied to the material it
was designed for.

### Option 4 — Apache-2.0 for code, CC BY 4.0 for content

Apache-2.0 adds an explicit patent grant. The code here is small tooling and demos with negligible
patent exposure; MIT's simplicity wins. The maintainer may switch to Apache-2.0 later; doing so only
affects future contributions unless all contributors agree.

## Decision

- Code, scripts, configuration, build tooling, interactive demos, and example code: **MIT**
  (`LICENSE`).
- Educational text, explanations, exercises, and original diagrams (including Mermaid source and
  original SVG): **CC BY 4.0** (`LICENSE-DOCS.md`).
- Third-party material keeps its own license and is recorded in `ASSET_ATTRIBUTION.md` (assets) and
  `THIRD_PARTY_NOTICES.md` (software). No NC, ND, ShareAlike, or unknown-license assets without
  explicit maintainer approval.
- `README.md`, `LICENSE`, and `LICENSE-DOCS.md` all state the scope of each license.

## Consequences

**Positive**

- Companies can reuse the content for internal training with attribution.
- Contributors know exactly what they are granting.
- CI (`scripts/check-assets.py`) fails if an asset is not in the attribution register.

**Negative**

- Two licenses mean two files to read; mitigated by the scope notes in each file.
- CC BY 4.0 requires attribution on every reuse, which some adopters find burdensome. This is
  intentional: it keeps the learning material traceable.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| A contributor pastes copyrighted text or an image | Pull request template and `CONTRIBUTING.md` require an originality confirmation; reviewers check; attribution register is mandatory. |
| Ambiguity about which license covers a file type | Scope lists in `LICENSE` and `LICENSE-DOCS.md`; when in doubt, ask in the pull request. |

## Follow-up actions

- [ ] Maintainer confirms the copyright holder name used in `LICENSE` ("Architecture Atlas contributors").
- [ ] Add a license check for Python dependencies if the dependency set grows (for example `pip-licenses` in CI).

## Notes

This ADR records an operational policy; it is not legal advice.
