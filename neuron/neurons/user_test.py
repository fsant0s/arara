from typing import Optional, Literal

from ..runtime_logging import log_new_neuron, logging_enabled
from . import User

class UserTest(User):
    """
    Represents a test user agent that simulates human interaction with the system.

    This agent follows a predefined sequence of messages (dialog), mimicking a user
    interacting naturally with other neurons. It is useful for testing conversations,
    verifying tool responses, or running automated scenarios.
    """

    DEFAULT_USER_DESCRIPTIONS = """
    A test user agent that interacts with the system using predefined, natural-language
    messages. Used to simulate typical user behavior during conversations.
    """

    def __init__(
        self,
        name: str = "user_test",
        description: Optional[str] = None,
        human_input_mode: Literal["ALWAYS", "NEVER"] = "ALWAYS",
        **kwargs,
    ):
        """
        Initializes a simulated user agent with a predefined dialog.

        Args:
            name (str): Agent name, used for identification in interactions.
            description (Optional[str]): Custom description of the agent behavior.
            human_input_mode (Literal): Determines whether human input is expected
                                        ("ALWAYS") or bypassed ("NEVER").
            **kwargs: Additional parameters passed to the base User class.
        """

        super().__init__(
            name=name,
            description=(description if description is not None else self.DEFAULT_USER_DESCRIPTIONS),
            human_input_mode=human_input_mode,
            **kwargs,
        )

        if logging_enabled():
            log_new_neuron(self, locals())

        # Internal state to control progression through the predefined dialog
        self._counter = 0

        # Simulated conversation sequence for testing purposes
        self._dialog = [
            "Gostaria de saber quanto é 100 euros em usd",
            "Quantas árvores existem no planeta terra?",
            "How much is 123.45 USD in EUR??",
            "Muito obrigado pelas informações!",
            "exit",
        ]

    def get_human_input(self, prompt):
        """
        Returns the next message in the simulated user dialog.

        Args:
            prompt (str): Prompt text shown to the user (ignored in this simulation).

        Returns:
            str: The next predefined user message.
        """
        reply = self._dialog[self._counter]
        self._counter += 1
        self._human_input.append(reply)
        return reply
