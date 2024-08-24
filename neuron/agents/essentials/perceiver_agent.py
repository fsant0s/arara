from typing import Optional, Dict, Any, List
from neuron.agents.conversable_agent import ConversableAgent

class PerceiverAgent(ConversableAgent):
    """
    An agent that receives a user's description of their preferences and maps them to the columns of a recommendation dataset based on those preferences.
    """

    DEFAULT_SYSTEM_MESSAGE = """
    You are a sophisticated AI assistant specializing in mapping user preferences to the columns of a recommendation dataset.
    Given a user's description of their preferences, your task is to extract relevant information and populate the columns of the dataset accordingly.
    The output should be a dictionary representing the dataset, where each key is a column name and each value is the information extracted from the user's preferences.
    Ensure that the information extracted is accurate and relevant to the user's preferences. 
    Note that some columns may not be filled if the user's description does not provide enough information.

    Example output:
    {
        "column1": "value extracted from user preferences",
        "column2": "another value from user preferences",
        "column3": None  # Not enough information provided to fill this column
    }
    """

    DEFAULT_DESCRIPTION = "An AI agent that receives a user's description of their preferences and maps them to the columns of a recommendation dataset based on those preferences."

    def __init__(
        self,
        columns: Optional[List[str]] = None,
        name="preference_mapper",
        system_message: Optional[str] = DEFAULT_SYSTEM_MESSAGE,
        description: Optional[str] = DEFAULT_DESCRIPTION,
        **kwargs,
    ):
        """
        Args:
            columns (List[str]): List of columns for the recommendation dataset.
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
        self.columns = columns
        self.preferences = {}

    def save_preferences(self, user_preferences: Dict[str, Any]) -> None:
        """
        Save the user's preferences.

        Args:
            user_preferences (Dict[str, Any]): The user's preferences as a dictionary.
        """
        self.preferences = user_preferences

    def get_preferences(self) -> Dict[str, Any]:
        """
        Retrieve the mapped preferences.

        Returns:
            Dict[str, Any]: A dictionary with the mapped preferences.
        """
        return self.preferences
