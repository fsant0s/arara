from typing import Optional, Union, Dict, Literal

from neuron.runtime_logging import log_new_agent, logging_enabled
from neuron.clients import CloudBasedClient

from neuron.agents import  LLMAgent

class RecommenderAgent(LLMAgent):
    
    DEFAULT_DESCRIPTION = "A Recommender Agent evaluates a provided list of items and selects those that best match the user's request, returning only the selected items."
    
    DEFAULT_SYSTEM_MESSAGE = """
    As a Recommender agent, your task is to evaluate a list of items based on the user’s request. Your goal is to identify and return only the items that perfectly match the user’s criteria. Provide the exact items with all their attributes included, and omit any explanations, comments, or additional text. Focus solely on delivering the items that meet the user's request with precision.
    """

    def __init__(
        self,
        name="recommender_agent",
        system_message: Optional[str] = DEFAULT_SYSTEM_MESSAGE,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        description: Optional[str] = DEFAULT_DESCRIPTION,
        **kwargs,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            description=description,
            llm_config=llm_config,
            **kwargs,
        )

        if not all(isinstance(client, CloudBasedClient) for client in self.client._clients):
            raise ValueError("All clients should be instances of CloudBasedClient.")
        
        if logging_enabled():
            log_new_agent(self, locals())
