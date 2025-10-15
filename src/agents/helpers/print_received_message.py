import json
import re
from typing import Dict, Literal, Union

from agents.base import BaseAgent
from capabilities.clients import ClientWrapper
from formatting_utils import colored
from ioflow import IOStream

from .content_str import content_str
from .message_to_dict import message_to_dict


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
            },
        }
    raise ValueError("No match found for the provided content string")


def parse_function_execution(content: str):
    match = re.match(
        r"\[FunctionExecutionResult\(content=['|\"](.*?)['|\"], name='(.*?)', call_id='(.*?)', is_error=(.*?)\)\]",
        content,
    )
    if match:
        result_content, name, call_id, is_error = match.groups()
        return {
            "name": name,
            "arguments": result_content,
            "call_id": call_id,
            "is_error": is_error == "True",
        }
    raise ValueError("No match found for the provided content string")


def print_function_call(iostream, parsed):
    function = parsed.get("function", {})
    name_field = function.get("name", "(unknown function)")

    # Divide quando houver concatenação de múltiplos FunctionCall
    parts = re.split(r"FunctionCall", name_field)

    for idx, part in enumerate(parts, start=1):
        text = part.strip()

        # 1) Tenta pegar name='foo' (aceita aspas simples/duplas e até sem a aspa final)
        m = re.search(r"name\s*=\s*['\"]?([A-Za-z0-9_.:-]+)", text)
        if m:
            clean_name = m.group(1)
        else:
            # 2) Se não houver "name=", tenta isolar o primeiro token "limpo"
            text_tmp = re.sub(r"^[\s,;:)'\"\\]+", "", text)
            text_tmp = re.split(r"[,\)]", text_tmp, maxsplit=1)[0]
            m2 = re.search(r"([A-Za-z0-9_.:-]+)$", text_tmp)
            clean_name = m2.group(1) if m2 else text_tmp.strip()

        clean_name = clean_name.strip(" '")  # remove aspas soltas no fim

        if not clean_name or clean_name == "(unknown function)":
            continue

        # Cabeçalho
        title = f"🛠️ Suggested Function Call [{idx}]: {clean_name}"
        iostream.print(colored(title, "green", attrs=["bold"]), flush=True)

        # Arguments — pegue os do próprio bloco
        # Bloco 1: usa os arguments do campo function
        # Blocos seguintes: extrai de arguments='...'(JSON) dentro do trecho atual
        if idx == 1:
            per_args = function.get("arguments", "(no arguments)")
        else:
            margs = re.search(r"arguments\s*=\s*'(\{.*?\})'", text)
            if margs:
                try:
                    per_args = json.loads(margs.group(1))
                except Exception:
                    per_args = {"_raw": margs.group(1)}
            else:
                per_args = "(no arguments)"

        # Impressão dos argumentos
        iostream.print(colored(" Arguments:", "green"), flush=True)
        if isinstance(per_args, dict):
            args_text = json.dumps(per_args, indent=2, ensure_ascii=False).splitlines()
            for line_content in args_text:
                iostream.print(colored(f" {line_content}", "green"), flush=True)
        else:
            iostream.print(colored(f" {per_args}", "green"), flush=True)

        iostream.print("", flush=True)


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
    sender: BaseAgent,
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
                if "context" in message:
                    content = ClientWrapper.instantiate(
                        content,
                        message["context"],
                        llm_config and llm_config.get("allow_format_str_template", False),
                    )
                iostream.print(content_str(content), flush=True)
        else:
            iostream.print(content_str(content), flush=True)
