from typing import Dict, Literal, Optional, Union

from ..runtime_logging import log_new_agent, logging_enabled
from neuron.clients import CloudBasedClient
from . import Agent

class UserAgent(Agent):

    DEFAULT_USER_AGENT_DESCRIPTIONS = """
    A user who provides detailed descriptions of the items they like, including features such as brand, category, price, intended use, and other specific preferences.
    """

    def __init__(
        self,
        name: str = "user_agent",
        description: Optional[str] = None,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            description=
                description if description is not None else self.DEFAULT_USER_AGENT_DESCRIPTIONS
            ,
            llm_config=llm_config,
            **kwargs,
        )

        if isinstance(llm_config, CloudBasedClient):
            raise ValueError("The 'llm_config' argument should not be a CloudBasedClient instance.")


        if logging_enabled():
            log_new_agent(self, locals())