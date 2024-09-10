import warnings
from typing import (
    Any, 
    Dict, 
    Literal, 
    Optional, 
    Union, 
)

from .agent import Agent

class LLMAgent(Agent):

    @property
    def system_message(self) -> str:
        """Return the system message."""
        return self._oai_system_message[0]["content"]

    def update_system_message(self, system_message: str) -> None:
        """Update the system message.

        Args:
            system_message (str): system message for the ChatCompletion inference.
        """
        self._oai_system_message[0]["content"] = system_message


    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        system_message: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize an LLM agent.

        Args:
            system_message (str): the system message of the agent.
        """
        super().__init__(name, description, llm_config, **kwargs)
        self._oai_system_message = [{"content": system_message, "role": "system"}]

    def _generate_oai_reply_from_client(self, llm_client, messages, cache) -> Union[str, Dict, None]:
        messages = self._oai_system_message + messages
        # unroll tool_responses
        all_messages = []
        for message in messages:
            all_messages.append(message)

        # TODO: #1143 handle token limit exceeded error
        response = llm_client.create(
            context=messages[-1].pop("context", None), messages=all_messages, cache=cache, agent=self
        )
        extracted_response = llm_client.extract_text_or_completion_object(response)[0]
        if extracted_response is None:
            warnings.warn(f"Extracted_response from {response} is None.", UserWarning)
            return None 
        return extracted_response.model_dump()                                       