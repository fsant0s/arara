from typing import Optional, Literal

from ..runtime_logging import log_new_neuron, logging_enabled
from . import User

class UserTest(User):
    """
    Represents a user interacting with the system, providing detailed descriptions
    of items of interest, including brand, category, price, and specific preferences.
    """

    DEFAULT_USER_DESCRIPTIONS = """
    A user test who provides detailed descriptions of the items they like, including features such as brand, category, price, intended use, and other specific preferences.
    """

    def __init__(
        self,
        name: str = "user_test",
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

        self._counter = 0
        self._dialog = [
            "Como vc ta?",
            "Que legal, obrigado por perguntar!",
            "Gostaria de saber quanto é 100 euros em usd",
            "How much is 123.45 USD in EUR??",
            "exit",
        ]

    def get_human_input(self, prompt):
        """Custmized function to get human input.

        Args:
            prompt (str): prompt for the human input.

        Returns:
            str: human input.
        """
        reply = self._dialog[self._counter]
        self._counter += 1
        self._human_input.append(reply)
        return reply
