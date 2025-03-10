#!/bin/bash
# Script to set up the development environment for the NEURON project

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up development environment for NEURON project...${NC}"

# Check if Python 3.12 is installed
if ! command -v python3.12 &> /dev/null; then
  echo -e "${RED}Python 3.12 is required but not found.${NC}"
  echo -e "${RED}Please install Python 3.12 before continuing.${NC}"
  exit 1
fi

# Check for uv package manager
if ! command -v uv &> /dev/null; then
  echo -e "${RED}UV package manager is required but not found.${NC}"
  echo -e "${RED}Please install UV package manager before continuing:${NC}"
  echo -e "${RED}curl -L https://astral.sh/uv/install.sh | sh${NC}"
  exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo -e "${BLUE}Creating virtual environment...${NC}"
  python3.12 -m venv .venv
else
  echo -e "${GREEN}Virtual environment already exists.${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing dependencies with development extras...${NC}"
uv pip install -e ".[dev]"
echo -e "${GREEN}All dependencies installed.${NC}"

# Set up pre-commit hooks if git is initialized
if [ -d ".git" ]; then
  if ! command -v pre-commit &> /dev/null; then
    echo -e "${BLUE}Installing pre-commit...${NC}"
    uv pip install pre-commit
  fi

  if [ ! -f ".pre-commit-config.yaml" ]; then
    echo -e "${BLUE}Creating pre-commit configuration...${NC}"
    cat > .pre-commit-config.yaml << 'EOL'
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
    -   id: black

-   repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
    -   id: isort

-   repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
    -   id: flake8
        additional_dependencies: [flake8-docstrings]
EOL
  fi

  echo -e "${BLUE}Installing pre-commit hooks...${NC}"
  pre-commit install
fi

# Create tests directory if it doesn't exist
if [ ! -d "tests" ]; then
  echo -e "${BLUE}Creating tests directory...${NC}"
  mkdir -p tests
  touch tests/__init__.py
  echo -e "${GREEN}Tests directory created.${NC}"
fi

echo -e "${GREEN}Development environment setup complete!${NC}"
echo -e "${BLUE}To activate the virtual environment, run:${NC}"
echo -e "${BLUE}source .venv/bin/activate${NC}"
