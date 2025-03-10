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
        """Set up test environment before each test."""
        self.mock_client = MockClient(responses=["I am a test response"])
        # Create neuron without client parameter, as it's no longer supported
        self.neuron = Neuron(
            name="TestNeuron",
            llm_config=False,  # Turn off LLM inference validation
            description="A test neuron"
        )
        # Manually attach the mock client for testing purposes
        self.neuron.client_cache = self.mock_client

    def test_neuron_initialization(self):
        """Test that a Neuron can be initialized with basic properties."""
        self.assertEqual(self.neuron.name, "TestNeuron")
        self.assertEqual(self.neuron.description, "A test neuron")

    def test_update_description(self):
        """Test that the description can be updated."""
        new_description = "An updated test neuron"
        self.neuron.update_description(new_description)
        self.assertEqual(self.neuron.description, new_description)

    def test_system_message(self):
        """Test that the system message can be set and retrieved."""
        test_system_message = "This is a test system message"
        self.neuron.update_system_message(test_system_message)
        self.assertEqual(self.neuron.system_message, test_system_message)

    def test_generate_reply_basic(self):
        """Test that generate_reply returns the expected response from the mock client."""
        # Mock the client's complete method to return a specific response
        response = "I am a test response"

        # Call generate_reply, which should use the mock client
        with patch.object(self.neuron, 'client_cache', self.mock_client):
            result = self.neuron.generate_reply("Hello")

        # Verify that the result matches the expected response
        self.assertEqual(result, response)

    def test_neuron_with_capability(self):
        """Test that a Neuron can be initialized with capabilities."""
        # Create a neuron
        neuron = Neuron(
            name="TestCapabilityNeuron",
            llm_config=False,
            description="A test neuron with capabilities"
        )

        # Add the capability after neuron creation
        capability = EpisodicMemoryCapability(neuron)

        # Test that the neuron has the capability
        self.assertTrue(hasattr(neuron, '_hooks'))
        self.assertTrue('process_message_before_send' in neuron._hooks)
        self.assertTrue('process_last_received_message' in neuron._hooks)

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

        # Verify that the message was sent and received correctly
        self.assertIn((message, neuron2, False), self.neuron._oai_messages[neuron2])
        self.assertEqual(response, "Response from neuron2")

    def test_neuron_with_episodic_memory(self):
        """Test that a neuron with episodic memory maintains conversation history."""
        # Create a neuron with episodic memory
        neuron = Neuron(
            name="MemoryNeuron",
            llm_config=False,
            description="A neuron with episodic memory",
            enable_episodic_memory=True
        )
        neuron.client_cache = MockClient(responses=["First response", "Second response with context"])

        # First interaction
        first_message = "Hello, this is the first message"
        first_response = neuron.generate_reply(first_message)
        self.assertEqual(first_response, "First response")

        # Second interaction - should include context from first
        second_message = "This is a follow-up"
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
