import pandas as pd
from typing import Dict, Optional, Union

from sklearn.metrics.pairwise import cosine_similarity

from neuron.agents import LearnerAgent

from ..helpers import (
    load_local_model,
    validate_llm_config,
    get_model_path,
     CustomDataset
)

from ..agent_capability import AgentCapability


class InferenceCapability(AgentCapability):
    """
    Capability responsible for processing dictionaries representing dataset columns,
    predicting None values based on a trained model. It supports handling of both local
    and cloud-based models, specializing in leveraging PyTorch models for inference.

    Attributes:
        name (str): Name of the capability.
        description_prompt (str): Brief description of the capability's function.
        llm_config (dict): Configuration for the language model handling.
        _llm_client (ClientWrapper, optional): Client for interacting with an API for models not hosted locally.
        model_path (str, optional): Path to the local model, if applicable.
    """

    DEFAULT_DESCRIPTION_PROMPT = "This capability predicts missing values in dataset columns using a trained model."

    def __init__(self, name: Optional[str] = "inference_capability",
                 dataset: pd.Dtaframe = None,
                 tokenizer: Optional[Union[str, Dict]] = None,
                 llm_config: Optional[Dict] = None, **kwargs) -> None:
        

       self.__model_path = get_model_path(llm_config)
        if self.__model_path:
            self.__model = load_local_model(self.model_path)

        self._dataset = CustomDataset.from_pandas(dataset)

    def add_to_agent(self, agent: LearnerAgent) -> None:
        if not isinstance(agent, LearnerAgent):
            raise TypeError("The provided agent must be a LearnerAgent.")
        
        # Append extra info to the description
        agent.update_description(
            agent.description
            + "\nYou've been given the special ability to make inference."
        )

        agent.register_hook("process_last_received_message", self.process_last_received_message)

    def process_last_received_message(self, content: Union[str, Dict]) -> Optional[Dict]:
        """Processes incoming content to predict missing values if content is a dictionary."""
        if not isinstance(content, Dict):
            raise ValueError("Content must be a dictionary to perform inference.")
        
        predicted_values = self.__infer(content)
        return predicted_values

    def __create_embeddings(self):
        self._dataset['embeddings'] = self._dataset['content'].apply(self.__get_embeddings)

    def __retrieve_docs(self, content: Dict) -> Dict:
        for row in self._dataset.iterrows():


        return {k: v if v is not None else "Like" for k, v in content.items()}

    def __get_embeddings(self, content: str) -> Dict:
        """Creates embeddings for the input content."""
        pass