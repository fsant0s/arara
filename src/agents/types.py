from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import logging

logger = logging.getLogger(__name__)

@dataclass
class FunctionCall:
    """A function call issued by the agent during a chat."""

    id: str
    """Unique identifier for the function call."""

    arguments: str
    """The JSON-formatted string containing the arguments to be passed to the function."""

    name: str
    """The name of the function to be invoked."""

@dataclass(kw_only=True)
class Response:
    """A response from calling .create()"""

    to_reply : bool = True
    """Whether the agent should reply."""

    chat_message: "ChatMessage"  # type hint as string to avoid direct evaluation
    """A chat message produced by the agent as the response."""

@dataclass
class ChatResult:
    """The result of a chat."""

    chat_id: int = None
    """chat id"""
    chat_history: List[Dict[str, Any]] = None
    """The chat history."""
    summary: str = None
    """A summary obtained from the chat."""
    cost: Dict[str, dict] = None  # keys: "usage_including_cached_inference", "usage_excluding_cached_inference"
    """The cost of the chat.
       The value for each usage type is a dictionary containing cost information for that specific type.
           - "usage_including_cached_inference": Cost information on the total usage, including the tokens in cached inference.
           - "usage_excluding_cached_inference": Cost information on the usage of tokens, excluding the tokens in cache. No larger than "usage_including_cached_inference".
    """
    human_input: List[str] = None
    """A list of human input solicited during the chat."""
