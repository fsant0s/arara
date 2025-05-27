import logging
from typing import Dict, List, Optional, Tuple, Union, Generator

from .helpers import NoEligibleSpeaker
from agents.types import Response
from agent_messages import TextMessage

from formatting_utils import colored
from runtime_logging import log_new_agent, logging_enabled

from ioflow.base import IOStream
from .agent import Agent

from .module import Module

logger = logging.getLogger(__name__)

class Orchestrator(Agent):
    """(In preview) A chat manager agent that can manage a module of multiple agents."""

    def __init__(
        self,
        module: Module,
        name: Optional[str] = "orchestrator",
        system_message: Optional[Union[str, List]] = "Chitchat manager.",
        silent: bool = False,
        **kwargs,
    ):
        if (
            kwargs.get("llm_config")
            and isinstance(kwargs["llm_config"], dict)
            and (kwargs["llm_config"].get("functions") or kwargs["llm_config"].get("tools"))
        ):
            raise ValueError(
                "Orchestrator is not allowed to make function/tool calls. Please remove the 'functions' or 'tools' config in 'llm_config' you passed in."
            )

        super().__init__(
            name=name,
            system_message=system_message,
            **kwargs,
        )
        if logging_enabled():
            log_new_agent(self, locals())
        # Store module
        self._module = module
        self._silent = silent

        self.unregister_reply_func(Agent._generate_oai_reply)
        self.register_reply(Agent, Orchestrator.run_chat, config=module, reset_config=Module.reset)

    @property
    def module(self) -> Module:
        """Returns the Module object."""
        return self._module

    def chat_messages_for_summary(self, agent: Agent) -> List[Dict]:
        """The list of messages in the module as a conversation to summarize.
        The agent is ignored.
        """
        return self._module.messages

    def _prepare_chat(
        self,
        recipient: Agent,
        clear_history: bool,
        prepare_recipient: bool = True,
        reply_at_receive: bool = True,
    ) -> None:
        super()._prepare_chat(recipient, clear_history, prepare_recipient, reply_at_receive)

        if clear_history:
            self._module.reset()

        for agent in self._module.agents:
            if (recipient != agent or prepare_recipient) and isinstance(agent, Agent):
                agent._prepare_chat(self, clear_history, False, reply_at_receive)

    def run_chat(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[Module] = None,
    ) -> Generator[Tuple[bool, Optional[str]], None, None]:
        """Run a Module."""
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]

        speaker = sender
        module = config
        send_introductions = getattr(module, "send_introductions", False)
        silent = getattr(self, "_silent", False)

        if send_introductions:
            # Broadcast the intro
            intro = module.introductions_msg()
            for agent in module.agents:
                self.send(intro, agent, request_reply=False, silent=True)

        if self.client_cache is not None:
            for a in module.agents:
                a.previous_cache = a.client_cache
                a.client_cache = self.client_cache
        for i in range(module.max_round):
            module.append(message, speaker)
            # broadcast the message to all agents except the speaker
            for agent in module.agents:
                if agent != speaker:
                    self.send(message, agent, request_reply=False, silent=True)

            if self._is_termination_msg(message) or i == module.max_round - 1:
                # The conversation is over or it's the last round
                break

            try:
                # select the next speaker
                speaker = module.select_speaker(speaker, self)
                if not silent:
                    iostream = IOStream.get_default()
                    iostream.print(colored(f"\nNext speaker: {speaker.name}\n", "green"), flush=True)
                # let the speaker speak
                # The speaker sends the message and requests a repl
                reply = None
                for reply in speaker.generate_reply(sender=self):
                    reply = reply
                    if not isinstance(reply, Response):
                        speaker.send(reply, self, silent=silent, request_reply=False)
                    # The speaker sends the message without requesting a reply
                    #speaker.send(reply, self, request_reply=False, silent=silent)
            except KeyboardInterrupt:
                # let the admin agent speak if interrupted
                if module.admin_name in module.agent_names:
                    # admin agent is one of the participants
                    speaker = module.agent_by_name(module.admin_name)
                    for reply in speaker.generate_reply(sender=self):
                    # The speaker sends the message without requesting a reply
                        speaker.send(reply, self, request_reply=False, silent=silent)
                else:
                    # admin agent is not found in the participants
                    raise
            except NoEligibleSpeaker:
                # No eligible speaker, terminate the conversation
                break

            if reply is None:
                # no reply is generated, exit the chat
                break
            # check for "clear history" phrase in reply and activate clear history function if found
            if (
                module.enable_clear_history
                and isinstance(reply, dict)
                and reply["content"]
                and "CLEAR HISTORY" in reply["content"].upper()
            ):
                reply["content"] = self.clear_agents_history(reply, module)

            # The speaker sends the message without requesting a reply
            speaker.send(reply, self, request_reply=False, silent=silent)
            message = self.last_message(speaker)

        if self.client_cache is not None:
            for a in module.agents:
                a.client_cache = a.previous_cache
                a.previous_cache = None


        if sender._conversation_terminated[self]: # An agent typed "exit"
             yield [(True, None)]
             return

        response = Response(
            chat_message=TextMessage(
                content=message["content"],
                sender=sender,
                receiver=self,
            )
        )
        yield [(True, response)]

    def clear_agents_history(self, reply: dict, module: Module) -> str:
        """Clears history of messages for all agents or selected one. Can preserve selected number of last messages.
        That function is called when user manually provide "clear history" phrase in his reply.
        When "clear history" is provided, the history of messages for all agents is cleared.
        When "clear history <agent_name>" is provided, the history of messages for selected agent is cleared.
        When "clear history <nr_of_messages_to_preserve>" is provided, the history of messages for all agents is cleared
        except last <nr_of_messages_to_preserve> messages.
        When "clear history <agent_name> <nr_of_messages_to_preserve>" is provided, the history of messages for selected
        agent is cleared except last <nr_of_messages_to_preserve> messages.
        Phrase "clear history" and optional arguments are cut out from the reply before it passed to the chat.

        Args:
            reply (dict): reply message dict to analyze.
            module (Module): Module object.
        """
        iostream = IOStream.get_default()

        reply_content = reply["content"]
        # Split the reply into words
        words = reply_content.split()
        # Find the position of "clear" to determine where to start processing
        clear_word_index = next(i for i in reversed(range(len(words))) if words[i].upper() == "CLEAR")
        # Extract potential agent name and steps
        words_to_check = words[clear_word_index + 2 : clear_word_index + 4]
        nr_messages_to_preserve = None
        nr_messages_to_preserve_provided = False
        agent_to_memory_clear = None

        for word in words_to_check:
            if word.isdigit():
                nr_messages_to_preserve = int(word)
                nr_messages_to_preserve_provided = True
            elif word[:-1].isdigit():  # for the case when number of messages is followed by dot or other sign
                nr_messages_to_preserve = int(word[:-1])
                nr_messages_to_preserve_provided = True
            else:
                for agent in module.agents:
                    if agent.name == word:
                        agent_to_memory_clear = agent
                        break
                    elif agent.name == word[:-1]:  # for the case when agent name is followed by dot or other sign
                        agent_to_memory_clear = agent
                        break
        # preserve last tool call message if clear history called inside of tool response
        if "tool_responses" in reply and not nr_messages_to_preserve:
            nr_messages_to_preserve = 1
            logger.warning(
                "The last tool call message will be saved to prevent errors caused by tool response without tool call."
            )
        # clear history
        if agent_to_memory_clear:
            if nr_messages_to_preserve:
                iostream.print(
                    f"Clearing history for {agent_to_memory_clear.name} except last {nr_messages_to_preserve} messages."
                )
            else:
                iostream.print(f"Clearing history for {agent_to_memory_clear.name}.")
            agent_to_memory_clear.clear_history(nr_messages_to_preserve=nr_messages_to_preserve)
        else:
            if nr_messages_to_preserve:
                iostream.print(f"Clearing history for all agents except last {nr_messages_to_preserve} messages.")
                # clearing history for module here
                temp = module.messages[-nr_messages_to_preserve:]
                module.messages.clear()
                module.messages.extend(temp)
            else:
                iostream.print("Clearing history for all agents.")
                # clearing history for module here
                module.messages.clear()
            # clearing history for agents
            for agent in module.agents:
                agent.clear_history(nr_messages_to_preserve=nr_messages_to_preserve)

        # Reconstruct the reply without the "clear history" command and parameters
        skip_words_number = 2 + int(bool(agent_to_memory_clear)) + int(nr_messages_to_preserve_provided)
        reply_content = " ".join(words[:clear_word_index] + words[clear_word_index + skip_words_number :])

        return reply_content
