import os

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

# Let's first define the assistant agent that suggests tool calls.
user = User(name="user")

# Agente simples que apenas responde mensagens
simple_agent = Agent(
    name="simple_agent",
    llm_config=llm_config,
    system_message="Você é um assistente amigável que responde às perguntas do usuário de forma natural e educada.",
)

chat_result = user.talk_to(simple_agent, message="Oi tudo bem?")
