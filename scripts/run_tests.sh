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
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

echo -e "${YELLOW}Running unit tests with coverage...${NC}"

# Run unit tests with coverage
pytest tests/unit -v --cov=neuron --cov-report=term --cov-report=html:reports/coverage_html --cov-report=xml:reports/coverage.xml

# Save the exit code
UNIT_EXIT_CODE=$?

echo -e "${YELLOW}Running integration tests...${NC}"

# Run integration tests (without coverage to avoid duplication)
pytest tests/integration -v

# Save the exit code
INTEGRATION_EXIT_CODE=$?

# Report results
echo
if [ $UNIT_EXIT_CODE -eq 0 ] && [ $INTEGRATION_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    echo -e "${YELLOW}Coverage report is available at reports/coverage_html/index.html${NC}"
else
    echo -e "${RED}Tests failed!${NC}"
    exit 1
fi

# Run linting checks
echo -e "${YELLOW}Running linting checks...${NC}"
flake8 neuron --count --select=E9,F63,F7,F82 --show-source --statistics
FLAKE_EXIT_CODE=$?

# Run type checking
echo -e "${YELLOW}Running type checking...${NC}"
mypy neuron
MYPY_EXIT_CODE=$?

# Report linting and type checking results
if [ $FLAKE_EXIT_CODE -eq 0 ] && [ $MYPY_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
else
    echo -e "${RED}Code quality checks failed!${NC}"
    exit 1
fi
