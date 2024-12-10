from typing import List, Any
from ..neurons import Neuron
from .base_component import BaseComponent
from ..io.base import IOStream
from ..formatting_utils import colored

class CycleComponent(BaseComponent):
    """Component that executes neurons in a cyclical fashion, with early stopping if the response is satisfactory."""

    def __init__(self, 
                 name: str, 
                 neurons: List[Neuron], 
                 repetitions: int = 3,
                 cycle_router_neuron: Neuron = None,
                 default_component: BaseComponent = None,
        ) -> None:
        """Initialize the CycleComponent.

        Args:
            name (str): The name of the component.
            neurons (List[Neuron]): A list of Neuron instances to execute in a cycle.
            repetitions (int, optional): Number of times to repeat the cycle. Defaults to 3.None.
        """
        super().__init__(name, neurons)
        self._repetitions = repetitions
        self._cycle_router_neuron = cycle_router_neuron
        self._default_component = default_component

        if self._cycle_router_neuron is not None and self._default_component is None:
            raise ValueError("A `default_component` must be specified to proceed. This error occurred because `_cycle_router_neuron` is not None. Please define a `default_component` before continuing.")


    def execute(self, sender: Neuron, message: Any, silent: bool) -> Any:
        """Execute neurons in a cycle for a specified number of repetitions, with early stopping.

        Neurons process messages in a cyclical order. The cycle repeats for the defined number
        of repetitions, or stops early if a specific condition (e.g., a 'Yes' in the response) is met.

        Args:
            sender (Neuron): The initial neuron sending the message.
            message (Any): The initial message to be processed.
            silent (bool): If True, suppresses output to the IOStream.

        Returns:
            Any: The final message after cycling through all neurons.
        """
        speaker = sender
        for _ in range(self._repetitions):
            for _, neuron in enumerate(self.neurons):
                speaker.send(message, neuron, request_reply=False, silent=False)
                response = neuron.generate_reply(sender=speaker)
                speaker = neuron  # Update speaker to the current neuron
                message = response  # Update message to the response for the next cycle

                if not silent:
                    iostream = IOStream.get_default()
                    iostream.print(colored(f"\nNext speaker: {speaker.name}\n", "green"), flush=True)

            #TODO: Implement a clearer and more effective early stopping condition
            if self._cycle_router_neuron:
                neuron.send(message, self._cycle_router_neuron, request_reply=False, silent=True)
                reply = self._cycle_router_neuron.generate_reply(sender=neuron)['content']
                if "TERMINATE" in reply:
                    return (neuron, message, None)
                
        return (neuron, message, self._default_component)
