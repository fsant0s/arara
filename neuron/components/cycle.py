from typing import List, Any
from ..agents import Agent
from .base_component import BaseComponent
from ..io.base import IOStream
from ..formatting_utils import colored

class CycleComponent(BaseComponent):
    """Component that executes agents in a cyclical fashion, with early stopping if the response is satisfactory."""

    def __init__(self, agents: List[Agent], repetitions: int = 3) -> None:
        """
        Initialize with a list of agents and the number of repetitions.

        Args:
            agents (List[Agent]): List of Agent instances.
            repetitions (int): Number of times to repeat the cycle.
        """
        self.agents = agents
        self.repetitions = repetitions

    def execute(self, sender: Agent, message: Any, silent: bool) -> Any:
        """
        Execute agents in a cycle for a specified number of repetitions, with early stopping 
        if the last agent's response contains 'Yes'.

        Args:
            speaker (Agent): The initial agent that sends the message.
            message (Any): The message to be passed to the agents.

        Returns:
            Any: The final message after cycling through all agents.
        """
        speaker = sender
        for _ in range(self.repetitions):
            for index, agent in enumerate(self.agents):
                
                speaker.send(message, agent, request_reply=False, silent=False)
                response = agent.generate_reply(sender=speaker)
                    
                # Check if it's the last agent in the cycle
                if index == len(self.agents) - 1:
                    if "Yes" in response:  # If the response is satisfactory, stop the cycle
                        return (agent, response)

                speaker = agent  # Update speaker to the current agent
                if not silent:
                    iostream = IOStream.get_default()
                    iostream.print(colored(f"\nNext speaker: {speaker.name}\n", "green"), flush=True)
                
                message = response  # Update message to the response for the next cycle
                

        return (agent, message)
