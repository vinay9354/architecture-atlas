# Convenience targets. Each one maps to a documented command in CONTRIBUTING.md.
.PHONY: setup validate coverage build serve lint test check

setup:
	python3 -m venv .venv && .venv/bin/pip install --quiet -r requirements.txt

validate:
	.venv/bin/python scripts/validate-content.py
	.venv/bin/python scripts/check-assets.py
	.venv/bin/python scripts/build-coverage.py --check

coverage:
	.venv/bin/python scripts/build-coverage.py

build:
	.venv/bin/mkdocs build --strict

serve:
	.venv/bin/mkdocs serve

lint:
	npx --yes markdownlint-cli2

test:
	.venv/bin/python -m unittest discover -s tests -v

check: validate build test
