from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, Union, Sequence
from ..tools import Tool, ToolSchema

class BaseClient(Protocol):
    """
    A client class must implement the following methods:
    - create must return a response object that implements the BaseClientResponseProtocol
    - cost must return the cost of the response
    - get_usage must return a dict with the following keys:
        - prompt_tokens
        - completion_tokens
        - total_tokens
        - cost
        - model

    This class is used to create a client that can be used by BaseClient.
    The response returned from create must adhere to the BaseClientResponseProtocol but can be extended however needed.
    The message_retrieval method must be implemented to return a list of str or a list of messages from the response.
    """

    RESPONSE_USAGE_KEYS = [
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "cost",
        "model",
    ]

    class BaseClientResponseProtocol(Protocol):
        class Choice(Protocol):
            class Message(Protocol):
                content: Optional[str]

            message: Message

        choices: List[Choice]
        model: str

    def create(self, params: Dict[str, Any]) -> BaseClientResponseProtocol: ...  # pragma: no cover

    def message_retrieval(
        self, response: BaseClientResponseProtocol
    ) -> Union[List[str], List[BaseClient.BaseClientResponseProtocol.Choice.Message]]:
        """
        Retrieve and return a list of strings or a list of Choice.Message from the response.

        NOTE: if a list of Choice.Message is returned, it currently needs to contain the fields of OpenAI's ChatCompletion Message object,
        since that is expected for function or tool calling in the rest of the codebase at the moment, unless a custom neuron is being used.
        """
        return response.content

    def cost(self, response: BaseClientResponseProtocol) -> float:
        return response.cost

    @staticmethod
    def get_usage(response: BaseClientResponseProtocol) -> Dict:
        """Return usage summary of the response using RESPONSE_USAGE_KEYS."""
        return {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "cost": response.cost,
            "model": response.model_name,
        }

    def convert_tools(tools: Sequence[Tool | ToolSchema],) -> List[Dict[str, Union[str, Dict]]]: ...
