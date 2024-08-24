from typing import Optional

from neuron.agents.conversable_agent import ConversableAgent

class CriticAgent(ConversableAgent):
    """
    An agent for creating detailed evaluation summaries to assess why a user will or will not enjoy given items based on the items' descriptions and the user's profile.
    """

    DEFAULT_SYSTEM_MESSAGE = """
    You are a sophisticated AI assistant specializing in evaluating user preferences for various items.
    Given detailed item descriptions and a user's profile, your task is to critique and determine if the user will likely enjoy each item.
    The output should be a list of dictionaries, where each dictionary represents an item and contains the following keys:
    [{"item_description": description of the item, "evaluation_summary": detailed summary of the evaluation criteria, "decision": yes or no}]
    Ensure that the "evaluation_summary" comprehensively explains the criteria and that the "decision" clearly indicates whether the user will like the item.
    """

    DEFAULT_DESCRIPTION = "An AI agent that creates detailed evaluation summaries to assess why a user will or will not enjoy given items based on the items' descriptions and the user's profile."


    def __init__(
        self,
        name="critic",
        system_message: Optional[str] = DEFAULT_SYSTEM_MESSAGE,
        description: Optional[str] = DEFAULT_DESCRIPTION,
        **kwargs,
    ):
        """
        Args:
            name (str): agent name.
            system_message (str): system message for the ChatCompletion inference.
                Please override this attribute if you want to reprogram the agent.
            description (str): The description of the agent.
            **kwargs (dict): Please refer to other kwargs in
                [ConversableAgent](../../conversable_agent#__init__).
        """
        super().__init__(
            name=name,
            system_message=system_message,
            description=description,
            **kwargs,
        )