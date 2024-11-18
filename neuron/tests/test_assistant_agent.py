import pytest
from unittest.mock import MagicMock, patch
from neuron.agents.assistant_agent import AssistantAgent
from neuron.clients import CloudBasedClient

@patch("neuron.clients.CloudBasedClient", autospec=True)
def test_should_initialize_assistant_agent_with_defaults(mock_client_class):
    # Mock the client and ensure it has the necessary _clients attribute
    mock_client = mock_client_class.return_value
    mock_client._clients = [MagicMock(spec=CloudBasedClient)]

    # Patch the client initialization in LLMAgent
    with patch("neuron.agents.llm_agent.LLMAgent.client", new_callable=MagicMock, return_value=mock_client):
        agent = AssistantAgent(name="AssistantAgent")
        assert agent.name == "AssistantAgent"
        assert agent.description == AssistantAgent.DEFAULT_DESCRIPTION
        assert agent.system_message == AssistantAgent.DEFAULT_SYSTEM_MESSAGE


""" def test_should_initialize_assistant_agent_with_custom_values():
    custom_description = "Custom assistant description"
    custom_system_message = "You are a custom assistant"
    custom_llm_config = {"model": "custom-model"}

    agent = AssistantAgent(
        name="CustomAgent",
        description=custom_description,
        system_message=custom_system_message,
        llm_config=custom_llm_config,
    )

    assert agent.name == "CustomAgent"
    assert agent.description == custom_description
    assert agent.system_message == custom_system_message
    assert agent.llm_config == custom_llm_config

def test_should_log_new_agent_if_logging_enabled():
    with patch("neuron.runtime_logging.logging_enabled", return_value=True), \
         patch("neuron.runtime_logging.log_new_agent") as mock_log_new_agent:
        agent = AssistantAgent(name="LoggableAgent")
        mock_log_new_agent.assert_called_once_with(agent, {"name": "LoggableAgent"})

def test_should_raise_error_if_client_is_not_cloudbased():
    mock_client = MagicMock()
    mock_client._clients = [MagicMock()]  # Mock não é do tipo `CloudBasedClient`

    with patch("neuron.agents.llm_agent.LLMAgent.client", new_callable=MagicMock, return_value=mock_client):
        with pytest.raises(ValueError, match="The client argument should be a CloudBasedClient instance."):
            AssistantAgent(name="InvalidClientAgent")
 """