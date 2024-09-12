"""
Example:
    llm_config={
    "config_list": [{
        "api_type": "local",
        "model_dir": "neuron/models/local_model",
        "model_name": "erasmo"
        }
]}
    agent = neuron.AssistantAgent("my_agent", llm_config=llm_config)
"""

from __future__ import annotations

import time
import uuid
from typing import Dict
import torch
import numpy as np
import pandas as pd

from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import ChatCompletionMessage, Choice
from openai.types.completion_usage import CompletionUsage

from .. import CustomClient

try:
    import be_great
except ImportError:
    raise ImportError("Please install the 'be_great' library to proceed.")

class BeGreatClient(CustomClient):

    def __init__(self, **kwargs):
     
        self._model_dir = kwargs.get("model_dir")
        self._model_name = kwargs.get("model")

        if not self._model_name:
            raise ValueError("The 'model' argument is required.")
        if not self._model_dir:
            raise ValueError("The 'model_dir' argument is required.")

        # Loading a pre trained huggingface model that was trained in a custom dataset.
        self._model = self._load_model(self._model_dir)

    def _load_model(self, model_dir: str) -> None:
        # Assuming that the model was already trained and saved in the model_dir
        model = be_great.GReaT.load_from_dir(model_dir)
        return model

    def _get_device(self) -> torch.device:
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def create(self, params: Dict) -> ChatCompletion:
        messages = params.get("messages", [])
        last_message = messages[-1]['content'] if messages else None
        parsed_data  = self._convert_str_to_dataframe(last_message)
        try:
            response = self._model.impute(parsed_data, temperature=0.7, k=100, max_length=200, device=self._get_device())
            response_id = str(uuid.uuid4())
        except Exception as e:
            raise RuntimeError(f"BeGreat exception occurred: {e}")        

        if response is not None:
            local_llm_finish = "stop"
            response_content = ', '.join([f"{col} is {response.at[0, col]}" for col in response.columns])
            response_id = response_id
        else:
            raise RuntimeError("Failed to get response from Local LLM.")
    
        message = ChatCompletionMessage(
            role="assistant",
            content=response_content
        )

        choices = [Choice(finish_reason=local_llm_finish, index=0, message=message)]
        response_oai = ChatCompletion(
            id=response_id,
            model=self._model_name,
            created=int(time.time()),
            object="chat.completion",
            choices=choices,
            usage=CompletionUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            ),
            cost=0,
        )
        return response_oai
    
    def _impute(self, message: str) -> str:
        """Impute missing values in the message."""
        # make imputations here
        return message


    def _convert_str_to_dataframe(self, input_str: str) -> dict:
        """
        Tenta converter uma string em formato JSON para um DataFrame do pandas.

        Parameters:
        input_str (str): A string que se espera estar no formato JSON válido.

        Returns:
        pd.DataFrame: Um DataFrame construído a partir do dicionário representado pela string JSON.

        Raises:
        ValueError: Se a string não estiver em um formato JSON válido, levanta um ValueError com uma mensagem indicativa.
        """
        try:
            return pd.DataFrame(eval(input_str))
        except Exception:
            raise ValueError("Unable to convert the string to a `pd.DataFrame`. Please check the format of `input_str`.")
