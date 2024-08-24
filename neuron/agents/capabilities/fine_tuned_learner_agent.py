from neuron.agents.conversable_agent import ConversableAgent
import torch
from typing import Optional, Dict, Any
from .agent_capability import AgentCapability

class FineTunedLearnerAgent(AgentCapability):
    """
    An agent that uses a fine-tuned model to learn the features that were not filled by the PerceiverAgent.
    The model is loaded locally and used to infer the missing columns in the dataset.
    """

    DEFAULT_SYSTEM_MESSAGE = """
    A sophisticated AI assistant specializing in learning and inferring missing features in a recommendation dataset using a fine-tuned model.
    Given a dataset with some columns not filled by user preferences, your task is to use the fine-tuned model to provide additional information to populate those missing columns.
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

    DEFAULT_DESCRIPTION = "An AI agent that uses a fine-tuned model to learn and infer missing features in a recommendation dataset based on initial user preferences."

    def __init__(
        self,
        model_path: str,
        name="fine_tuned_learner",
        system_message: Optional[str] = DEFAULT_SYSTEM_MESSAGE,
        description: Optional[str] = DEFAULT_DESCRIPTION,
        **kwargs,
    ):
        """
        Args:
            model_path (str): Path to the fine-tuned model.
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

        self._lmm_config = lmm_config
        self._description_prompt = description_prompt
        self._parent_agent = None
        self.__model = None
        if lmm_config:
            self._lmm_client = OpenAIWrapper(**lmm_config)
        else:
            self._lmm_client = None

        self._custom_caption_func = custom_caption_func
        assert (
            self._lmm_config or custom_caption_func
        ), "Vision Capability requires a valid lmm_config or custom_caption_func."


    def add_to_agent(self, agent: ConversableAgent):

        self._parent_agent = agent

        # Append extra info to the system message.
        agent.update_system_message(agent.system_message + "\nYou've been given the ability to interpret images.")
        # Register a hook for processing the last message.
        agent.register_hook(hookable_method="process_last_received_message", hook=self.process_last_received_message)
        self.__load_model()

    def __load_model(self, model_path: str):
        # Load the fine-tuned model from the specified path
        self.__model = torch.load(model_path)
        self.__model.eval()
        pass


    def process_last_received_message(self, incomplete_dataset: Dict[str, Any]) -> Dict[str, Any]:
        input_tensor = self.prepare_input(data)
        with torch.no_grad():
            output = self.model(input_tensor)
        return output[column].item()