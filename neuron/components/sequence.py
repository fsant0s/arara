from typing import Any, List

from ..formatting_utils import colored
from ..io.base import IOStream
from ..neurons import Neuron
from .base_component import BaseComponent


class SequentialComponent(BaseComponent):
    """Component that executes neurons sequentially, passing messages from one neuron to the next."""

    def __init__(self, name: str, neurons: List[Neuron]) -> None:
        """Initialize the SequentialComponent.

        Args:
            name (str): The name of the component.
            neurons (List[Neuron]): A list of neurons to be executed sequentially.
        """
        super().__init__(name, neurons)

    def execute(self, sender: Neuron, message: Any, silent: bool) -> Any:
        """Execute the sequential process, passing messages between neurons.

        Args:
            sender (Neuron): The initial neuron sending the message.
            message (Any): The initial message to be processed.
            silent (bool): If True, suppresses output to the IOStream.

        Returns:
            Any: The final response after all neurons have processed the message.
        """
        speaker = sender
        for neuron in self.neurons:
            speaker.send(message, neuron, request_reply=False, silent=False)
            response = neuron.generate_reply(sender=speaker)
            # Update the speaker to the current neuron for the next step
            speaker = neuron
            message = response

            if not silent:
                iostream = IOStream.get_default()
                iostream.print(colored(f"\nNext speaker: {speaker.name}\n", "green"), flush=True)

        return (neuron, message, None)
