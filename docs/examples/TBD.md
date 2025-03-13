# Product Recommendation Example

This example demonstrates how to build a product recommendation system using NEURON.

## Basic Product Recommender

Here's a simple product recommendation agent:

```python
from neuron.neurons import Neuron
from neuron.capabilities import EpisodicMemoryCapability, ReflectionCapability
from neuron.clients import ClientWrapper

# Initialize client
client = ClientWrapper(provider="groq", model="llama3-70b-8192")

# Create product recommender
product_recommender = Neuron(
    name="ProductRecommender",
    client=client,
    capabilities=[
        EpisodicMemoryCapability(),  # Remember past interactions
        ReflectionCapability()       # Self-improvement
    ]
)

# Process a user query
user_query = "I'm looking for a new laptop for programming and occasional gaming under $1200."
recommendation = product_recommender.process(user_query)
print(recommendation)
```

## Advanced Multi-Agent Recommender

For more sophisticated recommendations, we can build a multi-agent system:

```python
from neuron.neurons import Neuron, RouterNeuron
from neuron.capabilities import (
    EpisodicMemoryCapability,
    ReflectionCapability,
    SharedMemoryIOCapability,
    DataFrameRetrieverCapability
)
from neuron.clients import ClientWrapper

# Initialize client
client = ClientWrapper(provider="groq", model="llama3-70b-8192")

# Create product catalog accessor
catalog = DataFrameRetrieverCapability(data_source="product_catalog.csv")

# Create specialized agents
user_profiler = Neuron(
    name="UserProfiler",
    client=client,
    capabilities=[
        EpisodicMemoryCapability(),
        SharedMemoryIOCapability(scope="global")
    ],
    system_prompt="Analyze user requests to understand their preferences, needs, and constraints."
)

product_researcher = Neuron(
    name="ProductResearcher",
    client=client,
    capabilities=[
        SharedMemoryIOCapability(scope="global"),
        catalog
    ],
    system_prompt="Research products from the catalog that match user requirements."
)

recommendation_generator = Neuron(
    name="RecommendationGenerator",
    client=client,
    capabilities=[
        SharedMemoryIOCapability(scope="global"),
        ReflectionCapability()
    ],
    system_prompt="Generate personalized product recommendations with explanations."
)

# Create the multi-agent system
recommendation_system = RouterNeuron(
    name="RecommendationSystem",
    client=client,
    neurons=[user_profiler, product_researcher, recommendation_generator],
    routing_strategy="round_robin"  # Process through each agent in sequence
)

# Process a complex request
user_query = """
I'm a software developer looking for a laptop with at least 16GB RAM,
good battery life, and a crisp display for coding. I occasionally play
games like Minecraft and Valorant, but gaming isn't my primary concern.
My budget is around $1500.
"""

recommendation = recommendation_system.process(user_query)
print(recommendation)
```

## Handling User Feedback

We can enhance our recommendation system by incorporating user feedback:

```python
# Initial recommendation
initial_recommendation = recommendation_system.process(user_query)
print("Initial recommendation:", initial_recommendation)

# Process user feedback
user_feedback = "I'd prefer something with better battery life, even if it means sacrificing some gaming performance."

# Update the system with feedback
updated_recommendation = recommendation_system.process(
    user_feedback,
    context={"previous_recommendation": initial_recommendation}
)
print("Updated recommendation:", updated_recommendation)
```

## Production Considerations

When deploying to production, consider these enhancements:

1. **Persistent Storage**:
   ```python
   from neuron.capabilities import EpisodicMemoryCapability

   persistent_memory = EpisodicMemoryCapability(
       storage_type="database",
       connection_string="postgresql://user:password@localhost/recommender"
   )
   ```

2. **Monitoring and Logging**:
   ```python
   import logging
   from neuron.logger import configure_logging

   configure_logging(level=logging.INFO)
   ```

3. **Rate Limiting**:
   ```python
   from neuron.clients import ClientWrapper

   client = ClientWrapper(
       provider="groq",
       model="llama3-70b-8192",
       rate_limit=60  # requests per minute
   )
   ```

4. **Fallback Mechanisms**:
   ```python
   try:
       recommendation = recommendation_system.process(user_query)
   except Exception as e:
       logging.error(f"Primary system failed: {e}")
       recommendation = fallback_system.process(user_query)
   ```

## Complete Example

For a complete implementation including product catalog integration, user profiles, and feedback handling, see the Jupyter notebook in the [notebooks directory](../../notebooks/product_recommendation.ipynb).
