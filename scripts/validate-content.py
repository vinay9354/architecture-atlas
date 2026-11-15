#!/usr/bin/env python3
"""Content validation for Architecture Atlas.

Checks (all offline, no network):
  1. curriculum/coverage.yaml is well formed: unique IDs, valid statuses, destinations under docs/,
     and every non-Planned topic points at a page that exists.
  2. Topic pages (pages with a `status:` front-matter key) have the required metadata keys with
     valid values and a real `last_verified` date.
  3. Mermaid fences start with a known diagram type (cheap syntax guard; full rendering is
     verified in the browser or via `mkdocs serve`).
  4. Relative Markdown links and images inside docs/ resolve to existing files.
  5. No leftover template placeholders (e.g. "TODO-FILL") in published pages.

Exit code 1 if any error is found. Warnings do not fail the run.
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
COVERAGE = ROOT / "curriculum" / "coverage.yaml"

STATUS_VALUES = {"Planned", "Outline", "Draft", "Reviewed", "Needs update"}
LEVEL_VALUES = {"Beginner", "Intermediate", "Advanced", "Mixed"}
REQUIRED_TOPIC_KEYS = {"title", "description", "domain", "level", "status", "estimated_time", "last_verified"}
MERMAID_TYPES = (
    "flowchart", "graph", "sequenceDiagram", "stateDiagram-v2", "stateDiagram", "classDiagram",
    "erDiagram", "journey", "gantt", "pie", "timeline", "quadrantChart", "mindmap", "gitGraph",
    "xychart-beta", "block-beta", "C4Context", "C4Container", "C4Component", "C4Deployment", "sankey-beta",
)
PLACEHOLDERS = ("TODO-FILL", "lorem ipsum", "<<REPLACE")
LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
IMAGE_RE = re.compile(r"\!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^(\s*)```+\s*mermaid\s*$")

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def front_matter(text: str) -> dict | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError as exc:
        return {"__error__": str(exc)}
    return data if isinstance(data, dict) else {}


def check_coverage() -> None:
    data = yaml.safe_load(COVERAGE.read_text(encoding="utf-8"))
    seen: set[str] = set()
    for domain in data.get("domains", []):
        for key in ("id", "title", "section", "topics"):
            if key not in domain:
                err(f"coverage: domain missing '{key}': {domain}")
        if domain["id"] in seen:
            err(f"coverage: duplicate domain id {domain['id']}")
        seen.add(domain["id"])
        if not (DOCS / domain["section"]).is_dir():
            err(f"coverage: domain {domain['id']} section docs/{domain['section']} does not exist")
        for t in domain["topics"]:
            tid = t.get("id", "<missing id>")
            if tid in seen:
                err(f"coverage: duplicate topic id {tid}")
            seen.add(tid)
            for key in ("title", "status", "destination", "inventory"):
                if key not in t:
                    err(f"coverage: {tid} missing '{key}'")
            if t.get("status") not in STATUS_VALUES:
                err(f"coverage: {tid} has invalid status {t.get('status')!r}")
            dest = t.get("destination", "")
            if not dest.startswith("docs/") or not dest.endswith(".md"):
                err(f"coverage: {tid} destination must be a docs/*.md path, got {dest!r}")
            elif t.get("status") != "Planned" and not (ROOT / dest).is_file():
                err(f"coverage: {tid} is {t['status']} but destination {dest} does not exist")
    print(f"coverage.yaml: {len(data.get('domains', []))} domains, {len(seen) - len(data.get('domains', []))} topics")


def check_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT)
    fm = front_matter(text)
    if fm and "__error__" in fm:
        err(f"{rel}: invalid YAML front matter: {fm['__error__']}")
        fm = {}

    # Topic page metadata
    if fm and "status" in fm:
        missing = REQUIRED_TOPIC_KEYS - fm.keys()
        if missing:
            err(f"{rel}: missing front-matter keys {sorted(missing)}")
        if fm.get("status") not in STATUS_VALUES:
            err(f"{rel}: invalid status {fm.get('status')!r}")
        if fm.get("level") not in LEVEL_VALUES:
            err(f"{rel}: invalid level {fm.get('level')!r} (expected one of {sorted(LEVEL_VALUES)})")
        lv = fm.get("last_verified")
        if isinstance(lv, dt.date):
            if lv > dt.date.today():
                err(f"{rel}: last_verified {lv} is in the future")
        elif lv is not None:
            err(f"{rel}: last_verified must be an ISO date (YYYY-MM-DD), got {lv!r}")

    # Mermaid fences
    for n, line in enumerate(text.splitlines(), 1):
        m = FENCE_RE.match(line)
        if m:
            body = text.splitlines()[n:]
            first = next((ln.strip() for ln in body if ln.strip() and not ln.strip().startswith("%%")), "")
            if not first.startswith(MERMAID_TYPES):
                err(f"{rel}:{n}: mermaid block does not start with a known diagram type (got {first[:40]!r})")

    # Relative links and images
    for regex, kind in ((LINK_RE, "link"), (IMAGE_RE, "image")):
        for m in regex.finditer(text):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#", "tel:")) or "{{" in target:
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            if target.startswith("/"):
                err(f"{rel}: absolute {kind} '{m.group(1)}' - use a relative path")
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                err(f"{rel}: broken {kind} '{m.group(1)}'")

    # Placeholders
    lowered = text.lower()
    for ph in PLACEHOLDERS:
        if ph.lower() in lowered:
            err(f"{rel}: contains placeholder text {ph!r}")


def main() -> int:
    check_coverage()
    pages = sorted(p for p in DOCS.rglob("*.md"))
    for page in pages:
        check_page(page)
    print(f"checked {len(pages)} pages under docs/")
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"\n{len(errors)} error(s)")
        return 1
    print("content validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
