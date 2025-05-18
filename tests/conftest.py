"""
Shared fixtures for pytest.

This module contains fixtures that can be reused across tests.
"""

from typing import Any, Dict, List, Optional

import pytest

from src.capabilities import EpisodicMemoryCapability, ReflectionCapability
from src.agents import Agent
from src.agents.user import User
from tests.unit.mock_client import MockClient


@pytest.fixture
def mock_client():
    """Create a MockClient instance for testing."""
    return MockClient(responses=["Mock response"])


@pytest.fixture
def basic_agent(mock_client):
    """Create a basic Agent instance for testing."""
    return Agent(
        name="TestAgent",
        client=mock_client,
        description="A test agent for unit tests",
    )


@pytest.fixture
def memory_agent(mock_client):
    """Create a Agent instance with EpisodicMemoryCapability for testing."""
    return Agent(
        name="MemoryAgent",
        client=mock_client,
        capabilities=[EpisodicMemoryCapability()],
        description="A test agent with episodic memory",
    )


@pytest.fixture
def advanced_agent(mock_client):
    """Create a Agent instance with multiple capabilities for testing."""
    return Agent(
        name="AdvancedAgent",
        client=mock_client,
        capabilities=[EpisodicMemoryCapability(), ReflectionCapability()],
        description="A test agent with multiple capabilities",
    )


@pytest.fixture
def user():
    """Create a User instance for testing."""
    return User(name="TestUser")


@pytest.fixture
def conversation_history():
    """Create a sample conversation history for testing."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {
            "role": "assistant",
            "content": "I'm doing well, thank you. How can I help you today?",
        },
        {"role": "user", "content": "I need some information about neural networks."},
    ]


@pytest.fixture
def preset_responses():
    """Create a list of preset responses for testing."""
    return [
        "This is the first response.",
        "This is the second response.",
        "This is the third response.",
    ]


@pytest.fixture
def mock_client_with_preset_responses(preset_responses):
    """Create a MockClient with preset responses for testing."""
    return MockClient(responses=preset_responses)
