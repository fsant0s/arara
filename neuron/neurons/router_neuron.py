from typing import Any, Callable, List

from ..neurons import Neuron


class RouterNeuron(Neuron):
    """
    A Router is a Neuron responsible for determining the next component to execute.
    """

    def __init__(self, route_mapping_function: Callable[[Any, List], int], **kwargs: Any) -> None:
        """
        Initialize the router with a routing function.

        Args:
            name (str): The name of the router.
            routing_function (Callable[[Any, List], int]): A function that takes the current output and the list
                of components and returns the index of the next component to execute.
        """
        super().__init__(**kwargs)
        self._route_mapping_function = route_mapping_function
