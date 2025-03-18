from typing import List

import cohere

from ..capabilities.neuron_capability import NeuronCapability
from ..cognitions import SharedMemory
from ..neurons.base import BaseNeuron


class RerankCapability(NeuronCapability):

    def __init__(
        self,
        rerank_model_name: str = None,
        api_key: str = None,
        top_n: int = 5,
        shared_memory_read_keys: List[str] = None,
    ) -> None:
        super().__init__()

        self._re_rank_model_name = rerank_model_name
        self._cohere_client = cohere.Client(api_key)
        self._top_n = top_n
        self._shared_memory_read_keys = shared_memory_read_keys
        self._shared_memory = SharedMemory.get_instance()

    def on_add_to_neuron(self, neuron: BaseNeuron):
        neuron.register_hook(hookable_method="process_last_received_message", hook=self._rerank)
        self._neuron = neuron

    def _rerank(self, message: str):

        try:
            documents = eval(message)
        except (SyntaxError, NameError):
            raise ValueError(
                "The 'message' parameter must be a string representation of a list of strings."
            )

        # Ensure 'documents' is a list of strings
        if not isinstance(documents, list) or not all(isinstance(doc, str) for doc in documents):
            raise ValueError("The 'message' parameter must evaluate to a list of strings.")

        query = self._shared_memory._retrieve_recent(self._shared_memory_read_keys[0])[0]["content"]
        response = self._cohere_client.rerank(
            model=self._re_rank_model_name,
            query=query,
            documents=documents,
            top_n=self._top_n,
        )
        response_as_strings = [
            f"{i + 1}. {documents[item.index]}" for i, item in enumerate(response.results)
        ]
        response_as_strings = "\n".join(response_as_strings)
        return response_as_strings
