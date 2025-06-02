from typing import Optional

from runtime_logging import log_new_agent, logging_enabled
from . import Agent

class SilentAgent(Agent):
    """
    Represents an agent that does not produce any output. It can be used in multi-agent
    environments to observe interactions or trigger silent processes.
    """

    DEFAULT_SILENT_DESCRIPTION = """
    A silent agent that does not respond to any input. It can be used for observation,
    monitoring, or passive participation in conversations.
    """

    def __init__(
        self,
        name: str = "silent",
        description: Optional[str] = None,
        **kwargs,
    ):
        """
        Initializes a silent agent that never generates a reply.

        Args:
            name (str): Agent name, used for identification in conversations.
            description (Optional[str]): Optional description of the agent.
            **kwargs: Additional parameters passed to the base Agent class.
        """

        super().__init__(
            name=name,
            description=(description if description is not None else self.DEFAULT_SILENT_DESCRIPTION),
            human_input_mode="NEVER",
            **kwargs,
        )

        if logging_enabled():
            log_new_agent(self, locals())

        # Unregister default reply functions to ensure no output is produced
        self.unregister_reply_func(Agent._generate_oai_reply)
        self.unregister_reply_func(Agent.check_termination_and_human_reply)

    def generate_reply(self, sender=None):
        """
        Overrides the reply generation to return nothing.
        """
        if logging_enabled():
            print(f"[SilentAgent] '{self.name}' received a message but will not respond.")
        return
        yield  # This makes it a generator that yields nothing
