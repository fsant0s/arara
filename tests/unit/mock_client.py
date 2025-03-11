"""
Mock client for use in unit tests.
This client simulates responses without making actual API calls.
"""

from typing import Any, Dict, Generator, List, Optional, Union

from neuron.clients.base_client import BaseClient


class MockClient(BaseClient):
    """
    Mock client for testing purposes.
    This client allows setting predefined responses and records call history.
    """

    def __init__(self, responses: Optional[List[str]] = None):
        """
        Initialize the mock client with optional predefined responses.

        Args:
            responses: List of predefined string responses to return in sequence
        """
        self.calls = []
        self.responses = responses or ["Mock response"]
        self.current_response_index = 0

    def complete(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Return a mock completion response and record call details.

        Args:
            messages: List of message objects
            **kwargs: Additional arguments

        Returns:
            Dict containing a mock response with choices
        """
        self.calls.append({"messages": messages, "kwargs": kwargs})

        # Get the current response and increment the index
        response_text = self.responses[self.current_response_index % len(self.responses)]
        self.current_response_index += 1

        # Format the response like a real API response
        return {
            "id": "mock-completion-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "mock-model",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": response_text},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
        }

    def stream_complete(
        self, messages: List[Dict[str, Any]], **kwargs
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Yield mock streaming responses.
        Simulates streaming behavior by splitting responses into words.

        Args:
            messages: List of message objects
            **kwargs: Additional arguments

        Yields:
            Dict containing chunks of the mock response
        """
        self.calls.append({"messages": messages, "kwargs": kwargs, "streaming": True})

        # Get the current response and increment the index
        response_text = self.responses[self.current_response_index % len(self.responses)]
        self.current_response_index += 1

        # Split by words to simulate streaming
        words = response_text.split()

        for i, word in enumerate(words):
            yield {
                "id": f"mock-stream-id-{i}",
                "object": "chat.completion.chunk",
                "created": 1234567890 + i,
                "model": "mock-model",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": word + (" " if i < len(words) - 1 else "")},
                        "finish_reason": "stop" if i == len(words) - 1 else None,
                    }
                ],
            }

    def reset(self):
        """
        Reset the client's state.
        Clears call history and resets the response index.
        """
        self.calls = []
        self.current_response_index = 0

    def set_responses(self, responses: List[str]):
        """
        Set new predefined responses.

        Args:
            responses: New list of string responses
        """
        self.responses = responses
        self.current_response_index = 0
