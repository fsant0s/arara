from __future__ import annotations
import os

from typing import Any, Dict, List, Optional, Union

from src.capabilities.clients.base import BaseClient
from ...normalize_stop_reason import normalize_stop_reason
from ...parse_r1_content import parse_r1_content


from ...models import ChatCompletionTokenLogprob, TopLogprob, ModelFamily, CreateResult, RequestUsage


# Cost per thousand tokens - Input / Output (NOTE: Convert $/Million to $/K)
# see: https://github.com/AgentOps-AI/tokencost
OPENAI_PRICING_1K = {
    "gpt-4": (0.03, 0.06),
    "gpt-4o": (0.0025, 0.01),
}

class OpenAI(BaseClient):
    """Follows the Client protocol and wraps the OpenAI client."""

    def __init__(self, **kwargs: Optional[Dict[str, Any]]):
        super().__init__()
        # Ensure we have the api_key upon instantiation
        self._model_info = kwargs.get("model_info", None)
        self.api_key = kwargs.get("api_key", None)
        if not self.api_key:
            self.api_key = os.getenv("GROQ_API_KEY")

        assert (
            self.api_key
        ), "Please include the api_key in your config list entry for Groq or set the GROQ_API_KEY env variable."


    def message_retrieval(
        self, response
    ) -> List:
        """Retrieve the messages from the response."""
        return [choice.message for choice in response.choices]

    def create(self, params: Dict[str, Any]) -> CreateResult:
        messages = params.get("messages", [])

        # Convert AutoGen messages to Groq messages
        groq_messages = oai_messages_to_groq_messages(messages)

        # Parse parameters to the Groq API's parameters
        groq_params = self.parse_params(params)



        # Add tools to the call if we have them and aren't hiding them
        if "tools" in params:
            hide_tools = validate_parameter(
                params, "hide_tools", str, False, "never", None, ["if_all_run", "if_any_run", "never"]
            )
            if not should_hide_tools(groq_messages, params["tools"], hide_tools):
                groq_params["tools"] = self.convert_tools(params["tools"])

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
                    raise ValueError("function_call is deprecated and is not supported by this model client.")

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
                        reasoning_content = response.choices[0].message.model_extra.get("reasoning_content")
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
                    top_logprobs=[TopLogprob(logprob=y.logprob, bytes=y.bytes) for y in x.top_logprobs],
                    bytes=x.bytes,
                )
                for x in response.choices[0].logprobs.content
            ]

        #   This is for local R1 models.
        #TODO: test it.
        if isinstance(content, str) and thought is None and self._model_info is not None:
            if self._model_info["family"] == ModelFamily.R1:
                thought, content = parse_r1_content(content)

        usage = RequestUsage(
            # TODO backup token counting
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens
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
            cost=calculate_groq_cost(prompt_tokens, completion_tokens, groq_params["model"]),
            model_name=groq_params["model"],
        )

        return response

    def cost(self, response: Union[ChatCompletion, Completion]) -> float:
        """Calculate the cost of the response."""
        model = response.model
        if model not in OAI_PRICE1K:
            # log warning that the model is not found
            logger.warning(
                f'Model {model} is not found. The cost will be 0. In your config_list, add field {{"price" : [prompt_price_per_1k, completion_token_price_per_1k]}} for customized pricing.'
            )
            return 0

        n_input_tokens = response.usage.prompt_tokens if response.usage is not None else 0  # type: ignore [union-attr]
        n_output_tokens = response.usage.completion_tokens if response.usage is not None else 0  # type: ignore [union-attr]
        if n_output_tokens is None:
            n_output_tokens = 0
        tmp_price1K = OAI_PRICE1K[model]
        # First value is input token rate, second value is output token rate
        if isinstance(tmp_price1K, tuple):
            return (tmp_price1K[0] * n_input_tokens + tmp_price1K[1] * n_output_tokens) / 1000  # type: ignore [no-any-return]
        return tmp_price1K * (n_input_tokens + n_output_tokens) / 1000  # type: ignore [operator]
