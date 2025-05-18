"""
Example module demonstrating how to mark features as experimental.

This module shows how to use the experimental decorator to mark features
that are not yet considered stable parts of the public API.
"""

from typing import Any, Dict, List, Optional

from api_utils import experimental


@experimental
class ExperimentalMonitor:
    """
    An experimental monitoring class that provides advanced metrics.

    This class is marked as experimental, meaning it may change or be removed
    in future versions without following the standard deprecation process.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the experimental monitor.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.metrics: List[Dict[str, Any]] = []

    def track_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Track an event with associated data.

        Args:
            event_type: Type of event to track
            data: Associated event data
        """
        self.metrics.append({"type": event_type, "data": data})

    def get_metrics(self) -> List[Dict[str, Any]]:
        """
        Get all tracked metrics.

        Returns:
            List of tracked metrics
        """
        return self.metrics


@experimental(
    alternative="use_standard_calculation()",
    message="This implementation is subject to change as we optimize the algorithm.",
)
def calculate_complexity(input_data: Dict[str, Any]) -> float:
    """
    An experimental function to calculate complexity of input data.

    Args:
        input_data: Input data to analyze

    Returns:
        Complexity score between 0.0 and 1.0
    """
    # Simplified example implementation
    fields = len(input_data)
    depth = _calculate_nested_depth(input_data)
    return min(1.0, (fields * depth) / 100.0)


def _calculate_nested_depth(data: Dict[str, Any], current_depth: int = 1) -> int:
    """
    Calculate the maximum nesting depth of a dictionary.

    This is an internal helper function and not part of the public API.

    Args:
        data: Dictionary to analyze
        current_depth: Current nesting depth

    Returns:
        Maximum nesting depth
    """
    max_depth = current_depth

    for value in data.values():
        if isinstance(value, dict):
            depth = _calculate_nested_depth(value, current_depth + 1)
            max_depth = max(max_depth, depth)

    return max_depth
