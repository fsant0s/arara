"""
Integration test for a simple recommendation flow.

This test demonstrates how different components of the NEURON framework
work together to process a recommendation request.
"""

import unittest
from typing import List, Dict, Any

from neuron.neurons import Neuron, RouterNeuron
from neuron.capabilities import (
    EpisodicMemoryCapability,
    ReflectionCapability
)
from tests.unit.mock_client import MockClient


class TestRecommendationFlow(unittest.TestCase):
    """Integration tests for a recommendation flow using multiple neurons."""

    def setUp(self):
        """Set up test environment before each test."""
        # Create a mock client with predefined responses
        self.mock_client = MockClient()

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
        # Set up mock responses for each step in the flow
        self.mock_client.set_responses([
            # First response: User profiler extracts preferences
            "User preferences: Budget under $1000, 15-inch screen, good battery life, programming use case",

            # Second response: Recommender generates recommendations
            "Based on your preferences, I recommend the following laptops:\n" +
            "1. Dell XPS 15 - $999\n" +
            "2. Lenovo ThinkPad X1 Carbon - $950\n" +
            "3. MacBook Air M2 - $999"
        ])

        # Input query
        user_query = "I need a laptop for programming that costs less than $1000. " + \
                    "I want a 15-inch screen and good battery life."

        # Process through the router
        result = self.router.process(user_query)

        # Assertions to validate the flow
        self.assertIsNotNone(result)
        self.assertIn("recommend", result.lower())
        self.assertIn("dell xps", result.lower())
        self.assertIn("lenovo", result.lower())
        self.assertIn("macbook", result.lower())

        # Check that both neurons were involved in processing
        # The router should have used both the profiler and recommender
        self.assertEqual(len(self.mock_client.calls), 2)

    def test_follow_up_question(self):
        """Test handling a follow-up question that references previous context."""
        # Set up initial responses
        self.mock_client.set_responses([
            # First flow: Initial recommendation
            "User preferences: Gaming laptop, high performance, RGB lighting",
            "I recommend the ASUS ROG Strix G15 with NVIDIA RTX 4070, 16GB RAM, and RGB keyboard.",

            # Second flow: Follow-up about battery life
            "Previously recommended: ASUS ROG Strix G15 with NVIDIA RTX 4070",
            "The ASUS ROG Strix G15 typically has about 5-6 hours of battery life for normal usage, " +
            "but only 1-2 hours when gaming at full performance."
        ])

        # Initial query
        initial_query = "I'm looking for a good gaming laptop with RGB lighting."
        result1 = self.router.process(initial_query)

        # Verify initial response
        self.assertIn("asus rog", result1.lower())
        self.assertIn("rtx", result1.lower())

        # Follow-up query
        follow_up_query = "How's the battery life on that model?"
        result2 = self.router.process(follow_up_query)

        # Verify that the follow-up response references the previous recommendation
        self.assertIn("5-6 hours", result2)
        self.assertIn("1-2 hours when gaming", result2)

        # Check that all expected API calls were made
        self.assertEqual(len(self.mock_client.calls), 4)  # 2 neurons x 2 questions


if __name__ == "__main__":
    unittest.main()
