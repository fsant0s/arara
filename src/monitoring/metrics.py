"""
Metrics module for monitoring system performance.

This module provides utilities for measuring and tracking various performance metrics
of the ARARA framework, such as response times, resource usage, and operation counts.
"""

import logging
import os
import threading
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

import psutil

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects and manages performance metrics for the ARARA framework.

    This class provides methods to record, calculate, and report various performance metrics
    including response times, resource usage, and operation counts.
    """

    def __init__(self):
        """Initialize a new MetricsCollector."""
        self._response_times: Dict[str, List[float]] = {}
        self._operation_counts: Dict[str, int] = {}
        self._resource_usage: List[Dict[str, float]] = []
        self._lock = threading.Lock()
        self._resource_monitor_active = False
        self._resource_monitor_thread = None

    def record_response_time(self, operation_name: str, time_ms: float) -> None:
        """
        Record a response time for a specific operation.

        Args:
            operation_name: Name of the operation being measured
            time_ms: Time in milliseconds the operation took
        """
        with self._lock:
            if operation_name not in self._response_times:
                self._response_times[operation_name] = []
            self._response_times[operation_name].append(time_ms)

    def increment_operation_count(self, operation_name: str, count: int = 1) -> None:
        """
        Increment the count for a specific operation.

        Args:
            operation_name: Name of the operation being counted
            count: Amount to increment by (default: 1)
        """
        with self._lock:
            if operation_name not in self._operation_counts:
                self._operation_counts[operation_name] = 0
            self._operation_counts[operation_name] += count

    def get_average_response_time(self, operation_name: str) -> Optional[float]:
        """
        Get the average response time for a specific operation.

        Args:
            operation_name: Name of the operation

        Returns:
            Average response time in milliseconds or None if no data
        """
        with self._lock:
            if (
                operation_name not in self._response_times
                or not self._response_times[operation_name]
            ):
                return None

            return sum(self._response_times[operation_name]) / len(
                self._response_times[operation_name]
            )

    def get_operation_count(self, operation_name: str) -> int:
        """
        Get the count for a specific operation.

        Args:
            operation_name: Name of the operation

        Returns:
            Count of the operation
        """
        with self._lock:
            return self._operation_counts.get(operation_name, 0)

    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all collected metrics.

        Returns:
            Dictionary with all metrics data
        """
        with self._lock:
            metrics = {
                "response_times": {
                    op: {
                        "avg": sum(times) / len(times) if times else 0,
                        "min": min(times) if times else 0,
                        "max": max(times) if times else 0,
                        "count": len(times),
                    }
                    for op, times in self._response_times.items()
                },
                "operation_counts": dict(self._operation_counts),
                "resource_usage": (self._resource_usage[-10:] if self._resource_usage else []),
            }
            return metrics

    def clear_metrics(self) -> None:
        """Clear all collected metrics."""
        with self._lock:
            self._response_times = {}
            self._operation_counts = {}
            self._resource_usage = []

    def start_resource_monitoring(self, interval_seconds: float = 10.0) -> None:
        """
        Start monitoring system resources at regular intervals.

        Args:
            interval_seconds: Interval between measurements in seconds
        """
        if self._resource_monitor_active:
            logger.warning("Resource monitoring already active")
            return

        self._resource_monitor_active = True

        def monitor_resources():
            while self._resource_monitor_active:
                try:
                    process = psutil.Process(os.getpid())

                    # Get CPU and memory usage
                    cpu_percent = process.cpu_percent(interval=0.1)
                    memory_info = process.memory_info()
                    memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB

                    timestamp = datetime.now().isoformat()

                    with self._lock:
                        self._resource_usage.append(
                            {
                                "timestamp": timestamp,
                                "cpu_percent": cpu_percent,
                                "memory_mb": memory_mb,
                            }
                        )

                        # Limit the number of samples stored
                        if len(self._resource_usage) > 1000:
                            self._resource_usage = self._resource_usage[-1000:]

                except Exception as e:
                    logger.error(f"Error in resource monitoring: {e}")

                time.sleep(interval_seconds)

        self._resource_monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
        self._resource_monitor_thread.start()
        logger.info(f"Started resource monitoring at {interval_seconds}s intervals")

    def stop_resource_monitoring(self) -> None:
        """Stop the resource monitoring thread."""
        self._resource_monitor_active = False
        if self._resource_monitor_thread and self._resource_monitor_thread.is_alive():
            self._resource_monitor_thread.join(timeout=1.0)
            logger.info("Stopped resource monitoring")


# Global metrics collector instance
metrics_collector = MetricsCollector()


def measure_time(operation_name: Optional[str] = None):
    """
    Decorator to measure the execution time of a function.

    Args:
        operation_name: Custom name for the operation.
                       If None, the function name will be used.

    Returns:
        Decorated function that records timing metrics
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__

            # Record start time
            start_time = time.time()

            # Execute the function
            result = func(*args, **kwargs)

            # Calculate elapsed time in milliseconds
            elapsed_ms = (time.time() - start_time) * 1000

            # Record metrics
            metrics_collector.record_response_time(op_name, elapsed_ms)
            metrics_collector.increment_operation_count(op_name)

            # Log the timing information
            logger.debug(f"{op_name} executed in {elapsed_ms:.2f}ms")

            return result

        return wrapper

    return decorator


def count_operation(operation_name: Optional[str] = None):
    """
    Decorator to count the number of times a function is called.

    Args:
        operation_name: Custom name for the operation.
                       If None, the function name will be used.

    Returns:
        Decorated function that increments the operation count
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__

            # Increment count
            metrics_collector.increment_operation_count(op_name)

            # Execute the function
            return func(*args, **kwargs)

        return wrapper

    return decorator
