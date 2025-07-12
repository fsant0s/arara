import logging
from typing import Dict, List, Optional

from agents import BaseAgent


def has_self_loops(allowed_speaker_transitions: Dict) -> bool:
    """
    Returns True if there are self loops in the allowed_speaker_transitions_Dict.
    """
    return any([key in value for key, value in allowed_speaker_transitions.items()])


def check_graph_validity(
    allowed_speaker_transitions_dict: Dict,
    agents: List[BaseAgent],
):
    """
    allowed_speaker_transitions_dict: A dictionary where keys are agents and values can be either a list of agents or a dictionary for conditional transitions.
    agents: A list of BaseAgents

    Checks for the following:
        Errors
        1. The dictionary must have a structure of keys and (list or dict) as values.
        2. Every key exists in agents.
        3. Every value in the lists/dicts must be a BaseAgent.

        Warnings
        1. Warning if there are isolated agent nodes.
        2. Warning if the set of agents in allowed_speaker_transitions do not match agents.
        3. Warning if there are duplicated agents in any values of `allowed_speaker_transitions_dict`.
    """

    ### Errors

    # Check 1. The dictionary must have a structure of keys and (list or dict) as values
    if not isinstance(allowed_speaker_transitions_dict, dict):
        raise ValueError("allowed_speaker_transitions_dict must be a dictionary.")

    # Values can now be a list (static transitions) or a dict (conditional transitions)
    if not all(
        [isinstance(value, (list, dict)) for value in allowed_speaker_transitions_dict.values()]
    ):
        raise ValueError(
            "allowed_speaker_transitions_dict must have values that are either lists or dictionaries."
        )

    # Check 2. Every key exists in agents
    if not all([key in agents for key in allowed_speaker_transitions_dict.keys()]):
        raise ValueError("allowed_speaker_transitions_dict has keys not in agents.")

    # Check 3. Every agent mentioned must be a BaseAgent.
    for value in allowed_speaker_transitions_dict.values():
        if isinstance(value, list):
            if not all([isinstance(agent, BaseAgent) for agent in value]):
                raise ValueError(
                    "A list in allowed_speaker_transitions_dict contains non-BaseAgent elements."
                )
        elif isinstance(value, dict):
            for inner_list in value.values():
                if not isinstance(inner_list, list) or not all(
                    [isinstance(agent, BaseAgent) for agent in inner_list]
                ):
                    raise ValueError("A conditional transition must map to a list of BaseAgents.")

    ### Warnings

    # Warning 1. Warning if there are isolated agent nodes.
    has_outgoing_edge = []
    has_incoming_edge = []

    for key, value in allowed_speaker_transitions_dict.items():
        if isinstance(value, list) and len(value) > 0:
            has_outgoing_edge.append(key)
            has_incoming_edge.extend(value)
        elif isinstance(value, dict):
            if any(value.values()):
                has_outgoing_edge.append(key)
            for inner_list in value.values():
                has_incoming_edge.extend(inner_list)

    no_outgoing_edges = [agent for agent in agents if agent not in has_outgoing_edge]
    no_incoming_edges = [agent for agent in agents if agent not in has_incoming_edge]
    isolated_agents = set(no_incoming_edges).intersection(set(no_outgoing_edges))

    if len(isolated_agents) > 0:
        logging.warning(
            f"""Warning: There are isolated agent nodes; they have no incoming or outgoing edges. Isolated agents: {[agent.name for agent in isolated_agents]}"""
        )

    # Warning 2. Warning if the set of agents in allowed_speaker_transitions do not match agents
    agents_in_allowed_speaker_transitions = set(has_incoming_edge).union(set(has_outgoing_edge))
    full_anti_join = set(agents_in_allowed_speaker_transitions).symmetric_difference(set(agents))
    if len(full_anti_join) > 0:
        logging.warning(
            f"""Warning: The set of agents in allowed_speaker_transitions do not match agents. Offending agents: {[agent.name for agent in full_anti_join]}"""
        )

    # Warning 3. Warning if there are duplicated agents in any values of `allowed_speaker_transitions_dict`
    for key, value in allowed_speaker_transitions_dict.items():
        # Case 1: The value is a simple list of agents
        if isinstance(value, list):
            duplicates = [item for item in value if value.count(item) > 1]
            unique_duplicates = list(set(duplicates))
            if unique_duplicates:
                logging.warning(
                    f"For BaseAgent '{key.name}', the transition list has duplicate elements: {[agent.name for agent in unique_duplicates]}. Please remove duplicates."
                )
        # Case 2: The value is a dictionary for conditional routing
        elif isinstance(value, dict):
            for condition, inner_list in value.items():
                if isinstance(inner_list, list):
                    duplicates = [item for item in inner_list if inner_list.count(item) > 1]
                    unique_duplicates = list(set(duplicates))
                    if unique_duplicates:
                        logging.warning(
                            f"In conditional transitions for BaseAgent '{key.name}', the list for condition '{condition}' has duplicate elements: {[agent.name for agent in unique_duplicates]}. Please remove duplicates."
                        )


def invert_disallowed_to_allowed(
    disallowed_speaker_transitions_dict: dict, agents: List[BaseAgent]
) -> dict:
    """
    Start with a fully connected allowed_speaker_transitions_dict of all agents. Remove edges from the fully connected allowed_speaker_transitions_dict according to the disallowed_speaker_transitions_dict to form the allowed_speaker_transitions_dict.
    """
    # Create a fully connected allowed_speaker_transitions_dict of all agents
    allowed_speaker_transitions_dict = {
        agent: [other_agent for other_agent in agents] for agent in agents
    }

    # Remove edges from allowed_speaker_transitions_dict according to the disallowed_speaker_transitions_dict
    for key, value in disallowed_speaker_transitions_dict.items():
        allowed_speaker_transitions_dict[key] = [
            agent for agent in allowed_speaker_transitions_dict[key] if agent not in value
        ]

    return allowed_speaker_transitions_dict


def visualize_speaker_transitions_dict(
    speaker_transitions_dict: dict, agents: List[BaseAgent], export_path: Optional[str] = None
):
    """
    Visualize the speaker_transitions_dict using networkx.
    """
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError as e:
        logging.fatal("Failed to import networkx or matplotlib.")
        raise e

    G = nx.DiGraph()

    # Add nodes
    G.add_nodes_from([agent.name for agent in agents])

    # Add edges
    for key, value in speaker_transitions_dict.items():
        for agent in value:
            G.add_edge(key.name, agent.name)

    # Visualize
    nx.draw(G, with_labels=True, font_weight="bold")

    if export_path is not None:
        plt.savefig(export_path)
    else:
        plt.show()
