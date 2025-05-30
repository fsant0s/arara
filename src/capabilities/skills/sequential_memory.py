from .skill import Skill
from agents.base import BaseAgent
from typing import Union

class SequentialMemory(Skill):
    """
    An skill that allows a agent to inject relevant memory content before replying to a message.

    This is useful for enriching the agent's response context with previously stored memory entries,
    enhancing continuity and coherence in conversations.
    """

    def __init__(self) -> None:
        """
        Initialize the memory skill.
        """
        super().__init__()

    def on_add_to_agent(self, agent: BaseAgent):
        """
        Register this skill as a hook on the agent to inject memory content before replying.

        Args:
            agent (BaseAgent): The agent to which this skill is attached.

        Raises:
            TypeError: If the given agent is not an instance of BaseAgent.
        """
        if not isinstance(agent, BaseAgent):
            raise TypeError(
                f"Expected parameter 'agent' to be of type 'BaseAgent', but got {type(agent).__name__}."
            )
        # Register the hook to modify messages before the agent replies
        self._agent.register_hook(hookable_method="process_all_messages_before_reply", hook=self._get_memories)

    def _get_memories(
        self,
        processed_messages: Union[dict, str],
    ) ->  Union[dict, str]:
        """
        Fetch relevant memory entries from the agent's memory and append them to the message content.

        Args:
            processed_messages (Union[dict, str]): The content to which memory will be appended.

        Returns:
            str: The combined content with relevant memory included.
        """
        if self._agent._memory:
            lines = []
            # Iterate through all memory entries and format them
            for mem in self._agent._memory:
                for i, mc in enumerate(mem.query().results):
                    lines.append(f"{len(lines) + 1}. {mc.content}")

            # Format the memory contents as a system message
            formatted = "\nRelevant memory content (in chronological order):\n" + "\n".join(lines) + "\n"
            memories = [{
                'content': formatted,
                'role': 'assistant'
            }]
            # Append memory content to the processed user content
            return processed_messages + memories

        # Return the original content if no memory is found
        return processed_messages
