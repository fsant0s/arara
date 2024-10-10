from neuron.agents.llm_agents import PerceiverAgent
from neuron.clients import ClientWrapper
from neuron.code_utils import content_str

from ..agent_capability import AgentCapability

from typing import Dict, Optional, Union, List
import pandas as pd
import numpy as np

class SemanticTemplateFillerCapability(AgentCapability):

    "Capability responsbile for Semantically extracting information from textual descriptions and filling structured templates."

    DEFAULT_SYSTEM_MESSAGE = """
        Your task is to populate a template by extracting pertinent information from the provided text.

        Instructions:

        - Identify the relevant information in the provided text for each field in the template.
        - If any template field lacks corresponding information in the text, enter ‘np.nan’ for that field.
        - The output must strictly contain the requested fields without additional details.

        Example 1:
        Input: "João Silva, born on May 15, 1993, is 30 years old, works as a software engineer, and earns R$ 5,000.00 monthly."
        Template: 
            "Name": [],
            "Age": [],
            "Date of Birth": [],
            "Salary": []

        Template Output:
        {
            "Name": ["João Silva"],
            "Age": [30],
            "Date of Birth": ["1993-05-15"],
            "Salary": [5000.0]
        }

        Example 2:
        Input:"Maria Souza, born on March 20, 1985, works as a graphic designer."
        Template:
        {
            "Name": [],
            "Birthday": [],
            "Favorite Color": [],
            "Number of Pets": [],
            "Uses Glasses": []
        } 

        Template Output:
        {
            "Name": ["Maria Souza"],
            "Birthday": ["1985-03-20"],
            "Favorite Color": [np.nan], 
            "Number of Pets": [np.nan],  
            "Uses Glasses": [np.nan] 
        }
    """
    
    def __init__(
        self,
        name: Optional[str] = "semantic_template_filler_capability",
        system_message: Optional[str] = DEFAULT_SYSTEM_MESSAGE,
        llm_config: Optional[Union[Dict, bool]] = None,
        **kwargs,
    ) -> None:

        self.name = name
        self._system_message = system_message 
        self._parent_agent = None

        if llm_config:
            self._llm_client = ClientWrapper(**llm_config)
        else:
            self._llm_client = None

        assert (
            self._llm_client
        ), "The SemanticTemplateFillerCapability requires a valid llm_client."

    def add_to_agent(self, agent: PerceiverAgent):
        #TODO: log new capability to the agent's log.

        if not isinstance(agent, PerceiverAgent):
            raise TypeError("The provided agent must be an instance of PerceiverAgent.")
       

        # Append extra info to the description
        agent.update_description(
            agent.description
            + "\nYou've been given the special ability to extract information from textual descriptions and fill structured templates."
        )

        # Register a hook for processing the last message.
        agent.register_hook(hookable_method="process_last_received_message", hook=self.process_last_received_message)

    def process_last_received_message(self, content: Union[str, List[dict]]):
        """
        Processes the last received message and extracts information from it.
        """
        user_prompt = f"""
        Input: {content} 
        """
        response = self.__get_response(user_prompt)
        response = response.replace("</tool_response>", "").replace("<tool_response>", "") # Remove the tool_response tags. Probably a bug in the LLM client.
        
        try:
            pd.DataFrame(eval(response))
        except Exception as e:
            raise ValueError(f"Unable to convert the response {response} to a DataFrame.") from e

        return response


    def __get_response(self, content: str) -> dict:
        response = self._llm_client.create(
            agent=self,
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
                }
            ]
        )
        description = response.choices[0].message.content
        return content_str(description)