from typing import List, Dict, Union, Sequence
from ...tools import Tool, ToolSchema
from .assert_valid_name import assert_valid_name

def convert_tools(
        tools: Sequence[Tool | ToolSchema],
    ) -> List[Dict[str, Union[str, Dict]]]:
    result: List[Dict[str, Union[str, Dict]]] = []
    for tool in tools:
        if isinstance(tool, Tool):
            tool_schema = tool.schema
        else:
            assert isinstance(tool, dict)
            tool_schema = tool

        function_def = {
            "type": "function",
            "function": {
                "name": tool_schema["name"],
                "description": tool_schema.get("description", ""),
                "parameters": tool_schema.get("parameters", {}),
                # "strict" não é mais aceito diretamente pela OpenAI
            }
        }

        result.append(function_def)

    # Check if all tools have valid names.
    for tool_param in result:
        assert_valid_name(tool_param["function"]["name"])

    return result
