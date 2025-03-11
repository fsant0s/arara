from collections import defaultdict

from .base_memory import BaseMemory


class SharedMemory(BaseMemory):
    """
    A shared memory accessible by all neurons in the Pipeline.
    This memory stores episodic events contributed by all neurons as key-value pairs.
    """

    _instance = None  # Singleton instance

    def _initialize_memory(self):
        """
        Initializes the memory storage for the community memory.

        This function sets up the shared memory as a defaultdict of lists
        to store episodic events as key-value pairs.
        """
        self._shared_memory = defaultdict(list)

    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of SharedMemory.

        Ensures that the instance is globally accessible without creating duplicates.

        Returns:
            SharedMemory: The singleton instance of the shared memory.
        """
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._initialize_memory()
        return cls._instance

    def _store(self, key: str, value: str) -> None:
        """
        Store an event in the shared memory.

        Args:
            key (str): The key for the shared memory (e.g., message identifier).
            value (str): The value of the shared memory (e.g., the message content).
        """
        self._shared_memory[key].append(value)

    def _retrieve_recent(self, key: str, last_n: int = 1) -> str | None:
        """
        Retrieve recent values from the shared memory by key.

        Args:
            key (str): The key for the shared memory to retrieve.
            last_n (int): The number of most recent values to retrieve. Defaults to 1.

        Returns:
            str | None: The most recent value(s) of the shared memory if the key exists, otherwise None.
        """
        if key in self._shared_memory:
            return self._shared_memory[key][::-1][:last_n]
        return None

    def _retrieve_all(self, key: str) -> list | None:
        """
        Retrieve all values from the shared memory.

        Args:
            key (str): The key for the shared memory to retrieve.

        Returns:
            list | None: A list of all values for the shared memory if the key exists, otherwise None.
        """
        if key in self._shared_memory:
            return self._shared_memory[key]
        return None

    def clear_memory(self) -> None:
        """
        Clear all stored data in the shared memory.

        This method resets the shared memory to an empty state, removing all
        stored episodic events.
        """
        self._shared_memory.clear()
