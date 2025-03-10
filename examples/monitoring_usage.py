#!/usr/bin/env python3
"""
Example demonstrating usage of the NEURON monitoring and observability features.

This example shows how to:
1. Set up enhanced logging with contextual information
2. Use performance metrics for measuring operation timing
3. Monitor resource usage
4. Instrument code with decorators for automatic monitoring
"""

import logging
import time
import random
from pathlib import Path

from neuron.logger.enhanced_logger import (
    get_logger,
    configure_all_loggers,
    log_operation
)
from neuron.monitoring.metrics import (
    metrics_collector,
    measure_time,
    count_operation
)

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
configure_all_loggers(
    level=logging.INFO,
    log_file=str(log_dir / "monitoring_example.log"),
    console=True
)

# Get a contextual logger
logger = get_logger("monitoring_example")

# Add custom context to the logger
user_logger = logger.with_context(user_id="example_user", session_id="123456")


@measure_time("llm_operation")
@count_operation("llm_call")
def simulate_llm_api_call(prompt: str, model: str = "default", temperature: float = 0.7):
    """
    Simulate an LLM API call with random processing time.

    Args:
        prompt: The input prompt
        model: The model name
        temperature: Temperature parameter

    Returns:
        Simulated response
    """
    # Simulate variable response time
    processing_time = random.uniform(0.1, 1.5)
    time.sleep(processing_time)

    # Return a simple response
    return f"Simulated response to: {prompt}"


@log_operation(logger)
def process_user_request(request_id: str, input_text: str):
    """
    Process a user request with logging and metrics.

    Args:
        request_id: Unique request identifier
        input_text: User input text

    Returns:
        The processed result
    """
    logger.info(f"Processing request {request_id}",
               request_type="user_input",
               input_length=len(input_text))

    try:
        # Simulate request processing
        logger.debug(f"Preprocessing input text", input_length=len(input_text))

        # Simulate an API call
        response = simulate_llm_api_call(input_text, model="llama3-70b", temperature=0.5)

        # Simulate post-processing
        logger.debug(f"Post-processing response", response_length=len(response))

        return {
            "request_id": request_id,
            "result": response,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error processing request {request_id}: {str(e)}",
                    exc_info=True,
                    input_text=input_text)

        return {
            "request_id": request_id,
            "result": None,
            "status": "error",
            "error": str(e)
        }


def main():
    """Run the monitoring example."""
    # Start resource monitoring
    metrics_collector.start_resource_monitoring(interval_seconds=1.0)

    logger.info("Starting monitoring example")

    # Process several sample requests
    for i in range(5):
        request_id = f"req_{i+1}"
        input_text = f"Tell me about topic {i+1}"

        result = process_user_request(request_id, input_text)
        print(f"Request {i+1} result: {result['status']}")

        # Small pause between requests
        time.sleep(0.5)

    # Get and display metrics
    all_metrics = metrics_collector.get_all_metrics()
    print("\nPerformance Metrics:")
    print(f"  Total LLM calls: {metrics_collector.get_operation_count('llm_call')}")

    response_times = all_metrics["response_times"]
    if "llm_operation" in response_times:
        rt = response_times["llm_operation"]
        print(f"  LLM Operation: avg={rt['avg']:.2f}ms, min={rt['min']:.2f}ms, max={rt['max']:.2f}ms")

    # Stop resource monitoring
    metrics_collector.stop_resource_monitoring()

    logger.info("Completed monitoring example")


if __name__ == "__main__":
    main()
