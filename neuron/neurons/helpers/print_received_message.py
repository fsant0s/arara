from typing import Dict, Literal, Union

from neuron.capabilities.clients import ClientWrapper
from neuron.neurons.base import BaseNeuron

from .content_str import content_str
from ...formatting_utils import colored
from ...io import IOStream
from .message_to_dict import message_to_dict

import re
import json

def parse_function_call(content: str):
    match = re.match(r"\[FunctionCall\(id='(.*?)', arguments='(.*?)', name='(.*?)'\)\]", content)
    if match:
        id, arguments_json, name = match.groups()
        try:
            arguments = json.loads(arguments_json)
        except json.JSONDecodeError:
            arguments = "(Invalid arguments JSON)"
        return {
            "id": id,
            "function": {
                "name": name,
                "arguments": arguments,
            }
        }
    return None

def parse_function_execution(content: str):
    match = re.match(r"\[FunctionExecutionResult\(content='(.*?)', name='(.*?)', call_id='(.*?)', is_error=(.*?)\)\]", content)
    if match:
        result_content, name, call_id, is_error = match.groups()
        return {
            "name": name,
            "arguments": result_content,
            "call_id": call_id,
            "is_error": is_error == "True"
        }
    return None

def print_function_call(iostream, parsed):
    function = parsed.get("function", {})
    name = function.get("name", "(unknown function)")
    title = f"🛠️ Suggested Function Call: {name}"
    iostream.print(colored(f"{title}", "green"), flush=True)
    iostream.print(colored(f" Arguments:", "green"), flush=True)
    arguments = function.get("arguments", "(no arguments)")
    if isinstance(arguments, dict):
        args_text = json.dumps(arguments, indent=2, ensure_ascii=False).splitlines()
        for line_content in args_text:
            iostream.print(colored(f" {line_content}", "green"), flush=True)
    else:
        iostream.print(colored(f" {arguments}", "green"), flush=True)

def print_function_execution(iostream, parsed):
    name = parsed.get("name", "(unknown function)")
    title = f"✅ Function Execution Result: {name}"
    iostream.print(colored(f"{title}", "yellow"), flush=True)
    iostream.print(colored(f" Result:", "yellow"), flush=True)
    result_content = parsed.get("arguments", "(no result content)")
    result_lines = str(result_content).splitlines()
    for line_content in result_lines:
        iostream.print(colored(f" {line_content}", "yellow"), flush=True)

def print_sender_receiver(iostream, sender, name):
    title = f"{sender.name} ⟶ {name}"
    line = "─" * max(40, len(title) + 5)
    iostream.print(colored(f"╭ {title}", "cyan"), flush=True)
    iostream.print(colored(f"╰{line}", "cyan"), flush=True)

def print_received_message(
    message: Union[Dict, str],
    sender: BaseNeuron,
    name: str,
    llm_config: Union[Dict, Literal[False]],
) -> None:
    iostream = IOStream.get_default()

    iostream.print(colored(f"{sender.name} ⟶ {name}:", "cyan"), flush=True)

    message = message_to_dict(message)
    content = message.get("content")
    if content is not None:
        if isinstance(content, str):
            if content.startswith("[FunctionCall"):
                parsed = parse_function_call(content)
                if parsed:
                    print_function_call(iostream, parsed)
            elif content.startswith("[FunctionExecutionResult"):
                parsed = parse_function_execution(content)
                if parsed:
                    print_function_execution(iostream, parsed)
            else:
                # Texto normal
                if "context" in message:
                    content = ClientWrapper.instantiate(
                        content,
                        message["context"],
                        llm_config and llm_config.get("allow_format_str_template", False),
                    )
                iostream.print(content_str(content), flush=True)
        else:
            iostream.print(content_str(content), flush=True)
