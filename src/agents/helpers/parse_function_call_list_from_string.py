import re
from agents.types import FunctionCall
import json

def parse_function_call_list_from_string(content_str):
    """
    Parses a string containing one or more FunctionCall(...) representations like:
    "[FunctionCall(id='...', arguments='{\"key\": \"value\"}', name='...')]"

    Returns:
        A list of FunctionCall objects, or None if not valid.

    Notes:
        This preserves `arguments` as a JSON string, as required by the FunctionCall schema.
    """
    # Early exit if content doesn't look like it includes a FunctionCall
    if not isinstance(content_str, str) or "FunctionCall(" not in content_str:
        return None

    # Regex to extract id, arguments, and name from the FunctionCall string
    pattern = r"FunctionCall\(\s*id='(.*?)',\s*arguments='(.*?)',\s*name='(.*?)'\s*\)"
    matches = re.findall(pattern, content_str)

    if not matches:
        return None

    calls = []
    for call_id, arguments_str, name in matches:
        # Normalize arguments quotes to ensure it's valid JSON string
        fixed_arguments_str = arguments_str.replace("'", '"')

        # Optionally: validate if it's a proper JSON string
        try:
            _ = json.loads(fixed_arguments_str)
        except json.JSONDecodeError:
            continue  # Skip invalid FunctionCall

        # Create a FunctionCall object, keeping arguments as a string
        calls.append(FunctionCall(id=call_id, name=name, arguments=fixed_arguments_str))

    return calls if calls else None
