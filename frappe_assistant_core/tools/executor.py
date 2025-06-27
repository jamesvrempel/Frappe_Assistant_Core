"""
Tool executor module for handling tool execution
Provides centralized tool execution capabilities
"""

import frappe
from typing import Dict, Any
from .tool_registry import AutoToolRegistry
from frappe_assistant_core.utils.logger import api_logger


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    Execute a tool by name with the given arguments
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Arguments to pass to the tool
        
    Returns:
        Tool execution result as string
        
    Raises:
        Exception: If tool execution fails
    """
    try:
        api_logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        
        # Use the AutoToolRegistry to execute the tool
        result = AutoToolRegistry.execute_tool(tool_name, arguments)
        
        api_logger.info(f"Tool {tool_name} executed successfully")
        return result
        
    except Exception as e:
        api_logger.error(f"Tool execution failed for {tool_name}: {e}")
        raise


def validate_tool_arguments(tool_name: str, arguments: Dict[str, Any]) -> bool:
    """
    Validate tool arguments against the tool's schema
    
    Args:
        tool_name: Name of the tool
        arguments: Arguments to validate
        
    Returns:
        True if arguments are valid, False otherwise
    """
    try:
        # Get all tools to find the schema
        tools = AutoToolRegistry.get_all_tools()
        tool_schema = None
        
        for tool in tools:
            if tool.get("name") == tool_name:
                tool_schema = tool.get("inputSchema", {})
                break
        
        if not tool_schema:
            api_logger.warning(f"No schema found for tool: {tool_name}")
            return True  # Allow execution if no schema is defined
        
        # Basic validation - could be enhanced with jsonschema
        required_properties = tool_schema.get("properties", {})
        
        for prop_name, prop_config in required_properties.items():
            if prop_config.get("required", False) and prop_name not in arguments:
                api_logger.error(f"Missing required argument '{prop_name}' for tool {tool_name}")
                return False
        
        return True
        
    except Exception as e:
        api_logger.error(f"Argument validation failed for {tool_name}: {e}")
        return False


def get_tool_info(tool_name: str) -> Dict[str, Any]:
    """
    Get information about a specific tool
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool information dictionary or None if not found
    """
    try:
        tools = AutoToolRegistry.get_all_tools()
        
        for tool in tools:
            if tool.get("name") == tool_name:
                return tool
        
        return None
        
    except Exception as e:
        api_logger.error(f"Failed to get tool info for {tool_name}: {e}")
        return None