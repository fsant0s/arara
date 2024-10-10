from typing import Dict, Literal, Optional, Union

from neuron.runtime_logging import log_new_agent, logging_enabled
from neuron.clients import CloudBasedClient
from .llm_agent import LLMAgent

class AssistantAgent(LLMAgent):
    """(In preview) Assistant agent, designed to solve a task with LLM.

    AssistantAgent is a subclass of Agent configured with a default system message.
    """

    DEFAULT_SYSTEM_MESSAGE = """You are a helpful AI assistant."""

    DEFAULT_DESCRIPTION = "A helpful and general-purpose AI assistant."

    def __init__(
        self,
        name: str,
        description: Optional[str] = DEFAULT_DESCRIPTION,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        system_message: Optional[str] = DEFAULT_SYSTEM_MESSAGE,
        **kwargs,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            description=self.DEFAULT_DESCRIPTION,
            llm_config=llm_config,
            **kwargs,
        )

        if logging_enabled():
            log_new_agent(self, locals())

        if not all(isinstance(client, CloudBasedClient) for client in self.client._clients):
            raise ValueError("The client argument should be a CloudBasedClient instance.")