from typing import Protocol, List, Any, Optional

class MemoryProtocol(Protocol):
    """Protocol for memory management in an agent-based system.

    This protocol defines the minimal necessary structure for memory classes
    that store, retrieve, and manipulate memory-related information.
    """

    def store(self, item: Any) -> str:
        """Stores an item in memory.

        Args:
            item (Any): The data to be stored in memory.

        Returns:
            str: The ID of the stored memory entry.
        """
        pass

    def retrieve(self, query: Any) -> Optional[Any]:
        """Retrieves relevant information from memory.

        Args:
            query (Any): The query to search in memory.

        Returns:
            Optional[Any]: The first matching memory entry, or None if no match is found.
        """
        pass

    def clear(self) -> None:
        """Clears all stored memory entries."""
        pass

    def get_all(self) -> List[Any]:
        """Retrieves all stored memory entries.

        Returns:
            List[Any]: A list of all stored memory items.
        """
        pass

    def delete(self, item_id: str) -> None:
        """Deletes a specific memory entry.

        Args:
            item_id (str): The unique identifier of the memory entry to delete.
        """
        pass
