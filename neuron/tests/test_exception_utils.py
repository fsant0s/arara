import pytest
from neuron.exception_utils import AgentNameConflict, SenderRequired

# QUESTION: What is the purpose of this class? What does it do?
def test_should_raise_agent_name_conflict_exception():
    with pytest.raises(AgentNameConflict, match="Found multiple agents with the same name."):
        raise AgentNameConflict()

def test_should_raise_sender_required_exception():
    with pytest.raises(SenderRequired, match="Sender is required but not provided."):
        raise SenderRequired()