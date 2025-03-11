from typing import Dict, List

from neuron.neurons.base_neuron import BaseNeuron


def chat_messages(recipent, sender) -> Dict[BaseNeuron, List[Dict]]:
    """A dictionary of conversations from neuron to list of messages."""
    return recipent._oai_messages[sender]
