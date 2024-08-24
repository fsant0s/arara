from typing import Optional, Dict, Any
from neuron.agents.conversable_agent import ConversableAgent

class LearnerAgent(ConversableAgent):
    """
    An agent that learns the features that were not filled by the Perceiver.
    """

    DEFAULT_SYSTEM_MESSAGE = """
    You are a sophisticated AI assistant specializing in learning and inferring missing features in a recommendation dataset.
    Given a dataset with some columns not filled by user preferences, your task is to learn and provide additional information to populate those missing columns.
    The output should be a dictionary representing the dataset, where each key is a column name and each value is either the original information or the newly inferred information.

    Example input:
    {
        "column1": "value extracted from user preferences",
        "column2": None,
        "column3": "another value from user preferences"
    }

    Example output:
    {
        "column1": "value extracted from user preferences",
        "column2": "inferred value for column2",
        "column3": "another value from user preferences"
    }
    """

    DEFAULT_DESCRIPTION = "An AI agent that learns and infers missing features in a recommendation dataset based on initial user preferences."

    def __init__(
        self,
        name="learner",
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


