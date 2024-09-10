from typing import Optional, Union, Dict, Literal
from neuron.runtime_logging import log_new_agent, logging_enabled

from neuron.agents import Agent
from neuron.clients import CustomClient

class LearnerAgent(Agent):
    
    DEFAULT_DESCRIPTION = "A Learner Agent processes incoming data, inferring new information for further use."

    def __init__(
        self,
        name="learner_agent",
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        description: Optional[str] = DEFAULT_DESCRIPTION,
        **kwargs,
    ):
        super().__init__(
            name=name,
            llm_config=llm_config,
            description=
                description if description is not None else self.DEFAULT_DESCRIPTION
            ,
            **kwargs,
        )
        
        if not all(isinstance(client, CustomClient) for client in self.client._clients):
            raise ValueError("The client argument should be a CloudBasedClient instance.")
        
        if logging_enabled():
            log_new_agent(self, locals())