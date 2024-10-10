
from typing import List, Dict
from neuron.agents.base_agent import BaseAgent

def append_short_memories_before_reply(self: BaseAgent, messages: List[Dict]) -> List[Dict]:
    
    hook_list = self.hook_lists["append_short_memories_before_reply"]
    if len(hook_list) == 0:
        return messages  # No hooks registered.
    if messages is None:
        return None  # No message to process.
    if len(messages) == 0:
        return messages  # No message to process.
    last_message = messages[-1]
    if "context" in last_message:
        return messages  # Last message contains a context key.
    if "content" not in last_message:
        return messages  # Last message has no content.

    immediate_memories = []
    for hook in hook_list:
        immediate_memories += hook(messages)

    new_messages = messages + immediate_memories
    return new_messages
        
