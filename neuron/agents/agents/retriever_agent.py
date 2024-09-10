from typing import Optional, Union, Dict, Literal, Tuple, List

from neuron.runtime_logging import log_new_agent, logging_enabled
from neuron.agents import Agent

class RetrieverAgent(Agent):
    
    DEFAULT_DESCRIPTION = "A retriever Agent responsible to  incoming data, inferring new information for further use."

    def __init__(
        self,
        name="retriever_agent",
        system_message: Optional[str] = None,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        description: Optional[str] = DEFAULT_DESCRIPTION,
        **kwargs,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            description=
                description if description is not None else self.DEFAULT_DESCRIPTION
            ,
            **kwargs,
        )
        
        self.replace_reply_func(
            Agent._generate_oai_reply,
            RetrieverAgent._generate_oai_reply,
        )

        if logging_enabled():
            log_new_agent(self, locals())

    def _generate_oai_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[None] = None, #ClientFactory
    ) -> Tuple[bool, Union[str, Dict, None]]:
      
        # Check if system_message is absent or empty.
        # If not, it triggers the parent method, indicating further processing of
        # the returned message from one capability, which may involve an additional API call.
        if self.system_message is not None and self.system_message != "":
            return super()._generate_oai_reply(messages, sender, config)
        
        if messages is None:
            messages = self._oai_messages[sender]

        return True,  messages[0]
    