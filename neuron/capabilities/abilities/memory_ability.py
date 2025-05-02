from .ability import Ability
from ...neurons.base import BaseNeuron
from typing import Union

class MemoryAbility(Ability):
    """
    An ability that allows a neuron to inject relevant memory content before replying to a message.

    This is useful for enriching the neuron's response context with previously stored memory entries,
    enhancing continuity and coherence in conversations.
    """

    def __init__(self) -> None:
        """
        Initialize the memory ability.
        """
        super().__init__()

    def on_add_to_neuron(self, neuron: BaseNeuron):
        """
        Register this ability as a hook on the neuron to inject memory content before replying.

        Args:
            neuron (BaseNeuron): The neuron to which this ability is attached.

        Raises:
            TypeError: If the given neuron is not an instance of BaseNeuron.
        """
        if not isinstance(neuron, BaseNeuron):
            raise TypeError(
                f"Expected parameter 'neuron' to be of type 'BaseNeuron', but got {type(neuron).__name__}."
            )
        # Register the hook to modify messages before the neuron replies
        self._neuron.register_hook(hookable_method="process_all_messages_before_reply", hook=self._get_memories)

    def _get_memories(
        self,
        processed_user_content: Union[dict, str],
    ) -> str:
        """
        Fetch relevant memory entries from the neuron's memory and append them to the message content.

        Args:
            processed_user_content (Union[dict, str]): The content to which memory will be appended.

        Returns:
            str: The combined content with relevant memory included.
        """
        if self._neuron._memory:
            lines = []
            # Iterate through all memory entries and format them
            for mem in self._neuron._memory:
                for i, mc in enumerate(mem.query().results):
                    lines.append(f"{len(lines) + 1}. {mc.content}")

            # Format the memory contents as a system message
            formatted = "\nRelevant memory content (in chronological order):\n" + "\n".join(lines) + "\n"
            memories = [{
                'content': formatted,
                'role': 'system'
            }]
            # Append memory content to the processed user content
            return processed_user_content + memories

        # Return the original content if no memory is found
        return processed_user_content
