from typing import Dict, Literal, Optional, Union

from ..clients import CloudBasedClient
from ..runtime_logging import log_new_neuron, logging_enabled
from . import Neuron


class User(Neuron):

    DEFAULT_USER_DESCRIPTIONS = """
    A user who provides detailed descriptions of the items they like, including features such as brand, category, price, intended use, and other specific preferences.
    """

    def __init__(
        self,
        name: str = "user",
        description: Optional[str] = None,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            description=(
                description if description is not None else self.DEFAULT_USER_DESCRIPTIONS
            ),
            llm_config=llm_config,
            **kwargs,
        )

        if isinstance(llm_config, CloudBasedClient):
            raise ValueError("The 'llm_config' argument should not be a CloudBasedClient instance.")

        if logging_enabled():
            log_new_neuron(self, locals())
