from typing import Any, Dict, List, Tuple, Generator
import json
from agents.types import FunctionCall
from ..tools.base import BaseTool
from llm_messages import FunctionExecutionResult

def execute_tool_call(
    tool_call: FunctionCall,
    tools: List[BaseTool[Any, Any]],
) -> Generator[tuple[FunctionCall, FunctionExecutionResult], None, None]:
    """Execute a single tool call and return the result."""
    try:
        all_tools = tools
        if not all_tools:
            raise ValueError("No tools are available.")
        tool = next((t for t in all_tools if t.name == tool_call.name), None)
        if tool is None:
            raise ValueError(f"The tool '{tool_call.name}' is not available.")
        arguments: Dict[str, Any] = json.loads(tool_call.arguments) if tool_call.arguments else {}
        result = tool.run_json(arguments)
        result_as_str = tool.return_value_as_string(result)
        return (
            tool_call,
            FunctionExecutionResult(
                content=result_as_str,
                call_id=tool_call.id,
                is_error=False,
                name=tool_call.name,
            ),
        )
    except Exception as e:
        return (
            tool_call,
            FunctionExecutionResult(
                content=f"Error: {e}",
                call_id=tool_call.id,
                is_error=True,
                name=tool_call.name,
            ),
        )
