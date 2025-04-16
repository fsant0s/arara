from typing import List, Dict, Any

def should_hide_tools(messages: List[Dict[str, Any]], tools: List[Dict[str, Any]], hide_tools_param: str) -> bool:
    """
    Determines if tools should be hidden. This function is used to hide tools when they have been run, minimising the chance of the LLM choosing them when they shouldn't.
    Parameters:
        messages (List[Dict[str, Any]]): List of messages
        tools (List[Dict[str, Any]]): List of tools
        hide_tools_param (str): "hide_tools" parameter value. Can be "if_all_run" (hide tools if all tools have been run), "if_any_run" (hide tools if any of the tools have been run), "never" (never hide tools). Default is "never".

    Returns:
        bool: Indicates whether the tools should be excluded from the response create request

    Example Usage:
    ```python
        # Validating a numerical parameter within specific bounds
        messages = params.get("messages", [])
        tools = params.get("tools", None)
        hide_tools = should_hide_tools(messages, tools, params["hide_tools"])
    """

    if hide_tools_param == "never" or tools is None or len(tools) == 0:
        return False
    elif hide_tools_param == "if_any_run":
        # Return True if any tool_call_id exists, indicating a tool call has been executed. False otherwise.
        return any(["tool_call_id" in dictionary for dictionary in messages])
    elif hide_tools_param == "if_all_run":
        # Return True if all tools have been executed at least once. False otherwise.

        # Get the list of tool names
        check_tool_names = [item["function"]["name"] for item in tools]

        # Prepare a list of tool call ids and related function names
        tool_call_ids = {}

        # Loop through the messages and check if the tools have been run, removing them as we go
        for message in messages:
            if "tool_calls" in message:
                # Register the tool ids and the function names (there could be multiple tool calls)
                for tool_call in message["tool_calls"]:
                    tool_call_ids[tool_call["id"]] = tool_call["function"]["name"]
            elif "tool_call_id" in message:
                # Tool called, get the name of the function based on the id
                tool_name_called = tool_call_ids[message["tool_call_id"]]

                # If we had not yet called the tool, check and remove it to indicate we have
                if tool_name_called in check_tool_names:
                    check_tool_names.remove(tool_name_called)

        # Return True if all tools have been called at least once (accounted for)
        return len(check_tool_names) == 0
    else:
        raise TypeError(
            f"hide_tools_param is not a valid value ['if_all_run','if_any_run','never'], got '{hide_tools_param}'"
        )
