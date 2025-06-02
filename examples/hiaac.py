import os
import json
import time
import chainlit as cl

from agents import Agent, Module, Orchestrator, SilentAgent
from agents.helpers import append_oai_message, process_message_before_send
from capabilities.skills import WebCrawler, GoogleDocsReader

llm_config = {
    "config_list": [
        {
            "client": "maritaca",
            "temperature": 0.0,
            "model": "sabia-3",
            "api_key": os.getenv("MARITACA_API_KEY"),
            "base_url": "https://chat.maritaca.ai/api",

        }
    ]
}

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOOGLE_CREDENTIALS_PATH = os.path.join(PROJECT_ROOT, "secrets", "arara-461102-af3f0fba23f1.json")

with open(GOOGLE_CREDENTIALS_PATH, 'r', encoding='utf-8') as arquivo_json:
    creds = json.load(arquivo_json)

def build_orchestrator():
    student = SilentAgent(
        name="student",
        description="A HIAAC student.",
    )

    meeting_agent = Agent(
        name="meeting",
        description=(
            "Answers questions *strictly* about HIAAC meetings..."
        ),
        system_message=f"""
            Follow the user's instructions...
            Today is {time.strftime("%d/%m/%Y", time.localtime())}
        """,
        skills=[
            GoogleDocsReader(
                urls=["https://docs.google.com/document/d/1pAsptw5QUqHWSx-aj47SFbHEUGDvep6q8gHhI5tVE5A/edit?usp=sharing"],
                credentials_info=creds
            )
        ],
        llm_config=llm_config,
    )

    website = Agent(
        name="website",
        description="Answers questions *strictly* about HIAAC researchers...",
        system_message="Follow the user's instructions...",
        skills=[
            WebCrawler(
                urls=[
                    "https://hiaac.unicamp.br/researchers/",
                    "https://hiaac.unicamp.br/students/"
                ]
            )
        ],
        llm_config=llm_config,
    )

    conversational = Agent(
        name="AraraBot",
        description="Conversational agent for general topics...",
        system_message="You are a friendly chatbot...",
        llm_config=llm_config,
    )

    speaker_transitions = {
        student: [conversational, meeting_agent, website],
        conversational: [student],
        meeting_agent: [student],
        website: [student],
    }

    main_module = Module(
        admin_name="main_module",
        agents=[student, conversational, meeting_agent, website],
        speaker_selection_method="auto",
        speaker_transitions_type="allowed",
        allowed_or_disallowed_speaker_transitions=speaker_transitions,
    )

    orchestrator = Orchestrator(
        name="main_orchestrator",
        module=main_module,
        llm_config=llm_config,
    )

    return orchestrator, student

@cl.on_chat_start
async def on_chat_start():
    orchestrator, student = build_orchestrator()
    cl.user_session.set("orchestrator", orchestrator)
    cl.user_session.set("student", student)
    await cl.Message(content="""
    🦜 Olá! Eu sou o **Arara**, seu assistente conversacional criado especialmente para os estudantes do HIAAC!
    Posso te ajudar com dúvidas sobre **reuniões**, **pesquisadores**, e também bater um papo casual se quiser.
    Fique à vontade para explorar — é só me perguntar! 💬
    > ⚠️ **Importante:** Atualmente, estamos utilizando créditos oferecidos pela **Maritaca.AI** para manter este serviço funcionando.
    > Por favor, use com consciência para que todos possam aproveitar sem esgotar os recursos disponíveis. 🙏
    Este projeto é **aberto a contribuições** e está disponível em:
    🔗 [github.com/fsant0s/arara](https://github.com/fsant0s/arara)
    Se tiver ideias, sugestões ou quiser colaborar, a casa é sua. 💡🤝
    Vamos construir juntos!
    """).send()


@cl.on_message
async def main(query: cl.Message):
    orchestrator = cl.user_session.get("orchestrator")
    student = cl.user_session.get("student")

    append_oai_message(student, query.content, "assistant", orchestrator, is_sending=True)
    append_oai_message(orchestrator, query.content, "user", student, is_sending=False)

    for output in orchestrator.generate_reply(sender=student):
        message = process_message_before_send(student, output, orchestrator, silent=True)
        append_oai_message(orchestrator, message, "assistant", student, is_sending=True)
        append_oai_message(student, message, "user", orchestrator, is_sending=False)

    await cl.Message(content=message).send()
