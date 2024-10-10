from neuron.agents import LLMAgent
from .agent_cognition import AgentCognition
from typing import Union, List, Optional

class ImmediateWorkingMemory(AgentCognition):
    """A cognition that allows a Neuron to share immediate memory with other Neurons (LLM agents)."""

    def __init__(self, neurons: Optional[List[LLMAgent]] = None):
        self._neurons = neurons

    def add_to_agent(self, agent: LLMAgent):
        """Adds the immediate shared memory capability to the specified Agent."""
        if not isinstance(agent, LLMAgent):
            raise TypeError("The provided agent must be an instance of LLMAgent.")

        agent.register_hook(hookable_method="append_short_memories_before_reply", hook=self._get_immediate_short_memory)

    def _get_immediate_short_memory(self, content: Union[str, List[dict]]):
        """Immediate share memory with another Neuron."""
        memories = []
        for neuron in self._neurons:
            memory = self._get_memory(neuron)
            if memory:
                memories.append(memory)
    
        return memories
        
    def _get_memory(self, neuron):
        """Get the immediate memory shared by another Neuron."""
        for key, value in neuron._oai_messages.items():
            for item in value:
                if item['role'] == 'assistant' and item['name'] == neuron.name:
                    item_copy = item.copy()  
                    item_copy['role'] = 'user'
                    return item_copy
        return None
    

