from abc import ABC, abstractmethod

from ...neurons.base import BaseNeuron

class Ability(ABC):
    """Base class for modular abilities that can be added to a neuron."""

    def __init__(self) -> None:
        self._neuron = None

    def add_to_neuron(self, neuron: BaseNeuron):
        """
        Public method to attach the ability to a neuron.
        Automatically validates the neuron type before delegating to subclass logic.
        """
        if not isinstance(neuron, BaseNeuron):
            raise TypeError(
                f"Expected parameter 'neuron' to be of type 'BaseNeuron', but got {type(neuron).__name__}."
            )
        self._neuron = neuron
        # Delegate specific behavior to the subclass
        self.on_add_to_neuron(neuron)

    @abstractmethod
    def on_add_to_neuron(self, neuron: BaseNeuron):
        """
        Abstract method to be implemented by subclasses.
        Defines specific behavior for integrating the ability into the neuron.
        """
        pass
