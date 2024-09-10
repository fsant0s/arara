from neuron.agents.llm_agents import PerceiverAgent
from neuron.clients import ClientWrapper
from neuron.code_utils import content_str

from ..agent_capability import AgentCapability

from typing import Dict, Optional, Union, List
import pandas as pd

class SemanticTemplateFillerCapability(AgentCapability):

    "Capability responsbile for Semantically extracting information from textual descriptions and filling structured templates."

    DEFAULT_DESCRIPTION_PROMPT = """
        Task: Populate the template by extracting pertinent information from the provided text.

        Instructions:
        - Identify and fill in the template fields with corresponding information from the text.
        - If the text lacks information for a field, enter 'np.nan'.
        - Ensure the output strictly contains the requested fields without additional details.

        Example 1:
        Textual Description: "João Silva, born on May 15, 1993, is 30 years old, works as a software engineer, and earns R$ 5,000.00 monthly."
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
        Textual Description:"Maria Souza, born on March 20, 1985, works as a graphic designer."
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
        description_prompt: Optional[str] = DEFAULT_DESCRIPTION_PROMPT,
        row: pd.Series = None,
        llm_config: Optional[Union[Dict, bool]] = None,
        **kwargs,
    ) -> None:
    
        if not isinstance(row, pd.Series):
            raise TypeError("A valid pandas Series (row) must be provided for this capability.")
        
        if row.empty:
            raise ValueError("The row cannot be empty.")
        
        self.row = row
        self.name = name
        self._description_prompt = description_prompt 
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

        # Transform the row into a dictionary with types and content
        self.template = {
            column: "[]"
            for column, value in self.row.items()
        }

        # Register a hook for processing the last message.
        agent.register_hook(hookable_method="process_last_received_message", hook=self.process_last_received_message)

    def process_last_received_message(self, content: Union[str, List[dict]]):
        """
        Processes the last received message and extracts information from it.
        """
        user_prompt = f"""
        Textual Description: {content} 
        Template: {self.template}
        """
        response = self.__get_response(user_prompt)
        '''
        #TODO:
        Sometimes the response is:
        {'id': 1, 'result': {'name': ['sildofo'], 'address': ['np.nan'], 'city': ['np.nan'], 'state': ['np.nan'], 'postal_code': ['np.nan'], 'latitude': ['np.nan'], 'longitude': ['np.nan'], 'stars': ['np.nan'], 'review_count': ['np.nan'], 'is_open': ['np.nan'], 'attributes': ['np.nan'], 'categories': ['np.nan'], 'hours': ['np.nan']}}
        </tool_response>
        '''
        return response


    def __get_response(self, content: str) -> dict:
        """
        Args:
            img_data (str): base64 encoded image data.
        Returns:
            str: caption for the given image.
        """
        # calling client.create (ClientWrapper) to get the response
        response = self._llm_client.create(
            agent=self,
            context=None,
            messages=[
                {
                    "role": "system",
                    "content": self._description_prompt,
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