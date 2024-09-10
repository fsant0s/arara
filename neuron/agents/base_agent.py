from typing import Any, Dict, List, Optional, Protocol, Union, runtime_checkable

@runtime_checkable
class BaseAgent(Protocol):
    """(In preview) A protocol for Agent.

    An agent can communicate with other agents and perform actions.
    Different agents can differ in what actions they perform in the `receive` method.
    """

    @property
    def name(self) -> str:
        """The name of the agent."""
        ...

    @property
    def description(self) -> str:
        """The description of the agent. Used for the agent's introduction in
        a group chat setting."""
        ...

    def send(
        self,
        message: Union[Dict[str, Any], str],
        recipient: "BaseAgent",
        request_reply: Optional[bool] = None,
    ) -> None:
        """Send a message to another agent.

        Args:
            message (dict or str): the message to send. If a dict, it should be
            a JSON-serializable and follows the OpenAI's ChatCompletion schema.
            recipient (Agent): the recipient of the message.
            request_reply (bool): whether to request a reply from the recipient.
        """
        ...


    def receive(
        self,
        message: Union[Dict[str, Any], str],
        sender: "BaseAgent",
        request_reply: Optional[bool] = None,
    ) -> None:
        """Receive a message from another agent.

        Args:
            message (dict or str): the message received. If a dict, it should be
            a JSON-serializable and follows the OpenAI's ChatCompletion schema.
            sender (Agent): the sender of the message.
            request_reply (bool): whether the sender requests a reply.
        """

    def generate_reply(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        sender: Optional["BaseAgent"] = None,
        **kwargs: Any,
    ) -> Union[str, Dict[str, Any], None]:
        """Generate a reply based on the received messages.

        Args:
            messages (list[dict]): a list of messages received from other agents.
                The messages are dictionaries that are JSON-serializable and
                follows the OpenAI's ChatCompletion schema.
            sender: sender of an Agent instance.

        Returns:
            str or dict or None: the generated reply. If None, no reply is generated.
        """
        
