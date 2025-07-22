# -*- coding: utf-8 -*-
# Frappe Assistant Core - AI Assistant integration for Frappe Framework
# Copyright (C) 2025 Paul Clinton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Clean tool registry that provides a simple interface to the plugin manager.
Replaces the old wrapper with direct delegation to the plugin manager.
"""

import frappe
from typing import Dict, List, Any, Optional
from frappe_assistant_core.core.base_tool import BaseTool
from frappe_assistant_core.utils.plugin_manager import get_plugin_manager, ToolInfo


class ToolRegistry:
    """
    Simple tool registry that delegates to the plugin manager.
    Provides clean interface for tool access without workarounds.
    """
    
    def __init__(self):
        self.logger = frappe.logger("tool_registry")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        plugin_manager = get_plugin_manager()
        tools = plugin_manager.get_all_tools()
        tool_info = tools.get(tool_name)
        return tool_info.instance if tool_info else None
    
    def get_available_tools(self, user: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of available tools for user with permission checking.
        
        Args:
            user: Username to check permissions for
            
        Returns:
            List of tools in MCP format
        """
        plugin_manager = get_plugin_manager()
        tools = plugin_manager.get_all_tools()
        
        available_tools = []
        for tool_info in tools.values():
            try:
                # Check tool permissions for current user
                if self._check_tool_permission(tool_info.instance, user or frappe.session.user):
                    available_tools.append(tool_info.instance.get_metadata())
            except Exception as e:
                self.logger.warning(f"Failed to get metadata for tool {tool_info.name}: {e}")
        
        return available_tools
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool with given arguments"""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        # Check permissions
        if not self._check_tool_permission(tool, frappe.session.user):
            raise PermissionError(f"Permission denied for tool '{tool_name}'")
        
        return tool.execute(arguments)
    
    def refresh_tools(self) -> bool:
        """Refresh tool discovery"""
        plugin_manager = get_plugin_manager()
        return plugin_manager.refresh_plugins()
    
    def _check_tool_permission(self, tool_instance: BaseTool, user: str) -> bool:
        """Check if user has permission to use the tool"""
        try:
            if tool_instance.requires_permission:
                tool_instance.check_permission()
            return True
        except Exception as e:
            self.logger.debug(f"Permission check failed for tool {tool_instance.name} and user {user}: {e}")
            return False


# Global registry instance
_tool_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get or create global tool registry instance"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry