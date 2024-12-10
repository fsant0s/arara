from ..capabilities.neuron_capability import NeuronCapability
from ..neurons.base_neuron import BaseNeuron
from ..cognitions import SharedMemory

from itertools import zip_longest
from typing import Optional, List


class SharedMemoryIOCapability(NeuronCapability):
    """
    Provides shared memory capabilities to a neuron. 
    Enables neurons to read from and write to shared memory, facilitating inter-neuron communication and collaboration.

    Shared memory operations are divided into:
    - Writing: Neurons can store specific information in the shared memory.
    - Reading: Neurons can retrieve information stored by other neurons from the shared memory.
    """

    def __init__(
        self,
        neuron: BaseNeuron,
        shared_memory_write_keys: Optional[List[str]] = None,
        shared_memory_read_keys: Optional[List[str]] = None,
        shared_memory_transition_messages: Optional[List[str]] = None,
    ) -> None:
        """
        Initializes the SharedMemoryCapability with read and write functionalities.

        Args:
            neuron (BaseNeuron): The neuron to which this capability is attached.
            shared_memory_write_key (Optional[List[str]]): Keys to identify data for writing to shared memory.
            shared_memory_read_key (Optional[List[str]]): Keys to identify data for reading from shared memory.
            shared_memory_transition_message (Optional[List[str]]): Transition messages used to connect memory states.
        """
        super().__init__()
        self._shared_memory = SharedMemory.get_instance()
        self._shared_memory_write_keys = shared_memory_write_keys
        self._shared_memory_read_keys = shared_memory_read_keys
        self._shared_memory_transition_messages = shared_memory_transition_messages
        self.add_to_neuron(neuron)

    def on_add_to_neuron(self, neuron: BaseNeuron):
        """
        Registers hooks in the neuron to integrate shared memory read and write functionalities.

        Hooks:
        - 'process_message_before_send': Intercepts outgoing messages, enabling data to be written to shared memory.
        - 'process_last_received_message': Intercepts the last received message, enabling data retrieval from shared memory.

        Args:
            neuron (BaseNeuron): The neuron to which this capability is being added.
        """
        if self._shared_memory_write_keys is not None:
            neuron.register_hook(hookable_method="process_message_before_send", hook=self._write_to_shared_memory)
            
        if self._shared_memory_read_keys is not None and self._shared_memory_transition_messages is not None:
            neuron.register_hook(hookable_method="process_last_received_message", hook=self._read_to_shared_memory)

    def _write_to_shared_memory(self, sender, message, recipient, silent):
        """
        Writes the provided message to the shared memory under the specified keys.

        Args:
            sender: The sender of the message.
            message: The message to be written to shared memory.
            recipient: The recipient of the message.
            silent: Indicates if the operation should be performed silently.

        Returns:
            The original message, unmodified.
        """
        for key in self._shared_memory_write_keys:
            self._shared_memory._store(key=key, value=message)
        return message

    def _read_to_shared_memory(self, message):
        """
        Combines the input message with content retrieved from shared memory.

        The retrieved content is appended to the message using transition messages if provided, 
        or an empty string as the default.

        Args:
            message: The input message to be combined with retrieved memory content.

        Returns:
            A new message that includes the original input and retrieved memory content.
        """
        message_with_retrieved_memory = message
        for key, msg in zip_longest(self._shared_memory_read_keys, self._shared_memory_transition_messages, fillvalue=""):
            retrieved_memory = self._shared_memory._retrieve_all(key)
            retrieved_memory_content = retrieved_memory[0]['content']
            message_with_retrieved_memory += f"\n\n{msg}\n\n{retrieved_memory_content}"
        
        return message_with_retrieved_memory
