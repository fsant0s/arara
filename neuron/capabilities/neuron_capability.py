from abc import ABC, abstractmethod

from ..neurons.base import BaseNeuron


class NeuronCapability(ABC):
    """Base class for composable capabilities that can be added to a neuron."""

    def __init__(self) -> None:
        pass

    def add_to_neuron(self, neuron: BaseNeuron):
        """
        Public method to add capability to a neuron.
        Automatically validates the neuron type before delegating to subclass logic.
        """
        if not isinstance(neuron, BaseNeuron):
            raise TypeError(
                f"Expected parameter 'neuron' to be of type 'Neuron', but got {type(neuron).__name__}."
            )

        # Delegate specific behavior to the subclass
        self.on_add_to_neuron(neuron)

    @abstractmethod
    def on_add_to_neuron(self, neuron: BaseNeuron):
        """
        Abstract method to be implemented by subclasses.
        Defines specific behavior for adding the capability.
        """
        pass
