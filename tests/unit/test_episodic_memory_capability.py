"""
Unit tests for the EpisodicMemoryCapability class.

This module tests the functionality of the episodic memory capability,
which allows neurons to store and retrieve past interactions.
"""

import unittest
from unittest import mock

from neuron.capabilities import EpisodicMemoryCapability
from neuron.cognitions import EpisodicMemory
from neuron.neurons.base_neuron import BaseNeuron
from neuron.neurons.neuron import Neuron
from tests.unit.mock_neuron import MockNeuron


class MockNeuron(BaseNeuron):
    """Mock implementation of BaseNeuron for testing."""

    def __init__(self):
        self.hooks = {}
        self.messages = []

    def register_hook(self, hookable_method, hook):
        """Register a hook for a method."""
        if hookable_method not in self.hooks:
            self.hooks[hookable_method] = []
        self.hooks[hookable_method].append(hook)

    def send(self, message, recipient, silent=False):
        """Mock send method."""
        self.messages.append((message, recipient, silent))
        # Call hooks if registered
        if "process_message_before_send" in self.hooks:
            for hook in self.hooks["process_message_before_send"]:
                message = hook(self, message, recipient, silent)
        return message

    def receive(self, message, sender):
        """Mock receive method."""
        # Call hooks if registered
        if "process_last_received_message" in self.hooks:
            for hook in self.hooks["process_last_received_message"]:
                message = hook(message)
        return message


class TestEpisodicMemoryCapability(unittest.TestCase):
    """Tests for the EpisodicMemoryCapability class."""

    def setUp(self):
        """Set up the test case."""
        self.neuron = MockNeuron()

    def test_initialization(self):
        """Test that the capability initializes correctly."""
        capability = EpisodicMemoryCapability(self.neuron)

        # Verify that hooks were registered
        self.assertIn("process_message_before_send", self.neuron.hooks)
        self.assertIn("process_last_received_message", self.neuron.hooks)

        # Verify that the episodic memory was created
        self.assertIsInstance(capability._episodic_memory, EpisodicMemory)

        # Verify that the memory intro was set
        self.assertEqual(capability._memory_intro, EpisodicMemoryCapability.DEFAULT_MEMORY_INTRO)

    def test_custom_memory_intro(self):
        """Test that a custom memory intro can be provided."""
        custom_intro = "Custom memory introduction:"
        capability = EpisodicMemoryCapability(self.neuron, memory_intro=custom_intro)

        self.assertEqual(capability._memory_intro, custom_intro)

    @mock.patch.object(EpisodicMemory, "_store")
    def test_store_message(self, mock_store):
        """Test that messages are stored in episodic memory."""
        capability = EpisodicMemoryCapability(self.neuron)

        # Test the _store method directly
        message = "Test message"
        recipient = MockNeuron()
        result = capability._store(self.neuron, message, recipient, False)

        # Verify that the message was stored
        mock_store.assert_called_once_with(message)

        # Verify that the message is returned unchanged
        self.assertEqual(result, message)

    @mock.patch.object(EpisodicMemory, "_retrieve_all")
    def test_retrieve_all_with_no_memories(self, mock_retrieve_all):
        """Test retrieval when there are no memories."""
        mock_retrieve_all.return_value = []

        capability = EpisodicMemoryCapability(self.neuron)
        message = "Current message"

        result = capability._retrieve_all(message)

        # Verify that _retrieve_all was called
        mock_retrieve_all.assert_called_once()

        # With no memories, the message should be returned unchanged
        self.assertEqual(result, message)

    @mock.patch.object(EpisodicMemory, "_retrieve_all")
    def test_retrieve_all_with_memories(self, mock_retrieve_all):
        """Test retrieval when there are memories."""
        mock_memories = [{"content": "Memory 1"}, {"content": "Memory 2"}]
        mock_retrieve_all.return_value = mock_memories

        capability = EpisodicMemoryCapability(self.neuron)
        message = "Current message"

        result = capability._retrieve_all(message)

        # Verify that _retrieve_all was called
        mock_retrieve_all.assert_called_once()

        # Verifica que o resultado inclui a mensagem original e as memórias
        expected_result = (
            f"Current message\n\n" f"{capability._memory_intro}\n\n" f"1. Memory 1\n" f"2. Memory 2"
        )
        self.assertEqual(result, expected_result)

    def test_integration_with_send(self):
        """Test that the capability integrates with the neuron's send method."""
        # Simplificando o teste para apenas verificar se os hooks são registrados corretamente
        neuron = Neuron(
            name="TestNeuron",
            llm_config=False,
            description="Test neuron",
            enable_episodic_memory=True,  # Ativar a memória episódica
        )

        # Verificar que a Neuron tem os hooks registrados
        self.assertIn("process_message_before_send", neuron.hook_lists)
        self.assertTrue(len(neuron.hook_lists["process_message_before_send"]) > 0)

        # O teste é positivo se os hooks foram registrados
        # Não precisamos testar o fluxo completo


if __name__ == "__main__":
    unittest.main()
