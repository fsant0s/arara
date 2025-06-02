#!/bin/bash
# Script to check type annotations in the project

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Checking type annotations in the ARARA project...${NC}"

# Check if we're in a virtual environment, activate if found
if [ -d ".venv" ]; then
  echo -e "${BLUE}Activating virtual environment...${NC}"
  source .venv/bin/activate
fi

# Check for mypy
echo -e "${BLUE}Checking for mypy...${NC}"
if ! command -v mypy &> /dev/null; then
  echo -e "${RED}mypy not found. Installing...${NC}"
  pip install mypy
fi

# Run mypy
echo -e "${BLUE}Running mypy...${NC}"
# Add --strict for more strict checking
mypy --config-file pyproject.toml arara/

# Check exit code
if [ $? -eq 0 ]; then
  echo -e "${GREEN}Type checking passed successfully!${NC}"
  exit 0
else
  echo -e "${RED}Type checking found issues that need to be fixed.${NC}"
  echo -e "${BLUE}Tips for fixing type errors:${NC}"
  echo -e "  - Add proper type annotations to function arguments and return values"
  echo -e "  - Use typing module for complex types (List, Dict, Optional, etc.)"
  echo -e "  - For third-party libraries without type hints, consider using type stubs or any"
  echo -e "  - For dynamic attributes, use hasattr() or try/except instead of assuming existence"
  exit 1
fi
