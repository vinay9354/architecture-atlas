#!/usr/bin/env bash
# Build (or serve) the documentation site locally.
#
#   scripts/build-local.sh          # create .venv if needed, validate, strict build into ./site
#   scripts/build-local.sh serve    # same, then start the live-reload dev server
#   scripts/build-local.sh check    # validation + strict build + unit tests, no server
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PYTHON:-python3}"
if [ ! -x .venv/bin/python ]; then
  echo "==> creating virtual environment (.venv)"
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt

echo "==> validating content"
python scripts/validate-content.py
python scripts/build-coverage.py --check
python scripts/check-assets.py

echo "==> building site (strict)"
mkdocs build --strict

case "${1:-}" in
  serve)
    echo "==> serving at http://127.0.0.1:8000/"
    mkdocs serve
    ;;
  check)
    echo "==> running unit tests"
    python -m unittest discover -s tests -v
    ;;
  *) ;;
esac
