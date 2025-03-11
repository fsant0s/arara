from neuron.neurons.helpers import message_to_dict

from ...formatting_utils import colored
from ...io import IOStream


def print_router_message(
    router: "Router",
    previous_component_name: str,
    router_recived_message: str,
    router_output: str,
    next_component_name: str,
) -> None:

    router_name = router.name
    iostream = IOStream.get_default()
    router_output = message_to_dict(router_output)

    iostream.print(colored(f"Router Decision: {router_name}\n", "light_green"), "", flush=True)

    content = (
        f"[Component] Current: {previous_component_name}\n"
        f"[Router Name]: {router_name}\n"
        f"[System Message]:\n"
        f"   {router.system_message.strip()}\n"
        f"[Received Message]:\n"
        f"   {router_recived_message}\n"
        f"[Route Map]:\n"
        f"   {router._route_mapping_function()}\n"
        f"[Output]:\n"
        f"   {router_output}\n"
        f"[Final Decision]:\n"
        f"   {next_component_name}\n"
    )

    iostream.print(colored(content, "light_green"), flush=True)
    iostream.print("\n", "-" * 80, flush=True, sep="")
