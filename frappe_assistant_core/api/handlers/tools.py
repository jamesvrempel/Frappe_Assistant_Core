"""
Tools handlers for MCP protocol
Handles tools/list and tools/call requests
"""

import frappe
from typing import Dict, Any, Optional

from frappe_assistant_core.constants.definitions import (
    ErrorCodes, ErrorMessages, LogMessages
)
from frappe_assistant_core.utils.logger import api_logger
from frappe_assistant_core.tools.registry import get_assistant_tools
from frappe_assistant_core.api.handlers.tools_streaming import (
    should_stream_to_artifact, format_for_artifact_streaming
)


def handle_tools_list(request_id: Optional[Any]) -> Dict[str, Any]:
    """Handle tools/list request - return available tools"""
    try:
        api_logger.debug(LogMessages.TOOLS_LIST_REQUEST)
        
        tools = get_assistant_tools()
        
        response = {
            "jsonrpc": "2.0",
            "result": {
                "tools": tools
            }
        }
        
        # Only include id if it's not None
        if request_id is not None:
            response["id"] = request_id
            
        api_logger.info(f"Tools list request completed, returned {len(tools)} tools")
        return response
        
    except Exception as e:
        api_logger.error(f"Error in handle_tools_list: {e}")
        
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": ErrorCodes.INTERNAL_ERROR,
                "message": ErrorMessages.INTERNAL_ERROR,
                "data": str(e)
            }
        }
        
        # Only include id if it's not None
        if request_id is not None:
            response["id"] = request_id
            
        return response


def handle_tool_call(params: Dict[str, Any], request_id: Optional[Any]) -> Dict[str, Any]:
    """Handle tools/call request - execute specific tool"""
    try:
        api_logger.debug(LogMessages.TOOL_CALL_REQUEST.format(params))
        
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": ErrorCodes.INVALID_PARAMS,
                    "message": ErrorMessages.MISSING_TOOL_NAME
                }
            }
            if request_id is not None:
                response["id"] = request_id
            return response
        
        # Get tool registry and execute
        tools_registry = get_assistant_tools()
        tool_found = False
        
        for tool in tools_registry:
            if tool["name"] == tool_name:
                tool_found = True
                break
        
        if not tool_found:
            response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": ErrorCodes.INVALID_PARAMS,
                    "message": ErrorMessages.UNKNOWN_TOOL.format(tool_name)
                }
            }
            if request_id is not None:
                response["id"] = request_id
            return response
        
        # Execute the tool
        from frappe_assistant_core.tools.executor import execute_tool
        result = execute_tool(tool_name, arguments)
        
        # Ensure result is a string for Claude Desktop compatibility
        if not isinstance(result, str):
            result = str(result)
        
        # Check if result should be streamed to artifacts (> 5 lines or very long)
        should_stream = should_stream_to_artifact(result, tool_name)
        
        if should_stream:
            # Provide artifact streaming instructions with truncated result
            artifact_result = format_for_artifact_streaming(result, tool_name, arguments)
            result = artifact_result
        
        response = {
            "jsonrpc": "2.0",
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        }
        
        # Only include id if it's not None
        if request_id is not None:
            response["id"] = request_id
            
        api_logger.info(f"Tool call completed successfully: {tool_name}")
        return response
        
    except Exception as e:
        api_logger.error(f"Error in handle_tool_call: {e}")
        
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": ErrorCodes.INTERNAL_ERROR,
                "message": ErrorMessages.INTERNAL_ERROR,
                "data": str(e)
            }
        }
        
        # Only include id if it's not None
        if request_id is not None:
            response["id"] = request_id
            
        return response