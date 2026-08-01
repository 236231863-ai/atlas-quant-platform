#!/bin/bash
# Atlas Quant Platform - Build Script (Linux/macOS)
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${ROOT}/.venv/bin/python"
[ -x "$PYTHON" ] || PYTHON="python"

echo "=== Clean ==="
rm -rf "${ROOT}/dist" "${ROOT}/build" "${ROOT}"/*.spec

echo "=== Install ==="
"$PYTHON" -m pip install -r "${ROOT}/requirements-dev.txt" -c "${ROOT}/constraints.txt"

echo "=== Lint ==="
"$PYTHON" -m ruff check "$ROOT" --exclude ".venv" --exclude "tests" || echo "ruff not installed, skip"

echo "=== Test ==="
cd "$ROOT"
"$PYTHON" -m pytest tests/ -q

echo "=== Build Desktop ==="
"$PYTHON" -m PyInstaller --noconfirm --clean desktop/main.py --name Atlas --windowed

echo "Build complete."
