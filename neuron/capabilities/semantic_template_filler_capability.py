from typing import Dict, List, Optional, Union

import pandas as pd

from neuron.clients import ClientWrapper
from neuron.neurons.helpers import content_str

from ..neurons.base_neuron import BaseNeuron
from .neuron_capability import NeuronCapability


class SemanticTemplateFillerCapability(NeuronCapability):

    "Capability responsible for Semantically extracting information from textual descriptions and filling structured templates."

    DEFAULT_SYSTEM_MESSAGE = "Extract information from the input and fill the structured template."

    def __init__(
        self,
        name: Optional[str] = "semantic_template_filler_capability",
        system_message: Optional[str] = DEFAULT_SYSTEM_MESSAGE,
        llm_config: Optional[Union[Dict, bool]] = None,
        **kwargs,
    ) -> None:
        super().__init__()
        self.name = name
        self._system_message = system_message

        if llm_config:
            self._llm_client = ClientWrapper(**llm_config)
        else:
            self._llm_client = None

        assert self._llm_client, "The SemanticTemplateFillerCapability requires a valid llm_client."

    def on_add_to_neuron(self, neuron: BaseNeuron):
        # Append extra info to the description
        neuron.update_description(
            neuron.description
            + "\nYou've been given the special ability to extract information from textual descriptions and fill structured templates."
        )
        # Register a hook for processing the last message.
        neuron.register_hook(
            hookable_method="process_last_received_message",
            hook=self.process_last_received_message,
        )

    def process_last_received_message(self, content: Union[str, List[dict]]):
        """
        Processes the last received message and extracts information from it.
        """
        user_prompt = f"""
        Input: {content}
        """
        response = self.__get_response(user_prompt)
        response = response.replace("</tool_response>", "").replace(
            "<tool_response>", ""
        )  # Remove the tool_response tags. Probably a bug in the LLM client.

        try:
            pd.DataFrame(eval(response))
        except Exception as e:
            raise ValueError(f"Unable to convert the response {response} to a DataFrame.") from e

        return response

    def __get_response(self, content: str) -> dict:
        response = self._llm_client.create(
            neuron=self,
            context=None,
            messages=[
                {
                    "role": "system",
                    "content": self._system_message,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": content},
                    ],
                },
            ],
        )
        content = response.choices[0].message.content
        return content_str(content)
