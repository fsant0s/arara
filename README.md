<p align="center">
  <img src="logo.png" alt="ARARA Logo" width="120"/><br/>
  <strong style="font-size: 1.8em;">ARARA</strong><br/>
  <em>A Multi-Agent Framework for Conversational Recommendation Systems with Large Language Models</em>
</p>


## Overview

Several multi-agent frameworks have emerged recently — such as AutoGen, CrewAI, and LangGraph — aiming to coordinate LLM agents.
But here's the gap:

- ❌ No dialogue planning
- ❌ No memory-based decisions
- ❌ No user-intent alignment
- ❌ No modular, task-oriented orchestration
- ❌ ...and none are designed for **conversational recommendation** tasks

**ARARA** fills this gap.

It is a modular, extensible framework for orchestrating LLM-based agents in complex recommendation scenarios, especially those involving dialogue, memory, tools, and reflection.

### Key Features

- **Agent-based Dialogue Planning**: Dynamically selects the most suitable agent to respond based on dialogue context and user intent
- **Contextual Memory Integration**: Memory is treated as a first-class capability, enabling agents to retain and reason over relevant information
- **Introspective Agents**: Built-in reflection mechanisms allow agents to self-evaluate and adapt their behavior
- **Multi-LLM Support**: Compatible with Groq, OpenAI, and Maritaca.
- **Compositional Modularity**: Agents can operate independently or within orchestrated modules, promoting reusability and scalability
- **Conversational Recommendation Focus**: Designed specifically for multi-turn, personalized, dialogue-driven recommendation scenarios


---

## Architecture

<p align="center">
  <img src="https://github.com/fsant0s/arara/assets/architecture.png" alt="ARARA Architecture" width="600"/>
</p>

The ARARA architecture includes:

- **Single Agents** that respond directly to user prompts
- A central **Orchestrator Agent** that coordinates the interactionm
- **Modules**: groups of agents governed by internal orchestrators, designed to handle specific subtasks
- Decision flows for choosing who speaks next, invoking tools, using memory, and returning coherent responses to users

This structure allows for both horizontal and vertical scaling of agent-based workflows.

---

## Project Structure
The current structure of the `src/` directory in ARARA is organized as follows:

```
src/
├── agents/ # Core agent and orchestrator implementations
├── capabilities/ # Specialized capabilities for agents:
│ # ├── clients/: Wrappers and configs for LLM providers (e.g., OpenAI, Groq, Maritaca)
│ # ├── memory/: Implementations of memory mechanisms (short-term, episodic, etc.)
│ # ├── skills/: Built-in skills such as WebCrawler, WebSearch, Vision, etc.
│ # └── tools/: Tool execution and integration with external functions
├── ioflow/ # Input and output flow management
├── logger/ # Logging utilities for tracking and debugging
├── monitoring/ # Runtime monitoring and diagnostics
├── cache/ # Caching mechanisms and temporary data
```

This modular structure is designed to support:
- **Separation of responsibilities** across capabilities, execution flow, and logging
- **Scalability** through reusable and decoupled components
- **Ease of maintenance**, allowing new features and agents to be added independently


---

## Use Cases

ARARA is ideal for building **dialogue-driven recommendation systems**. Example applications include:

1. **Conversational E-commerce**
   - Agents that understand user preferences over multiple turns
   - Personalized product recommendations with contextual awareness

2. **Media and Content Discovery**
   - Systems that suggest articles, videos, or music based on ongoing user conversations
   - Adaptation through memory and feedback

3. **AI-Powered Research Assistants**
   - Multi-agent setups to retrieve, analyze, and recommend documents or data
   - Collaboration between explainer, retriever, and recommender agents

4. **Personalized Assistants**
   - Agents that track and recall preferences
   - Support proactive and reactive dialogue planning

5. **Conversational Recommender Systems Research**
- A modular experimentation environment for researchers working on conversational recommendation
- Facilitates evaluation of memory strategies, dialogue planning, and agent coordination


---

## Quick Start Example

Here’s a basic example from [`notebooks/memory.ipynb`](notebooks/memory.ipynb):

```python
from agents import Agent, User
from agents.scripted_users import UserMemory
from capabilities.memory import ListMemory, MemoryContent
import os

# LLM configuration
llm_config = {
    "config_list": [
        {
            "client": "groq",
            "temperature": 0.0,
            "model": "llama-3.3-70b-versatile",
            "api_key": os.getenv("GROQ_API_KEY")
        }
    ]
}

# Create memory
sequential_memory = ListMemory(name="chat_history")
sequential_memory.add(MemoryContent(content="User likes beef."))

# Example tool
def get_recipe(diet_type: str = "standard") -> str:
    if diet_type == "vegan":
        return "Chickpea pasta with sautéed vegetables"
    elif diet_type == "peanut":
        return "Thai peanut stir-fry"
    else:
        return "Creamy chicken alfredo"

# Create user and agent
user = UserMemory(name="user")
assistant = Agent(
    name="assistant_agent",
    llm_config=llm_config,
    tools=[get_recipe],
    memory=[sequential_memory],
)

# Ask a question
chat_result = user.talk_to(
    assistant_agent,
    message="Can you recommend me something for dinner?"
)
```

More advanced examples can be found in the `notebooks/` directory.

---

## Run Locally

Clone the repository:

```bash
git clone https://github.com/fsant0s/arara.git
cd arara
```

Install dependencies:

```bash
./scripts/setup_dev_env.sh
```

Or manually:

```bash
uv pip install -e ".[dev]"
```

Set up your environment:

```bash
cp .env.example .env
# Then edit .env with your API keys
```

---

## Dependencies

All production dependencies are version-pinned. Development and testing dependencies are optional and separated.

See [DEPENDENCIES.md](DEPENDENCIES.md) for a full list.

---

## Development

We follow strict code quality practices. Tools used:

- **Black**: Formatting
- **isort**: Import ordering
- **flake8**: Linting
- **mypy**: Static type checking

To apply:

```bash
black . && isort . && flake8 . && mypy .
```

---

## Testing

To run unit and integration tests with coverage:

```bash
./scripts/run_tests.sh
```

Details in [tests/README.md](tests/README.md).

---

## Contributing

We welcome contributions!

Please check:
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

---

## Versioning and Releases

We follow:

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

Scripts:

```bash
python scripts/bump_version.py
python scripts/generate_changelog.py
```

---

## Security

Security best practices and contact details are outlined in [SECURITY.md](SECURITY.md).

---

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).

> **Note**: ARARA is based on [AutoGen](https://github.com/microsoft/autogen) and respects its licensing model.
