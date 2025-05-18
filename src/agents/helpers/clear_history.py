from typing import Optional

from agents.base import BaseAgent
from ioflow.console import IOStream
from formatting_utils import colored

def clear_history(self, recipient: Optional[BaseAgent] = None, nr_messages_to_preserve: Optional[int] = None):
        """Clear the chat history of the agent.

        Args:
            recipient: the agent with whom the chat history to clear. If None, clear the chat history with all agents.
            nr_messages_to_preserve: the number of newest messages to preserve in the chat history.
        """
        iostream = IOStream.get_default()
        if recipient is None:
            if nr_messages_to_preserve:
                for key in self._oai_messages:
                    nr_messages_to_preserve_internal = nr_messages_to_preserve
                    # if breaking history between function call and function response, save function call message
                    # additionally, otherwise openai will return error
                    first_msg_to_save = self._oai_messages[key][-nr_messages_to_preserve_internal]
                    if "tool_responses" in first_msg_to_save:
                        nr_messages_to_preserve_internal += 1
                        iostream.print(
                            f"Preserving one more message for {self.name} to not divide history between tool call and "
                            f"tool response."
                        )
                    # Remove messages from history except last `nr_messages_to_preserve` messages.
                    self._oai_messages[key] = self._oai_messages[key][-nr_messages_to_preserve_internal:]
            else:
                self._oai_messages.clear()
        else:
            self._oai_messages[recipient].clear()
            if nr_messages_to_preserve:
                iostream.print(
                    colored(
                        "WARNING: `nr_preserved_messages` is ignored when clearing chat history with a specific agent.",
                        "yellow",
                    ),
                    flush=True,
                )
