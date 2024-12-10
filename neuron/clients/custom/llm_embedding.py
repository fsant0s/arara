from __future__ import annotations

import time
import torch
import uuid
from typing import Dict

from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import ChatCompletionMessage, Choice
from openai.types.completion_usage import CompletionUsage

from .. import CustomClient
from neuron.clients.helpers import load_local_llm

class LLMEmbedding(CustomClient):

    def __init__(self, **kwargs):
        """
        LLMEmbedding is a class responsible for loading locally stored models, particularly large language models (LLMs).
        Currently, it supports loading models saved as .pt files (PyTorch) pre-trained using Huggingface.

        Future Improvements:
        - Implement support for other file formats such as .bin, .h5, .tensors, etc.
        - Extend functionality to load non-LLM models.

        Arguments:
            model_dir (str): Path to the model file.
            model_name (str): Name of the model.
        """
        
        self._model_dir = kwargs.get("model_dir")
        self._model_name = kwargs.get("model")

        if not self._model_dir:
            raise ValueError("The 'model_dir' argument is required.")
        if not self._model_name:
            raise ValueError("The 'model_name' argument is required.")

        # Loading a pre trained huggingface model that was trained in a custom dataset.
        self._model, self._tokenizer = load_local_llm(self._model_name, self._model_dir)

    def create(self, params: Dict) -> ChatCompletion:
        messages = params.get("messages", [])
        last_message = messages[-1]['content'] if messages else None
        try:
            inputs = self._tokenizer(last_message, return_tensors="pt")
            reponse = self._model(inputs['input_ids'].clone().detach())
            embeddings = reponse.logits
            reponse = str(embeddings.mean(dim=1)[0].tolist())
            response_id = str(uuid.uuid4())
        except Exception as e:
            raise RuntimeError(f"LocalLLM exception occurred: {e}")
        
        if reponse is not None:
            local_llm_finish = "stop"
            response_content = reponse
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