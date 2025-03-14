from typing import Optional, Union
from .. import BaseNeuron
from ...cache import AbstractCache

def reflection_with_llm(
        sender,
        prompt,
        messages,
        llm_agent: Optional[BaseNeuron] = None,
        cache: Optional[AbstractCache] = None,
        role: Union[str, None] = None,
    ) -> str:
        """Get a chat summary using reflection with an llm client based on the conversation history.

        Args:
            prompt (str): The prompt (in this method it is used as system prompt) used to get the summary.
            messages (list): The messages generated as part of a chat conversation.
            llm_agent: the agent with an llm client.
            cache (AbstractCache or None): the cache client to be used for this conversation.
            role (str): the role of the message, usually "system" or "user". Default is "system".
        """
        if not role:
            role = "system"

        system_msg = [
            {
                "role": role,
                "content": prompt,
            }
        ]

        messages = messages + system_msg
        if llm_agent and llm_agent.client is not None:
            llm_client = llm_agent.client
        elif sender.client is not None:
            llm_client = sender.client
        else:
            raise ValueError("No OpenAIWrapper client is found.")

        response = sender._generate_oai_reply_from_client(llm_client=llm_client, messages=messages, cache=cache)
        return response
