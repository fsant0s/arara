from typing import Dict, Union

from neuron.neurons.base import BaseNeuron

from .message_to_dict import message_to_dict


def append_oai_message(
    self: BaseNeuron,
    message: Union[Dict, str],
    role,
    conversation_id: BaseNeuron,
    is_sending: bool,
) -> bool:
    message = message_to_dict(message)
    # create oai message to be appended to the oai conversation that can be passed to oai directly.
    oai_message = {
        k: message[k]
        for k in ("content", "function_call", "tool_calls", "tool_responses", "tool_call_id", "name", "context")
        if k in message and message[k] is not None
    }

    if "content" not in oai_message:
        if "function_call" in oai_message or "tool_calls" in oai_message:
            oai_message["content"] = None  # if only function_call is provided, content will be set to None.
        else:
            return False

    if message.get("role") in ["function", "tool"]:
        oai_message["role"] = message.get("role")
    elif "override_role" in message:
        # If we have a direction to override the role then set the
        # role accordingly. Used to customise the role for the
        # select speaker prompt.
        oai_message["role"] = message.get("override_role")
    else:
        oai_message["role"] = role

    if oai_message.get("function_call", False) or oai_message.get("tool_calls", False):
        oai_message["role"] = "assistant"  # only messages with role 'assistant' can have a function call.
    elif "name" not in oai_message:
        # If we don't have a name field, append it
        if is_sending:
            oai_message["name"] = self.name
        else:
            oai_message["name"] = conversation_id.name

    self._oai_messages[conversation_id].append(oai_message)

    return True
