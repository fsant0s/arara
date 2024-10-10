"""Create an OpenAI-compatible client using Groq's API.

Example:
    llm_config={
        "config_list": [{
            "api_type": "groq",
            "model": "mixtral-8x7b-32768",
            "api_key": os.environ.get("GROQ_API_KEY")
            }
    ]}

    agent = neuron.AssistantAgent("my_agent", llm_config=llm_config)

Install Groq's python library using: pip install --upgrade groq

Resources:
- https://console.groq.com/docs/quickstart
"""

from __future__ import annotations

import copy
import os
import time
import warnings
from typing import Any, Dict

from groq import Groq
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import ChatCompletionMessage, Choice
from openai.types.completion_usage import CompletionUsage

from neuron.clients.helpers import validate_parameter
from .. import CloudBasedClient

# Cost per thousand tokens - Input / Output (NOTE: Convert $/Million to $/K)
# see: https://github.com/AgentOps-AI/tokencost
GROQ_PRICING_1K = {
    "llama3-70b-8192": (0.00059, 0.00079),
    "mixtral-8x7b-32768": (0.00024, 0.00024),
    "llama3-8b-8192": (0.00005, 0.00008),
    "gemma-7b-it": (0.00007, 0.00007),
    "llama3-groq-70b-8192-tool-use-preview": (0.00089, 0.00089),

}

class GroqClient(CloudBasedClient):
    """Client for Groq's API."""

    def __init__(self, **kwargs):
        """Requires api_key or environment variable to be set

        Args:
            api_key (str): The API key for using Groq (or environment variable GROQ_API_KEY needs to be set)
        """
        # Ensure we have the api_key upon instantiation
        self.api_key = kwargs.get("api_key", None)
        if not self.api_key:
            api_key = os.getenv("GROQ_API_KEY")

        assert (
            self.api_key
        ), "Please include the api_key in your config list entry for Groq or set the GROQ_API_KEY env variable."

    
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
        groq_params["max_tokens"] = validate_parameter(params, "max_tokens", int, True, None, (0, None), None)
        groq_params["presence_penalty"] = validate_parameter(
            params, "presence_penalty", (int, float), True, None, (-2, 2), None
        )
        groq_params["seed"] = validate_parameter(params, "seed", int, True, None, None, None)
        groq_params["stream"] = validate_parameter(params, "stream", bool, True, False, None, None)
        groq_params["temperature"] = validate_parameter(params, "temperature", (int, float), True, 1, (0, 2), None)
        groq_params["top_p"] = validate_parameter(params, "top_p", (int, float), True, None, None, None)

        # Groq parameters not supported by their models yet, ignoring
        # logit_bias, logprobs, top_logprobs

        # Groq parameters we are ignoring:
        # n (must be 1), response_format (to enforce JSON but needs prompting as well), user,
        # parallel_tool_calls (defaults to True), stop
        # function_call (deprecated), functions (deprecated)
        # tool_choice (none if no tools, auto if there are tools)

        return groq_params

    def create(self, params: Dict) -> ChatCompletion:
        messages = params.get("messages", [])

        # Convert NEURON messages to Groq messages
        groq_messages = oai_messages_to_groq_messages(messages)
        
        # Parse parameters to the Groq API's parameters
        groq_params = self.parse_params(params)

        groq_params["messages"] = groq_messages
        
        # Token counts will be returned
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        # In case you put the client in __init__ it wll cause crash 
        client = Groq(api_key=self.api_key, max_retries=5)

        try:
            response = client.chat.completions.create(**groq_params)
        except Exception as e:
            raise RuntimeError(f"Groq exception occurred: {e}")
        else:
            response.choices[0].message.content
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens

        if response is not None:
            groq_finish = "stop"
            response_content = response.choices[0].message.content
            response_id = response.id
        else:
            raise RuntimeError("Failed to get response from Groq after retrying 5 times.")

        # 3. convert output
        message = ChatCompletionMessage(
            role="assistant",
            content=response_content
        )

        choices = [Choice(finish_reason=groq_finish, index=0, message=message)]

        response_oai = ChatCompletion(
            id=response_id,
            model=groq_params["model"],
            created=int(time.time()),
            object="chat.completion",
            choices=choices,
            usage=CompletionUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            ),
            cost=calculate_groq_cost(prompt_tokens, completion_tokens, groq_params["model"]),
        )
        return response_oai


def oai_messages_to_groq_messages(messages: list[Dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert messages from OAI format to Groq's format.
    We correct for any specific role orders and types.
    """

    groq_messages = copy.deepcopy(messages)

    # Remove the name field
    for message in groq_messages:
        if "name" in message:
            message.pop("name", None)

    return groq_messages


def calculate_groq_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Calculate the cost of the completion using the Groq pricing."""
    total = 0.0

    if model in GROQ_PRICING_1K:
        input_cost_per_k, output_cost_per_k = GROQ_PRICING_1K[model]
        input_cost = (input_tokens / 1000) * input_cost_per_k
        output_cost = (output_tokens / 1000) * output_cost_per_k
        total = input_cost + output_cost
    else:
        warnings.warn(f"Cost calculation not available for model {model}", UserWarning)

    return total
