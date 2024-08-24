from typing import Optional, Dict, Any
from neuron.agents.conversable_agent import ConversableAgent

class ExplainableAgent(ConversableAgent):
    """
    An agent that explains the recommendation decision made by the CriticAgent.
    """

    DEFAULT_SYSTEM_MESSAGE = """
    You are a sophisticated AI assistant specializing in explaining recommendation decisions made by another AI agent.
    Given the decision from the CriticAgent and the criteria used for that decision, your task is to provide a clear and detailed explanation for the recommendation.
    Use the Chain of Thought method to enhance the model's ability to explain the decision step by step.
    Ensure that the explanation is comprehensive and easy to understand.

    Example output:
    {
        "decision": "yes",
        "explanation": "The user is likely to enjoy this item because it matches their preference for high-quality audio and modern design. Additionally, the positive reviews and the brand's reputation for durability further support this recommendation."
    }
    """

    DEFAULT_DESCRIPTION = "An AI agent that explains recommendation decisions made by the CriticAgent, providing clear and detailed explanations for why a recommendation is being made."

    def __init__(
        self,
        name="explainable_agent",
        system_message: Optional[str] = DEFAULT_SYSTEM_MESSAGE,
        description: Optional[str] = DEFAULT_DESCRIPTION,
        **kwargs,
    ):
        """
        Args:
            name (str): Agent name.
            system_message (str): System message for the ChatCompletion inference.
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
