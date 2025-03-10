# Basic Usage

This guide will help you get started with the NEURON framework by creating a simple recommendation agent.

## Creating Your First Neuron

Here's how to create a basic recommendation agent using NEURON:

```python
from neuron.neurons import Neuron
from neuron.capabilities import EpisodicMemoryCapability
from neuron.clients import ClientWrapper

# Initialize LLM client
client = ClientWrapper(provider="groq", model="llama3-70b-8192")

# Create a simple recommendation neuron
recommender = Neuron(
    name="SimpleRecommender",
    client=client,
    capabilities=[
        EpisodicMemoryCapability()  # Add memory capability
    ]
)

# Use the neuron to process a request
response = recommender.process("I need a recommendation for a laptop for video editing.")
print(response)
```

## Core Components

### Neurons

Neurons are the fundamental agents in the framework:

```python
from neuron.neurons import Neuron, RouterNeuron

# Create a basic neuron
basic_neuron = Neuron(name="BasicNeuron", client=client)

# Create a router neuron that can direct requests to different neurons
router = RouterNeuron(
    name="Router",
    client=client,
    neurons=[neuron1, neuron2, neuron3]
)
```

### Capabilities

Capabilities extend neuron functionality:

```python
from neuron.capabilities import (
    EpisodicMemoryCapability,
    ReflectionCapability,
    SharedMemoryIOCapability
)

# Create a neuron with multiple capabilities
advanced_neuron = Neuron(
    name="AdvancedNeuron",
    client=client,
    capabilities=[
        EpisodicMemoryCapability(),          # Store conversation history
        ReflectionCapability(),              # Self-improvement
        SharedMemoryIOCapability(scope="global")  # Share memory with other neurons
    ]
)
```

### Clients

Clients provide access to LLM providers:

```python
from neuron.clients import ClientWrapper

# Create a client for Groq
groq_client = ClientWrapper(
    provider="groq",
    model="llama3-70b-8192",
    api_key="your_api_key"  # Optional if in environment variables
)

# Configure additional parameters
client_with_options = ClientWrapper(
    provider="groq",
    model="llama3-70b-8192",
    temperature=0.7,
    max_tokens=2048
)
```

## Processing User Requests

```python
# Simple processing
result = neuron.process("What are good books on machine learning?")

# Processing with context
context = {"user_preferences": {"genre": "sci-fi", "length": "short"}}
result = neuron.process("Recommend me a book.", context=context)

# Processing with streaming response
for chunk in neuron.process_stream("Tell me about deep learning."):
    print(chunk, end="", flush=True)
```

## Working with Multiple Neurons

Create a multi-agent system:

```python
from neuron.neurons import Neuron, RouterNeuron

# Create specialized neurons
researcher = Neuron(name="Researcher", client=client)
analyzer = Neuron(name="Analyzer", client=client)
recommender = Neuron(name="Recommender", client=client)

# Create a router to coordinate them
system = RouterNeuron(
    name="RecommendationSystem",
    client=client,
    neurons=[researcher, analyzer, recommender]
)

# Process a request through the entire system
result = system.process("I need a new smartphone with good camera quality.")
```

## Next Steps

- See the [Architecture Documentation](architecture.md) for a deeper understanding
- Check out the [Example Use Cases](examples/) for more advanced scenarios
- Learn about [Extending NEURON](extending.md) with custom capabilities
