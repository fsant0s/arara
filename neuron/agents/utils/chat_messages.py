from typing import Dict, List
from ..agent import Agent

def chat_messages(recipent, sender) -> Dict[Agent, List[Dict]]:
    """A dictionary of conversations from agent to list of messages."""
    return recipent._oai_messages[sender]