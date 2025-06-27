"""
API handlers for different MCP methods
Modular organization for better maintainability
"""

from .initialize import handle_initialize
from .tools import handle_tools_list, handle_tool_call
from .prompts import handle_prompts_list, handle_prompts_get

__all__ = [
    "handle_initialize",
    "handle_tools_list", 
    "handle_tool_call",
    "handle_prompts_list",
    "handle_prompts_get"
]