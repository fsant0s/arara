import copy
import logging
import warnings
from collections import defaultdict
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, Union

from ..capabilities import EpisodicMemoryCapability, ReflectionCapability, SharedMemoryIOCapability
from ..runtime_logging import log_event, logging_enabled
from .base_neuron import BaseNeuron
from .helpers import (
    append_oai_message,
    chat_messages,
    match_trigger,
    process_all_messages_before_reply,
    process_last_received_message,
    process_message_before_send,
    process_received_message,
    validate_llm_config,
    content_str,
    prepare_chat,
    reflection_with_llm,
    gather_usage_summary,
    consolidate_chat_info,
)

from openai import BadRequestError

from .chat import ChatResult
from ..cache.cache import AbstractCache
from ..io import IOStream
from termcolor import colored

logger = logging.getLogger(__name__)


class Neuron(BaseNeuron):
    """
    A neural agent capable of processing requests and generating responses using LLMs.

    Neurons are the core components of the NEURON framework. They can be equipped with
    various capabilities, communicate with each other, and interact with LLM providers.

    Attributes:
        llm_config: Configuration for LLM inference.
        DEFAULT_CONFIG: Default configuration for LLM inference.
    """

    llm_config: Union[Dict, Literal[False]]
    DEFAULT_CONFIG = False  # False or dict, the default config for llm inference
    DEFAULT_SUMMARY_METHOD = "last_msg"
    DEFAULT_SUMMARY_PROMPT = "Summarize the takeaway from the conversation in a contextualized manner, providing a detailed summary of all parties involved, without adding introductory phrases"

    @property
    def name(self) -> str:
        """
        Get the name of the neuron.

        Returns:
            str: The name of the neuron.
        """
        return self._name

    @property
    def description(self) -> str:
        """
        Get the description of the neuron.

        Returns:
            str: The description of the neuron.
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """
        Set the description of the neuron.

        Args:
            description (str): The new description.
        """
        self._description = description

    def update_description(self, description: str) -> None:
        """
        Update the description of the neuron.

        Args:
            description (str): The new description.
        """
        self.description = description

    @property
    def system_message(self) -> str:
        """
        Get the system message for this neuron.

        Returns:
            str: The system message.
        """
        return self._oai_system_message[0]["content"]

    def update_system_message(self, system_message: str) -> None:
        """
        Update the system message for this neuron.

        Args:
            system_message (str): The new system message.
        """
        self._oai_system_message[0]["content"] = system_message

    @property
    def chat_messages(self) -> Dict["Neuron", List[Dict]]:
        """A dictionary of conversations from agent to list of messages."""
        return self._oai_messages

    def max_consecutive_auto_reply(self, sender: Optional["Neuron"] = None) -> int:
        """
            The maximum number of consecutive auto replies.
        """
        return self._max_consecutive_auto_reply if sender is None else self._max_consecutive_auto_reply_dict[sender]

    def update_max_consecutive_auto_reply(self, value: int, sender: Optional["Neuron"] = None):
        """
        Update the maximum number of consecutive auto replies.

        Args:
            value (int): the maximum number of consecutive auto replies.
            sender (Agent): when the sender is provided, only update the max_consecutive_auto_reply for that sender.
        """
        if sender is None:
            self._max_consecutive_auto_reply = value
            for k in self._max_consecutive_auto_reply_dict:
                self._max_consecutive_auto_reply_dict[k] = value
        else:
            self._max_consecutive_auto_reply_dict[sender] = value

    def chat_messages_for_summary(self, agent: "Neuron") -> List[Dict]:
        """A list of messages as a conversation to summarize."""
        return self._oai_messages[agent]

    def __init__(
        self,
        name: str,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        description: Optional[str] = None,
        chat_messages: Optional[Dict[BaseNeuron, List[Dict]]] = None,
        default_auto_reply: Union[str, Dict] = "",
        enable_episodic_memory: bool = False,
        shared_memory_write_keys: Optional[List[str]] = None,
        shared_memory_read_keys: Optional[List[str]] = None,
        shared_memory_transition_message: Optional[List[str]] = None,
        enable_reflection: bool = False,
        system_message: str = "",
        is_termination_msg: Optional[Callable[[Dict], bool]] = None,
        human_input_mode: Literal["ALWAYS", "NEVER"] = "NEVER",
        max_consecutive_auto_reply: int = 0,
    ):
        """
        Initialize a Neuron.

        Args:
            name (str): The name of the neuron.
            llm_config (Optional[Union[Dict, Literal[False]]], optional):
                Configuration for LLM inference. Defaults to None.
            description (Optional[str], optional):
                A description of the neuron. Defaults to None.
            chat_messages (Optional[Dict[BaseNeuron, List[Dict]]], optional):
                Chat messages for the neuron. Defaults to None.
            default_auto_reply (Union[str, Dict], optional):
                Default auto-reply message. Defaults to "".
            enable_episodic_memory (bool, optional):
                Whether to enable episodic memory. Defaults to False.
            shared_memory_write_keys (Optional[List[str]], optional):
                Keys for shared memory writing. Defaults to None.
            shared_memory_read_keys (Optional[List[str]], optional):
                Keys for shared memory reading. Defaults to None.
            shared_memory_transition_message (Optional[List[str]], optional):
                Transition messages for shared memory. Defaults to None.
            enable_reflection (bool, optional):
                Whether to enable reflection capability. Defaults to False.
            system_message (str, optional):
                System message for the neuron. Defaults to "".
            human_input_mode (str, optional):
                NEVER: Human intervention is never requested.
                ALWAYS: Human input is always requested. The human can skip to an automatic response, provide feedback, or end the conversation. max_consecutive_auto_reply is ignored in this mode.
            max_consecutive_auto_reply (int):
                The maximum number of consecutive auto replies.
            is_termination_msg (function): a function that takes a message in the form of a dictionary
                and returns a boolean value indicating if this received message is a termination message.
                The dict can contain the following keys: "content", "role", "name", "function_call".
        """
        # a dictionary of conversations, default value is list
        if chat_messages is None:
            self._oai_messages = defaultdict(list)
        else:
            self._oai_messages = chat_messages

        self._default_auto_reply = default_auto_reply
        self.client_cache = None  # TODO: To be implemented
        self.llm_config = self.DEFAULT_CONFIG if llm_config is None else llm_config
        self.reply_at_receive = defaultdict(bool)
        self._name = name
        self._description = description
        self._reply_func_list = []
        self._enable_episodic_memory = enable_episodic_memory
        self._oai_system_message = None

        if system_message:
            self._oai_system_message = [{"content": system_message, "role": "system"}]

        # HUMAN IN THE LOOP
        self._max_consecutive_auto_reply = max_consecutive_auto_reply
        self._consecutive_auto_reply_counter = defaultdict(int)
        self._max_consecutive_auto_reply_dict = defaultdict(self.max_consecutive_auto_reply)
        self.human_input_mode = human_input_mode
        self._human_input = []

        self._is_termination_msg = (
            is_termination_msg
            if is_termination_msg is not None
            else (lambda x: content_str(x.get("content")) == "TERMINATE")
        )

        # Take a copy to avoid modifying the given dict
        if isinstance(llm_config, dict):
            try:
                llm_config = copy.deepcopy(llm_config)
            except TypeError as e:
                raise TypeError(
                    "Please implement __deepcopy__ method for each value class in llm_config to support deepcopy."
                ) from e

        # Registered hooks are kept in lists, indexed by hookable method, to be called in their order of registration.
        # New hookable methods should be added to this list as required to support new neuron capabilities.
        self.hook_lists: Dict[str, List[Callable]] = {
            "process_last_received_message": [],
            "process_message_before_send": [],
            "process_all_messages_before_reply": [],
        }
        self.client = validate_llm_config(self.llm_config, llm_config, self.DEFAULT_CONFIG)
        self.register_reply([BaseNeuron, None], Neuron._generate_oai_reply)
        self.register_reply([BaseNeuron, None], Neuron.check_termination_and_human_reply)

        # Register capabilities
        if enable_reflection:
            self._reflection_capability = ReflectionCapability(self)

        self._shared_memory_capability = SharedMemoryIOCapability(
            self,
            shared_memory_write_keys,
            shared_memory_read_keys,
            shared_memory_transition_message,
        )

        if self._enable_episodic_memory:
            self._episodic_memory_capability = EpisodicMemoryCapability(self)

    def initiate_chat(
        self,
        recipient: "Neuron",
        should_clear_history: bool = True,
        silent: Optional[bool] = False,
        message: Optional[Union[Dict, str, Callable]] = None,
        summary_method: Optional[Union[str, Callable]] = DEFAULT_SUMMARY_METHOD,
        summary_args: Optional[dict] = {},
        cache: Optional[AbstractCache] = None,
        **kwargs,
    ) -> None:
        """
        Initiate a chat with another neuron.

        Args:
            recipient (Neuron): The neuron to chat with.
            should_clear_history (bool, optional):
                Whether to clear chat history. Defaults to True.
            silent (Optional[bool], optional):
                Whether to send messages silently. Defaults to True.
            message (Optional[Union[Dict, str, Callable]], optional):
                Initial message to send. Defaults to None.
            **kwargs: Additional arguments.
        """
        _chat_info = locals().copy()
        _chat_info["sender"] = self
        consolidate_chat_info(_chat_info, uniform_sender=self)
        for agent in [self, recipient]:
            agent.previous_cache = agent.client_cache
            agent.client_cache = cache


        prepare_chat(self, recipient, should_clear_history)
        msg2send = message
        self.send(msg2send, recipient, silent=silent)

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

    def send(
        self,
        message: Union[Dict, str],
        recipient: BaseNeuron,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        """
        Send a message to another neuron.

        Args:
            message (Union[Dict, str]): The message to send.
            recipient (BaseNeuron): The recipient neuron.
            request_reply (Optional[bool], optional):
                Whether to request a reply. Defaults to None.
            silent (Optional[bool], optional):
                Whether to send silently. Defaults to False.

        Returns:
            Union[str, Dict, None]: The reply from the recipient if requested.
        """
        message = process_message_before_send(self, message, recipient, silent)
        valid = append_oai_message(self, message, "assistant", recipient, is_sending=True)
        if valid:
            recipient.receive(message, self, request_reply, silent)
        else:
            raise ValueError(
                "Message can't be converted into a valid ChatCompletion message. Either content or function_call must be provided."
            )

    def receive(
        self,
        message: Union[Dict, str],
        sender: BaseNeuron,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ):
        """
        Receive a message from another neuron.

        Args:
            message (Union[Dict, str]): The received message.
            sender (BaseNeuron): The sender neuron.
            request_reply (Optional[bool], optional):
                Whether a reply is requested. Defaults to None.
            silent (Optional[bool], optional):
                Whether to process silently. Defaults to False.

        Returns:
            Union[str, Dict, None]: The reply if requested.
        """
        process_received_message(self, message, sender, silent)
        if (
            request_reply is False
            or request_reply is None
            and self.reply_at_receive[sender] is False
        ):
            return
        reply = self.generate_reply(messages=chat_messages(self, sender), sender=sender)
        if reply is not None:
            self.send(reply, sender, silent=silent)

    def generate_reply(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        sender: Optional["BaseNeuron"] = None,
        **kwargs: Any,
    ) -> Union[str, Dict, None]:
        """
        Generate a reply based on provided messages.

        Args:
            messages (Optional[List[Dict[str, Any]]], optional):
                Messages to generate a reply for. Defaults to None.
            sender (Optional[BaseNeuron], optional):
                The sender neuron. Defaults to None.
            **kwargs: Additional arguments.

        Returns:
            Union[str, Dict, None]: The generated reply.
        """
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
                final, reply = reply_func(
                    self,
                    messages=messages,
                    sender=sender,
                    config=reply_func_tuple["config"],
                )
                if logging_enabled() and final is not None and reply is not None:
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

    def _generate_oai_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[BaseNeuron] = None,
        config: Optional[None] = None,  # APIProtocol
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """Generate a reply using neuron.clients."""
        client = self.client if config is None else config
        if client is None:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]
        extracted_response = self._generate_oai_reply_from_client(
            client, messages, self.client_cache
        )
        return (False, None) if extracted_response is None else (True, extracted_response)

    def _generate_oai_reply_from_client(
        self, llm_client, messages, cache
    ) -> Union[str, Dict, None]:
        # unroll tool_responses

        if self._oai_system_message is not None:
            messages = self._oai_system_message + messages

        all_messages = []
        for message in messages:
            all_messages.append(message)

        response = llm_client.create(
            context=messages[-1].pop("context", None),
            messages=all_messages,
            cache=cache,
            neuron=self,
        )
        extracted_response = llm_client.extract_text_or_completion_object(response)[0]
        if extracted_response is None:
            warnings.warn(f"Extracted_response from {response} is None.", UserWarning)
            return None

        return extracted_response.model_dump()

    def register_reply(
        self,
        trigger: Union[Type[BaseNeuron], str, BaseNeuron, Callable[[BaseNeuron], bool], List],
        reply_func: Callable,
        position: int = 0,
        config: Optional[Any] = None,
        reset_config: Optional[Callable] = None,
        *,
        remove_other_reply_funcs: bool = False,
    ):
        if not isinstance(trigger, (type, str, BaseNeuron, Callable, list)):
            raise ValueError("trigger must be a class, a string, a neuron, a callable or a list.")
        if remove_other_reply_funcs:
            self._reply_func_list.clear()
        self._reply_func_list.insert(
            position,
            {
                "trigger": trigger,
                "reply_func": reply_func,
                "config": copy.copy(config),
                "reset_config": reset_config,
            },
        )

    def replace_reply_func(self, old_reply_func: Callable, new_reply_func: Callable):
        """Replace a registered reply function with a new one.

        Args:
            old_reply_func (Callable): the old reply function to be replaced.
            new_reply_func (Callable): the new reply function to replace the old one.
        """
        for f in self._reply_func_list:
            if f["reply_func"] == old_reply_func:
                f["reply_func"] = new_reply_func

    def register_hook(self, hookable_method: str, hook: Callable):
        """
        Registers a hook to be called by a hookable method, in order to add a capability to the neuron.
        Registered hooks are kept in lists (one per hookable method), and are called in their order of registration.

        Args:
            hookable_method: A hookable method name implemented by Neuron.
            hook: A method implemented by a subclass of NeuronCapability.
        """
        assert hookable_method in self.hook_lists, f"{hookable_method} is not a hookable method."
        hook_list = self.hook_lists[hookable_method]
        assert hook not in hook_list, f"{hook} is already registered as a hook."
        hook_list.append(hook)

    def last_message(self, neuron: Optional[BaseNeuron] = None) -> Optional[Dict]:
        """The last message exchanged with the neuron.

        Args:
            neuron (BaseNeuron): The neuron in the conversation.
                If None and more than one neuron's conversations are found, an error will be raised.
                If None and only one conversation is found, the last message of the only conversation will be returned.

        Returns:
            The last message exchanged with the neuron.
        """
        if neuron is None:
            n_conversations = len(self._oai_messages)
            if n_conversations == 0:
                return None
            if n_conversations == 1:
                for conversation in self._oai_messages.values():
                    return conversation[-1]
            raise ValueError(
                "More than one conversation is found. Please specify the sender to get the last message."
            )
        if neuron not in self._oai_messages.keys():
            raise KeyError(
                f"The neuron '{neuron.name}' is not present in any conversation. No history available for this neuron."
            )
        return self._oai_messages[neuron][-1]

    def _summarize_chat(
        self,
        summary_method,
        summary_args,
        recipient: Optional["Neuron"] = None,
        cache: Optional[AbstractCache] = None,
    ) -> str:
        """Get a chat summary from an agent participating in a chat.

        Args:
            summary_method (str or callable): the summary_method to get the summary.
                The callable summary_method should take the recipient and sender agent in a chat as input and return a string of summary. E.g,
                ```python
                def my_summary_method(
                    sender: ConversableAgent,
                    recipient: ConversableAgent,
                    summary_args: dict,
                ):
                    return recipient.last_message(sender)["content"]
                ```
            summary_args (dict): a dictionary of arguments to be passed to the summary_method.
            recipient: the recipient agent in a chat.
            prompt (str): the prompt used to get a summary when summary_method is "reflection_with_llm".

        Returns:
            str: a chat summary from the agent.
        """
        summary = ""
        if summary_method is None:
            return summary
        if "cache" not in summary_args:
            summary_args["cache"] = cache
        if summary_method == "reflection_with_llm":
            summary_method = self._reflection_with_llm_as_summary
        elif summary_method == "last_msg":
            summary_method = self._last_msg_as_summary

        if isinstance(summary_method, Callable):
            summary = summary_method(self, recipient, summary_args)
        else:
            raise ValueError(
                "If not None, the summary_method must be a string from [`reflection_with_llm`, `last_msg`] or a callable."
            )
        return summary

    @staticmethod
    def _last_msg_as_summary(sender, recipient, summary_args) -> str:
        """Get a chat summary from the last message of the recipient."""
        summary = ""
        try:
            content = recipient.last_message(sender)["content"]
            if isinstance(content, str):
                summary = content.replace("TERMINATE", "")
            elif isinstance(content, list):
                # Remove the `TERMINATE` word in the content list.
                summary = "\n".join(
                    x["text"].replace("TERMINATE", "") for x in content if isinstance(x, dict) and "text" in x
                )
        except (IndexError, AttributeError) as e:
            warnings.warn(f"Cannot extract summary using last_msg: {e}. Using an empty str as summary.", UserWarning)
        return summary

    @staticmethod
    def _reflection_with_llm_as_summary(sender, recipient, summary_args):
        prompt = summary_args.get("summary_prompt")
        prompt = Neuron.DEFAULT_SUMMARY_PROMPT if prompt is None else prompt
        if not isinstance(prompt, str):
            raise ValueError("The summary_prompt must be a string.")
        msg_list = recipient.chat_messages_for_summary(sender)
        agent = sender if recipient is None else recipient
        role = summary_args.get("summary_role", None)
        if role and not isinstance(role, str):
            raise ValueError("The summary_role in summary_arg must be a string.")
        try:
            summary = reflection_with_llm(
                sender, prompt, msg_list, llm_agent=agent, cache=summary_args.get("cache"), role=role
            )
        except BadRequestError as e:
            warnings.warn(
                f"Cannot extract summary using reflection_with_llm: {e}. Using an empty str as summary.", UserWarning
            )
            summary = ""
        return summary

    def check_termination_and_human_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[BaseNeuron] = None,
        config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, None]]:
        """Check if the conversation should be terminated, and if human reply is provided.

        This method checks for conditions that require the conversation to be terminated, such as reaching a maximum number of consecutive auto-replies or encountering a termination message. Additionally, it prompts for and processes human input based on the configured human input mode, which can be 'ALWAYS' or 'NEVER'. The method also manages the consecutive auto-reply counter for the conversation and prints relevant messages based on the human input received.

        Args:
            - messages (Optional[List[Dict]]): A list of message dictionaries, representing the conversation history.
            - sender (Optional[BaseNeuron]): The agent object representing the sender of the message.
            - config (Optional[Any]): Configuration object, defaults to the current instance if not provided.

        Returns:
            - Tuple[bool, Union[str, Dict, None]]: A tuple containing a boolean indicating if the conversation should be terminated, and a human reply which can be a string, a dictionary, or None.
        """

        iostream = IOStream.get_default()
        if config is None:
            config = self
        if messages is None:
            messages = self._oai_messages[sender] if sender else []
        message = messages[-1]
        reply = ""
        no_human_input_msg = ""
        sender_name = "the sender" if sender is None else sender.name

        if self.human_input_mode == "ALWAYS":
            reply = self.get_human_input(
                f"Replying as {self.name}. Provide feedback to {sender_name}. Press enter to skip and use auto-reply, or type 'exit' to end the conversation: "
            )
            no_human_input_msg = "NO HUMAN INPUT RECEIVED." if not reply else ""
            # if the human input is empty, and the message is a termination message, then we will terminate the conversation
            reply = reply if reply or not self._is_termination_msg(message) else "exit"
        else:
            # self._max_consecutive_auto_reply sets the maximum allowed consecutive interactions between any two agents.
            # A value of 0 means no limit.
            if self._max_consecutive_auto_reply == 0 and self.human_input_mode == "NEVER":
                return False, None
            elif self._consecutive_auto_reply_counter[sender] >= self._max_consecutive_auto_reply_dict[sender] or self._is_termination_msg(message):
                reply = "exit"

        # print the no_human_input_msg
        if no_human_input_msg:
            iostream.print(colored(f"\n>>>>>>>> {no_human_input_msg}", "red"), flush=True)

        # stop the conversation
        if reply == "exit":
            # reset the consecutive_auto_reply_counter
            self._consecutive_auto_reply_counter[sender] = 0
            return True, None

        # send the human reply
        if reply or self._max_consecutive_auto_reply_dict[sender] == 0:
            # reset the consecutive_auto_reply_counter
            self._consecutive_auto_reply_counter[sender] = 0
            response = {"role": "user", "content": reply}
            return True, response

        self._consecutive_auto_reply_counter[sender] += 1
        # increment the consecutive_auto_reply_counter
        if self.human_input_mode != "NEVER":
            iostream.print(colored("\n>>>>>>>> USING AUTO REPLY...", "red"), flush=True)

        return False, None


    def get_human_input(self, prompt: str) -> str:
        """Get human input.

        Override this method to customize the way to get human input.

        Args:
            prompt (str): prompt for the human input.

        Returns:
            str: human input.
        """
        iostream = IOStream.get_default()

        reply = iostream.input(prompt)
        self._human_input.append(reply)
        return reply
