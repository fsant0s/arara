#!/bin/bash
# Script to run tests and generate coverage reports

# Ensure we're in the project root directory
cd "$(dirname "$0")/.." || exit

# Create the output directory for coverage reports if it doesn't exist
mkdir -p reports

# Set up colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Run unit tests with coverage
echo "Running unit tests with coverage..."
pytest tests/unit -v --cov=neuron --cov-report=html:reports/coverage_html --cov-report=xml:reports/coverage.xml

# Check if unit tests passed
if [ $? -ne 0 ]; then
    echo "Tests failed!"
    exit 1
fi

# Run integration tests
echo "Running integration tests..."
pytest tests/integration -v

# Check if integration tests passed
if [ $? -ne 0 ]; then
    echo "Integration tests failed!"
    exit 1
fi

echo "All tests passed!"
echo "Coverage report is available at reports/coverage_html/index.html"

# Run linting checks (but don't fail if they fail)
echo "Running linting checks..."
flake8 neuron || echo "Linting errors found. You can fix them later."

# Run type checking (but don't fail if they fail)
echo "Running type checking..."
mypy neuron || echo "Type checking errors found. You can fix them later."

echo "Test execution completed successfully!"
exit 0
