from typing import Optional

from neuron.neurons.base_neuron import BaseNeuron

from ...formatting_utils import colored
from ...io.base import IOStream


def clear_history(
    self,
    recipient: Optional[BaseNeuron] = None,
    nr_messages_to_preserve: Optional[int] = None,
):
    """Clear the chat history of the neuron.

    Args:
        recipient: the neuron with whom the chat history to clear. If None, clear the chat history with all neurons.
        nr_messages_to_preserve: the number of newest messages to preserve in the chat history.
    """
    # TODO: Implement this logic.
    from ...cognitions import SharedMemory
    from ...components import BaseComponent, CycleComponent, Pipeline

    SharedMemory.get_instance().clear_memory()
    if isinstance(self, Pipeline):
        for component in self._nodes:
            if isinstance(component, BaseComponent):
                if isinstance(component, CycleComponent):
                    if component._cycle_router_neuron is not None:  # If
                        component._cycle_router_neuron._oai_messages.clear()
                for neuron in component.neurons:
                    neuron._oai_messages.clear()
                    if self._enable_episodic_memory:
                        neuron._episodic_memory_capability._episodic_memory._episodes.clear()

    if nr_messages_to_preserve:
        iostream = IOStream.get_default()
        iostream.print(
            colored(
                "WARNING: `nr_preserved_messages` is ignored when clearing chat history with a specific neuron.",
                "yellow",
            ),
            flush=True,
        )
