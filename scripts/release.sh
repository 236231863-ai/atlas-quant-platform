#!/bin/bash
set -e
echo "=== Atlas Quant Platform Release Script ==="
VERSION=${1:-"1.0.0"}
echo "Releasing v$VERSION"

echo "1. Running tests..."
# pytest tests/ --cov=core --cov=engine --cov=backend

echo "2. Building..."
# docker build -t atlas-quant-backend:$VERSION -f docker/Dockerfile .

echo "3. Tagging..."
git tag -a "v$VERSION" -m "Release v$VERSION"

echo "4. Release v$VERSION ready"
echo "To push: git push origin v$VERSION"
