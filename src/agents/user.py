from typing import Optional, Literal

from runtime_logging import log_new_agent, logging_enabled
from . import Agent

class User(Agent):
    """
    Represents a user-type agent responsible for initiating and maintaining interactions
    with other agents in the system.

    This agent simulates or represents human input in a conversation, providing questions,
    responses, or general free-form communication. It is ideal for testing or modeling
    human behavior in conversational environments.
    """

    DEFAULT_USER_DESCRIPTIONS = """
    An agent that represents a human user interacting with the system. Its communication is free-form
    and may involve questions, comments, or spontaneously expressed preferences.
    """

    def __init__(
        self,
        name: str = "user",
        description: Optional[str] = None,
        human_input_mode: Literal["ALWAYS", "NEVER"] = "ALWAYS",
        **kwargs,
    ):
        """
        Initializes a user-type agent.

        Args:
            name (str): Agent name, used for identification in conversations.
            description (Optional[str]): Optional textual description of the agent's role or behavior.
            human_input_mode (Literal): Defines whether the agent should wait for human input ("ALWAYS")
                                        or operate automatically ("NEVER").
            **kwargs: Additional parameters passed to the base Agent class.
        """

        # Initialize the base Agent class with the appropriate parameters
        super().__init__(
            name=name,
            description=(description if description is not None else self.DEFAULT_USER_DESCRIPTIONS),
            human_input_mode=human_input_mode,
            **kwargs,
        )

        # Log this agent if logging is enabled
        if logging_enabled():
            log_new_agent(self, locals())
