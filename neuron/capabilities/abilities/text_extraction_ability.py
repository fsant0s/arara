from .ability import Ability
from ...neurons.base import BaseNeuron
from ...messages import (
    TextMessage,
    ToolCallRequestEvent,
    ToolCallExecutionEvent,
)
from ...base import Response
from typing import Union


class TextExtractionAbility(Ability):
    """
    An ability that enables a neuron to normalize various message types into plain text content.

    This is useful for preparing messages for processing, display, or logging by extracting their semantic content,
    regardless of the original message format (TextMessage, ToolCall, or Response).
    """

    def __init__(self, neuron: BaseNeuron) -> None:
        """
        Initialize the ability and bind it to a neuron.

        Args:
            neuron (BaseNeuron): The neuron to which this ability is attached.
        """
        super().__init__()
        self._neuron = neuron
        self.add_to_neuron(neuron)

    def on_add_to_neuron(self, neuron: BaseNeuron):
        """
        Register this ability as a utility hook.
        """
        neuron.register_hook(hookable_method="process_message_before_send", hook=self._extract_text)

    def _extract_text(
        self,
        sender: BaseNeuron,
        message: Union[str, TextMessage, ToolCallRequestEvent, ToolCallExecutionEvent, Response, None],
        recipient: BaseNeuron,
        silent: bool
    ) -> str:
        """
        Normalize a message object into plain string content.

        Args:
            message: The message to process.

        Returns:
            str: The extracted text content.

        Raises:
            TypeError: If the message type is unsupported.
        """
        if message is None:
            return ""

        if isinstance(message, dict):
            return message['content']

        if isinstance(message, str):
            return message

        if isinstance(message, TextMessage):
            return message.content

        if isinstance(message, (ToolCallRequestEvent, ToolCallExecutionEvent)):
            return message.content if isinstance(message.content, str) else str(message.content)

        if isinstance(message, Response):
            return message.chat_message.content

        raise TypeError(f"Unsupported message type: {type(message)}")
