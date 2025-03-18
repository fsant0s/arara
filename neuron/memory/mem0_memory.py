import os
from typing import Any, List, Optional, Dict
from mem0 import MemoryClient
from memory_protocol import MemoryProtocol  # Assuming MemoryProtocol is defined elsewhere

# Ensure MEM0 API Key is set
os.environ["MEM0_API_KEY"] = os.getenv("MEM0_API_KEY")

class Mem0Memory(MemoryProtocol):
    """Mem0-based implementation of MemoryProtocol.

    This class provides a structured wrapper around Mem0's API, aligning
    its function names to the standard methods defined in MemoryProtocol.

    Features:
    - Supports structured storage with `add()`
    - Retrieves individual and multiple memories with `get()` and `get_all()`
    - Allows complex queries with filtering via `search()`
    - Implements batch operations for updates and deletions
    - Tracks memory history efficiently
    """

    def __init__(self, user_id: Optional[str] = None, version: str = "v2") -> None:
        """Initializes the Mem0Memory client.

        Args:
            user_id (Optional[str]): The identifier for a specific user's memory.
            version (str): API version (default: "v2").
        """
        self.client = MemoryClient()
        self.user_id = user_id  # Enables user-specific memory management
        self.version = version  # Ensures consistency in API versioning

    def store(self, user_message: str, assistant_response: Optional[str] = None) -> str:
        """Stores a user and assistant message pair in memory.

        Args:
            user_message (str): The user's message to be stored.
            assistant_response (Optional[str]): The assistant's response (if available).

        Returns:
            str: The ID of the stored memory entry.
        """
        messages = [{"role": "user", "content": user_message}]
        if assistant_response:
            messages.append({"role": "assistant", "content": assistant_response})

        return self.client.add(messages, user_id=self.user_id, version=self.version)

    def retrieve(self, query: str, filters: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Retrieves relevant information from memory based on a query.

        Args:
            query (str): The query to search in memory.
            filters (Optional[Dict[str, Any]]): Optional filters to refine the search.

        Returns:
            Optional[Any]: The first matching memory entry, or None if no match is found.
        """
        results = self.client.search(query, version=self.version, filters=filters or {})
        return results[0] if results else None  # Return first result or None

    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Retrieves all stored memory entries with optional filters.

        Args:
            filters (Optional[Dict[str, Any]]): Filtering criteria for retrieved memories.

        Returns:
            List[Any]: A list of all stored memory items matching the filters.
        """
        return self.client.get_all(filters=filters or {}, version=self.version)

    def get(self, memory_id: str) -> Optional[Any]:
        """Retrieves a specific memory entry by its ID.

        Args:
            memory_id (str): The unique identifier of the memory entry.

        Returns:
            Optional[Any]: The retrieved memory entry, or None if not found.
        """
        return self.client.get(memory_id)

    def update(self, memory_id: str, new_content: str) -> None:
        """Updates an existing memory entry.

        Args:
            memory_id (str): The unique identifier of the memory entry to update.
            new_content (str): The updated content for the memory.
        """
        self.client.update(memory_id, new_content)

    def batch_update(self, updates: List[Dict[str, str]]) -> None:
        """Updates multiple memory entries in batch.

        Args:
            updates (List[Dict[str, str]]): List of updates containing `memory_id` and `text` fields.
        """
        self.client.batch_update(updates)

    def delete(self, memory_id: str) -> None:
        """Deletes a specific memory entry.

        Args:
            memory_id (str): The unique identifier of the memory entry to delete.
        """
        self.client.delete(memory_id=memory_id)

    def batch_delete(self, memory_ids: List[str]) -> None:
        """Deletes multiple memory entries in batch.

        Args:
            memory_ids (List[str]): A list of memory entry IDs to delete.
        """
        delete_memories = [{"memory_id": mem_id} for mem_id in memory_ids]
        self.client.batch_delete(delete_memories)

    def clear(self) -> None:
        """Deletes all stored memory entries for the given user."""
        self.client.delete_all(user_id=self.user_id)

    def history(self, memory_id: str) -> List[Dict[str, Any]]:
        """Retrieves the history of a specific memory entry.

        Args:
            memory_id (str): The ID of the memory entry whose history should be retrieved.

        Returns:
            List[Dict[str, Any]]: A list of history events showing how the memory changed over time.
        """
        return self.client.history(memory_id)
