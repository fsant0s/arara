from typing import Optional, Literal

from runtime_logging import log_new_agent, logging_enabled
from .. import User

class UserModule(User):
    """
    Represents an automated user agent for testing tool calling behavior.

    This agent simulates a user interacting with tools by following a predefined
    sequence of natural-language messages. It is intended for use in experiments
    and validation of tool calling workflows.
    """

    DEFAULT_USER_DESCRIPTIONS = """
    An automated user agent that sends predefined natural-language messages
    designed to trigger tool calls. Useful for testing tool interactions
    and running scripted evaluation scenarios.
    """

    def __init__(
        self,
        name: str = "user_test",
        description: Optional[str] = None,
        human_input_mode: Literal["ALWAYS", "NEVER"] = "ALWAYS",
        **kwargs,
    ):
        """
        Initializes an automated user agent with a fixed dialog for tool calling tests.

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

        # Internal counter to track the current message in the predefined dialog
        self._counter = 0

        # Predefined sequence of messages to trigger tool calls
        self._dialog = [
            "Qualquer um",
            "exit"
        ]

    def get_human_input(self, prompt):
        """
        Returns the next message in the predefined tool-calling dialog.

        Args:
            prompt (str): The input prompt shown to the user (ignored in this implementation).

        Returns:
            str: The next scripted message, typically designed to trigger a tool call.
        """
        reply = self._dialog[self._counter]
        self._counter += 1
        self._human_input.append(reply)
        return reply
