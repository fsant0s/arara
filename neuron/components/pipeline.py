from typing import Any, Dict, List, Optional, Tuple, Union

from ..neurons import BaseNeuron, Neuron, RouterNeuron
from ..neurons.helpers import get_next_component
from .base import BaseComponent

class Pipeline(Neuron):

    def __init__(self, **kwargs):
        """
        Initialize the Pipeline as a graph of components.

        Args:
            components (List[Any]): List of neurons or components to execute.
        """
        super().__init__(name="Pipeline", **kwargs)
        self.replace_reply_func(Neuron._generate_oai_reply, Pipeline.execute)
        self._nodes = set()
        self._edges = {}  # Stores connections between components
        self._entry_point = None  # The starting component of the pipeline

    def _add_node(self, component: Any) -> None:
        """
        Add a component to the pipeline.

        Args:
            component (BaseComponent): The component to add.
        """
        self._nodes.add(component)

    def add_edge(self, from_component: Any, to_component: Any) -> None:
        """
        Add a directed edge between two components, automatically adding components to the graph.
        In the future, from_component and to_component can be a tool, for example.
        Args:
            from_component (Any): The starting component.
            to_component (Any): The destination component.
        """
        # Add components to the set of nodes
        self._nodes.add(from_component)
        self._nodes.add(to_component)

        # Initialize edge list for the from_component if it doesn't exist
        if from_component not in self._edges:
            self._edges[from_component] = None

        # Add the edge
        self._edges[from_component] = to_component

    def set_entry_point(self, component: Any) -> None:
        """
        Set the entry point for the pipeline.

        Args:
            component (Any): The component to set as the entry point.
        """
        self._nodes.add(
            component
        )  # This is necessary to ensure that the entry point is in the graph.
        self._entry_point = component

    def execute(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[BaseNeuron] = None,
        config: Optional[None] = None,
        reply_to_user: Optional[bool] = True,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """
        Execute the pipeline starting from the entry point.

        Args:
            messages (Optional[List[Dict]]): List of messages.
            sender (Optional[BaseNeuron]): Initial sender.
            config (Optional[None]): Configuration for execution.
            reply_to_user (Optional[bool]): Whether to reply to the user.

        Returns:
            Tuple[bool, Union[str, Dict, None]]: Status and final result.
        """
        if self._entry_point is None:
            raise RuntimeError("Entry point not set for the pipeline.")
        current_component = self._entry_point
        message = messages[-1]
        user = sender

        while current_component:
            neuron, message, default_component = current_component.execute(
                sender, message, silent=True
            )
            sender = neuron

            if default_component is not None:
                current_component = default_component
                continue

            # Determine the next component
            next_component = self._edges.get(current_component, [])
            if not next_component:
                break  # No further connections; end execution

            if isinstance(next_component, BaseComponent):
                current_component = next_component
            else:
                if isinstance(next_component, RouterNeuron):
                    # Use router to decide the next component if multiple options exist
                    router = next_component
                    next_component_name = get_next_component(
                        router, current_component.name, message, neuron
                    )
                    if next_component not in self._nodes:
                        raise ValueError("RouterNeuron returned an invalid component.")
                    current_component = next_component_name
                else:
                    raise ValueError("Invalid component type in the pipeline.")

        # Send the message to the user at the end of the pipeline
        if reply_to_user:
            print("acabou o pipeline")
            output = neuron.send(message, user, request_reply=True, silent=False)
        print("Pipeline output: ", output)
        return True, output
