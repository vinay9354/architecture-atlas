# Security policy

## Reporting a vulnerability

This repository is a documentation site with small, local-only lab scripts. It has no backend,
stores no user data, and uses no third-party tracking. Even so, security problems are possible,
for example:

- A lab or example that teaches an insecure practice or leaks a secret.
- A GitHub Actions workflow with excessive permissions or a supply-chain risk.
- An interactive demo with a cross-site scripting (XSS) bug.
- An accidentally committed credential.

**Please report these privately** through GitHub's private vulnerability reporting:
<https://github.com/vinay9354/architecture-atlas/security/advisories/new>.

Do **not** open a public issue for an exploitable problem. Public issues are fine for general
hardening suggestions that reveal nothing exploitable (use the "Security hardening" issue template).

## What to include

- Where the problem is (file path, workflow name, page URL).
- What the impact is and how you found it.
- Steps to reproduce, if applicable. Remove any real credentials or personal data.

## What to expect

- Acknowledgement within 7 days.
- A fix or mitigation plan, with credit to you if you want it, once the issue is confirmed.
- Coordinated disclosure: we ask that you give us reasonable time to fix the problem before
  discussing it publicly.

## Scope notes

- Vulnerabilities in third-party tools (MkDocs, Mermaid, GitHub Actions) should be reported to
  those projects; tell us too if the repository's configuration makes the impact worse.
- The learning content discusses attacks (prompt injection, SQL injection, DDoS, and so on) for
  defensive education. Describing an attack class in a page is not a vulnerability report.
