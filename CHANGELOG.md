# Changelog

All notable changes to the NEURON project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2025-03-10

### Added
- adicionar testes de integração e configurar CI/CD com GitHub Actions ([348f260](https://github.com/fsant0s/neuron/commit/348f260))
- add enhanced contextual logger with request tracking [logging] ([ba225b5](https://github.com/fsant0s/neuron/commit/ba225b5))
- add metrics collection system for performance monitoring [monitoring] ([d3bc816](https://github.com/fsant0s/neuron/commit/d3bc816))
- add security-specific exceptions ([232f3ca](https://github.com/fsant0s/neuron/commit/232f3ca))
- add security utilities for credential management ([57a5e38](https://github.com/fsant0s/neuron/commit/57a5e38))
- add security scanning script ([937ef88](https://github.com/fsant0s/neuron/commit/937ef88))
- add type checking script ([34fae88](https://github.com/fsant0s/neuron/commit/34fae88))
- add code formatting script ([ba286c1](https://github.com/fsant0s/neuron/commit/ba286c1))
- add script to automate version bumping ([360de4a](https://github.com/fsant0s/neuron/commit/360de4a))
- add script to automatically generate changelog entries ([ae9f37d](https://github.com/fsant0s/neuron/commit/ae9f37d))
- Initial executable version of NEURON ([601de97](https://github.com/fsant0s/neuron/commit/601de97))

### Fixed
- adicionar arquivo MockNeuron e corrigir testes ([179e431](https://github.com/fsant0s/neuron/commit/179e431))
- melhorar implementação do MockClient e corrigir imports ([9aeaf44](https://github.com/fsant0s/neuron/commit/9aeaf44))
- correções adicionais nos testes com neuron e episodic_memory ([4759034](https://github.com/fsant0s/neuron/commit/4759034))
- resolve test compatibility issues with updated code structure ([ba6fa3c](https://github.com/fsant0s/neuron/commit/ba6fa3c))

### Documentation
- update changelog ([d976e80](https://github.com/fsant0s/neuron/commit/d976e80))
- add standardized Google-style docstrings to Neuron class ([457b33f](https://github.com/fsant0s/neuron/commit/457b33f))
- set up MkDocs with comprehensive technical documentation ([ec8d776](https://github.com/fsant0s/neuron/commit/ec8d776))
- expand README with detailed project description, architecture, and examples ([cee30e6](https://github.com/fsant0s/neuron/commit/cee30e6))
- create CODE_OF_CONDUCT.md ([624f032](https://github.com/fsant0s/neuron/commit/624f032))
- add contributing document ([6c06479](https://github.com/fsant0s/neuron/commit/6c06479))
- add comprehensive security guidelines ([8fc021e](https://github.com/fsant0s/neuron/commit/8fc021e))
- enhance environment variable documentation ([bee8864](https://github.com/fsant0s/neuron/commit/bee8864))
- update README with dependency management and development instructions ([93d849d](https://github.com/fsant0s/neuron/commit/93d849d))
- add detailed dependency documentation ([d03ff8a](https://github.com/fsant0s/neuron/commit/d03ff8a))
- add versioning information to README.md ([802fb7f](https://github.com/fsant0s/neuron/commit/802fb7f))
- add initial CHANGELOG.md ([c57a7fc](https://github.com/fsant0s/neuron/commit/c57a7fc))
- add versioning policy documentation ([ff793ce](https://github.com/fsant0s/neuron/commit/ff793ce))

### Tests
- melhorar testes de runtime_logging para tratamento de exceções ([ea50c36](https://github.com/fsant0s/neuron/commit/ea50c36))
- atualizar testes do Neuron para refletir mudanças na API ([2f3226d](https://github.com/fsant0s/neuron/commit/2f3226d))
- adicionar arquivos de testes e configuração ([326132f](https://github.com/fsant0s/neuron/commit/326132f))
- implement comprehensive test suite for core components ([2c6b3d8](https://github.com/fsant0s/neuron/commit/2c6b3d8))

### Build
- update README.md and pyproject ([7f92981](https://github.com/fsant0s/neuron/commit/7f92981))
- create templates for issue (bug report, documentation e feature requests) ([35483f9](https://github.com/fsant0s/neuron/commit/35483f9))
- add linting and formatting configuration ([ebf2968](https://github.com/fsant0s/neuron/commit/ebf2968))
- add development environment setup script ([7e894b7](https://github.com/fsant0s/neuron/commit/7e894b7))
- pin exact dependency versions and add documentation ([f3ad21a](https://github.com/fsant0s/neuron/commit/f3ad21a))

### CI
- add automated security checking script ([d7de233](https://github.com/fsant0s/neuron/commit/d7de233))

### Maintenance
- update dependencies and documentation for monitoring system ([4f477ae](https://github.com/fsant0s/neuron/commit/4f477ae))
- add editor configurations for consistent code style ([93a930d](https://github.com/fsant0s/neuron/commit/93a930d))
- add detailed flake8 linter configuration ([8ff934c](https://github.com/fsant0s/neuron/commit/8ff934c))
- add bandit security scanner configuration ([9da700a](https://github.com/fsant0s/neuron/commit/9da700a))
- add pre-commit hooks configuration ([4f61c82](https://github.com/fsant0s/neuron/commit/4f61c82))
- translate to english ([4fb4dc3](https://github.com/fsant0s/neuron/commit/4fb4dc3))

### Others
- removing .env ([ea86a6b](https://github.com/fsant0s/neuron/commit/ea86a6b))
- "Add new tests in agent.py, assistant_agent, round_robin.py" ([44497f0](https://github.com/fsant0s/neuron/commit/44497f0))
- "Create partial test_round_robin.py" ([8468536](https://github.com/fsant0s/neuron/commit/8468536))
- "Create runtime_logging.py" ([0a18a92](https://github.com/fsant0s/neuron/commit/0a18a92))
- "Create test_formatting_utils.py and add formatcolor in the pyproject.toml" ([8c35648](https://github.com/fsant0s/neuron/commit/8c35648))
- "Create test for exception_utils.py" ([aa2ce01](https://github.com/fsant0s/neuron/commit/aa2ce01))
- "Add coverage and test case for code covarege" ([71ea124](https://github.com/fsant0s/neuron/commit/71ea124))
- "Configue github actions using codecov" ([0a9242b](https://github.com/fsant0s/neuron/commit/0a9242b))
- "Add requirements.txt generated by uv package manager" ([1800525](https://github.com/fsant0s/neuron/commit/1800525))
- "Update pyproject.toml" ([c48f392](https://github.com/fsant0s/neuron/commit/c48f392))
- "Add uv.lock and coverage" ([b42c59b](https://github.com/fsant0s/neuron/commit/b42c59b))
- "Fix incompatibility between .python-version and pyproject.toml" ([ab731ba](https://github.com/fsant0s/neuron/commit/ab731ba))
- "Add init project with uv package manager" ([942e88e](https://github.com/fsant0s/neuron/commit/942e88e))
- "Add minimal README.md" ([6c5ee6c](https://github.com/fsant0s/neuron/commit/6c5ee6c))
- "Set python version to 3.12.6" ([405c39e](https://github.com/fsant0s/neuron/commit/405c39e))
- feat/KnowledgeRepresenterAgent done ([f3f88b3](https://github.com/fsant0s/neuron/commit/f3f88b3))
- component and immediate short memory done. Missing: evaluator agent and test cycle using feature_imputer_agent ([165843e](https://github.com/fsant0s/neuron/commit/165843e))
- feat/KnowledgeRepresenterAgent done ([d434ccf](https://github.com/fsant0s/neuron/commit/d434ccf))
- second commit ([0991cf4](https://github.com/fsant0s/neuron/commit/0991cf4))
- First commit: ([9ac1d3a](https://github.com/fsant0s/neuron/commit/9ac1d3a))

## [0.1.0] - 2025-03-10

### Added
- add enhanced contextual logger with request tracking [logging] ([ba225b5](https://github.com/fsant0s/neuron/commit/ba225b5))
- add metrics collection system for performance monitoring [monitoring] ([d3bc816](https://github.com/fsant0s/neuron/commit/d3bc816))
- add security-specific exceptions ([232f3ca](https://github.com/fsant0s/neuron/commit/232f3ca))
- add security utilities for credential management ([57a5e38](https://github.com/fsant0s/neuron/commit/57a5e38))
- add security scanning script ([937ef88](https://github.com/fsant0s/neuron/commit/937ef88))
- add type checking script ([34fae88](https://github.com/fsant0s/neuron/commit/34fae88))
- add code formatting script ([ba286c1](https://github.com/fsant0s/neuron/commit/ba286c1))
- add script to automate version bumping ([360de4a](https://github.com/fsant0s/neuron/commit/360de4a))
- add script to automatically generate changelog entries ([ae9f37d](https://github.com/fsant0s/neuron/commit/ae9f37d))
- Initial executable version of NEURON ([601de97](https://github.com/fsant0s/neuron/commit/601de97))

### Documentation
- add standardized Google-style docstrings to Neuron class ([457b33f](https://github.com/fsant0s/neuron/commit/457b33f))
- set up MkDocs with comprehensive technical documentation ([ec8d776](https://github.com/fsant0s/neuron/commit/ec8d776))
- expand README with detailed project description, architecture, and examples ([cee30e6](https://github.com/fsant0s/neuron/commit/cee30e6))
- create CODE_OF_CONDUCT.md ([624f032](https://github.com/fsant0s/neuron/commit/624f032))
- add contributing document ([6c06479](https://github.com/fsant0s/neuron/commit/6c06479))
- add comprehensive security guidelines ([8fc021e](https://github.com/fsant0s/neuron/commit/8fc021e))
- enhance environment variable documentation ([bee8864](https://github.com/fsant0s/neuron/commit/bee8864))
- update README with dependency management and development instructions ([93d849d](https://github.com/fsant0s/neuron/commit/93d849d))
- add detailed dependency documentation ([d03ff8a](https://github.com/fsant0s/neuron/commit/d03ff8a))
- add versioning information to README.md ([802fb7f](https://github.com/fsant0s/neuron/commit/802fb7f))
- add initial CHANGELOG.md ([c57a7fc](https://github.com/fsant0s/neuron/commit/c57a7fc))
- add versioning policy documentation ([ff793ce](https://github.com/fsant0s/neuron/commit/ff793ce))

### Build
- create templates for issue (bug report, documentation e feature requests) ([35483f9](https://github.com/fsant0s/neuron/commit/35483f9))
- add linting and formatting configuration ([ebf2968](https://github.com/fsant0s/neuron/commit/ebf2968))
- add development environment setup script ([7e894b7](https://github.com/fsant0s/neuron/commit/7e894b7))
- pin exact dependency versions and add documentation ([f3ad21a](https://github.com/fsant0s/neuron/commit/f3ad21a))

### CI
- add automated security checking script ([d7de233](https://github.com/fsant0s/neuron/commit/d7de233))

### Maintenance
- update dependencies and documentation for monitoring system ([4f477ae](https://github.com/fsant0s/neuron/commit/4f477ae))
- add editor configurations for consistent code style ([93a930d](https://github.com/fsant0s/neuron/commit/93a930d))
- add detailed flake8 linter configuration ([8ff934c](https://github.com/fsant0s/neuron/commit/8ff934c))
- add bandit security scanner configuration ([9da700a](https://github.com/fsant0s/neuron/commit/9da700a))
- add pre-commit hooks configuration ([4f61c82](https://github.com/fsant0s/neuron/commit/4f61c82))
- translate to english ([4fb4dc3](https://github.com/fsant0s/neuron/commit/4fb4dc3))

### Others
- removing .env ([ea86a6b](https://github.com/fsant0s/neuron/commit/ea86a6b))
- "Add new tests in agent.py, assistant_agent, round_robin.py" ([44497f0](https://github.com/fsant0s/neuron/commit/44497f0))
- "Create partial test_round_robin.py" ([8468536](https://github.com/fsant0s/neuron/commit/8468536))
- "Create runtime_logging.py" ([0a18a92](https://github.com/fsant0s/neuron/commit/0a18a92))
- "Create test_formatting_utils.py and add formatcolor in the pyproject.toml" ([8c35648](https://github.com/fsant0s/neuron/commit/8c35648))
- "Create test for exception_utils.py" ([aa2ce01](https://github.com/fsant0s/neuron/commit/aa2ce01))
- "Add coverage and test case for code covarege" ([71ea124](https://github.com/fsant0s/neuron/commit/71ea124))
- "Configue github actions using codecov" ([0a9242b](https://github.com/fsant0s/neuron/commit/0a9242b))
- "Add requirements.txt generated by uv package manager" ([1800525](https://github.com/fsant0s/neuron/commit/1800525))
- "Update pyproject.toml" ([c48f392](https://github.com/fsant0s/neuron/commit/c48f392))
- "Add uv.lock and coverage" ([b42c59b](https://github.com/fsant0s/neuron/commit/b42c59b))
- "Fix incompatibility between .python-version and pyproject.toml" ([ab731ba](https://github.com/fsant0s/neuron/commit/ab731ba))
- "Add init project with uv package manager" ([942e88e](https://github.com/fsant0s/neuron/commit/942e88e))
- "Add minimal README.md" ([6c5ee6c](https://github.com/fsant0s/neuron/commit/6c5ee6c))
- "Set python version to 3.12.6" ([405c39e](https://github.com/fsant0s/neuron/commit/405c39e))
- feat/KnowledgeRepresenterAgent done ([f3f88b3](https://github.com/fsant0s/neuron/commit/f3f88b3))
- component and immediate short memory done. Missing: evaluator agent and test cycle using feature_imputer_agent ([165843e](https://github.com/fsant0s/neuron/commit/165843e))
- feat/KnowledgeRepresenterAgent done ([d434ccf](https://github.com/fsant0s/neuron/commit/d434ccf))
- second commit ([0991cf4](https://github.com/fsant0s/neuron/commit/0991cf4))
- First commit: ([9ac1d3a](https://github.com/fsant0s/neuron/commit/9ac1d3a))

## [0.1.0] - 2025-03-10

### Added
- add script to automate version bumping ([360de4a](https://github.com/fsant0s/neuron/commit/360de4a))
- add script to automatically generate changelog entries ([ae9f37d](https://github.com/fsant0s/neuron/commit/ae9f37d))
- Initial executable version of NEURON ([601de97](https://github.com/fsant0s/neuron/commit/601de97))

### Documentation
- update README with dependency management and development instructions ([93d849d](https://github.com/fsant0s/neuron/commit/93d849d))
- add detailed dependency documentation ([d03ff8a](https://github.com/fsant0s/neuron/commit/d03ff8a))
- add versioning information to README.md ([802fb7f](https://github.com/fsant0s/neuron/commit/802fb7f))
- add initial CHANGELOG.md ([c57a7fc](https://github.com/fsant0s/neuron/commit/c57a7fc))
- add versioning policy documentation ([ff793ce](https://github.com/fsant0s/neuron/commit/ff793ce))

### Build
- add linting and formatting configuration ([ebf2968](https://github.com/fsant0s/neuron/commit/ebf2968))
- add development environment setup script ([7e894b7](https://github.com/fsant0s/neuron/commit/7e894b7))
- pin exact dependency versions and add documentation ([f3ad21a](https://github.com/fsant0s/neuron/commit/f3ad21a))

### Maintenance
- translate to english ([4fb4dc3](https://github.com/fsant0s/neuron/commit/4fb4dc3))

### Others
- removing .env ([ea86a6b](https://github.com/fsant0s/neuron/commit/ea86a6b))
- "Add new tests in agent.py, assistant_agent, round_robin.py" ([44497f0](https://github.com/fsant0s/neuron/commit/44497f0))
- "Create partial test_round_robin.py" ([8468536](https://github.com/fsant0s/neuron/commit/8468536))
- "Create runtime_logging.py" ([0a18a92](https://github.com/fsant0s/neuron/commit/0a18a92))
- "Create test_formatting_utils.py and add formatcolor in the pyproject.toml" ([8c35648](https://github.com/fsant0s/neuron/commit/8c35648))
- "Create test for exception_utils.py" ([aa2ce01](https://github.com/fsant0s/neuron/commit/aa2ce01))
- "Add coverage and test case for code covarege" ([71ea124](https://github.com/fsant0s/neuron/commit/71ea124))
- "Configue github actions using codecov" ([0a9242b](https://github.com/fsant0s/neuron/commit/0a9242b))
- "Add requirements.txt generated by uv package manager" ([1800525](https://github.com/fsant0s/neuron/commit/1800525))
- "Update pyproject.toml" ([c48f392](https://github.com/fsant0s/neuron/commit/c48f392))
- "Add uv.lock and coverage" ([b42c59b](https://github.com/fsant0s/neuron/commit/b42c59b))
- "Fix incompatibility between .python-version and pyproject.toml" ([ab731ba](https://github.com/fsant0s/neuron/commit/ab731ba))
- "Add init project with uv package manager" ([942e88e](https://github.com/fsant0s/neuron/commit/942e88e))
- "Add minimal README.md" ([6c5ee6c](https://github.com/fsant0s/neuron/commit/6c5ee6c))
- "Set python version to 3.12.6" ([405c39e](https://github.com/fsant0s/neuron/commit/405c39e))
- feat/KnowledgeRepresenterAgent done ([f3f88b3](https://github.com/fsant0s/neuron/commit/f3f88b3))
- component and immediate short memory done. Missing: evaluator agent and test cycle using feature_imputer_agent ([165843e](https://github.com/fsant0s/neuron/commit/165843e))
- feat/KnowledgeRepresenterAgent done ([d434ccf](https://github.com/fsant0s/neuron/commit/d434ccf))
- second commit ([0991cf4](https://github.com/fsant0s/neuron/commit/0991cf4))
- First commit: ([9ac1d3a](https://github.com/fsant0s/neuron/commit/9ac1d3a))

### Added
- Base framework for agent-based recommendation system
- Implementation of neurons for distributed processing
- Capabilities such as episodic memory, shared memory, and reflection
- Integration with LLM providers such as OpenAI and Groq
- Utilities for logging, formatting, and exception handling

### Changed

### Removed

### Fixed

### Security

## [0.1.0] - 2024-03-08

### Added
- Initial framework version
- Basic neuron structure
- Implementation of base capabilities
- Clients for LLM services
- Utilities for logging and formatting
