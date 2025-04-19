from typing import Optional, Literal

from ..runtime_logging import log_new_neuron, logging_enabled
from . import Neuron

class User(Neuron):
    """
    Represents a user interacting with the system, providing detailed descriptions
    of items of interest, including brand, category, price, and specific preferences.
    """

    DEFAULT_USER_DESCRIPTIONS = """
    A user who provides detailed descriptions of the items they like, including features such as brand, category, price, intended use, and other specific preferences.
    """

    def __init__(
        self,
        name: str = "user",
        description: Optional[str] = None,
        human_input_mode: Literal["ALWAYS", "NEVER"] = "ALWAYS",
        **kwargs,
    ):
        """
        Initializes an instance of the User class, a type of Neuron.

        Args:
            **kwargs: Additional arguments for configuring the Neuron.
        """

        super().__init__(
            name=name,
            description=(
                description if description is not None else self.DEFAULT_USER_DESCRIPTIONS
            ),
            human_input_mode=human_input_mode,
            **kwargs,
        )

        if logging_enabled():
            log_new_neuron(self, locals())


