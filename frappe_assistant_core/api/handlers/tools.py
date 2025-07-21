"""
Clean tools handlers using the new plugin manager architecture.
Replaces workarounds with proper state management and error handling.
"""

import frappe
from typing import Dict, Any, Optional

from frappe_assistant_core.constants.definitions import (
    ErrorCodes, ErrorMessages, LogMessages
)
from frappe_assistant_core.utils.logger import api_logger
from frappe_assistant_core.core.tool_registry import get_tool_registry
from frappe_assistant_core.utils.plugin_manager import PluginError, PluginNotFoundError, PluginValidationError
from frappe_assistant_core.api.handlers.tools_streaming import (
    should_stream_to_artifact, format_for_artifact_streaming
)


def handle_tools_list(request_id: Optional[Any]) -> Dict[str, Any]:
    """Handle tools/list request - return available tools"""
    try:
        api_logger.debug(LogMessages.TOOLS_LIST_REQUEST)
        
        registry = get_tool_registry()
        tools = registry.get_available_tools(user=frappe.session.user)
        
        response = {
            "jsonrpc": "2.0",
            "result": {
                "tools": tools
            }
        }
        
        if request_id is not None:
            response["id"] = request_id
            
        api_logger.info(f"Tools list request completed for user {frappe.session.user}, returned {len(tools)} tools")
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
        
        # Execute tool using registry
        registry = get_tool_registry()
        api_logger.info(f"Executing tool {tool_name} for user {frappe.session.user}")
        
        try:
            result = registry.execute_tool(tool_name, arguments)
        except ValueError as e:
            # Tool not found
            api_logger.warning(f"Tool {tool_name} not available for user {frappe.session.user}")
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
        except PermissionError:
            # Permission denied
            api_logger.warning(f"Permission denied for tool {tool_name} and user {frappe.session.user}")
            response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": ErrorCodes.AUTHENTICATION_REQUIRED,
                    "message": ErrorMessages.ACCESS_DENIED
                }
            }
            if request_id is not None:
                response["id"] = request_id
            return response
        
        # Ensure result is a string for Claude Desktop compatibility
        if not isinstance(result, str):
            result = str(result)
        
        # Check if result should be streamed to artifacts
        should_stream = should_stream_to_artifact(result, tool_name)
        if should_stream:
            result = format_for_artifact_streaming(result, tool_name, arguments)
        
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
        
        if request_id is not None:
            response["id"] = request_id
            
        return response