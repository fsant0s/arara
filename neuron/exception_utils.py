from typing import Any


class NeuronNameConflict(Exception):
    def __init__(self, msg: str = "Found multiple neurons with the same name.", *args: Any, **kwargs: Any):
        super().__init__(msg, *args, **kwargs)

class SenderRequired(Exception):
    """Exception raised when the sender is required but not provided."""

    def __init__(self, message: str = "Sender is required but not provided."):
        self.message = message
        super().__init__(self.message)

