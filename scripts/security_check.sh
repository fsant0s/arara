#!/bin/bash
# Script to perform security checks on the codebase

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Running security checks on the NEURON project...${NC}"

# Check if we're in a virtual environment, activate if found
if [ -d ".venv" ]; then
  echo -e "${BLUE}Activating virtual environment...${NC}"
  source .venv/bin/activate
fi

# Check for bandit
echo -e "${BLUE}Checking for bandit security scanner...${NC}"
if ! command -v bandit &> /dev/null; then
  echo -e "${RED}bandit not found. Installing...${NC}"
  pip install bandit
fi

# Run different security scans
echo -e "${BLUE}Running bandit for security vulnerabilities...${NC}"
bandit -r neuron/ -c pyproject.toml

# Check for hardcoded credentials
echo -e "${BLUE}Checking for hardcoded credentials...${NC}"
grep -r --include="*.py" -E "(pass|password|pwd|secret|token|key).*['\"][a-zA-Z0-9_\.\-\+\/\=]{8,}['\"]" neuron/
if [ $? -eq 0 ]; then
  echo -e "${RED}WARNING: Potential hardcoded credentials found!${NC}"
  echo -e "${YELLOW}Consider using environment variables or a secure vault for sensitive information.${NC}"
else
  echo -e "${GREEN}No obvious hardcoded credentials found.${NC}"
fi

# Check for insecure imports
echo -e "${BLUE}Checking for potentially insecure imports...${NC}"
grep -r --include="*.py" -E "import (pickle|marshal|shelve|subprocess|os.system|eval)" neuron/
if [ $? -eq 0 ]; then
  echo -e "${YELLOW}Potentially risky imports found. Review for proper security controls.${NC}"
else
  echo -e "${GREEN}No obviously risky imports found.${NC}"
fi

echo -e "${GREEN}Security checks completed.${NC}"
echo -e "${BLUE}Consider these additional security practices:${NC}"
echo -e "  - Validate all user inputs"
echo -e "  - Implement proper authentication and authorization"
echo -e "  - Use HTTPS for all external connections"
echo -e "  - Keep dependencies updated regularly"
echo -e "  - Encrypt sensitive data at rest and in transit"
