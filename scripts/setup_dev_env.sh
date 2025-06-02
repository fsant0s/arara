#!/bin/bash
# Script to set up the development environment for the ARARA project

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up development environment for ARARA project...${NC}"

# Install uv package manager if not installed
install_uv() {
  echo -e "${BLUE}Installing UV package manager...${NC}"
  curl -L https://astral.sh/uv/install.sh | sh

  # Add UV to PATH for the current session
  export PATH="$HOME/.cargo/bin:$PATH"

  # Check if installation was successful
  if ! command -v uv &> /dev/null; then
    echo -e "${RED}Failed to install UV package manager.${NC}"
    echo -e "${RED}Please install it manually: curl -L https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
  fi

  echo -e "${GREEN}UV package manager installed successfully.${NC}"
}

# Check for uv package manager
if ! command -v uv &> /dev/null; then
  echo -e "${YELLOW}UV package manager not found. Installing...${NC}"
  install_uv
else
  echo -e "${GREEN}UV package manager is already installed.${NC}"
fi

# Determine the required Python version
get_python_version() {
  local python_version=""

  # Check .python-version file first
  if [ -f ".python-version" ]; then
    python_version=$(cat .python-version | tr -d '\r\n')
    echo -e "${BLUE}Python version ${python_version} found in .python-version file.${NC}" >&2
    echo "$python_version"
    return
  fi

  # Check pyproject.toml if .python-version doesn't exist
  if [ -f "pyproject.toml" ]; then
    # Extract Python version from pyproject.toml (looking for requires-python)
    local extracted_version=$(grep -Po 'requires-python\s*=\s*"\K[^"]+' pyproject.toml | tr -d '=' | tr -d '<>' | tr -d ' ')
    if [ -n "$extracted_version" ]; then
      python_version=$extracted_version
      echo -e "${BLUE}Python version ${python_version} found in pyproject.toml.${NC}" >&2
      echo "$python_version"
      return
    fi
  fi

  # Default to latest Python 3.12 if not found
  echo -e "${YELLOW}No specific Python version found. Using Python 3.12 as default.${NC}" >&2
  echo "3.12"
}

PYTHON_VERSION=$(get_python_version)

# Ensure the required Python version is available
echo -e "${BLUE}Checking if Python ${PYTHON_VERSION} is available...${NC}"
if ! uv python list | grep -q "${PYTHON_VERSION}"; then
  echo -e "${YELLOW}Python ${PYTHON_VERSION} not found in UV Python list.${NC}"
  echo -e "${BLUE}Installing Python ${PYTHON_VERSION} with UV...${NC}"

  uv python install "${PYTHON_VERSION}"

  if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install Python ${PYTHON_VERSION} with UV.${NC}"
    echo -e "${RED}Please install it manually or check the UV documentation.${NC}"
    exit 1
  fi

  echo -e "${GREEN}Python ${PYTHON_VERSION} installed successfully.${NC}"
else
  echo -e "${GREEN}Python ${PYTHON_VERSION} is already available.${NC}"
fi

# Create and activate virtual environment using UV
echo -e "${BLUE}Creating virtual environment with UV...${NC}"
uv venv -p ${PYTHON_VERSION} .venv

# Activate the virtual environment
source .venv/bin/activate
echo -e "${GREEN}Virtual environment activated.${NC}"

# Install dependencies
echo -e "${BLUE}Installing dependencies with development extras...${NC}"
uv pip install -e ".[dev]"
echo -e "${GREEN}All dependencies installed.${NC}"

# Synchronize dependencies to ensure everything is up-to-date
echo -e "${BLUE}Synchronizing dependencies...${NC}"
uv sync
echo -e "${GREEN}Dependencies synchronized successfully.${NC}"

# Set up pre-commit hooks if git is initialized
if [ -d ".git" ]; then
  echo -e "${BLUE}Setting up pre-commit hooks...${NC}"

  # Create pre-commit config if it doesn't exist
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
        args: [--line-length=100]

-   repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
    -   id: isort
        args: ["--profile", "black", "--filter-files"]

-   repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
    -   id: flake8
        additional_dependencies: [flake8-docstrings]
        args: ["--max-line-length=100"]
EOL
  fi

  # Install pre-commit using UV
  echo -e "${BLUE}Installing pre-commit package...${NC}"
  uv pip install pre-commit

  # Verify pre-commit was installed
  if ! command -v pre-commit &> /dev/null; then
    echo -e "${YELLOW}pre-commit command not found, trying to use it from .venv/bin...${NC}"
    if [ -f ".venv/bin/pre-commit" ]; then
      echo -e "${BLUE}Using pre-commit from virtual environment...${NC}"
      .venv/bin/pre-commit install
    else
      echo -e "${RED}pre-commit not found. Skipping hook installation.${NC}"
    fi
  else
    # Install the pre-commit hooks
    pre-commit install
  fi
  echo -e "${GREEN}Pre-commit hooks installed.${NC}"
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
