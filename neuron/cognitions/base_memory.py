from abc import ABC, abstractmethod
from typing import Any


class BaseMemory(ABC):
    """
    Base class for different types of memory.
    """

    @abstractmethod
    def _store(self, value: Any) -> None:
        """
        Stores a value in memory.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def _retrieve_recent(self, key: str, last_n: int) -> list:
        """
        Retrieves the n most recent values from memory.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def _retrieve_all(self, key: str) -> list:
        """
        Retrieves all values from memory.
        """
        raise NotImplementedError("Subclasses must implement this method.")
