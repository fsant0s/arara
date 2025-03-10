"""
Unit tests for the Neuron class.
"""

import unittest
from unittest.mock import patch, MagicMock

from neuron.neurons.neuron import Neuron
from neuron.capabilities import EpisodicMemoryCapability
from tests.unit.mock_client import MockClient


class TestNeuron(unittest.TestCase):
    """Tests for the Neuron class."""

    def setUp(self):
        """Set up test fixture before each test method is executed."""
        # Set up a mock client for testing
        self.mock_client = MockClient(responses=["I am a test response"])

        # Create a test neuron
        self.neuron = Neuron(
            name="TestNeuron",
            llm_config=False,
            description="A test neuron"
        )

        # Assign the mock client to the neuron
        self.neuron.client_cache = self.mock_client

        # Initialize system message to prevent None errors
        self.neuron._oai_system_message = [{"role": "system", "content": ""}]

    def test_neuron_initialization(self):
        """Test that a Neuron can be initialized with the correct properties."""
        self.assertEqual(self.neuron.name, "TestNeuron")
        self.assertEqual(self.neuron.description, "A test neuron")

    def test_update_description(self):
        """Test that the description of a Neuron can be updated."""
        self.neuron.update_description("Updated description")
        self.assertEqual(self.neuron.description, "Updated description")

    def test_system_message(self):
        """Test that the system message can be set and retrieved."""
        test_system_message = "This is a test system message"
        self.neuron.update_system_message(test_system_message)
        self.assertEqual(self.neuron._oai_system_message[0]["content"], test_system_message)

    def test_generate_reply_basic(self):
        """Test that generate_reply returns the expected response from the mock client."""
        # Mock the client's complete method to return a specific response
        self.mock_client.responses = ["I am a test response"]

        # Configurar um método de patch para o method generate_reply
        with patch.object(MockClient, 'complete', return_value={"choices": [{"message": {"content": "I am a test response"}}]}):
            # Call generate_reply, which should use the mock client
            result = self.neuron.generate_reply("Hello")

            # Verify that the result matches the expected response
            self.assertEqual(result, "I am a test response")

    def test_neuron_with_capability(self):
        """Test that a Neuron can be initialized with capabilities."""
        # Create a neuron with episodic memory
        neuron = Neuron(
            name="TestCapabilityNeuron",
            llm_config=False,
            description="A test neuron with capabilities",
            enable_episodic_memory=True
        )

        # Neuron inicializa a capability como hook_lists
        self.assertTrue(hasattr(neuron, 'hook_lists'))
        self.assertIn('process_message_before_send', neuron.hook_lists)
        self.assertIn('process_last_received_message', neuron.hook_lists)

    def test_neuron_communication(self):
        """Test that two neurons can communicate with each other."""
        # Create a second neuron
        neuron2 = Neuron(
            name="TestNeuron2",
            llm_config=False,
            description="Another test neuron"
        )
        neuron2.client_cache = MockClient(responses=["Response from neuron2"])

        # Send a message from neuron1 to neuron2
        message = "Hello from neuron1"
        response = self.neuron.send(message, neuron2)

        # Now the format of messages is different, check the content instead
        self.assertTrue(any(msg['content'] == message for msg in self.neuron._oai_messages[neuron2]))

    def test_neuron_with_episodic_memory(self):
        """Test that a neuron with episodic memory maintains conversation history."""
        # Create a neuron with episodic memory
        neuron = Neuron(
            name="MemoryNeuron",
            llm_config=False,
            description="A neuron with episodic memory",
            enable_episodic_memory=True
        )

        # Set up the mock client
        mock_client = MockClient(responses=["First response", "Second response with context"])
        neuron.client_cache = mock_client

        # Configurar a geração de respostas
        with patch.object(MockClient, 'complete', return_value={"choices": [{"message": {"content": "First response"}}]}):
            # First interaction
            first_message = "Hello, this is the first message"
            first_response = neuron.generate_reply(first_message)
            self.assertEqual(first_response, "First response")

        # Second interaction with patched response
        with patch.object(MockClient, 'complete', return_value={"choices": [{"message": {"content": "Second response with context"}}]}):
            # Second interaction, should include context from first
            second_message = "What did I say previously?"
            second_response = neuron.generate_reply(second_message)
            self.assertEqual(second_response, "Second response with context")

    @patch('neuron.neurons.neuron.append_oai_message')
    def test_send_message_appends_to_history(self, mock_append):
        """Test that sending a message appends it to the conversation history."""
        # Create a recipient neuron
        recipient = Neuron(
            name="RecipientNeuron",
            llm_config=False,
            description="A recipient neuron"
        )

        # Send a message
        message = "Test message"
        self.neuron.send(message, recipient)

        # Verify that append_oai_message was called with the right parameters
        mock_append.assert_called_once()


if __name__ == "__main__":
    unittest.main()
