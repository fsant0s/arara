# Installation Guide

This guide will help you set up the NEURON framework in your development environment.

## Prerequisites

Before installing NEURON, ensure you have:

- Python 3.12 or higher
- Git
- A package manager (preferably [uv](https://github.com/astral-sh/uv))

## Installation Methods

### Method 1: Automatic Setup (Recommended)

NEURON includes a script to automatically set up your development environment:

```bash
# Clone the repository
git clone https://github.com/fsant0s/neuron.git
cd neuron

# Run the setup script
./scripts/setup_dev_env.sh
```

This script will:
1. Create a virtual environment
2. Install all required dependencies
3. Configure pre-commit hooks
4. Set up the basic test structure

### Method 2: Manual Installation

If you prefer to set up manually:

```bash
# Clone the repository
git clone https://github.com/fsant0s/neuron.git
cd neuron

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package in development mode
uv pip install -e .

# Install development dependencies
uv pip install ipykernel pytest pytest-cov black isort flake8 mypy
```

## Environment Configuration

NEURON requires API keys for the LLM services you'll be using. Set up your environment variables:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your API keys and other configuration:
   ```
   # LLM Service API Keys
   GROQ_API_KEY=your_groq_api_key_here

   # Additional configuration
   LOG_LEVEL=INFO
   ```

## Verify Installation

To verify that NEURON is installed correctly:

```bash
# Activate your virtual environment if it's not already activated
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the tests
pytest
```

If all tests pass, your installation is working correctly.

## Next Steps

Now that you have NEURON installed, you can:

- Continue to [Basic Usage](basic_usage.md) to create your first neural agent
- Explore the [Architecture](architecture.md) to understand how NEURON works
- Check out the examples in the [notebooks](../notebooks/) directory
