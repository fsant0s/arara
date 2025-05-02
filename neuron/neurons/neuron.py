import copy
import logging
import warnings
from collections import defaultdict
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, Union, Awaitable, Generator, Sequence

from openai import BadRequestError

from ..capabilities.abilities import (
    Ability,
    TextExtractionAbility,
    MemoryAbility
)
from .base import BaseNeuron
from .helpers import (
    append_oai_message,
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

from ..capabilities.memory import Memory
from .types import FunctionCall, Response, ChatResult
from ..capabilities.tools.execute_tool_call import execute_tool_call
from ..messages import (
    ModelClientStreamingChunkEvent,
    TextMessage,
    ThoughtEvent,
    ToolCallExecutionEvent,
    ToolCallRequestEvent,
    ToolCallSummaryMessage
)

from ..models import (
    AssistantMessage,
    CreateResult,
    FunctionExecutionResult,
    CreateResult
)

from ..capabilities.tools import FunctionTool
from ..cache.cache import AbstractCache
from ..io import IOStream

from ..capabilities.tools.execute_tool_call import execute_tool_call

from termcolor import colored

logger = logging.getLogger(__name__)

class Neuron(BaseNeuron):
    """
    A neural agent capable of processing requests and generating responses using LLMs.

    Neurons are the core components of the NEURON framework. They can be equipped with
    various capabilities, communicate with each other, and interact with LLM providers.
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
        system_message: str = "",
        is_termination_msg: Optional[Callable[[Dict], bool]] = None,
        human_input_mode: Literal["ALWAYS", "NEVER"] = "NEVER",
        max_consecutive_auto_reply: int = 0,
        tools: List[FunctionTool | Callable[..., Any] | Callable[..., Awaitable[Any]]] | None = None,
        tool_call_summary_format: str = "{result}",
        reflect_on_tool_use: bool = False,
        abilities: Optional[List[Ability]] = [],
        self_reflection: bool = False,
        memory: Sequence[Memory] | None = None,
    ):
        """
        Initialize a Neuron.

        Args:
            name (str): Unique identifier for the neuron.

            llm_config (Optional[Union[Dict, Literal[False]]], optional):
                Configuration for large language model inference. Set to False to disable LLM use.

            description (Optional[str], optional):
                Textual description of the neuron's purpose or behavior.

            chat_messages (Optional[Dict[BaseNeuron, List[Dict]]], optional):
                Dictionary storing chat history between this neuron and others.

            default_auto_reply (Union[str, Dict], optional):
                Default message used when no specific reply is generated.

            system_message (str, optional):
                Message prepended to the conversation to guide LLM behavior.

            is_termination_msg (Optional[Callable[[Dict], bool]], optional):
                Function that returns True if a given message indicates conversation termination.
                The input is a dictionary with keys like "content", "role", "name", or "function_call".

            human_input_mode (Literal["ALWAYS", "NEVER"], optional):
                Defines whether human input is required at every turn ("ALWAYS") or never ("NEVER").

            max_consecutive_auto_reply (int, optional):
                Maximum number of automatic replies before requiring human input (ignored if human_input_mode="ALWAYS").

            tools (Optional[List[FunctionTool | Callable[..., Any] | Callable[..., Awaitable[Any]]]], optional):
                A list of external tools or functions the neuron can call.

            tool_call_summary_format (str, optional):
                Format string used to summarize tool call results. Variables: `{tool_name}`, `{arguments}`, `{result}`.

            reflect_on_tool_use (bool, optional):
                If True, performs an additional inference using the tool result to refine the response.

            abilities (Optional[List[Ability]], optional):
                List of specific capabilities or skills assigned to the neuron.

            self_reflection (bool, optional):
                Enables internal reflection mechanisms, allowing the neuron to review its own outputs.
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
        self._oai_system_message = None
        self._tool_call_summary_format = tool_call_summary_format
        self._reflect_on_tool_use = reflect_on_tool_use
        self._conversation_terminated = defaultdict(bool)
        self._self_reflection = self_reflection

        if system_message:
            self._oai_system_message = [{"content": system_message, "role": "system"}]

        self._memory = None
        if memory is not None:
            if isinstance(memory, list):
                self._memory = memory
            else:
                raise TypeError(f"Expected Memory, List[Memory], or None, got {type(memory)}")

        # Avoid mutable default argument
        self._abilities = abilities if abilities is not None else []

        # Add default abilities (they are always included)
        self._abilities.append(TextExtractionAbility())
        self._abilities.append(MemoryAbility())

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
        # New hookable methods should be added to this list as required to support new neuron abilities.
        self.hook_lists: Dict[str, List[Callable]] = {
            "process_last_received_message": [],
            "process_message_before_send": [],
            "process_all_messages_before_reply": [],
        }

        self.client = validate_llm_config(self.llm_config, llm_config, self.DEFAULT_CONFIG)
        self.register_reply([BaseNeuron, None], Neuron._generate_oai_reply)
        self.register_reply([BaseNeuron, None], Neuron.check_termination_and_human_reply)

        # Tools initialization
        self._tools: List[FunctionTool] = []
        if tools:
            for tool in tools:
                if isinstance(tool, FunctionTool):
                    self._tools.append(tool)
                elif callable(tool):
                    self._tools.append(FunctionTool(tool))
                else:
                    raise ValueError(f"Unsupported tool type: {type(tool)}")

        # Ensure that tool names are unique
        tool_names = [tool.name for tool in self._tools]
        if len(tool_names) != len(set(tool_names)):
            raise ValueError(f"Tool names must be unique: {tool_names}")

        self._add_abilities()

    def _add_abilities(self):
        """
        Attach all abilities declared in the neuron, including self abilities.
        """
        for ability in self._abilities:
            if isinstance(ability, Ability):
                ability.add_to_neuron(self)
            else:
                raise TypeError(f"Unsupported ability type: {type(ability)}")

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
        self.send(message, recipient, silent=silent, request_reply=True)

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
            cost=gather_usage_summary(self, recipient),
            human_input=self._human_input,
        )

        return chat_result

    def send(
        self,
        message: Union[Dict, str],
        recipient: BaseNeuron,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False
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
        if not valid:
            raise ValueError(
                "Message can't be converted into a valid ChatCompletion message. Either content or function_call must be provided."
            )
        recipient.receive(message, self, request_reply, silent)

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
            (request_reply is False
            or request_reply is None
            and self.reply_at_receive[sender] is False)
            or self._conversation_terminated[sender] # User typed "exit"
        ):
            return


        for reply in self.generate_reply(sender=sender):
            # It is the final yield. If the type is Response, it marks the generator's last yield.
            request_reply = False
            if isinstance(reply, Response) or isinstance(reply, TextMessage):
                request_reply = True
            self.send(reply, sender, silent=silent, request_reply=request_reply)

    def generate_reply(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        sender: Optional["BaseNeuron"] = None,
        **kwargs: Any,
    ) -> Generator[Response | ToolCallRequestEvent, None, None]:
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

        # Iterate over registered reply functions and trigger the ones that match the sender
        for entry in self._reply_func_list:
            if not match_trigger(self, entry["trigger"], sender):
                continue

            reply_func = entry["reply_func"]
            config = entry["config"]
            for response_batch in reply_func(self, messages=messages, sender=sender, config=config):
                for is_final, reply in response_batch:
                    if not is_final:
                        continue
                    if reply is None:
                        return
                    yield reply

    def _generate_oai_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[BaseNeuron] = None,
        config: Optional[None] = None,
    ) -> Generator[Tuple[bool, Union[ToolCallRequestEvent, Response, None]], None, None]:
        """Generate a reply using neuron.clients."""
        client = self.client if config is None else config
        if client is None:
            yield [(False, None)]
            return
        if messages is None:
            messages = self._oai_messages[sender]

        for extracted_response in self._generate_oai_reply_from_client(client, messages, self.client_cache, sender):
            if extracted_response is not None:
                yield [(True, extracted_response)]
            else:
                yield [(False, None)]

    def _generate_oai_reply_from_client(
        self, llm_client, messages, cache, sender=None
    ) -> Generator[Response | ToolCallRequestEvent, None, None]:
        # Gather all relevant state here

        if self._oai_system_message is not None:
            messages = self._oai_system_message + messages

        all_messages = []
        for message in messages:
            all_messages.append(message)

        response = llm_client.create(
            context=messages[-1].pop("context", None),
            messages=all_messages,
            tools=self._tools,
            cache=cache,
            neuron=self,
        )

        for output_event in self._process_model_result(
            model_result=response,
            sender=sender,
        ):
            yield output_event

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
            hook: A method implemented by a subclass of NeuronAbility.
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

    def _last_msg_as_summary(self, sender, recipient, summary_args) -> str:
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

    def _reflection_with_llm_as_summary(self, sender, recipient, summary_args):
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
    ) -> Generator[Tuple[bool, Union[str, None]], None, None]:
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
                yield [(False, None)]
                return

            elif self._consecutive_auto_reply_counter[sender] >= self._max_consecutive_auto_reply_dict[sender] or self._is_termination_msg(message):
                reply = "exit"

        # print the no_human_input_msg
        if no_human_input_msg:
            iostream.print(colored(f"\n>>>>>>>> {no_human_input_msg}", "red"), flush=True)

        # stop the conversation
        if reply == "exit":
            # reset the consecutive_auto_reply_counter
            self._consecutive_auto_reply_counter[sender] = 0
            self._conversation_terminated[sender] = True
            yield [(True, None)]
            return
        # send the human reply
        if reply or self._max_consecutive_auto_reply_dict[sender] == 0:
            # reset the consecutive_auto_reply_counter
            self._consecutive_auto_reply_counter[sender] = 0
            response = TextMessage(
                content=reply,
                sender=sender,
                receiver=self,
            )
            yield [(True, response)]
            return
        self._consecutive_auto_reply_counter[sender] += 1
        # increment the consecutive_auto_reply_counter
        if self.human_input_mode != "NEVER":
            iostream.print(colored("\n>>>>>>>> USING AUTO REPLY...", "red"), flush=True)

        yield [(False, None)]
        return

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

    def _process_model_result(
        self,
        model_result: CreateResult,
        sender: BaseNeuron,
    ) -> Generator[Response | ToolCallRequestEvent, None, None]:

        """
        Handle final responses from model_result, including tool calls, and reflection if needed.
        """
        if model_result is None:
            warnings.warn(f"Extracted_response from {model_result} is None.", UserWarning)
            yield None
            return

        # If direct text response (string)
        if isinstance(model_result.content, str):
            if self._self_reflection:
                pass
                # yield self._perform_self_reflection(
                # )

            else:
                yield Response(
                    chat_message=TextMessage(
                        content=model_result.content,
                        sender=sender,
                        receiver=self,
                        models_usage=model_result.usage,
                    )
                )
            return


        # Otherwise, we have function calls
        assert isinstance(model_result.content, list) and all(
            isinstance(item, FunctionCall) for item in model_result.content
        )

        # STEP 1: Yield ToolCallRequestEvent
        tool_call_msg = ToolCallRequestEvent(
            content=model_result.content,
            sender=sender,
            receiver=self,
            models_usage=model_result.usage,
        )

        yield tool_call_msg

        # STEP 2: Execute tool calls (synchronous version)
        executed_calls_and_results = [
            execute_tool_call(
                tool_call=call,
                tools=self._tools,
            )
            for call in model_result.content
        ]
        exec_results = [result for _, result in executed_calls_and_results]

        # Yield ToolCallExecutionEvent
        tool_call_result_msg = ToolCallExecutionEvent(
            content=exec_results,
            sender=sender,
            receiver=self,
        )
        yield tool_call_result_msg

        # STEP 3: Reflect or summarize tool results
        if self._reflect_on_tool_use:
            for reflection_response in self._reflect_on_tool_use_flow(
                sender=sender,
            ):
                yield reflection_response
        else:
            for sumarize_response in self._summarize_tool_use(
                executed_calls_and_results=executed_calls_and_results,
                sender=sender,
            ):
                yield sumarize_response

    def _reflect_on_tool_use_flow(
        self,
        sender: BaseNeuron,
    ) -> Generator[Response | ModelClientStreamingChunkEvent | ThoughtEvent, None, None]:
        """
        If reflect_on_tool_use=True, we do another inference based on tool results
        and yield the final text response (or streaming chunks).
        """
        messages = sender._oai_messages[self]
        messages = self._oai_system_message + messages

        reflection_result = self.client.create(
            context=messages[-1].pop("context", None),
            messages=messages,
            tools=[],
            cache=None,
            neuron=self,
        )

        if not reflection_result or not isinstance(reflection_result.content, str):
            raise RuntimeError("Reflect on tool use produced no valid text response.")

        if reflection_result.thought:
            thought_event = ThoughtEvent(content=reflection_result.thought, sender=self)
            yield thought_event

        yield Response(
            chat_message=TextMessage(
                content=reflection_result.content,
                sender=sender,
                receiver=self,
                models_usage=reflection_result.usage,
            )
        )
        return

    def _summarize_tool_use(
        self,
        executed_calls_and_results: List[Tuple[FunctionCall, FunctionExecutionResult]],
        sender: BaseNeuron,
    ) -> Generator[Response, None, None]:
        """
        If reflect_on_tool_use=False, create a summary message of all tool calls.
        """
        normal_tool_calls = [(call, result) for call, result in executed_calls_and_results]
        tool_call_summaries: List[str] = []
        for tool_call, tool_call_result in normal_tool_calls:
            tool_call_summaries.append(
                self._tool_call_summary_format.format(
                    tool_name=tool_call.name,
                    arguments=tool_call.arguments,
                    result=tool_call_result.content,
                )
            )
        tool_call_summary = "\n".join(tool_call_summaries)
        yield Response(
            chat_message=ToolCallSummaryMessage(
                content=tool_call_summary,
                sender=sender,
                receiver=self,
            )
        )
        return

    def _perform_self_reflection(
        self,
        sender: BaseNeuron,
        model_result: CreateResult,
    ) -> Response:
        """
        Performs self-reflection using the output of a model result and returns a Response.

        Args:
            agent_name (str): The name of the neuron agent.
            target_name (str): The name of the recipient neuron.
            model_result (CreateResult): The result from the model before reflection.
            model_client (ClientWrapper): The model client to use for generating the reflection.

        Returns:
            Response: A response object containing the self-reflected message.
        """
        # Build reflection prompt
        content_to_reflect = model_result.content
        if not isinstance(content_to_reflect, str):
            raise TypeError("Reflection requires model_result.content to be a string.")

        prompt = f"Reflect on the reasoning behind this response: \n\n{content_to_reflect}\n\nWhat led you to this response? Provide insights or doubts if any."

        # Compose full message history for reflection
        reflection_messages = "target" + [
            AssistantMessage(
                content=content_to_reflect,
                sender=sender,
                receiver=self,
            ),
            TextMessage(
                content=prompt,
                sender=sender,
                receiver=self,
            )
        ]

        reflection_result = self.client.create(
            context=None,
            messages=reflection_messages,
            tools=None,
            cache=None,
            neuron=self,
        )

        reflection_text = reflection_result.content if isinstance(reflection_result.content, str) else str(reflection_result.content)

        # Add reflection as thought
        #thought_event = ThoughtEvent(content=reflection_text, source_name=agent_name)

        return Response(
            chat_message=TextMessage(
                content=content_to_reflect,
                sender=sender,
                receiver=self,
                models_usage=model_result.usage,
            ),
        )
