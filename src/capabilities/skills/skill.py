from abc import ABC, abstractmethod

from agents.base import BaseAgent

class Skill(ABC):
    """Base class for modular skills that can be added to an agent."""

    def __init__(self) -> None:
        self._agent = None

    def add_to_agent(self, agent: BaseAgent):
        """
        Public method to attach the skill to an agent.
        Automatically validates the agent type before delegating to subclass logic.
        """
        if not isinstance(agent, BaseAgent):
            raise TypeError(
                f"Expected parameter 'agent' to be of type 'BaseAgent', but got {type(agent).__name__}."
            )
        self._agent = agent
        # Delegate specific behavior to the subclass
        self.on_add_to_agent(agent)

    @abstractmethod
    def on_add_to_agent(self, agent: BaseAgent):
        """
        Abstract method to be implemented by subclasses.
        Defines specific behavior for integrating the skill into the agent.
        """
        pass
