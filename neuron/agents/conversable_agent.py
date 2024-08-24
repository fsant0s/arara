from typing import Optional, Dict, List, Union, Literal, Callable, Any, Tuple, Type 

import copy
import inspect
import logging

from collections import defaultdict

import warnings

from . import LLMAgent, Agent

from .utils import (
    validate_llm_config,
    append_oai_message,
    process_message_before_send, 
    process_received_message, 
    process_last_received_message, 
    process_all_messages_before_reply,
    prepare_chat,
    chat_messages,
    match_trigger,
)

from ..runtime_logging import logging_enabled, log_event

logger = logging.getLogger(__name__)

class ConversableAgent(LLMAgent):
    """(In preview) A class for generic communicative agents that can be configured as User, Perceive, Learner, ERASMO, DFReader, Critic, or Explainer agents."""


    llm_config: Union[Dict, Literal[False]]
    DEFAULT_CONFIG = False  # False or dict, the default config for llm inference

    @property
    def name(self) -> str:
        """Get the name of the agent."""
        return self._name

    @property
    def description(self) -> str:
        """Get the description of the agent."""
        return self._description

    @description.setter
    def description(self, description: str):
        """Set the description of the agent."""
        self._description = description

    def update_system_message(self, system_message: str) -> None:
        """Update the system message.

        Args:
            system_message (str): system message for the ChatCompletion inference.
        """
        self._oai_system_message[0]["content"] = system_message

    def __init__(
        self,
        name: str,
        system_message: Optional[Union[str, List]] = "You are a helpful AI Assistant.",
        description: Optional[str] = None,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        chat_messages: Optional[Dict[Agent, List[Dict]]] = None,
    ):
        
        # a dictionary of conversations, default value is list
        if chat_messages is None:
            self._oai_messages = defaultdict(list)
        else:
            self._oai_messages = chat_messages

        self.client_cache = None
        self.llm_config = self.DEFAULT_CONFIG if llm_config is None else llm_config
        self.reply_at_receive = defaultdict(bool)
        self._name = name   
        self._description = description if description is not None else system_message
        self._reply_func_list = []
        self._oai_system_message = [{"content": system_message, "role": "system"}]

        # Take a copy to avoid modifying the given dict
        if isinstance(llm_config, dict):
            try:
                llm_config = copy.deepcopy(llm_config)
            except TypeError as e:
                raise TypeError(
                    "Please implement __deepcopy__ method for each value class in llm_config to support deepcopy."
                    " Refer to the docs for more details: https://microsoft.github.io/neuron/docs/topics/llm_configuration#adding-http-client-in-llm_config-for-proxy"
                ) from e

        # Registered hooks are kept in lists, indexed by hookable method, to be called in their order of registration.
        # New hookable methods should be added to this list as required to support new agent capabilities.
        self.hook_lists: Dict[str, List[Callable]] = {
            "process_last_received_message": [],
            "process_message_before_send": [],
            "process_all_messages_before_reply": [],
        }
        self.client = validate_llm_config(self.llm_config, llm_config, self.DEFAULT_CONFIG)
        self.register_reply([Agent, None], ConversableAgent.__generate_oai_reply)


    def initiate_chat(
        self,
        recipient: "ConversableAgent",
        should_clear_history: bool = True,
        silent: Optional[bool] = False,
        message: Optional[Union[Dict, str, Callable]] = None,
        **kwargs,
    ) -> None:

        
        _chat_info = locals().copy()
        _chat_info["sender"] = self
        prepare_chat(self, recipient, should_clear_history)
        if isinstance(message, Callable):
            msg2send = message(_chat_info["sender"], _chat_info["recipient"], kwargs)
        else:
            msg2send = message #self.generate_init_message(message, **kwargs)
        self.send(msg2send, recipient, silent=silent)
        '''
        summary = self._summarize_chat(
            summary_method,
            summary_args,
            recipient,
            cache=cache,
        )
        for agent in [self, recipient]:
            agent.client_cache = agent.previous_cache
            agent.previous_cache = None
        chat_result = ChatResult(
            chat_history=self.chat_messages[recipient],
            summary=summary,
            cost=gather_usage_summary([self, recipient]),
            human_input=self._human_input,
        )
        return chat_result
        '''


    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        message = process_message_before_send(self, message, recipient, silent)
        # When the agent composes and sends the message, the role of the message is "assistant"
        # unless it's "function".
        
        valid = append_oai_message(self, message, "assistant", recipient)
        if valid:
            recipient.receive(message, self, request_reply, silent)
        else:
            raise ValueError(
                "Message can't be converted into a valid ChatCompletion message. Either content or function_call must be provided."
            )
    
    def receive(
        self,
        message: Union[Dict, str],
        sender: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        process_received_message(self, message, sender, silent)
        if request_reply is False or request_reply is None and self.reply_at_receive[sender] is False:
            return
        reply = self.generate_reply(messages=chat_messages(self, sender), sender=sender)
        if reply is not None:
            self.send(reply, sender, silent=silent)


    def generate_reply(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        sender: Optional["Agent"] = None,
        **kwargs: Any,
    ) -> Union[str, Dict, None]:
        if all((messages is None, sender is None)):
            error_msg = f"Either {messages=} or {sender=} must be provided."
            logger.error(error_msg)
            raise AssertionError(error_msg)

        if messages is None:
            messages = self._oai_messages[sender]
        
        # Call the hookable method that gives registered hooks a chance to process the last message.
        # Message modifications do not affect the incoming messages or self._oai_messages.
        messages = process_last_received_message(self, messages)

        # Call the hookable method that gives registered hooks a chance to process all messages.
        # Message modifications do not affect the incoming messages or self._oai_messages.
        messages = process_all_messages_before_reply(self, messages)

        for reply_func_tuple in self._reply_func_list:
            reply_func = reply_func_tuple["reply_func"]
            if match_trigger(self, reply_func_tuple["trigger"], sender):
                final, reply = reply_func(self, messages=messages, sender=sender, config=reply_func_tuple["config"])
                if logging_enabled():
                    log_event(
                        self,
                        "reply_func_executed",
                        reply_func_module=reply_func.__module__,
                        reply_func_name=reply_func.__name__,
                        final=final,
                        reply=reply,
                    )
                if final:
                    return reply
        return self._default_auto_reply
    

    def __generate_oai_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[None] = None, #OpenAIWrapper
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """Generate a reply using neuron.oai."""
        client = self.client if config is None else config
        if client is None:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]
        extracted_response = self.__generate_oai_reply_from_client(
            client, self._oai_system_message + messages, self.client_cache
        )
        return (False, None) if extracted_response is None else (True, extracted_response)

    def __generate_oai_reply_from_client(self, llm_client, messages, cache) -> Union[str, Dict, None]:
        # unroll tool_responses
        all_messages = []
        for message in messages:
            tool_responses = message.get("tool_responses", [])
            if tool_responses:
                all_messages += tool_responses
                # tool role on the parent message means the content is just concatenation of all of the tool_responses
                if message.get("role") != "tool":
                    all_messages.append({key: message[key] for key in message if key != "tool_responses"})
            else:
                all_messages.append(message)

        # TODO: #1143 handle token limit exceeded error
        response = llm_client.create(
            context=messages[-1].pop("context", None), messages=all_messages, cache=cache, agent=self
        )
        extracted_response = llm_client.extract_text_or_completion_object(response)[0]
        if extracted_response is None:
            warnings.warn(f"Extracted_response from {response} is None.", UserWarning)
            return None 
        
        return extracted_response.model_dump()
    
    def register_reply(
        self,
        trigger: Union[Type[Agent], str, Agent, Callable[[Agent], bool], List],
        reply_func: Callable,
        position: int = 0,
        config: Optional[Any] = None,
        reset_config: Optional[Callable] = None,
        *,
        ignore_async_in_sync_chat: bool = False,
        remove_other_reply_funcs: bool = False,
    ):
        if not isinstance(trigger, (type, str, Agent, Callable, list)):
            raise ValueError("trigger must be a class, a string, an agent, a callable or a list.")
        if remove_other_reply_funcs:
            self._reply_func_list.clear()
        self._reply_func_list.insert(
            position,
            {
                "trigger": trigger,
                "reply_func": reply_func,
                "config": copy.copy(config),
                "init_config": config,
                "reset_config": reset_config,
                "ignore_async_in_sync_chat": ignore_async_in_sync_chat and inspect.iscoroutinefunction(reply_func),
            },
        )