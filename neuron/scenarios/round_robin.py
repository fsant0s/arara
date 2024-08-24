import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union

from ..code_utils import content_str
from ..io.base import IOStream
from ..runtime_logging import log_new_agent, logging_enabled
from ..agents import Agent, ConversableAgent

logger = logging.getLogger(__name__)

@dataclass
class RoundRobin:
    agents: List[Agent]
    messages: List[Dict]
    max_round: int = 3
    admin_name: str = "Admin"
    
    def __post_init__(self):
        pass

    def reset(self):
        self.messages.clear()

class RoundRobinManager(ConversableAgent):
    def __init__(
        self,
        groupchat: RoundRobin,
        name: Optional[str] = "chat_manager",
        system_message: Optional[Union[str, List]] = "Group chat manager.",
        silent: bool = False,
        **kwargs,
    ):
        
        super().__init__(
            name=name,
            system_message=system_message,
            **kwargs,
        )
        if logging_enabled():
            log_new_agent(self, locals())
        # Store groupchat
        self._groupchat = groupchat

        self._silent = silent

        # Order of register_reply is important.
        self.register_reply(Agent, RoundRobinManager.fire, config=groupchat, reset_config=RoundRobin.reset)


    @property
    def groupchat(self) -> RoundRobin:
        return self._groupchat

    def fire(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[RoundRobin] = None,
    ) -> Tuple[bool, Optional[str]]:

        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        speaker = sender
        round_robin = config

        for agent in round_robin.agents:
            if agent != speaker:
                self.send(message, agent, request_reply=False, silent=True)

        searcher = round_robin.agents[-1]
        
        reply = searcher.generate_reply(sender=self)
        searcher.send(reply, self, request_reply=False, silent=False)
        return True, None

   

   