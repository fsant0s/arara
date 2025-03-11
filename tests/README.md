# NEURON Project Tests

This directory contains tests for the NEURON project, organized into different categories to ensure code quality and reliability.

## Directory Structure

- `unit/`: Unit tests for individual components
- `integration/`: Integration tests to verify interaction between components
- `conftest.py`: Shared fixtures for use across all tests

## Running Tests

To run all tests and generate coverage reports, use the provided script:

```bash
./scripts/run_tests.sh
```

Alternatively, you can run specific tests using pytest directly:

```bash
# Run only unit tests
python -m pytest tests/unit -v

# Run only integration tests
python -m pytest tests/integration -v

# Run a specific test file
python -m pytest tests/unit/test_neuron.py -v

# Run with coverage
python -m pytest tests/unit -v --cov=neuron
```

## Available Fixtures

The `conftest.py` file defines several useful fixtures for testing:

- `mock_client`: A mock client for testing without real API calls
- `basic_neuron`: A basic Neuron instance
- `memory_neuron`: A Neuron with episodic memory capability
- `advanced_neuron`: A Neuron with multiple capabilities
- `user`: A User instance for testing
- `conversation_history`: A sample conversation history
- `preset_responses`: Predefined responses for testing
- `mock_client_with_preset_responses`: A mock client with predefined responses

## Mock Client

For tests that should not make real API calls, use the `MockClient` available in `tests/unit/mock_client.py`. This client simulates responses and allows verification of calls made during tests.

## Adding New Tests

When adding new tests:

1. Follow the existing directory structure
2. Use available fixtures whenever possible
3. Keep unit tests focused on individual components
4. Use integration tests to verify interaction between components
5. Ensure tests are independent and do not depend on the state of other tests
