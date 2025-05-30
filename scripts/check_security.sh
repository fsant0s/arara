#!/bin/bash
# Script to check for common security issues in the codebase
# This is intended to be run in CI/CD pipelines

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to check for common security issues
check_for_hardcoded_credentials() {
  echo -e "${BLUE}Checking for hardcoded credentials...${NC}"

  # Define patterns to search for
  patterns=(
    "api_key\s*=\s*['\"][a-zA-Z0-9_\.\-\+\/\=]{8,}['\"]"
    "password\s*=\s*['\"][^'\"\$]+['\"]"
    "token\s*=\s*['\"][a-zA-Z0-9_\.\-\+\/\=]{8,}['\"]"
    "secret\s*=\s*['\"][a-zA-Z0-9_\.\-\+\/\=]{8,}['\"]"
  )

  # Excluded files and directories
  exclude_dirs=(
    ".git"
    ".venv"
    "__pycache__"
    "*.pyc"
    "tests"
  )

  exclude_pattern=$(printf " --exclude-dir=%s" "${exclude_dirs[@]}")

  # Combine all patterns
  all_patterns=$(printf "|%s" "${patterns[@]}")
  all_patterns=${all_patterns:1}  # Remove leading |

  # Search for patterns
  found_issues=0
  results=$(grep -r --include="*.py" -E "$all_patterns" $exclude_pattern . || true)

  if [ -n "$results" ]; then
    echo -e "${RED}Potential hardcoded credentials found:${NC}"
    echo "$results"
    found_issues=1
  else
    echo -e "${GREEN}No hardcoded credentials found.${NC}"
  fi

  return $found_issues
}

check_for_vulnerable_imports() {
  echo -e "${BLUE}Checking for potentially vulnerable imports...${NC}"

  vulnerable_imports=(
    "import pickle"
    "import marshal"
    "from pickle import"
    "from marshal import"
    "eval\("
    "exec\("
    "os\.system\("
    "subprocess\.call\("
    "subprocess\.Popen\("
    "__import__\("
  )

  all_imports=$(printf "|%s" "${vulnerable_imports[@]}")
  all_imports=${all_imports:1}

  found_issues=0
  results=$(grep -r --include="*.py" -E "$all_imports" . --exclude-dir=.git --exclude-dir=.venv || true)

  if [ -n "$results" ]; then
    echo -e "${YELLOW}Potentially vulnerable imports found:${NC}"
    echo "$results"
    echo -e "${YELLOW}These imports may be legitimate but should be reviewed for security implications.${NC}"
    found_issues=1
  else
    echo -e "${GREEN}No potentially vulnerable imports found.${NC}"
  fi

  return $found_issues
}

run_bandit() {
  echo -e "${BLUE}Running bandit security scanner...${NC}"

  if ! command -v bandit &> /dev/null; then
    echo -e "${RED}bandit not found. Installing...${NC}"
    pip install bandit
  fi

  # Run bandit with a good set of rules
  bandit -r arara/ -c pyproject.toml -ll || return 1

  echo -e "${GREEN}Bandit scan completed successfully.${NC}"
  return 0
}

check_dependency_vulnerabilities() {
  echo -e "${BLUE}Checking for known vulnerabilities in dependencies...${NC}"

  if ! command -v safety &> /dev/null; then
    echo -e "${RED}safety not found. Installing...${NC}"
    pip install safety
  fi

  # Use safety to check for vulnerabilities in installed packages
  # Ignoring some vulnerabilities might be necessary in some cases
  safety check --full-report || return 1

  echo -e "${GREEN}Dependency vulnerability check completed successfully.${NC}"
  return 0
}

# Run all checks
echo -e "${BLUE}Running security checks for ARARA project...${NC}"

# Initialize status
checks_failed=0

# Run each check and aggregate status
check_for_hardcoded_credentials
if [ $? -ne 0 ]; then
  checks_failed=1
fi

check_for_vulnerable_imports
if [ $? -ne 0 ]; then
  checks_failed=1
fi

run_bandit
if [ $? -ne 0 ]; then
  checks_failed=1
fi

check_dependency_vulnerabilities
if [ $? -ne 0 ]; then
  checks_failed=1
fi

# Final status
if [ $checks_failed -eq 0 ]; then
  echo -e "${GREEN}All security checks passed!${NC}"
  exit 0
else
  echo -e "${RED}Some security checks failed. Please review the output above.${NC}"
  exit 1
fi
