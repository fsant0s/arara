import pytest
from unittest.mock import MagicMock, patch
from collections import defaultdict
from typing import Dict, List

from neuron.agents import Agent, BaseAgent

def test_should_initialize_agent_with_default_values():
    agent = Agent(name="TestAgent")
    assert agent.name == "TestAgent"
    assert agent.description is None
    assert isinstance(agent._oai_messages, defaultdict)
    assert agent.llm_config is False

""" def test_should_initialize_agent_with_custom_values():
    mock_llm_config = {"key": "value"}
    agent = Agent(
        name="TestAgent",
        description="This is a test agent.",
        llm_config=mock_llm_config,
    )
    assert agent.name == "TestAgent"
    assert agent.description == "This is a test agent."
    assert agent.llm_config == mock_llm_config """

def test_should_update_description():
    agent = Agent(name="TestAgent")
    agent.update_description("Updated description")
    assert agent.description == "Updated description"
""" 
def test_should_register_reply_function():
    agent = Agent(name="TestAgent")
    reply_func = MagicMock()
    trigger = BaseAgent
    agent.register_reply(trigger, reply_func)

    assert len(agent._reply_func_list) == 1
    assert agent._reply_func_list[0]["reply_func"] == reply_func
    assert agent._reply_func_list[0]["trigger"] == trigger """

""" def test_should_replace_reply_function():
    agent = Agent(name="TestAgent")
    old_func = MagicMock()
    new_func = MagicMock()

    agent.register_reply(BaseAgent, old_func)
    agent.replace_reply_func(old_func, new_func)

    assert len(agent._reply_func_list) == 1
    assert agent._reply_func_list[0]["reply_func"] == new_func """

def test_should_register_hook():
    agent = Agent(name="TestAgent")
    hook = MagicMock()

    agent.register_hook("process_last_received_message", hook)

    assert len(agent.hook_lists["process_last_received_message"]) == 1
    assert agent.hook_lists["process_last_received_message"][0] == hook

def test_should_fail_registering_hook_for_invalid_method():
    agent = Agent(name="TestAgent")
    with pytest.raises(AssertionError, match="invalid_method is not a hookable method"):
        agent.register_hook("invalid_method", MagicMock())
    
def test_should_generate_reply_with_hooks():
    agent = Agent(name="TestAgent")
    mock_sender = MagicMock()

    # Mock hooks
    agent.register_hook("process_last_received_message", MagicMock())
    agent.register_hook("process_all_messages_before_reply", MagicMock())
    agent.register_hook("append_short_memories_before_reply", MagicMock())

    agent._oai_messages[mock_sender] = [{"content": "test"}]
    reply = agent.generate_reply(sender=mock_sender)

    assert reply == ""  # Default auto-reply

def test_should_fail_generate_reply_with_no_sender_or_messages():
    agent = Agent(name="TestAgent")
    with pytest.raises(AssertionError, match="Either .* must be provided."):
        agent.generate_reply()

def test_should_initiate_chat():
    agent = Agent(name="TestAgent")
    recipient = MagicMock()
    agent.send = MagicMock()

    agent.initiate_chat(recipient, message={"content": "Hello"})
    agent.send.assert_called_once_with({"content": "Hello"}, recipient, silent=True)

def test_should_send_message():
    agent = Agent(name="TestAgent")
    recipient = MagicMock()
    recipient.receive = MagicMock()

    agent.send({"content": "Test message"}, recipient)
    recipient.receive.assert_called_once()

def test_should_fail_sending_invalid_message():
    agent = Agent(name="TestAgent")
    recipient = MagicMock()

    with pytest.raises(ValueError, match="Message can't be converted into a valid ChatCompletion message"):
        agent.send({}, recipient)

def test_should_receive_message_and_reply():
    agent = Agent(name="TestAgent")
    sender = MagicMock()
    sender.name = "SenderAgent"
    agent.reply_at_receive[sender] = True
    agent.send = MagicMock()

    agent.receive({"content": "Hello"}, sender)
    agent.send.assert_called_once()

def test_should_not_reply_on_receive_if_disabled():
    agent = Agent(name="TestAgent")
    sender = MagicMock()
    sender.name = "SenderAgent"
    agent.reply_at_receive[sender] = False
    agent.send = MagicMock()

    agent.receive({"content": "Hello"}, sender)
    agent.send.assert_not_called()

def test_should_return_last_message():
    agent = Agent(name="TestAgent")
    sender = MagicMock()
    agent._oai_messages[sender].append({"content": "Last message"})

    last_message = agent.last_message(sender)
    assert last_message["content"] == "Last message"

def test_should_fail_returning_last_message_for_invalid_sender():
    agent = Agent(name="TestAgent")
    with pytest.raises(KeyError):
        agent.last_message(MagicMock())

def test_should_fail_returning_last_message_with_multiple_conversations():
    agent = Agent(name="TestAgent")
    agent._oai_messages[MagicMock()] = [{"content": "Message 1"}]
    agent._oai_messages[MagicMock()] = [{"content": "Message 2"}]

    with pytest.raises(ValueError, match="More than one conversation is found."):
        agent.last_message()

""" def test_should_generate_oai_reply_from_client():
    agent = Agent(name="TestAgent")
    mock_client = MagicMock()
    mock_client.create.return_value = {"choices": [{"text": "Generated reply"}]}
    mock_client.extract_text_or_completion_object.return_value = [{"content": "Generated reply"}]
    messages = [{"content": "Hello"}]

    # Simula o método para obter resposta
    reply = agent._generate_oai_reply_from_client(mock_client, messages, None)

    assert reply["content"] == "Generated reply"
    mock_client.create.assert_called_once() """

""" def test_should_register_and_clear_reply_functions():
    agent = Agent(name="TestAgent")
    func1 = MagicMock()
    func2 = MagicMock()

    # Registra a primeira função
    agent.register_reply(BaseAgent, func1)
    assert len(agent._reply_func_list) == 1

    # Registra outra função removendo a anterior
    agent.register_reply(BaseAgent, func2, remove_other_reply_funcs=True)
    assert len(agent._reply_func_list) == 1
    assert agent._reply_func_list[0]["reply_func"] == func2 """

def test_should_return_last_message_from_specific_agent():
    agent = Agent(name="TestAgent")
    sender = MagicMock()
    agent._oai_messages[sender] = [{"content": "First message"}, {"content": "Last message"}]

    last_message = agent.last_message(sender)
    assert last_message["content"] == "Last message"

def test_should_return_last_message_with_single_conversation():
    agent = Agent(name="TestAgent")
    mock_sender = MagicMock()
    agent._oai_messages[mock_sender] = [{"content": "Only message"}]

    last_message = agent.last_message()
    assert last_message["content"] == "Only message"

def test_should_return_none_when_no_messages():
    agent = Agent(name="TestAgent")
    last_message = agent.last_message()
    assert last_message is None

def test_should_fail_register_reply_with_invalid_trigger():
    agent = Agent(name="TestAgent")
    with pytest.raises(ValueError, match="trigger must be a class, a string, an agent, a callable or a list."):
        agent.register_reply(123, MagicMock())

def test_should_fail_generate_oai_reply_without_client():
    agent = Agent(name="TestAgent", llm_config=None)
    result = agent._generate_oai_reply(messages=[{"content": "test"}], sender=MagicMock())
    assert result == (False, None)

""" def test_should_fail_initialization_with_invalid_llm_config():
    class NonCopyable:
        pass

    invalid_config = {"key": NonCopyable()}

    with pytest.raises(TypeError, match="Please implement __deepcopy__ method"):
        Agent(name="TestAgent", llm_config=invalid_config) """