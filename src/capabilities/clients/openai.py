from __future__ import annotations

import copy
import os
from typing import Any, Dict, List, Optional, Union

from openai import OpenAI as OpenAIClientInternal
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessage
from openai.types.chat.chat_completion_chunk import ChoiceDelta

from agents.types import FunctionCall
from function_utils import normalize_stop_reason
from llm_messages import ChatCompletionTokenLogprob, CreateResult, RequestUsage, TopLogprob

from .base import BaseClient
from .utils.calculate_token_cost import calculate_token_cost
from .utils.convert_tools import convert_tools
from .utils.normalize_name import normalize_name
from .utils.should_hide_tools import should_hide_tools
from .utils.validate_parameter import validate_parameter


class OpenAIClient(BaseClient):
    """Client for OpenAI's or Maritaca's API."""

    PROVIDER_NAME = None

    def __init__(self, **kwargs):
        """
        Initializes the OpenAIClient for either OpenAI or Maritaca depending on the base_url.

        Args:
            api_key (str, optional): The API key. If not provided, it will try to use the appropriate
                                     environment variable based on the provider.
            model_info (dict, optional): Information about the model, potentially used for cost calculation.
            base_url (str, optional): Base URL to determine the provider (OpenAI or Maritaca).
        """
        super().__init__(**kwargs)
        self._model_info = kwargs.get("model_info", None)
        self.base_url = kwargs.get("base_url", None)

        # Determine provider based on base_url
        if self.base_url and "maritaca" in self.base_url.lower():
            if not self.base_url:
                raise ValueError(
                    "The 'base_url' parameter is required when using the Maritaca provider."
                )
            self.PROVIDER_NAME = "maritaca"
            self.api_key = kwargs.get("api_key", os.getenv("MARITACA_API_KEY"))
        else:
            self.PROVIDER_NAME = "openai"
            self.api_key = kwargs.get("api_key", os.getenv("OPENAI_API_KEY"))

        assert (
            self.api_key
        ), f"Please set the API key for {self.PROVIDER_NAME.upper()} using the correct environment variable."

        self.client = OpenAIClientInternal(
            api_key=self.api_key, max_retries=kwargs.get("max_retries", 5), base_url=self.base_url
        )

    def message_retrieval(
        self, response: Union[ChatCompletionMessage, ChatCompletionChunk]
    ) -> List[ChatCompletionMessage]:
        """
        Retrieve and return a list of Choice.Message from the response.
        For OpenAI, this typically means the main message from the first choice.
        """
        if hasattr(response, "choices") and response.choices:
            return [choice.message for choice in response.choices if choice.message]
        return []

    def parse_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Loads and validates parameters for the OpenAI API from the input parameters.
        Uses the validate_parameter function assumed to be imported from utils.
        """
        openai_params = {}

        # Model is mandatory
        openai_params["model"] = params.get("model")
        if not openai_params["model"]:
            raise ValueError("Parameter 'model' is required for OpenAI and cannot be None.")

        # Parameters based on OpenAI API documentation (May 2024)
        # For each call to validate_parameter, we provide all 7 arguments:
        # params, param_name, allowed_types, allow_None, default_value, numerical_bound, allowed_values

        openai_params["audio"] = validate_parameter(params, "audio", dict, True, None, None, None)
        openai_params["frequency_penalty"] = validate_parameter(
            params,
            "frequency_penalty",
            (int, float),
            True,
            None,
            (-2.0, 2.0),
            None,  # API Default: 0
        )
        # function_call is deprecated
        # functions is deprecated
        openai_params["logit_bias"] = validate_parameter(
            params, "logit_bias", dict, True, None, None, None  # API Default: null
        )
        # openai_params["logprobs"] = validate_parameter(
        #     params, "logprobs", bool, False, False, None, None # API Default: false
        # )
        # if openai_params.get("logprobs"):
        #     openai_params["top_logprobs"] = validate_parameter(
        #         params, "top_logprobs", int, True, None, (0, 20), None # API Default: null
        #     )

        # max_tokens is deprecated, prefer max_completion_tokens
        # If user provides max_tokens, it might be for older models or specific use cases.
        # We'll validate it if present but prioritize max_completion_tokens if both are somehow provided.
        # (Logic to prioritize one over the other if both are present is not added here, assumes user provides one)
        openai_params["max_tokens"] = validate_parameter(
            params, "max_tokens", int, True, None, (1, None), None
        )
        openai_params["max_completion_tokens"] = validate_parameter(
            params, "max_completion_tokens", int, True, None, (1, None), None  # API Default: null
        )

        openai_params["metadata"] = validate_parameter(
            params, "metadata", dict, True, None, None, None
        )
        openai_params["modalities"] = validate_parameter(
            params,
            "modalities",
            list,
            True,
            None,
            None,
            None,  # API Default: ["text"] (effectively, if omitted)
        )
        openai_params["n"] = validate_parameter(
            params, "n", int, False, 1, (1, None), None  # API Default: 1
        )
        openai_params["parallel_tool_calls"] = validate_parameter(
            params, "parallel_tool_calls", bool, True, None, None, None  # API Default: true
        )
        openai_params["presence_penalty"] = validate_parameter(
            params,
            "presence_penalty",
            (int, float),
            True,
            None,
            (-2.0, 2.0),
            None,  # API Default: 0
        )
        openai_params["reasoning_effort"] = validate_parameter(
            params,
            "reasoning_effort",
            str,
            True,
            None,
            None,
            ["low", "medium", "high"],  # API Default: medium
        )
        openai_params["response_format"] = validate_parameter(
            params,
            "response_format",
            dict,
            True,
            None,
            None,
            None,  # API Default: null (standard text)
        )
        openai_params["seed"] = validate_parameter(
            params, "seed", int, True, None, None, None  # API Default: null
        )
        openai_params["service_tier"] = validate_parameter(
            params,
            "service_tier",
            str,
            True,
            None,
            None,
            ["auto", "default", "flex"],  # API Default: auto
        )
        openai_params["stop"] = validate_parameter(
            params, "stop", (str, list), True, None, None, None  # API Default: null
        )
        openai_params["store"] = validate_parameter(
            params, "store", bool, True, None, None, None  # API Default: false
        )
        openai_params["stream"] = validate_parameter(
            params, "stream", bool, False, False, None, None  # API Default: false
        )
        if openai_params.get("stream"):
            openai_params["stream_options"] = validate_parameter(
                params,
                "stream_options",
                dict,
                True,
                {"include_usage": True},
                None,
                None,  # API Default: null (client default for include_usage)
            )
        openai_params["temperature"] = validate_parameter(
            params, "temperature", (int, float), True, None, (0.0, 2.0), None  # API Default: 1
        )
        openai_params["top_p"] = validate_parameter(
            params, "top_p", (int, float), True, None, (0.0, 1.0), None  # API Default: 1
        )
        openai_params["user"] = validate_parameter(
            params, "user", str, True, None, None, None  # API Default: null
        )

        # Tools and tool_choice
        if "tools" in params and params["tools"]:
            openai_params["tools"] = convert_tools(
                params["tools"]
            )  # Assumes convert_tools is robust
            # API default for tool_choice: 'none' if no tools, 'auto' if tools are present.
            # If user provides it, we validate; otherwise, it's omitted and API handles default.
            openai_params["tool_choice"] = validate_parameter(
                params,
                "tool_choice",
                (str, dict),
                True,
                None,
                None,
                None,
                # String values for tool_choice could be ["none", "auto", "required"],
                # but validate_parameter doesn't support conditional allowed_values based on type.
            )

        # Remove None values so that OpenAI API uses its defaults for unspecified optional parameters
        return {k: v for k, v in openai_params.items() if v is not None}

    def _oai_messages_to_openai_messages(
        self, messages: list[Dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Converts messages to OpenAI's expected format.
        OpenAI's format is the standard, so this is mostly a pass-through
        or minor cleaning. The example Groq client removed 'name'.
        For OpenAI, 'name' can be used with 'tool' role (as tool_call_id) or optionally with other roles.
        For simplicity and consistency with the provided Groq example, we'll make a deep copy.
        If 'name' causes issues or is not desired, it can be removed here.
        """
        # Perform a deep copy to avoid modifying the original messages list
        openai_messages = copy.deepcopy(messages)

        # Example: Clean up 'name' field if it's not meant for OpenAI's specific uses (e.g., participant identifier)
        # OpenAI uses 'name' in tool messages to specify the function name that was called (if role is 'tool').
        # It's not typically used in 'user' or 'system' messages unless for specific reasons.
        # The 'tool_call_id' is used for responses to tool_calls.
        # For now, we keep it simple. If autogen's 'name' field conflicts, logic can be added here.
        # for message in openai_messages:
        #     if "name" in message and message.get("role") not in ["tool", "assistant"]: # Keep name if it's a tool response or assistant with function name
        #         message.pop("name", None)
        return openai_messages

    def create(self, params: Dict) -> CreateResult:
        """
        Creates a chat completion using the OpenAI API.
        """
        messages = params.get("messages", [])
        if not messages:
            raise ValueError("Messages list cannot be empty.")

        openai_messages = self._oai_messages_to_openai_messages(messages)
        openai_api_params = self.parse_params(params)
        openai_api_params["messages"] = openai_messages

        # Handle 'hide_tools' logic if present (from Groq example)
        # This logic might be specific to the calling agent's framework
        if "tools" in openai_api_params and "hide_tools" in params:
            hide_tools_policy = validate_parameter(
                params,
                "hide_tools",
                str,
                False,
                "never",
                None,
                ["if_all_run", "if_any_run", "never"],
            )
            if should_hide_tools(openai_messages, openai_api_params["tools"], hide_tools_policy):
                openai_api_params.pop("tools", None)
                openai_api_params.pop("tool_choice", None)

        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        response_content: Union[str, List[FunctionCall]]
        response_id: Optional[str] = None
        model_identifier: Optional[str] = None
        final_finish_reason: Optional[str] = None
        logprobs_data: Optional[List[ChatCompletionTokenLogprob]] = None

        try:
            response_obj = self.client.chat.completions.create(**openai_api_params)
        except Exception as e:
            # Consider more specific OpenAI error types like openai.APIError, openai.RateLimitError etc.
            raise RuntimeError(f"OpenAI API request failed: {e}")

        if openai_api_params.get("stream"):
            accumulated_content = ""
            tool_call_assembler: Dict[int, Dict[str, Any]] = (
                {}
            )  # {index: {"id": "", "name": "", "arguments": ""}}

            # For stream_options usage
            stream_usage_data = None

            for chunk in response_obj:  # response_obj is a Stream[ChatCompletionChunk]
                if not chunk.choices:
                    continue

                choice = chunk.choices[0]
                delta: ChoiceDelta = choice.delta

                if response_id is None:  # Capture from first chunk
                    response_id = chunk.id
                if model_identifier is None:
                    model_identifier = chunk.model

                if delta.content:
                    accumulated_content += delta.content

                if delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        index = tc_delta.index
                        if index not in tool_call_assembler:
                            tool_call_assembler[index] = {
                                "id": None,
                                "name": None,
                                "arguments_buffer": "",
                            }

                        if tc_delta.id:
                            tool_call_assembler[index]["id"] = tc_delta.id
                        if tc_delta.function:
                            if tc_delta.function.name:
                                tool_call_assembler[index]["name"] = tc_delta.function.name
                            if tc_delta.function.arguments:
                                tool_call_assembler[index][
                                    "arguments_buffer"
                                ] += tc_delta.function.arguments

                if choice.finish_reason:
                    final_finish_reason = choice.finish_reason

                # Check for usage data if stream_options={"include_usage": True} was set
                if hasattr(chunk, "usage") and chunk.usage:
                    stream_usage_data = chunk.usage

            # After stream processing
            if final_finish_reason == "tool_calls":
                assembled_tool_calls: List[FunctionCall] = []
                for index in sorted(tool_call_assembler.keys()):
                    call_data = tool_call_assembler[index]
                    # Ensure all parts are present; arguments might be empty if not fully formed
                    if call_data["id"] and call_data["name"]:
                        # Attempt to parse arguments, default to raw string if not valid JSON
                        parsed_args = call_data["arguments_buffer"]
                        # try:
                        #     # OpenAI tool arguments are strings that are JSON objects
                        #     # No need to parse here, FunctionCall expects a string
                        # except json.JSONDecodeError:
                        #     # Keep as raw string if not valid JSON, or handle error
                        #     pass # parsed_args remains the buffer string

                        assembled_tool_calls.append(
                            FunctionCall(
                                id=call_data["id"],
                                name=normalize_name(call_data["name"]),
                                arguments=parsed_args,
                            )
                        )
                response_content = assembled_tool_calls
            else:
                response_content = accumulated_content

            if stream_usage_data:
                prompt_tokens = stream_usage_data.prompt_tokens or 0
                completion_tokens = stream_usage_data.completion_tokens or 0
                total_tokens = stream_usage_data.total_tokens or 0
            # Logprobs are generally not straightforward to assemble from stream deltas
            # and are often best retrieved from non-streaming or handled if API provides full logprob objects per chunk.
            # For simplicity, logprobs_data remains None for streaming here.

        else:  # Non-streaming response
            # response_obj is a ChatCompletion
            response_id = response_obj.id
            model_identifier = response_obj.model

            message = response_obj.choices[0].message
            final_finish_reason = response_obj.choices[0].finish_reason

            if message.tool_calls:
                final_finish_reason = "tool_calls"  # Ensure finish reason reflects tool usage
                tool_calls_content: List[FunctionCall] = []
                for tool_call in message.tool_calls:
                    if tool_call.type == "function":
                        tool_calls_content.append(
                            FunctionCall(
                                id=tool_call.id,
                                name=normalize_name(tool_call.function.name),
                                arguments=tool_call.function.arguments,
                            )
                        )
                response_content = tool_calls_content
            else:
                response_content = message.content or ""

            if response_obj.usage:
                prompt_tokens = response_obj.usage.prompt_tokens
                completion_tokens = response_obj.usage.completion_tokens
                total_tokens = response_obj.usage.total_tokens

            # Handle logprobs for non-streaming
            if openai_api_params.get("logprobs") and response_obj.choices[0].logprobs:
                logprobs_data = []
                for logprob_item in response_obj.choices[0].logprobs.content:
                    top_logprobs_list = []
                    if logprob_item.top_logprobs:
                        for top_lp in logprob_item.top_logprobs:
                            top_logprobs_list.append(
                                TopLogprob(
                                    token=top_lp.token, logprob=top_lp.logprob, bytes=top_lp.bytes
                                )
                            )
                    logprobs_data.append(
                        ChatCompletionTokenLogprob(
                            token=logprob_item.token,
                            logprob=logprob_item.logprob,
                            top_logprobs=top_logprobs_list,
                            bytes=logprob_item.bytes,
                        )
                    )

        if response_id is None or model_identifier is None or final_finish_reason is None:
            raise RuntimeError("Failed to get a complete response from OpenAI.")

        usage_obj = RequestUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

        calculated_cost = calculate_token_cost(
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            provider=self.PROVIDER_NAME,
            model_name=model_identifier,
        )

        return CreateResult(
            response_id=response_id,
            model=model_identifier,  # This is the actual model used, from response
            finish_reason=normalize_stop_reason(final_finish_reason),
            content=response_content,
            usage=usage_obj,
            cached=False,  # Assuming not cached unless explicitly handled
            logprobs=logprobs_data,
            thought=None,  # OpenAI API doesn't provide a standard 'thought' field
            cost=calculated_cost,
            model_name=model_identifier,  # Redundant with model, but matches CreateResult structure
        )
