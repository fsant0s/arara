from typing import Optional, Union, Dict, Literal

from neuron.agents import Agent
from neuron.runtime_logging import log_new_agent, logging_enabled
from neuron.clients import CustomClient

class KnowledgeRepresenterAgent(Agent):
    
    DEFAULT_DESCRIPTION = "Agent responsible for generating content representations (embeddings)"

    def __init__(
        self,
        name="knowledge_representer",
        description: Optional[str] = DEFAULT_DESCRIPTION,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            description=
                description if description is not None else self.DEFAULT_DESCRIPTION
            ,
            llm_config=llm_config,
            **kwargs,
        )

        if not all(isinstance(client, CustomClient) for client in self.client._clients):
            raise ValueError("The client argument should be a CustomClient instance.")
        
        if logging_enabled():
            log_new_agent(self, locals())