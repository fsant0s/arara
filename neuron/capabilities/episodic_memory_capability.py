from neuron.neurons.base import BaseNeuron

from ..cognitions import EpisodicMemory
from .neuron_capability import NeuronCapability


class EpisodicMemoryCapability(NeuronCapability):
    """
    Provides a neuron with the ability to store and retrieve episodic memories.
    Episodic memory allows the neuron to maintain context based on past interactions.
    """

    DEFAULT_MEMORY_INTRO = "The following are the neuron's retrieved memories, listed from the most recent to the oldest:"

    def __init__(
        self,
        neuron: BaseNeuron,
        memory_intro: str = DEFAULT_MEMORY_INTRO,
    ) -> None:
        """
        Initializes the episodic memory capability for the neuron.
        An episodic memory instance is created and linked to the neuron.

        Args:
            neuron (Neuron): The neuron to which this capability will be attached.
            memory_intro (str): The introduction to display when retrieving memories.
        """
        super().__init__()
        self._episodic_memory = EpisodicMemory()  # Initializes a new episodic memory instance.
        self._memory_intro = memory_intro  # Sets the introduction for retrieved memories.
        self.add_to_neuron(neuron)  # Attaches this capability to the specified neuron.

    def on_add_to_neuron(self, neuron: BaseNeuron):
        """
        Sets up hooks for the neuron to integrate episodic memory into its workflow.
        The hooks allow storing messages before sending and retrieving recent memories.

        Args:
            neuron (BaseNeuron): The neuron receiving this capability.
        """
        neuron.register_hook(
            hookable_method="process_message_before_send", hook=self._store
        )  # Hook to store messages.
        neuron.register_hook(
            hookable_method="process_last_received_message", hook=self._retrieve_all
        )  # Hook to retrieve memory.

    def _store(self, sender: BaseNeuron, message: str, recipient: BaseNeuron, silent: bool):
        """
        Stores a message in episodic memory before it is sent.

        Args:
            sender (Neuron): The neuron sending the message.
            message (str): The message being sent.
            recipient (Neuron): The target neuron for the message.
            silent (bool): Indicates whether the message is sent without user feedback.

        Returns:
            str: The original message, passed through unchanged.
        """
        self._episodic_memory._store(message)  # Adds the message to episodic memory.
        return message

    def _retrieve_all(self, message: str):
        """
        Retrieves the most recent memory from episodic memory.

        Args:
            message (str): The current message context to process.

        Returns:
            str: The original message, allowing the neuron to act with additional context if needed.
        """
        retrieved_episodes = (
            self._episodic_memory._retrieve_all()
        )  # Retrieves all memories from episodic memory.
        if not len(retrieved_episodes):
            return message

        retrieved_episodes = "\n".join(
            f"{i + 1}. {item['content']}" for i, item in enumerate(retrieved_episodes)
        )
        message += "\n\n" + self._memory_intro + "\n\n" + retrieved_episodes
        return message
