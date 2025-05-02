from typing import Any, Dict

from neuron.neurons import BaseNeuron

usage_including_cached_inference = {"total_cost": 0}
usage_excluding_cached_inference = {"total_cost": 0}

def gather_usage_summary(sender: BaseNeuron, receiver: BaseNeuron) -> Dict[Dict[str, Dict], Dict[str, Dict]]:
    r"""Gather usage summary from all neurons.

    Args:
        sender (BaseNeuron): The sender neuron.
        receiver (BaseNeuron): The receiver neuron.

    Returns:
        dictionary: A dictionary containing two keys:
          - "usage_including_cached_inference": Cost information on the total usage, including the tokens in cached inference.
          - "usage_excluding_cached_inference": Cost information on the usage of tokens, excluding the tokens in cache. No larger than "usage_including_cached_inference".

    Example:

    ```python
    {
        "usage_including_cached_inference" : {
            "total_cost": 0.0006090000000000001,
            "gpt-35-turbo": {
                    "cost": 0.0006090000000000001,
                    "prompt_tokens": 242,
                    "completion_tokens": 123,
                    "total_tokens": 365
            },
        },

        "usage_excluding_cached_inference" : {
            "total_cost": 0.0006090000000000001,
            "gpt-35-turbo": {
                    "cost": 0.0006090000000000001,
                    "prompt_tokens": 242,
                    "completion_tokens": 123,
                    "total_tokens": 365
            },
        }
    }
    ```

    Note:

    If none of the neurons incurred any cost (not having a client), then the usage_including_cached_inference and usage_excluding_cached_inference will be `{'total_cost': 0}`.
    """
    from ..conversational_orchestrator import ConversationalOrchestratorManager

    def aggregate_summary(usage_summary: Dict[str, Any], neuron_summary: Dict[str, Any], neuron_name: str) -> None:

        if neuron_summary is None:
            return

        usage_summary["total_cost"] += neuron_summary.get("total_cost", 0)

        for model, data in neuron_summary.items():
            if model != "total_cost":
                if neuron_name not in usage_summary:
                    usage_summary[neuron_name] = neuron_summary
                else:
                    usage_summary[neuron_name]["total_cost"] += neuron_summary.get("total_cost", 0)
                    usage_summary[neuron_name][model]["cost"] += data.get("cost", 0)
                    usage_summary[neuron_name][model]["prompt_tokens"] += data.get("prompt_tokens", 0)
                    usage_summary[neuron_name][model]["completion_tokens"] += data.get("completion_tokens", 0)
                    usage_summary[neuron_name][model]["total_tokens"] += data.get("total_tokens", 0)

    neurons = [sender, receiver]
    if isinstance(receiver, ConversationalOrchestratorManager):
        for neuron in receiver.chitchat.agents:
            if getattr(neuron, "client", None):
                neurons.append(neuron)

    for neuron in neurons:
        if getattr(neuron, "client", None):
            aggregate_summary(usage_including_cached_inference, neuron.client.total_usage_summary, neuron._name)
            aggregate_summary(usage_excluding_cached_inference, neuron.client.actual_usage_summary, neuron._name)

    return {
        "usage_including_cached_inference": usage_including_cached_inference,
        "usage_excluding_cached_inference": usage_excluding_cached_inference,
    }
