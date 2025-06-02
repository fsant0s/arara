#!/bin/bash
# Script to format all Python code in the project

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Formatting Python code in the ARARA project...${NC}"

# Check if we're in a virtual environment, activate if found
if [ -d ".venv" ]; then
  echo -e "${BLUE}Activating virtual environment...${NC}"
  source .venv/bin/activate
fi

# Check for required tools
echo -e "${BLUE}Checking for required formatting tools...${NC}"
if ! command -v black &> /dev/null; then
  echo -e "${RED}Black not found. Installing...${NC}"
  pip install black
fi

if ! command -v isort &> /dev/null; then
  echo -e "${RED}isort not found. Installing...${NC}"
  pip install isort
fi

# Format code
echo -e "${BLUE}Running Black formatter...${NC}"
black arara --exclude "scripts/.*\.sh$" --line-length=100

echo -e "${BLUE}Running isort for import sorting...${NC}"
isort arara --skip-glob "scripts/*.sh"

# Check if pre-commit is installed and run appropriate hooks
if command -v pre-commit &> /dev/null; then
  echo -e "${BLUE}Running pre-commit hooks...${NC}"
  pre-commit run --all-files
fi

echo -e "${GREEN}Code formatting complete!${NC}"
echo -e "${BLUE}Run the following to check for linting issues:${NC}"
echo -e "${BLUE}flake8 arara${NC}"
