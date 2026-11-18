#!/bin/bash
# harness-loop.sh - The Evaluation Loop Stop Condition

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "Running Harness Verification..."

# 1. Check Code Organization & Complexity
echo "Validating Structure..."
ruff check . || { echo "❌ Linting failed. Break down large functions or fix service boundaries."; exit 1; }

# 2. Security Check
echo "Validating Security..."
bandit -r missions services dao -q -c pyproject.toml || {
  echo "❌ Security vulnerabilities detected."
  exit 1
}

# 3. Integration Tests & Coverage
echo "Running Tests (Target: >80% Coverage)..."
pytest --cov=missions --cov=services --cov=dao --cov-fail-under=80 || {
  echo "❌ Tests failed or coverage is below 80%. Write additional tests."
  exit 1
}

# 4. Typecheck / compile
echo "Validating Build..."
python3 -m compileall missions services dao -q || {
  echo "❌ Build or typecheck failed."
  exit 1
}

echo "✅ All constraints satisfied. Terminal state reached."
exit 0