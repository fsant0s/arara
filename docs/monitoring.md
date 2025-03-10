# Monitoring and Observability

The NEURON framework includes comprehensive monitoring and observability features to help track performance, diagnose issues, and understand system behavior in production environments.

## Logging System

NEURON provides an enhanced logging system that adds contextual information to log entries, making it easier to trace requests and understand system behavior.

### Enhanced Contextual Logging

The enhanced logger automatically adds useful context to each log entry:

- Request IDs for tracking operations through the system
- Timestamp and hostname information
- Source file, line number, and function name
- Custom context data relevant to the operation

```python
from neuron.logger.enhanced_logger import get_logger

# Get a logger for a specific component
logger = get_logger("my_component")

# Add custom context to all log messages from this logger
user_logger = logger.with_context(user_id="123", session_id="abc456")

# Log with additional context for this specific message
user_logger.info("Processing user request",
                 input_size=1024,
                 features=["recommendation", "personalization"])
```

### Log Operation Decorator

You can easily instrument functions with comprehensive logging using the `log_operation` decorator:

```python
from neuron.logger.enhanced_logger import log_operation, get_logger

logger = get_logger("my_service")

@log_operation(logger)
def process_recommendation(user_id: str, preferences: list):
    # Function implementation
    # ...
    return results
```

This decorator automatically:
- Logs the start of the operation with arguments
- Measures execution time
- Logs successful completion with timing information
- Captures and logs exceptions with full stack traces

## Performance Metrics

NEURON's metrics collector provides tools for measuring and analyzing performance metrics.

### Measuring Operation Times

The `measure_time` decorator automatically tracks execution time for operations:

```python
from neuron.monitoring.metrics import measure_time

@measure_time("llm_inference")
def get_llm_response(prompt: str):
    # LLM operation here
    # ...
    return response
```

### Counting Operations

You can track how many times specific operations are performed:

```python
from neuron.monitoring.metrics import count_operation

@count_operation("database_query")
def fetch_user_data(user_id: str):
    # Database query
    # ...
    return user_data
```

### Resource Monitoring

NEURON can monitor system resource usage in real-time:

```python
from neuron.monitoring.metrics import metrics_collector

# Start monitoring resources (CPU, memory) every 10 seconds
metrics_collector.start_resource_monitoring(interval_seconds=10.0)

# Later, get resource usage data
metrics = metrics_collector.get_all_metrics()
resource_usage = metrics["resource_usage"]

# Stop monitoring when no longer needed
metrics_collector.stop_resource_monitoring()
```

## Integration Example

Here's a complete example that combines logging and metrics:

```python
import logging
from neuron.logger.enhanced_logger import get_logger, configure_all_loggers, log_operation
from neuron.monitoring.metrics import measure_time, count_operation, metrics_collector

# Configure logging for the application
configure_all_loggers(
    level=logging.INFO,
    log_file="logs/application.log",
    console=True
)

# Get a logger for this component
logger = get_logger("recommendation_service")

# Start resource monitoring
metrics_collector.start_resource_monitoring()

@measure_time("recommendation_generation")
@count_operation("recommendation_request")
@log_operation(logger)
def generate_recommendations(user_id: str, limit: int = 10):
    logger.info(f"Generating recommendations for user",
               user_id=user_id,
               limit=limit)

    # Implementation...

    return recommendations

# Application shutdown
def shutdown():
    # Get final metrics
    metrics = metrics_collector.get_all_metrics()

    # Log performance information
    avg_time = metrics["response_times"]["recommendation_generation"]["avg"]
    count = metrics["operation_counts"]["recommendation_request"]
    logger.info(f"Application shutting down",
               avg_recommendation_time_ms=avg_time,
               total_recommendations=count)

    # Stop monitoring
    metrics_collector.stop_resource_monitoring()
```

## Best Practices

1. **Use Contextual Logging**: Add relevant context to log messages to make debugging easier
2. **Instrument Critical Paths**: Apply monitoring to performance-critical operations
3. **Set Appropriate Log Levels**: Use DEBUG for development, INFO for production
4. **Monitor Resource Usage**: Track CPU and memory during development to identify potential issues
5. **Add Request IDs**: Use request IDs to track operations across distributed systems
