from typing import Any, Dict

from src.agents import BaseAgent

usage_including_cached_inference = {"total_cost": 0}
usage_excluding_cached_inference = {"total_cost": 0}

def gather_usage_summary(sender: BaseAgent, receiver: BaseAgent) -> Dict[Dict[str, Dict], Dict[str, Dict]]:
    r"""Gather usage summary from all agents.

    Args:
        sender (BaseAgent): The sender src.
        receiver (BaseAgent): The receiver src.

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

    If none of the agents incurred any cost (not having a client), then the usage_including_cached_inference and usage_excluding_cached_inference will be `{'total_cost': 0}`.
    """
    from ..orchestrator import Orchestrator

    def aggregate_summary(usage_summary: Dict[str, Any], agent_summary: Dict[str, Any], agent_name: str) -> None:

        if agent_summary is None:
            return

        usage_summary["total_cost"] += agent_summary.get("total_cost", 0)

        for model, data in agent_summary.items():
            if model != "total_cost":
                if agent_name not in usage_summary:
                    usage_summary[agent_name] = agent_summary
                else:
                    usage_summary[agent_name]["total_cost"] += agent_summary.get("total_cost", 0)
                    usage_summary[agent_name][model]["cost"] += data.get("cost", 0)
                    usage_summary[agent_name][model]["prompt_tokens"] += data.get("prompt_tokens", 0)
                    usage_summary[agent_name][model]["completion_tokens"] += data.get("completion_tokens", 0)
                    usage_summary[agent_name][model]["total_tokens"] += data.get("total_tokens", 0)

    agents = [sender, receiver]
    if isinstance(receiver, Orchestrator):
        for agent in receiver.chitchat.agents:
            if getattr(agent, "client", None):
                agents.append(agent)

    for agent in agents:
        if getattr(agent, "client", None):
            aggregate_summary(usage_including_cached_inference, agent.client.total_usage_summary, agent._name)
            aggregate_summary(usage_excluding_cached_inference, agent.client.actual_usage_summary, agent._name)

    return {
        "usage_including_cached_inference": usage_including_cached_inference,
        "usage_excluding_cached_inference": usage_excluding_cached_inference,
    }
