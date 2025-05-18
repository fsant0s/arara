"""
Unit tests for the BaseClient protocol.

This module tests the functionality of the BaseClient protocol
and ensures that implementations follow the expected interface.
"""

import unittest
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from src.capabilities.clients.base import BaseClient


@dataclass
class MockMessage:
    """Mock implementation of the Message protocol."""

    content: Optional[str]


@dataclass
class MockChoice:
    """Mock implementation of the Choice protocol."""

    message: MockMessage


@dataclass
class MockUsage:
    """Mock implementation of Usage for responses."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class MockResponse:
    """Mock implementation of the BaseClientResponseProtocol."""

    choices: List[MockChoice]
    model: str
    usage: MockUsage
    cost: float


class MockBaseClient:
    """Mock implementation of BaseClient."""

    RESPONSE_USAGE_KEYS = BaseClient.RESPONSE_USAGE_KEYS

    def create(self, params: Dict[str, Any]) -> Any:
        """Create a mock response."""
        message = MockMessage(content=params.get("content", "Mock response"))
        choice = MockChoice(message=message)
        usage = MockUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        return MockResponse(
            choices=[choice],
            model=params.get("model", "mock-model"),
            usage=usage,
            cost=0.01,
        )

    def message_retrieval(self, response: Any) -> Union[List[str], List[Any]]:
        """Retrieve messages from the response."""
        return [choice.message for choice in response.choices]

    def cost(self, response: Any) -> float:
        """Return the cost of the response."""
        return response.cost

    @staticmethod
    def get_usage(response: Any) -> Dict:
        """Return usage summary of the response."""
        return {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "cost": response.cost,
            "model": response.model,
        }


class TestBaseClient(unittest.TestCase):
    """Tests for the BaseClient protocol."""

    def setUp(self):
        """Set up the test case."""
        self.client = MockBaseClient()
        self.params = {"content": "Test content", "model": "test-model"}

    def test_create(self):
        """Test that create returns a response with the expected structure."""
        response = self.client.create(self.params)

        # Verify response structure
        self.assertIsInstance(response, MockResponse)
        self.assertEqual(len(response.choices), 1)
        self.assertEqual(response.choices[0].message.content, "Test content")
        self.assertEqual(response.model, "test-model")

    def test_message_retrieval(self):
        """Test that message_retrieval returns the expected messages."""
        response = self.client.create(self.params)
        messages = self.client.message_retrieval(response)

        # Verify messages
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].content, "Test content")

    def test_cost(self):
        """Test that cost returns the cost of the response."""
        response = self.client.create(self.params)
        cost = self.client.cost(response)

        # Verify cost
        self.assertEqual(cost, 0.01)

    def test_get_usage(self):
        """Test that get_usage returns the usage summary with expected keys."""
        response = self.client.create(self.params)
        usage = self.client.get_usage(response)

        # Verify usage summary contains all required keys
        for key in BaseClient.RESPONSE_USAGE_KEYS:
            self.assertIn(key, usage)

        # Verify usage values
        self.assertEqual(usage["prompt_tokens"], 10)
        self.assertEqual(usage["completion_tokens"], 20)
        self.assertEqual(usage["total_tokens"], 30)
        self.assertEqual(usage["cost"], 0.01)
        self.assertEqual(usage["model"], "test-model")


if __name__ == "__main__":
    unittest.main()
