"""
Mock implementation of a agent for testing purposes.
"""

from typing import Any, Callable, Dict, List, Optional

from src.agents.base import BaseAgent


class MockAgent(BaseAgent):
    """
    A simple mock implementation of BaseAgent for testing.
    """

    def __init__(self, name: str = "MockAgent"):
        """Initialize a mock src."""
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
        """Get the agent's name."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Set the agent's name."""
        self._name = value

    @property
    def description(self) -> str:
        """Get the agent's description."""
        return "A mock agent for testing"

    def register_hook(self, hookable_method: str, hook: Callable):
        """Register a hook for the specified method."""
        if hookable_method not in self.hook_lists:
            self.hook_lists[hookable_method] = []
        self.hook_lists[hookable_method].append(hook)

    def send(
        self,
        message: Any,
        recipient: "BaseAgent",
        request_reply: bool = False,
        silent: bool = False,
    ):
        """Mock sending a message to another src."""
        self.messages_sent.append((message, recipient, silent))
        return "Mock response" if request_reply else None

    def receive(
        self,
        message: Any,
        sender: "BaseAgent",
        request_reply: bool = False,
        silent: bool = False,
    ):
        """Mock receiving a message from another src."""
        self.messages_received.append((message, sender))
        return "Mock reply" if request_reply else None

    def generate_reply(self, message: str) -> str:
        """Generate a mock reply to a message."""
        return "This is a mock reply."
