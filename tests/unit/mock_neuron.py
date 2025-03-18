"""
Mock implementation of a neuron for testing purposes.
"""

from typing import Any, Callable, Dict, List, Optional

from neuron.neurons.base import BaseNeuron


class MockNeuron(BaseNeuron):
    """
    A simple mock implementation of BaseNeuron for testing.
    """

    def __init__(self, name: str = "MockNeuron"):
        """Initialize a mock neuron."""
        self.name = name
        self.messages_received = []
        self.messages_sent = []
        self.hook_lists = {
            "process_last_received_message": [],
            "process_message_before_send": [],
            "process_all_messages_before_reply": [],
        }

    @property
    def name(self) -> str:
        """Get the neuron's name."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Set the neuron's name."""
        self._name = value

    @property
    def description(self) -> str:
        """Get the neuron's description."""
        return "A mock neuron for testing"

    def register_hook(self, hookable_method: str, hook: Callable):
        """Register a hook for the specified method."""
        if hookable_method not in self.hook_lists:
            self.hook_lists[hookable_method] = []
        self.hook_lists[hookable_method].append(hook)

    def send(
        self,
        message: Any,
        recipient: "BaseNeuron",
        request_reply: bool = False,
        silent: bool = False,
    ):
        """Mock sending a message to another neuron."""
        self.messages_sent.append((message, recipient, silent))
        return "Mock response" if request_reply else None

    def receive(
        self,
        message: Any,
        sender: "BaseNeuron",
        request_reply: bool = False,
        silent: bool = False,
    ):
        """Mock receiving a message from another neuron."""
        self.messages_received.append((message, sender))
        return "Mock reply" if request_reply else None

    def generate_reply(self, message: str) -> str:
        """Generate a mock reply to a message."""
        return "This is a mock reply."
