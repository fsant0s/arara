from unittest.mock import MagicMock
from neuron.scripts.round_robin import RoundRobin, RoundRobinManager

def test_should_instantiate_round_robin():
    # Instancia o RoundRobin com agentes e mensagens fictícios
    agents = []  # Pode ser uma lista vazia ou uma lista de mocks de agentes
    messages = []
    round_robin = RoundRobin(agents=agents, messages=messages)

    # Verifica se o objeto foi instanciado corretamente
    assert round_robin.agents == agents
    assert round_robin.messages == messages
    assert round_robin.max_round == 3
    assert round_robin.admin_name == "Admin"

def test_should_instantiate_round_robin_manager():
    # Instancia o RoundRobin com agentes e mensagens fictícios
    agents = []  # Pode ser uma lista vazia ou uma lista de mocks de agentes
    messages = []
    round_robin = RoundRobin(agents=agents, messages=messages)

    # Instancia o RoundRobinManager com o RoundRobin criado anteriormente
    manager = RoundRobinManager(groupchat=round_robin)

    # Verifica se o objeto foi instanciado corretamente
    assert manager.groupchat == round_robin
    assert manager.name == "chat_manager"
    assert manager.system_message == "Group chat manager."
    assert manager._silent == False


""" def test_should_fire_round_robin_manager():
    # Cria mocks para os agentes
    agent1 = MagicMock(name="Agent1")
    agent2 = MagicMock(name="Agent2")
    agent3 = MagicMock(name="Agent3")
    agent4 = MagicMock(name="Agent4")
    agent5 = MagicMock(name="Agent5")
    agent6 = MagicMock(name="Agent6")
    agent7 = MagicMock(name="Agent7")
    agent8 = MagicMock(name="Agent8")

    # Configura a lista de agentes e uma mensagem inicial válida para o formato ChatCompletion
    agents = [agent1, agent2, agent3, agent4, agent5, agent6, agent7, agent8]
    initial_message = {"type": "text", "content": "Initial message"}  # Adiciona um campo 'content' válido
    messages = [initial_message]
    round_robin = RoundRobin(agents=agents, messages=messages)

    # Instancia o RoundRobinManager com o RoundRobin criado
    manager = RoundRobinManager(groupchat=round_robin)

    # Configura as respostas simuladas dos agentes
    for i, agent in enumerate(agents, start=1):
        agent.generate_reply.return_value = {"type": "text", "content": f"Reply from agent {i}"}
        agent.send = MagicMock()

    # Certifica-se de que _oai_messages está definido para todos os agentes no manager
    manager._oai_messages = {agent: messages.copy() for agent in agents}

    # Mocka o método `send` no próprio RoundRobinManager
    manager.send = MagicMock()

    # Executa o método fire do RoundRobinManager
    result = manager.fire(messages=messages, sender=agent1, config=round_robin)

    # Verifica o resultado e as interações dos agentes
    assert result == (True, None)

    # Verifica se o método send foi chamado corretamente pelo manager
    manager.send.assert_any_call(initial_message, agent2, request_reply=False, silent=True)
    for agent in agents:
        agent.send.assert_called() """
