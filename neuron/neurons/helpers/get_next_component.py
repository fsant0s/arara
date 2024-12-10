from typing import Any, Optional
from .print_router_message import print_router_message

def get_next_component(router_neuron, previous_component_name: str,message: Any,  sender: Optional["BaseNeuron"] = None, silent: Optional[bool] = False) -> Any:
        """
        Determine the next component based on the routing function.
        Args:
            output (Any): The output from the current component.
            components (List): The list of all available components.

        Returns:
            Any: The next component to execute.
        """
        
        sender.send(message, router_neuron, request_reply=False, silent=True)      
        router_recived_message = message
        router_output = router_neuron.generate_reply(sender=sender)['content']
        next_component = router_neuron._route_mapping_function().get(router_output)

        if not silent:
            print_router_message(
                router_neuron, 
                previous_component_name, 
                router_recived_message, 
                router_output, 
                next_component.name
            )

        return next_component