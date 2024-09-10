from typing import Optional, Union, Dict, Literal

from neuron.agents import Agent
from neuron.runtime_logging import log_new_agent, logging_enabled

class KnowledgeRepresenterAgent(Agent):
    
    DEFAULT_DESCRIPTION = "Agent responsible for generating content representations (embeddings)"

    def __init__(
        self,
        name="knowledge_representer",
        system_message: Optional[str] = None,
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

        #TODO: check if self.config is a dict to Knowledge representer
        
        if logging_enabled():
            log_new_agent(self, locals())