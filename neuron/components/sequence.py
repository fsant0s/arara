from typing import List, Any
from ..agents import Agent
from .base_component import BaseComponent
from ..io.base import IOStream
from ..formatting_utils import colored

class SequentialComponent(BaseComponent):
    """Component that executes agents sequentially, passing messages from one agent to the next."""

    def __init__(self, agents: List[Agent], **kwargs) -> None:
        self.agents = agents

    def execute(self, sender: Agent, message: Any, silent: bool) -> Any:

        speaker = sender
        for agent in self.agents:
            # Send the message from the current speaker to the current agent
            speaker.send(message, agent, request_reply=False, silent=False)

            # The agent generates a reply in response to the message
            response = agent.generate_reply(sender=speaker)

            # Update the speaker to the current agent for the next step
            speaker = agent
            if not silent:
                iostream = IOStream.get_default()
                iostream.print(colored(f"\nNext speaker: {speaker.name}\n", "green"), flush=True)
                
            # Update the message to the new response for the next agent
            message = response

        # Return the final message after all agents have processed it
        return (agent, message)
