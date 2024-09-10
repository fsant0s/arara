from typing import Dict, Union

def message_to_dict(message: Union[Dict, str]) -> Dict:
    """Convert a message to a dictionary.

    The message can be a string or a dictionary. The string will be put in the "content" field of the new dictionary.
    """
    if isinstance(message, str):
        return {"content": message}
    elif isinstance(message, dict):
        return message
    else:
        return dict(message)   