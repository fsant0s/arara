from __future__ import annotations

import copy
import json
import uuid
from typing import Any, Dict, List, Union

from ollama import Client

from agents.types import FunctionCall
from function_utils import normalize_stop_reason
from llm_messages import CreateResult, RequestUsage

from .base import BaseClient
from .utils.calculate_token_cost import calculate_token_cost
from .utils.convert_tools import convert_tools
from .utils.normalize_name import normalize_name
from .utils.should_hide_tools import should_hide_tools
from .utils.validate_parameter import validate_parameter


class OllamaClient(BaseClient):
    """Client for Ollama's API."""

    PROVIDER_NAME = "ollama"

    def __init__(self, **kwargs):
        """Initialize Ollama client.

        Args:
            host (str): Ollama host URL (default: http://127.0.0.1:11434)
            base_url (str): Alias for host parameter
            model_info (dict): Model information
        """
        super().__init__()

        self._model_info = kwargs.get("model_info", None)

        # Accept both host and base_url for compatibility
        self.host = kwargs.get("host", None)
        if self.host is None:
            self.host = kwargs.get("base_url", None)

        # Initialize Ollama client
        self.client = Client(host=self.host)

    def message_retrieval(self, response) -> List:
        """
        Retrieve and return a list of strings or a list of Choice.Message from the response.

        NOTE: if a list of Choice.Message is returned, it currently needs to contain the fields of OpenAI's ChatCompletion Message object,
        since that is expected for function or tool calling in the rest of the codebase at the moment, unless a custom agent is being used.
        """
        return [response.message.content]

    def parse_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Loads the parameters for Ollama API from the passed in parameters and returns a validated set. Checks types, ranges, and sets defaults"""
        ollama_params = {}

        # Check that we have what we need to use Ollama's API
        # We won't enforce the available models as they are likely to change
        ollama_params["model"] = params.get("model", None)
        assert ollama_params[
            "model"
        ], "Please specify the 'model' in your config list entry to nominate the Ollama model to use."

        # Validate allowed Ollama parameters and put them in options
        options = {}

        # Runtime options that go in the options object
        options["temperature"] = validate_parameter(
            params, "temperature", (int, float), True, 0.7, (0, 2), None
        )
        options["top_p"] = validate_parameter(
            params, "top_p", (int, float), True, None, (0, 1), None
        )
        options["top_k"] = validate_parameter(params, "top_k", int, True, None, (0, None), None)
        options["repeat_penalty"] = validate_parameter(
            params, "repeat_penalty", (int, float), True, None, (0, None), None
        )
        options["presence_penalty"] = validate_parameter(
            params, "presence_penalty", (int, float), True, None, (-2, 2), None
        )
        options["frequency_penalty"] = validate_parameter(
            params, "frequency_penalty", (int, float), True, None, (-2, 2), None
        )
        options["seed"] = validate_parameter(params, "seed", int, True, None, None, None)
        options["num_predict"] = validate_parameter(
            params, "num_predict", int, True, None, (0, None), None
        )
        options["stop"] = validate_parameter(params, "stop", (list, tuple), True, None, None, None)

        # Remove None values from options
        options = {k: v for k, v in options.items() if v is not None}

        # Add options to ollama_params if not empty
        if options:
            ollama_params["options"] = options

        # Direct parameters for the chat method
        ollama_params["stream"] = validate_parameter(
            params, "stream", bool, True, False, None, None
        )
        ollama_params["format"] = validate_parameter(
            params, "format", str, True, None, None, ["", "json"]
        )
        ollama_params["keep_alive"] = validate_parameter(
            params, "keep_alive", (int, float, str), True, None, None, None
        )
        ollama_params["think"] = validate_parameter(params, "think", bool, True, None, None, None)

        return ollama_params

    def create(self, params: Dict) -> CreateResult:
        """Create a chat completion using Ollama's API."""
        messages = params.get("messages", [])

        # Convert Arara messages to Ollama messages
        ollama_messages = self._oai_messages_to_ollama_messages(messages)

        # Parse parameters to the Ollama API's parameters
        ollama_params = self.parse_params(params)

        # Add tools to the call if we have them and aren't hiding them
        if "tools" in params:
            hide_tools = validate_parameter(
                params,
                "hide_tools",
                str,
                False,
                "never",
                None,
                ["if_all_run", "if_any_run", "never"],
            )
            if not should_hide_tools(ollama_messages, params["tools"], hide_tools):
                ollama_params["tools"] = convert_tools(params["tools"])

        ollama_params["messages"] = ollama_messages

        # Token counts will be returned (Ollama doesn't provide token counts by default)
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        # Streaming tool call recommendations
        content: Union[str, List[FunctionCall]]
        streaming_tool_calls = []
        response_content = None
        finish_reason = None
        thought: str | None = None

        try:
            response = self.client.chat(**ollama_params)
        except Exception as e:
            raise RuntimeError(f"Ollama exception occurred: {e}")
        else:
            if ollama_params["stream"]:
                # Read in the chunks as they stream, taking in tool_calls which may be across
                # multiple chunks if more than one suggested
                response_content = ""
                for chunk in response:
                    if chunk.message.content:
                        response_content = response_content + chunk.message.content

                    if hasattr(chunk.message, "tool_calls") and chunk.message.tool_calls:
                        # We have a tool call recommendation
                        for tool_call in chunk.message.tool_calls:
                            # Convert arguments to JSON string if it's a dict
                            arguments = tool_call.function.arguments
                            if isinstance(arguments, dict):
                                arguments = json.dumps(arguments)

                            streaming_tool_calls.append(
                                FunctionCall(
                                    id=str(uuid.uuid4()),
                                    arguments=arguments,
                                    name=normalize_name(tool_call.function.name),
                                )
                            )

                    if chunk.done:
                        # Ollama doesn't provide token counts in streaming mode
                        prompt_tokens = 0
                        completion_tokens = 0
                        total_tokens = 0
            else:
                # Non-streaming finished
                response_content = response.message.content or ""

                # Ollama doesn't provide token counts by default
                prompt_tokens = 0
                completion_tokens = 0
                total_tokens = 0

        if response is not None:
            if ollama_params["stream"]:
                # Streaming response
                if streaming_tool_calls:
                    finish_reason = "tool_calls"
                    content = streaming_tool_calls
                else:
                    finish_reason = "stop"
                    content = response_content

                response_id = f"ollama-stream-{id(response)}"
            else:
                # Non-streaming response
                # If we have tool calls as the response, populate completed tool calls for our return OAI response
                response_id = f"ollama-{id(response)}"

                if hasattr(response.message, "tool_calls") and response.message.tool_calls:
                    finish_reason = "tool_calls"
                    content = []
                    for tool_call in response.message.tool_calls:
                        # Convert arguments to JSON string if it's a dict
                        arguments = tool_call.function.arguments
                        if isinstance(arguments, dict):
                            arguments = json.dumps(arguments)

                        content.append(
                            FunctionCall(
                                id=str(uuid.uuid4()),
                                arguments=arguments,
                                name=normalize_name(tool_call.function.name),
                            )
                        )
                else:
                    # if not tool_calls, then it is a text response and we populate the content and thought fields.
                    finish_reason = "stop"
                    content = response.message.content or ""

                    # Check for thinking content if available
                    if hasattr(response, "thinking") and response.thinking:
                        thought = response.thinking
        else:
            raise RuntimeError("Failed to get response from Ollama.")

        # Ollama doesn't provide logprobs
        logprobs = None

        usage = RequestUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

        calculated_cost = calculate_token_cost(
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            provider=self.PROVIDER_NAME,
            model_name=ollama_params["model"],
        )

        # Use 0.0 if cost is None (for Ollama, which is free)
        if calculated_cost is None:
            calculated_cost = 0.0

        response = CreateResult(
            response_id=response_id,
            model=ollama_params["model"],
            finish_reason=normalize_stop_reason(finish_reason),
            content=content,
            usage=usage,
            cached=False,
            logprobs=logprobs,
            thought=thought,
            cost=calculated_cost,
            model_name=ollama_params["model"],
        )

        return response

    def _oai_messages_to_ollama_messages(
        self, messages: list[Dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Convert messages from OAI format to Ollama's format.
        We correct for any specific role orders and types.
        """

        ollama_messages = copy.deepcopy(messages)

        # Remove the name field as Ollama doesn't support it
        for message in ollama_messages:
            if "name" in message:
                message.pop("name", None)

        return ollama_messages
