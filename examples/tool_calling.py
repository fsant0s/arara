import os
from datetime import datetime
from typing import Literal

from agents import Agent, User

llm_config = {
    "config_list": [
        {
            "client": "ollama",
            "temperature": 0.7,
            "model": "llama3.2",
            "base_url": "http://localhost:11434",
        }
    ]
}

Operator = Literal["+", "-", "*", "/"]


def calculator(a: float, b: float, operator: Operator) -> float:
    """Performs basic arithmetic operations between two numbers.

    Parameters:
    - a (float): The first number.
    - b (float): The second number.
    - operator (str): One of the following: "+", "-", "*", "/".

    Returns:
    - float: The result of the operation.

    Raises:
    - ValueError: If the operator is invalid or division by zero occurs.
    """
    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        return a / b
    else:
        raise ValueError(f"Unsupported operator '{operator}'")


# Let's first define the assistant agent that suggests tool calls.
user = User(name="user")

# Novo agente com lógica de decisão melhorada
math = Agent(
    name="calc_agent",
    llm_config=llm_config,
    system_message="Você é um assistente amigável que ajuda a responder as perguntas do usuário.",
    tools=[calculator],
    reflect_on_tool_use=True,
)

chat_result = user.talk_to(math, message="Oi tudo bem?")
