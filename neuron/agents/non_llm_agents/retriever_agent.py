from typing import Optional, Union, Dict, Tuple, List, Literal

from neuron.runtime_logging import log_new_agent, logging_enabled
from neuron.agents import LLMAgent
from neuron.clients import CloudBasedClient

class RetrieverAgent(LLMAgent):
    
    DEFAULT_SYSTEM_MESSAGE = """
    You are the Retriever agent. You will receive a dataset composed of pandas rows containing n elements. Your task is to describe each of these elements in detail, focusing on their key attributes and any relevant information. Provide clear and concise descriptions to enable the next agent, the Assessor, to determine which of these data entries best matches the user's description.
    """

    DEFAULT_DESCRIPTION = """
    Your task is to receive a dataset of pandas rows and provide detailed descriptions of each element, highlighting key attributes and relevant information. This will help the Assessor agent identify the entries that best match the user's criteria.
    """


    def __init__(
        self,
        name="retriever_agent",
        system_message: Optional[str] = DEFAULT_SYSTEM_MESSAGE,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        description: Optional[str] = DEFAULT_DESCRIPTION,
        **kwargs,
    ):
        
        super().__init__(
            name=name,
            system_message=system_message,
            description= description,
            llm_config=llm_config,
            **kwargs,
        )

        if not all(isinstance(client, CloudBasedClient) for client in self.client._clients):
            raise ValueError("The client argument should be a CloudBasedClient instance.")

        if logging_enabled():
            log_new_agent(self, locals())

