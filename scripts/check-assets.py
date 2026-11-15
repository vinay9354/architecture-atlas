#!/usr/bin/env python3
"""Verify that every binary/image asset under docs/assets is accounted for in ASSET_ATTRIBUTION.md.

Original assets created in this repository are listed in the "Original assets" table; third-party
assets must appear in the third-party register with license details. Any file not mentioned in
either table fails the check. Stylesheets and JavaScript authored here are exempt (they are code,
covered by the MIT license) but must still live under docs/stylesheets or docs/assets/interactive.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "docs" / "assets"
REGISTER = ROOT / "ASSET_ATTRIBUTION.md"
EXEMPT_SUFFIXES = {".css", ".js", ".mjs", ".md", ".gitkeep"}


def main() -> int:
    register = REGISTER.read_text(encoding="utf-8") if REGISTER.exists() else ""
    missing: list[Path] = []
    total = 0
    for path in sorted(ASSETS.rglob("*")):
        if not path.is_file() or path.suffix.lower() in EXEMPT_SUFFIXES:
            continue
        total += 1
        rel = path.relative_to(ROOT).as_posix()
        if rel not in register:
            missing.append(path)
    for p in missing:
        print(f"ERROR: {p.relative_to(ROOT)} is not listed in ASSET_ATTRIBUTION.md")
    print(f"checked {total} asset file(s); {len(missing)} unregistered")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
