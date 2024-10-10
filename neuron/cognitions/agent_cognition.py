from neuron.agents import Agent

class AgentCognition:
    """Base class for composable cognitions that can be added to an agent."""

    def __init__(self):
        pass

    def add_to_agent(self, agent: Agent):
        """
        Adds a particular cognition to the given agent. Must be implemented by the cognition subclass.
        An implementation will typically call agent.register_hook() one or more times.
        """
        raise NotImplementedError