from typing import Callable

def consolidate_chat_info(chat_info: dict, uniform_sender=None) -> None:
    r"""Consolidate chat information ensuring proper format and validating the summary method.

    Args:
        chat_info (dict or list): A single dictionary or list of dictionaries containing chat information.
        uniform_sender (optional): If provided, this value will uniformly overwrite the sender for all chat info entries.

    Returns:
        None

    Raises:
        AssertionError: If 'summary_method' is not one of the allowed values.
    """
    if isinstance(chat_info, dict):
        chat_info = [chat_info]
    for c in chat_info:
        if uniform_sender is None:
            assert "sender" in c, "sender must be provided."
            sender = c["sender"]
        else:
            sender = uniform_sender
        assert "recipient" in c, "recipient must be provided."
        summary_method = c.get("summary_method")
        assert (
            summary_method is None
            or isinstance(summary_method, Callable)
            or summary_method in ("last_msg", "reflection_with_llm")
        ), "summary_method must be a string chosen from 'reflection_with_llm' or 'last_msg' or a callable, or None."
        if summary_method == "reflection_with_llm":
            assert (
                sender.client is not None or c["recipient"].client is not None
            ), "llm client must be set in either the recipient or sender when summary_method is reflection_with_llm."
