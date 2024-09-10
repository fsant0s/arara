from typing import Dict, List
from neuron.agents.base_agent import BaseAgent

def chat_messages(recipent, sender) -> Dict[BaseAgent, List[Dict]]:
    """A dictionary of conversations from agent to list of messages."""
    return recipent._oai_messages[sender]