
from typing import List, Any
from ..agents import Agent
from ..agents import Agent, BaseAgent
from typing import List, Dict, Tuple, Union, Optional

class Pipeline(Agent):

    def __init__(self, components, **kwargs):
        """
        Initialize with a list of agents or components to be executed in sequence.

        Args:
            components (List): List of agents or components to execute in order.
        """

        super().__init__(
            name="Pipeline",
            **kwargs,
        )
        self.replace_reply_func(
            Agent._generate_oai_reply, Pipeline.execute
        )
        self.components = components

    def execute(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[BaseAgent] = None,
        config: Optional[None] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        
        message = messages[-1]
        user = sender
        for component in self.components:
            agent, message = component.execute(sender, message, silent=True)
            sender = agent
            if component == self.components[-1]:
                agent.send(message, user, request_reply=False, silent=False)
    
        return True, None