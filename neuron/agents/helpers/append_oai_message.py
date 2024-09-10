from .message_to_dict import message_to_dict

from typing import Union, Dict
from neuron.agents.base_agent import BaseAgent

def append_oai_message(self: BaseAgent, message: Union[Dict, str], role, conversation_id: BaseAgent) -> bool:
        
    message = message_to_dict(message)
    
    # create oai message to be appended to the oai conversation that can be passed to oai directly.
    oai_message = {
        k: message[k]
        for k in ("content", "name", "context")
        if k in message and message[k] is not None
    }
    
    if "content" not in oai_message:
        return False

    oai_message["role"] = role
    self._oai_messages[conversation_id].append(oai_message)

    return True
    