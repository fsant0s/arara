from __future__ import annotations

import copy
import os
from typing import Any, Dict, List, Union

from groq import Groq, Stream

from agents.types import FunctionCall
from function_utils import normalize_stop_reason
from llm_messages import ChatCompletionTokenLogprob, CreateResult, RequestUsage, TopLogprob

from .base import BaseClient
from .utils.calculate_token_cost import calculate_token_cost
from .utils.convert_tools import convert_tools
from .utils.normalize_name import normalize_name
from .utils.should_hide_tools import should_hide_tools
from .utils.validate_parameter import validate_parameter


class GroqClient(BaseClient):
    """Client for Groq's API."""

    PROVIDER_NAME = "groq"

    def __init__(self, **kwargs):
        """Requires api_key or environment variable to be set

        Args:
            api_key (str): The API key for using Groq (or environment variable GROQ_API_KEY needs to be set)
        """
        super().__init__()
        # Ensure we have the api_key upon instantiation
        self._model_info = kwargs.get("model_info", None)
        self.api_key = kwargs.get("api_key", None)
        if not self.api_key:
            self.api_key = os.getenv("GROQ_API_KEY")

        assert (
            self.api_key
        ), "Please include the api_key in your config list entry for Groq or set the GROQ_API_KEY env variable."

    def message_retrieval(self, response) -> List:
        """
        Retrieve and return a list of strings or a list of Choice.Message from the response.

        NOTE: if a list of Choice.Message is returned, it currently needs to contain the fields of OpenAI's ChatCompletion Message object,
        since that is expected for function or tool calling in the rest of the codebase at the moment, unless a custom agent is being used.
        """
        return [choice.message for choice in response.choices]

    def parse_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Loads the parameters for Groq API from the passed in parameters and returns a validated set. Checks types, ranges, and sets defaults"""
        groq_params = {}

        # Check that we have what we need to use Groq's API
        # We won't enforce the available models as they are likely to change
        groq_params["model"] = params.get("model", None)
        assert groq_params[
            "model"
        ], "Please specify the 'model' in your config list entry to nominate the Groq model to use."

        # Validate allowed Groq parameters
        # https://console.groq.com/docs/api-reference#chat
        groq_params["frequency_penalty"] = validate_parameter(
            params, "frequency_penalty", (int, float), True, None, (-2, 2), None
        )
        groq_params["max_tokens"] = validate_parameter(
            params, "max_tokens", int, True, None, (0, None), None
        )
        groq_params["presence_penalty"] = validate_parameter(
            params, "presence_penalty", (int, float), True, None, (-2, 2), None
        )
        groq_params["seed"] = validate_parameter(params, "seed", int, True, None, None, None)
        groq_params["stream"] = validate_parameter(params, "stream", bool, True, False, None, None)
        groq_params["temperature"] = validate_parameter(
            params, "temperature", (int, float), True, 1, (0, 2), None
        )
        groq_params["top_p"] = validate_parameter(
            params, "top_p", (int, float), True, None, None, None
        )

        # Groq parameters not supported by their models yet, ignoring
        # logit_bias, logprobs, top_logprobs

        # Groq parameters we are ignoring:
        # n (must be 1), response_format (to enforce JSON but needs prompting as well), user,
        # parallel_tool_calls (defaults to True), stop
        # function_call (deprecated), functions (deprecated)
        # tool_choice (none if no tools, auto if there are tools)

        return groq_params

    def create(self, params: Dict) -> CreateResult:

        messages = params.get("messages", [])

        # Convert Arara messages to Groq messages
        groq_messages = self._oai_messages_to_groq_messages(messages)

        # Parse parameters to the Groq API's parameters
        groq_params = self.parse_params(params)

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
            if not should_hide_tools(groq_messages, params["tools"], hide_tools):
                groq_params["tools"] = convert_tools(params["tools"])

        groq_params["messages"] = groq_messages

        # We use chat model by default, and set max_retries to 5 (in line with typical retries loop)
        client = Groq(api_key=self.api_key, max_retries=5)

        # Token counts will be returned
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        # Streaming tool call recommendations
        content: Union[str, List[FunctionCall]]
        streaming_tool_calls = []
        ans = None
        finish_reason = None
        thought: str | None = None
        try:
            response = client.chat.completions.create(**groq_params)
        except Exception as e:
            raise RuntimeError(f"Groq exception occurred: {e}")
        else:

            if groq_params["stream"]:
                # Read in the chunks as they stream, taking in tool_calls which may be across
                # multiple chunks if more than one suggested
                ans = ""
                for chunk in response:
                    ans = ans + (chunk.choices[0].delta.content or "")

                    if chunk.choices[0].delta.tool_calls:
                        # We have a tool call recommendation
                        for tool_call in chunk.choices[0].delta.tool_calls:
                            streaming_tool_calls.append(
                                FunctionCall(
                                    id=tool_call.id,
                                    arguments=tool_call.function.arguments,
                                    name=normalize_name(tool_call.function.name),
                                )
                            )

                    if chunk.choices[0].finish_reason:
                        prompt_tokens = chunk.x_groq.usage.prompt_tokens
                        completion_tokens = chunk.x_groq.usage.completion_tokens
                        total_tokens = chunk.x_groq.usage.total_tokens
            else:
                # Non-streaming finished
                ans: str = response.choices[0].message.content

                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens

        if response is not None:

            if isinstance(response, Stream):
                # Streaming response
                if chunk.choices[0].finish_reason == "tool_calls":
                    finish_reason = "tool_calls"
                    content = streaming_tool_calls
                else:
                    finish_reason = "stop"

                response_id = chunk.id
            else:
                if response.choices[0].message.function_call is not None:
                    raise ValueError(
                        "function_call is deprecated and is not supported by this model client."
                    )

                # Non-streaming response
                # If we have tool calls as the response, populate completed tool calls for our return OAI response
                response_id = response.id
                if response.choices[0].finish_reason == "tool_calls":
                    finish_reason = "tool_calls"
                    content = []
                    for tool_call in response.choices[0].message.tool_calls:
                        content.append(
                            FunctionCall(
                                id=tool_call.id,
                                arguments=tool_call.function.arguments,
                                name=normalize_name(tool_call.function.name),
                            )
                        )
                else:
                    # if not tool_calls, then it is a text response and we populate the content and thought fields.
                    finish_reason = response.choices[0].finish_reason
                    content = response.choices[0].message.content or ""
                    # if there is a reasoning_content field, then we populate the thought field. This is for models such as R1 - direct from deepseek api.
                    if response.choices[0].message.model_extra is not None:
                        reasoning_content = response.choices[0].message.model_extra.get(
                            "reasoning_content"
                        )
                        if reasoning_content is not None:
                            thought = reasoning_content
        else:
            raise RuntimeError("Failed to get response from Groq after retrying 5 times.")

        logprobs = None
        if response.choices[0].logprobs and response.choices[0].logprobs.content:
            logprobs = [
                ChatCompletionTokenLogprob(
                    token=x.token,
                    logprob=x.logprob,
                    top_logprobs=[
                        TopLogprob(logprob=y.logprob, bytes=y.bytes) for y in x.top_logprobs
                    ],
                    bytes=x.bytes,
                )
                for x in response.choices[0].logprobs.content
            ]

        usage = RequestUsage(
            # TODO backup token counting
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

        calculated_cost = calculate_token_cost(
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            provider=self.PROVIDER_NAME,
            model_name=groq_params["model"],
        )

        response = CreateResult(
            response_id=response_id,
            model=groq_params["model"],
            finish_reason=normalize_stop_reason(finish_reason),
            content=content,
            usage=usage,
            cached=False,
            logprobs=logprobs,
            thought=thought,
            cost=calculated_cost,
            model_name=groq_params["model"],
        )

        return response

    def _oai_messages_to_groq_messages(
        self, messages: list[Dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Convert messages from OAI format to Groq's format.
        We correct for any specific role orders and types.
        """

        groq_messages = copy.deepcopy(messages)

        # Remove the name field
        for message in groq_messages:
            if "name" in message:
                message.pop("name", None)

        return groq_messages
