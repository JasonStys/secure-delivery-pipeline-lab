#!/usr/bin/env bash
# Jason Stys: run all local quality gates from the repository root.
# Variables: none; commands use the caller's isolated Python environment.
# Steps: lint/format/type maps; tests/coverage; measured benchmark.
set -euo pipefail
python -m ruff check .
python -m ruff format --check .
python -m mypy
python scripts/code_map.py --check
python -m pytest --cov --cov-report=term-missing --cov-report=json:artifacts/coverage.json --junitxml=artifacts/junit.xml
python scripts/benchmark.py
