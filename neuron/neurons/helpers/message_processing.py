from typing import Dict, List, Union

from neuron.neurons.base import BaseNeuron

from ...runtime_logging import log_event, logging_enabled
from .append_oai_message import append_oai_message
from .print_received_message import print_received_message


def process_message_before_send(
    self: BaseNeuron, message: Union[Dict, str], recipient: BaseNeuron, silent: bool
) -> Union[Dict, str]:
    """Process the message before sending it to the recipient."""
    hook_list = self.hook_lists["process_message_before_send"]
    for hook in hook_list:
        message = hook(sender=self, message=message, recipient=recipient, silent=silent)
    return message


def process_received_message(
    self: BaseNeuron, message: Union[Dict, str], sender: BaseNeuron, silent: bool
) -> None:
    # When the neuron receives a message, the role of the message is "user".
    valid = append_oai_message(self, message, "user", sender, is_sending=False)
    if logging_enabled():
        log_event(self, "received_message", message=message, sender=sender.name, valid=valid)

    if not valid:
        raise ValueError(
            "Received message can't be converted into a valid ChatCompletion message. Either content or function_call must be provided."
        )
    if not silent:
        print_received_message(message, sender, self.name, self.llm_config)


def process_last_received_message(self: BaseNeuron, messages: List[Dict]) -> List[Dict]:
    """
    Calls any registered capability hooks to use and potentially modify the text of the last message,
    as long as the last message is not a function call or exit command.
    """

    # If any required condition is not met, return the original message list.
    hook_list = self.hook_lists["process_last_received_message"]
    if len(hook_list) == 0:
        return messages  # No hooks registered.
    if messages is None:
        return None  # No message to process.
    if len(messages) == 0:
        return messages  # No message to process.
    last_message = messages[-1]
    if "context" in last_message:
        return messages  # Last message contains a context key.
    if "content" not in last_message:
        return messages  # Last message has no content.

    user_content = last_message["content"]
    if not isinstance(user_content, str) and not isinstance(user_content, list):
        # if the user_content is a string, it is for regular LLM
        # if the user_content is a list, it should follow the multimodal LMM format.
        return messages
    if user_content == "exit":
        return messages  # Last message is an exit command.

    # Call each hook (in order of registration) to process the user's message.
    processed_user_content = user_content
    for hook in hook_list:
        processed_user_content = hook(processed_user_content)
    if processed_user_content == user_content:
        return messages  # No hooks actually modified the user's message.

    # Replace the last user message with the expanded one.
    messages = messages.copy()
    messages[-1]["content"] = processed_user_content
    return messages


def process_all_messages_before_reply(self: BaseNeuron, messages: List[Dict]) -> List[Dict]:
    """
    Calls any registered capability hooks to process all messages, potentially modifying the messages.
    """
    hook_list = self.hook_lists["process_all_messages_before_reply"]
    # If no hooks are registered, or if there are no messages to process, return the original message list.
    if len(hook_list) == 0 or messages is None:
        return messages

    # Call each hook (in order of registration) to process the messages.
    processed_messages = messages
    for hook in hook_list:
        processed_messages = hook(processed_messages)
    return processed_messages
