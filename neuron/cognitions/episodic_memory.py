from .base_memory import BaseMemory

class EpisodicMemory(BaseMemory):
    """
    Provides episodic memory capabilities to a neuron. 
    Cognitively, episodic memory is the ability to remember specific events, or episodes, in the past. 
    This class provides a simple implementation of episodic memory, where the neuron can store and retrieve messages from memory.
    
    Subclasses of this class can be used to provide different memory implementations.
    """

    def __init__(self) -> None:
        """
        Initializes the episodic memory as an empty list.
        """
        self._episodes = list()  
    

    def _store(self, value: str) -> None:
        """
        Store an event in the episodic memory.

        Args:
            value (str): The content of the event to store in memory.
        """
        self._episodes.append(value)  
    
    def _retrieve_recent(self, last_n: int = 1) -> list:
        """
        Retrieve the most recent episodes from the episodic memory.

        Args:
            last_n (int): The number of most recent episodes to retrieve. Defaults to 1.
        
        Returns:
            list: A list containing up to the last_n most recent episodes in memory.
        """
        return self._episodes[::-1][:last_n]  
    
    def _retrieve_all(self) -> list:
        """
        Retrieve all episodes stored in the episodic memory.

        Returns:
            list: A list containing all episodes stored in memory.
        """
        return self._episodes
