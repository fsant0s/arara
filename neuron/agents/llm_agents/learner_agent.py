from typing import Optional, Union, Dict, Literal

from neuron.runtime_logging import log_new_agent, logging_enabled
from neuron.clients import CloudBasedClient

from neuron.agents import  LLMAgent

class LearnerAgent(LLMAgent):
    
    DEFAULT_DESCRIPTION = "An Assessor Agent evaluates data elements to determine the best match with the user's description."
    DEFAULT_SYSTEM_MESSAGE = """
    You have been assigned the role of an Assessor agent. Your task is to evaluate a list of items against the user's specific request. Follow these guidelines:

    1. Carefully review the user’s request for key requirements.
    2. Analyze each provided item to determine if it matches the key requirements.
    3. If you find at least one matching item, return only the matching items.
    4. If no item matches, respond with a message indicating that there was no match.
    5. Focus solely on the user's key requirements without providing detailed lists or additional explanations.
    """

    def __init__(
        self,
        name="learner_agent",
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
