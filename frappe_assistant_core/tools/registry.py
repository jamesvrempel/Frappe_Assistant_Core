"""
Registry wrapper for backward compatibility
Provides a simplified interface to the AutoToolRegistry
"""

from .tool_registry import AutoToolRegistry
from typing import List, Dict, Any


def get_assistant_tools() -> List[Dict[str, Any]]:
    """Get all tools available to the current user"""
    return AutoToolRegistry.get_tools_for_user()


def get_all_tools() -> List[Dict[str, Any]]:
    """Get all tools regardless of user permissions"""
    return AutoToolRegistry.get_all_tools()


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Execute a tool by name with the given arguments"""
    return AutoToolRegistry.execute_tool(tool_name, arguments)


def clear_cache():
    """Clear the tools cache"""
    AutoToolRegistry.clear_cache()