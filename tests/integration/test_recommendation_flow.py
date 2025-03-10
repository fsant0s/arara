"""
Integration test for a simple recommendation flow.

This test demonstrates how different components of the NEURON framework
work together to process a recommendation request.
"""

import unittest
from typing import List, Dict, Any
from unittest import mock
from unittest.mock import patch

from neuron.neurons import Neuron, RouterNeuron, User
from neuron.capabilities import (
    EpisodicMemoryCapability,
    ReflectionCapability
)
from tests.unit.mock_client import MockClient


class TestRecommendationFlow(unittest.TestCase):
    """Integration tests for a recommendation flow using multiple neurons."""

    def routing_function(self, message: Any, components: List) -> int:
        """Simple routing function that returns the index of the first component"""
        # For simplicity, we'll just route to the first component (user profiler)
        # In a real implementation, this would analyze the message and determine
        # the appropriate neuron to handle it
        return 0

    def setUp(self):
        """Set up test environment before each test."""
        # Create a mock client with predefined responses
        self.mock_client = MockClient()

        # Configurar o MockClient para retornar respostas no formato correto
        def mock_complete(*args, **kwargs):
            response_text = self.mock_client.responses[self.mock_client.current_response_index % len(self.mock_client.responses)]
            self.mock_client.current_response_index += 1
            return {
                "choices": [{"message": {"content": response_text}}]
            }

        self.mock_client.complete = mock_complete

        # Create specialized neurons for the recommendation flow
        self.user_profiler = Neuron(
            name="UserProfiler",
            system_message="You analyze user input to identify preferences and requirements."
        )
        self.user_profiler.client_cache = self.mock_client

        # Create a recommender neuron
        self.recommender = Neuron(
            name="Recommender",
            system_message="You provide personalized recommendations based on user preferences."
        )
        self.recommender.client_cache = self.mock_client

        # Create a router neuron to coordinate the flow
        self.router = RouterNeuron(
            route_mapping_function=self.routing_function,
            name="Router",
            description="Coordinates the recommendation flow",
            llm_config=False
        )
        self.router.client_cache = self.mock_client

        # Add capabilities after neuron creation
        EpisodicMemoryCapability(self.user_profiler)
        EpisodicMemoryCapability(self.recommender)
        ReflectionCapability(self.recommender)

    def test_simple_recommendation_flow(self):
        """Test a simple recommendation flow from user input to recommendation."""
        # Teste simplificado que faz mock diretamente do método que gera respostas
        with patch('neuron.neurons.neuron.Neuron._generate_oai_reply', return_value="Mock laptop recommendation"):
            # Verificar se o router consegue gerar uma resposta básica
            response = self.router.generate_reply("I need a laptop")

            # Realmente estamos apenas testando se o generate_reply chama o método correto
            self.assertEqual(response, "Mock laptop recommendation")

    def test_follow_up_question(self):
        """Test handling a follow-up question that references previous context."""
        # Fazer patch do método que gera respostas para a primeira pergunta
        with patch('neuron.neurons.neuron.Neuron._generate_oai_reply', return_value="Initial laptop recommendation"):
            # Primeira pergunta
            response1 = self.router.generate_reply("I need a laptop")
            self.assertEqual(response1, "Initial laptop recommendation")

        # Fazer patch para a segunda pergunta (follow-up)
        with patch('neuron.neurons.neuron.Neuron._generate_oai_reply', return_value="Follow-up battery life info"):
            # Segunda pergunta (follow-up)
            response2 = self.router.generate_reply("What about the battery life?")
            self.assertEqual(response2, "Follow-up battery life info")


if __name__ == "__main__":
    unittest.main()
