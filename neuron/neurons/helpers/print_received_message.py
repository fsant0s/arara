from typing import Union, Dict, Literal

from neuron.clients import ClientWrapper
from neuron.neurons.base_neuron import BaseNeuron

from .message_to_dict import message_to_dict

from ...io import IOStream
from ...formatting_utils import colored
from ...code_utils import content_str

def print_received_message(message: Union[Dict, str], sender: BaseNeuron, name: str, llm_config : Union[Dict, Literal[False]]) -> None:
    iostream = IOStream.get_default()
    # print the message received
    iostream.print(colored(sender.name, "yellow"), "(to", f"{name}):\n", flush=True)
    message = message_to_dict(message)

    if message.get("role") in ["function", "tool"]:
        if message["role"] == "function":
            id_key = "name"
        else:
            id_key = "tool_call_id"
        id = message.get(id_key, "No id found")
        func_print = f"***** Response from calling {message['role']} ({id}) *****"
        iostream.print(colored(func_print, "green"), flush=True)
        iostream.print(message["content"], flush=True)
        iostream.print(colored("*" * len(func_print), "green"), flush=True)
    else:
        content = message.get("content")
        if content is not None:
            if "context" in message:
                content = ClientWrapper.instantiate(
                    content,
                    message["context"],
                    llm_config and llm_config.get("allow_format_str_template", False),
                )
            iostream.print(content_str(content), flush=True)
        if "function_call" in message and message["function_call"]:
            function_call = dict(message["function_call"])
            func_print = (
                f"***** Suggested function call: {function_call.get('name', '(No function name found)')} *****"
            )
            iostream.print(colored(func_print, "green"), flush=True)
            iostream.print(
                "Arguments: \n",
                function_call.get("arguments", "(No arguments found)"),
                flush=True,
                sep="",
            )
            iostream.print(colored("*" * len(func_print), "green"), flush=True)
        if "tool_calls" in message and message["tool_calls"]:
            for tool_call in message["tool_calls"]:
                id = tool_call.get("id", "No tool call id found")
                function_call = dict(tool_call.get("function", {}))
                func_print = f"***** Suggested tool call ({id}): {function_call.get('name', '(No function name found)')} *****"
                iostream.print(colored(func_print, "green"), flush=True)
                iostream.print(
                    "Arguments: \n",
                    function_call.get("arguments", "(No arguments found)"),
                    flush=True,
                    sep="",
                )
                iostream.print(colored("*" * len(func_print), "green"), flush=True)

    iostream.print("\n", "-" * 80, flush=True, sep="")

 