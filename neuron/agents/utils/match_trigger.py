from typing import Union, Optional, Callable, List 
from ...agents import Agent
from ...exception_utils import SenderRequired

def match_trigger(self: Agent, trigger: Union[None, str, type, Agent, Callable, List], sender: Optional[Agent]) -> bool:
    """Check if the sender matches the trigger.

    Args:
        - trigger (Union[None, str, type, Agent, Callable, List]): The condition to match against the sender.
        Can be `None`, string, type, `Agent` instance, callable, or a list of these.
        - sender (Agent): The sender object or type to be matched against the trigger.

    Returns:
        - bool: Returns `True` if the sender matches the trigger, otherwise `False`.

    Raises:
        - ValueError: If the trigger type is unsupported.
    """
    if trigger is None:
        return sender is None
    elif isinstance(trigger, str):
        if sender is None:
            raise SenderRequired()
        return trigger == sender.name
    elif isinstance(trigger, type):
        return isinstance(sender, trigger)
    elif isinstance(trigger, Agent):
        # return True if the sender is the same type (class) as the trigger
        return trigger == sender
    elif isinstance(trigger, Callable):
        rst = trigger(sender)
        assert isinstance(rst, bool), f"trigger {trigger} must return a boolean value."
        return rst
    elif isinstance(trigger, list):
        return any(match_trigger(self, t, sender) for t in trigger)
    else:
        raise ValueError(f"Unsupported trigger type: {type(trigger)}")