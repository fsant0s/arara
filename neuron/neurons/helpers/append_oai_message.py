from .message_to_dict import message_to_dict

from typing import Union, Dict
from neuron.neurons.base_neuron import BaseNeuron

def append_oai_message(self: BaseNeuron, message: Union[Dict, str], role, conversation_id: BaseNeuron, is_sending: bool) -> bool:
        
    message = message_to_dict(message)
    
    # create oai message to be appended to the oai conversation that can be passed to oai directly.
    oai_message = {
        k: message[k]
        for k in ("content", "name", "context")
        if k in message and message[k] is not None
    }
    
    if "content" not in oai_message:
        return False
    
    if "name" not in oai_message:
        # If we don't have a name field, append it
        if is_sending:
            oai_message["name"] = self.name
        else:
            oai_message["name"] = conversation_id.name

    oai_message["role"] = role
    self._oai_messages[conversation_id].append(oai_message)

    return True
    