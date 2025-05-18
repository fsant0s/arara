# Contributing Guide for the ARARA Project

Thank you for considering contributing to ARARA! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Environment](#development-environment)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)
- [Project Structure](#project-structure)

## Code of Conduct

This project and all participants are subject to the [Code of Conduct](CODE_OF_CONDUCT.md). By contributing, you agree to follow its guidelines.

## How to Contribute

Contributions to ARARA can take several forms:

1. Reporting bugs and issues
2. Suggesting new features
3. Improving documentation
4. Submitting code fixes
5. Adding tests
6. Reviewing pull requests

For all contributions that involve code, follow the workflow below:

1. Fork the repository
2. Clone your fork locally: `git clone https://github.com/your-username/arara.git`
3. Create a branch for your contribution: `git checkout -b feature/your-feature`
4. Make your changes
5. Add tests for your changes (when applicable)
6. Run the tests and other checks
7. Commit your changes following the [commit guidelines](#commit-guidelines)
8. Push the changes to your fork: `git push origin feature/your-feature`
9. Create a Pull Request following the [provided template](PULL_REQUEST_TEMPLATE.md)

## Development Environment

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/fsant0s/arara.git
cd arara

# Set up the development environment automatically
./scripts/setup_dev_env.sh

# Or set up manually
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
pip install ipykernel pytest pytest-cov black isort flake8 mypy
```

## Coding Standards

The ARARA project follows strict coding standards to maintain code quality and consistency:

### Code Formatting

- We use [Black](https://black.readthedocs.io/) with a line length of 88 characters
- We use [isort](https://pycqa.github.io/isort/) for organizing imports
- Run `./scripts/format_code.sh` before committing changes

### Style and Quality

- We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for code style
- We use [flake8](https://flake8.pycqa.org/) for linting
- Code must pass all pre-commit checks

### Documentation

- All new code must include docstrings in Google format
- Public classes and functions must have complete docstrings
- Keep documentation updated when making changes

### Typing

- We use type annotations for all functions and methods
- We check types with [mypy](https://mypy.readthedocs.io/)
- All new code must pass type checking

### Tests

- All new code must have unit tests
- Maintain code coverage above 80%
- Tests must be written using pytest

## Commit Guidelines

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Changes that do not affect code meaning (whitespace, formatting, etc.)
- **refactor**: Code changes that neither fix bugs nor add features
- **perf**: Performance improvements
- **test**: Adding or fixing tests
- **build**: Changes to the build system or external dependencies
- **ci**: Changes to CI configuration files
- **chore**: Other changes that don't modify src or test files

### Examples

```
feat(api): add endpoint for user search

fix(parser): resolve memory issue with large inputs

docs: update README with latest examples
```

## Pull Request Process

1. Make sure your code follows the coding standards
2. Run all tests and checks
3. Create a PR following the [provided template](PULL_REQUEST_TEMPLATE.md)
4. Wait for review from maintainers
5. Address all comments and change requests
6. After approval, a maintainer will merge your PR

## Reporting Bugs

To report bugs, use the [bug report issue template](ISSUE_TEMPLATE/bug_report.md) and provide:

- A clear and concise description of the bug
- Detailed steps to reproduce the issue
- Expected behavior and observed behavior
- Screenshots, logs, or other relevant details
- Environment (operating system, Python version, etc.)

## Requesting Features

To request new features, use the [feature request issue template](ISSUE_TEMPLATE/feature_request.md) and provide:

- A clear description of the requested feature
- Justification for the feature (why it's necessary/useful)
- Possible implementations or ideas
- Acceptance criteria

## Project Structure

The ARARA project is organized as follows:

```
arara/
├── capabilities/   # Capabilities for neural agents
├── clients/        # Clients for different LLMs and APIs
├── cognitions/     # Cognition modules
├── components/     # Reusable base components
├── io/             # Input/output and communication
├── logger/         # Logging utilities
├── agents/         # Agents implementations
├── notebooks/      # Example notebooks
└── scripts/        # Utility scripts
```

Familiarize yourself with this structure to understand where your contribution fits best.

## Questions?

If you have questions about the contribution process, open an issue with the "question" tag or contact the maintainers.

Thank you for contributing to ARARA!
