from typing import List
from llm_messages import LLMMessage, UserMessage
from .content_to_str import content_to_str

def remove_images(messages: List[LLMMessage]) -> List[LLMMessage]:
    """Remove images from a list of LLMMessages"""
    str_messages: List[LLMMessage] = []
    for message in messages:
        if isinstance(message, UserMessage) and isinstance(message.content, list):
            str_messages.append(UserMessage(content=content_to_str(message.content), source=message.source))
        else:
            str_messages.append(message)
    return str_messages
