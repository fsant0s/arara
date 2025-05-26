# ARARA
A Multi-Agent Framework for Conversational Recommendation System with Large Language Models

## Overview

ARARA is a modular framework designed to build complex agent-based recommendation systems. It leverages the power of Large Language Models (LLMs) through a flexible architecture of interconnected agents with specialized capabilities.

Key features:
- **Modular Architecture**: Build systems using interconnected agents with specialized roles
- **Memory Capabilities**: Episodic memory and shared memory for enhanced context awareness
- **Reflection Mechanisms**: Self-improvement through introspection and error analysis
- **Flexible LLM Integration**: Support for multiple LLM providers (OpenAI, Groq, etc.)
- **Extensible Design**: Easily add custom capabilities and LLM providers

## Architecture

ARARA follows a modular architecture organized around these key components:

```
src/
├── agents/         # Core agents implementations
├── capabilities/    # Specialized abilities for agents
├── clients/         # LLM provider integrations
├── cognitions/      # Higher-level thinking processes
├── components/      # Reusable building blocks
├── logger/          # Logging utilities
└── io/              # Input/output handling
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      Application                         │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                    ARARA Framework                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Agents   │◄─┤Capabilities│ │Cognitions│ │Components│ │
│  └────┬─────┘  └──────────┘  └──────────┘  └──────────┘ │
│       │        ┌──────────┐                             │
│       ├───────►│    IO    │                             │
│       │        └──────────┘                             │
│  ┌────▼─────┐                    ┌──────────┐           │
│  │ Clients  │────────────────────► Logger   │           │
│  └────┬─────┘                    └──────────┘           │
└───────┼─────────────────────────────────────────────────┘
        │
┌───────▼─────────────────────────────────────────────────┐
│                    LLM Providers                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  OpenAI  │  │   Groq   │  │ Anthropic│  │  Custom  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Use Cases

ARARA is designed for building sophisticated recommendation systems in various domains:

1. **E-commerce Product Recommendations**
   - Personalized product recommendations based on user preferences
   - Cross-sells and up-sells with contextual awareness

2. **Content Recommendation Systems**
   - Article and media recommendations with understanding of content themes
   - Learning user preferences through interactions

3. **Knowledge Discovery**
   - Research assistance with relevant document identification
   - Connecting related pieces of information across databases

4. **Expert Systems**
   - Domain-specific advice based on specialized knowledge
   - Multi-agent collaboration for complex problem solving

## Quick Start Example

Here's a simple example of creating a basic recommendation agent:

```python
from agents import Agent
from capabilities import EpisodicMemoryCapability, ReflectionCapability

# Configure LLM client
client = ClientWrapper(provider="groq", model="llama3-70b-8192")

# Create a recommendation agent with memory and reflection
recommender = Agent(
    name="ProductRecommender",
    client=client,
    capabilities=[
        EpisodicMemoryCapability(),
        ReflectionCapability()
    ]
)

# Use the recommender
user_query = "I'm looking for a smartphone with good battery life under $500"
recommendations = recommender.process(user_query)
print(recommendations)
```

For more complex examples, see the [notebooks](notebooks/) directory.

## Run Locally

Clone the project

~~~bash
  git clone https://github.com/fsant0s/arara.git
~~~

Go to the project directory

~~~bash
  cd arara
~~~

### Install dependencies

First, ensure you have Python 3.12 and the uv package manager installed.

To set up the development environment automatically:

~~~bash
./scripts/setup_dev_env.sh
~~~

This script will:
1. Create a virtual environment
2. Install all dependencies
3. Configure pre-commit hooks
4. Set up a basic test structure

Alternatively, install dependencies manually:

~~~bash
# Install package in development mode (without dev dependencies)
uv pip install -e .

# Install with development dependencies
uv pip install -e ".[dev]"
~~~

### Environment Configuration

Copy the example environment file and configure your LLM API keys:

```bash
cp .env.example .env
```

Edit the .env file with your API keys for the LLM services you're using.

## Dependencies

The ARARA project carefully manages its dependencies to ensure reproducibility and reliability.

- All production dependencies have fixed versions to guarantee consistent behavior
- Development dependencies are organized separately from production code
- For a detailed description of all dependencies, see [DEPENDENCIES.md](DEPENDENCIES.md)

## Development

### Code Style

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Code linting
- **mypy**: Type checking

Configuration for these tools is in the `pyproject.toml` file.

To run these tools:

~~~bash
# Format code
black .
isort .

# Check code
flake8 .
mypy .
~~~

### Testing

ARARA uses automated tests to ensure code quality and reliability:

- **Unit Tests**: Verify individual components
- **Integration Tests**: Validate interaction between components
- **Coverage Reports**: Monitor test coverage

To run all tests and generate coverage reports:

~~~bash
./scripts/run_tests.sh
~~~

For more details about the test structure and how to add new tests, see [tests/README.md](tests/README.md).

## Contributing

Contributions are always welcome!

See [CONTRIBUTING.md](CONTRIBUTING.md) for ways to get started.

Please adhere to this project's [Code of Conduct](CODE_OF_CONDUCT.md).

## Versioning and Releases

### Conventional Commits

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) pattern for commit messages, allowing automatic CHANGELOG generation and facilitating semantic versioning.

Basic format for commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common commit types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Changes that do not affect code meaning
- **refactor**: Code changes that neither fix bugs nor add features
- **perf**: Performance improvements
- **test**: Adding or fixing tests
- **build**: Changes to the build system or dependencies
- **ci**: Changes to CI configuration files

### Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/). For more details, see the [VERSIONING.md](VERSIONING.md) file.

### Versioning Scripts

The project includes scripts to facilitate version management:

- `scripts/bump_version.py`: Increments the project version (major, minor, patch)
- `scripts/generate_changelog.py`: Generates entries for CHANGELOG.md from commits

## Security

Security is a priority for the ARARA project. See [SECURITY.md](SECURITY.md) for details on:

- How we handle secure credentials
- Input validation practices
- Reporting security vulnerabilities

## License

[MIT](https://choosealicense.com/licenses/mit/)
