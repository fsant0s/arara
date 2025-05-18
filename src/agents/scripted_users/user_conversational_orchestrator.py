from typing import Optional, Literal

from runtime_logging import log_new_agent, logging_enabled
from .. import User

class UserConversationalOrchestrator(User):
    """
    Represents an automated user agent designed for conversational testing scenarios.

    This agent simulates a natural conversation with the system by following a predefined
    sequence of messages. It is particularly useful for testing recommendation flows
    that begin with casual dialog and evolve into explicit recommendation requests.
    """

    DEFAULT_USER_DESCRIPTIONS = """
    An automated user agent that interacts with the system using natural, predefined messages
    intended to simulate a realistic conversation. The dialog begins with casual messages
    and transitions into a recommendation request.
    """

    def __init__(
        self,
        name: str = "user_conversational",
        description: Optional[str] = None,
        human_input_mode: Literal["ALWAYS", "NEVER"] = "ALWAYS",
        **kwargs,
    ):
        """
        Initializes an automated conversational user agent with a predefined dialog flow.

        Args:
            name (str): The name used to identify the agent in interactions.
            description (Optional[str]): A description of the agent's behavior.
            human_input_mode (Literal): Indicates whether human input is expected
                                        ("ALWAYS") or bypassed ("NEVER").
            **kwargs: Additional arguments passed to the base User class.
        """
        super().__init__(
            name=name,
            description=(description if description is not None else self.DEFAULT_USER_DESCRIPTIONS),
            human_input_mode=human_input_mode,
            **kwargs,
        )

        if logging_enabled():
            log_new_agent(self, locals())

        # Internal counter to track current message in the dialog
        self._counter = 0

        # Predefined conversational dialog simulating a natural flow into a recommendation request
        self._dialog = [
            "I'm thinking about watching something tonight. Can you recommend me a good movie to relax?",
            "Thanks! That sounds great.",
            "exit",
        ]

    def get_human_input(self, prompt):
        """
        Returns the next message in the predefined conversational dialog.

        Args:
            prompt (str): The input prompt shown to the user (ignored in this implementation).

        Returns:
            str: The next scripted conversational message.
        """
        reply = self._dialog[self._counter]
        self._counter += 1
        self._human_input.append(reply)
        return reply
