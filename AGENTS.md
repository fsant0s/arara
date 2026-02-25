# AGENTS.md

## Cursor Cloud specific instructions

### Project overview
ARARA is a Python 3.12.6 multi-agent framework for conversational recommendation systems. Source code lives under `src/` (installed as editable package). No external databases or services are required — unit tests use mocks and caching defaults to file-based DiskCache.

### Running commands
Activate the virtual environment before running any command: `source .venv/bin/activate`

### Key commands
- **Lint**: `black --check src/ tests/`, `isort --check-only src/ tests/`, `flake8 src/ tests/ --max-line-length=100 --exclude=.git,__pycache__,build,dist --ignore=E203,W503,D100,D104`
- **Type check**: `mypy --config-file pyproject.toml src/`
- **Tests**: `pytest tests/unit -v --ignore=tests/unit/test_agent.py` (see known issues below)
- **Format code**: `black src/ tests/ && isort src/ tests/`
- See `scripts/` directory for helper shell scripts (format, test, type-check, security).

### Known issues
- `tests/unit/test_agent.py` has a broken relative import (`from ....arara.src.agents import Agent`) and will fail collection. Exclude it when running the test suite.
- The `agents` module has circular imports between `llm_messages.py` → `agents.types` → `agents.__init__` → `agents.agent` → `agent_messages.py` → `llm_messages.py`. Individual sub-modules (e.g. `cache`, `security_utils`, `function_utils`, `monitoring`) import cleanly.
- The existing codebase has pre-existing black/isort/flake8/mypy violations. These are not regressions.

### Dependency management
Uses `uv` with a lockfile (`uv.lock`). To install/refresh: `uv sync --extra dev`. The `uv pip install -e ".[dev]"` command also works but `uv sync --extra dev` uses the lockfile for reproducible installs.

### LLM API keys
End-to-end agent flows require at least one LLM API key (GROQ_API_KEY, OPENAI_API_KEY, COHERE_API_KEY) set in a `.env` file. Unit tests do not require any API keys.
