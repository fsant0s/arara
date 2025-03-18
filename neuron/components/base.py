from abc import ABC, abstractmethod
from typing import Any, List

from ..neurons import Neuron


class BaseComponent(ABC):
    """Base abstract class for components that define an execution process.

    Derived classes must implement the `execute` method.
    """

    def __init__(self, name: str, neurons: List[Neuron]) -> None:
        """Initialize the BaseComponent with a name.

        Args:
            name (str): The name of the component.
        """
        self.name = name
        self.neurons = neurons

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Defines the execution process for the component.

        This method must be implemented by any subclass.

        Args:
            args (Any): Positional arguments for the execution process.
            kwargs (Any): Keyword arguments for the execution process.

        Returns:
            Any: Result of the execution process.
        """
        ...

    def get_router(self) -> Any:
        """Get the router associated with the component.

        Returns:
            Any: The router associated with the component.
        """
        return getattr(self, "_router", None)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"(name={self.name})"
