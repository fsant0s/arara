import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union

from ..code_utils import content_str
from ..io.base import IOStream
from ..runtime_logging import log_new_agent, logging_enabled
from ..agents import Agent, LLMAgent, BaseAgent

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

class RoundRobinManager(LLMAgent):
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
        self._groupchat = groupchat
        self._silent = silent

        # Order of register_reply is important.
        self.register_reply(BaseAgent, RoundRobinManager.fire, config=groupchat, reset_config=RoundRobin.reset)


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

        user = round_robin.agents[0]
        perceiver = round_robin.agents[1]
        reply = perceiver.generate_reply(sender=self)
        
        perceiver.send(reply, self, request_reply=False, silent=False)

        message = self.last_message(perceiver)
        for agent in round_robin.agents:
            if agent != perceiver:
                self.send(message, agent, request_reply=False, silent=True)

        learner = round_robin.agents[2]

        reply_from_learner = learner.generate_reply(sender=self)
        learner.send(reply_from_learner, self, request_reply=False, silent=False)

        message = self.last_message(learner)
        for agent in round_robin.agents:
            if agent != learner:
                self.send(message, agent, request_reply=False, silent=True)


        kr = round_robin.agents[3]
        embeddings = kr.generate_reply(sender=self)
        reply_from_kr = "Embeddings done :D. Sending to the next agent."
        kr.send(reply_from_kr, self, request_reply=False, silent=False)

        return True, None

   

   