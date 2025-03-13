from typing import Dict, Literal, Optional, Union, Any, List, Tuple, Callable
from collections import defaultdict


from ..clients import CloudBasedClient
from ..runtime_logging import log_new_neuron, logging_enabled
from . import Neuron, BaseNeuron

from ..io import IOStream
from termcolor import colored
from .helpers import content_str

class User(Neuron):

    DEFAULT_USER_DESCRIPTIONS = """
    A user who provides detailed descriptions of the items they like, including features such as brand, category, price, intended use, and other specific preferences.
    """

    def __init__(
        self,
        name: str = "user_neuron",
        description: Optional[str] = None,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
        **kwargs,
    ):
        """
        Initialize an User.

        """
        super().__init__(
            name=name,
            description=(
                description if description is not None else self.DEFAULT_USER_DESCRIPTIONS
            ),
            llm_config=llm_config,
            **kwargs,
        )

        if isinstance(llm_config, CloudBasedClient):
            raise ValueError("The 'llm_config' argument should not be a CloudBasedClient instance.")

        if logging_enabled():
            log_new_neuron(self, locals())




        self.register_reply([BaseNeuron, None], User.check_termination_and_human_reply)

    def check_termination_and_human_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[BaseNeuron] = None,
        config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, None]]:
        """Check if the conversation should be terminated, and if human reply is provided.

        This method checks for conditions that require the conversation to be terminated, such as reaching
        a maximum number of consecutive auto-replies or encountering a termination message. Additionally,
        it prompts for and processes human input based on the configured human input mode, which can be
        'ALWAYS' or 'NEVER'. The method also manages the consecutive auto-reply counter
        for the conversation and prints relevant messages based on the human input received.

        Args:
            - messages (Optional[List[Dict]]): A list of message dictionaries, representing the conversation history.
            - sender (Optional[BaseNeuron]): The agent object representing the sender of the message.
            - config (Optional[Any]): Configuration object, defaults to the current instance if not provided.

        Returns:
            - Tuple[bool, Union[str, Dict, None]]: A tuple containing a boolean indicating if the conversation
            should be terminated, and a human reply which can be a string, a dictionary, or None.
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
            if self._consecutive_auto_reply_counter[sender] >= self._max_consecutive_auto_reply_dict[sender]:
                if self.human_input_mode == "NEVER":
                    reply = "exit"
                else:
                    # self.human_input_mode == "TERMINATE":
                    terminate = self._is_termination_msg(message)
                    reply = self.get_human_input(
                        f"Please give feedback to {sender_name}. Press enter or type 'exit' to stop the conversation: "
                        if terminate
                        else f"Please give feedback to {sender_name}. Press enter to skip and use auto-reply, or type 'exit' to stop the conversation: "
                    )
                    no_human_input_msg = "NO HUMAN INPUT RECEIVED." if not reply else ""
                    # if the human input is empty, and the message is a termination message, then we will terminate the conversation
                    reply = reply if reply or not terminate else "exit"
            elif self._is_termination_msg(message):
                if self.human_input_mode == "NEVER":
                    reply = "exit"
                else:
                    # self.human_input_mode == "TERMINATE":
                    reply = self.get_human_input(
                        f"Please give feedback to {sender_name}. Press enter or type 'exit' to stop the conversation: "
                    )
                    no_human_input_msg = "NO HUMAN INPUT RECEIVED." if not reply else ""
                    # if the human input is empty, and the message is a termination message, then we will terminate the conversation
                    reply = reply or "exit"

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
            # User provided a custom response, return function and tool failures indicating user interruption
            tool_returns = []
            if message.get("function_call", False):
                tool_returns.append(
                    {
                        "role": "function",
                        "name": message["function_call"].get("name", ""),
                        "content": "USER INTERRUPTED",
                    }
                )

            if message.get("tool_calls", False):
                tool_returns.extend(
                    [
                        {"role": "tool", "tool_call_id": tool_call.get("id", ""), "content": "USER INTERRUPTED"}
                        for tool_call in message["tool_calls"]
                    ]
                )

            response = {"role": "user", "content": reply}
            if tool_returns:
                response["tool_responses"] = tool_returns

            return True, response

        # increment the consecutive_auto_reply_counter
        self._consecutive_auto_reply_counter[sender] += 1
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
