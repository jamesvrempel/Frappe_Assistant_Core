"""
Automatic tool discovery and registration system.
Discovers tools from core and enabled plugins.
"""

import frappe
from frappe import _
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Type, Optional
from frappe_assistant_core.core.base_tool import BaseTool
from frappe_assistant_core.utils.plugin_manager import get_plugin_manager


class ToolRegistry:
    """
    Registry for all available tools.
    Handles discovery from core and plugins.
    """
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.logger = frappe.logger("frappe_assistant_core.tool_registry")
        self._discover_tools()
    
    def _discover_tools(self):
        """Discover all available tools"""
        self.tools.clear()
        
        # All tools are now discovered through the plugin system
        # Core tools are in the 'core' plugin which is always enabled
        self._discover_plugin_tools()
        
        self.logger.info(
            f"Tool discovery complete. Found {len(self.tools)} tools"
        )
    
    # Core tools are now handled through the plugin system
    
    def _discover_plugin_tools(self):
        """Discover tools from enabled plugins"""
        try:
            plugin_manager = get_plugin_manager()
            
            # Get enabled plugins from settings
            try:
                settings = frappe.get_single("Assistant Core Settings")
                enabled_plugins = []
                
                # Handle both old and new settings format
                if hasattr(settings, 'enabled_plugins') and settings.enabled_plugins:
                    enabled_plugins = [p.plugin_name for p in settings.enabled_plugins if getattr(p, 'enabled', False)]
                elif hasattr(settings, 'plugins') and settings.plugins:
                    # Fallback for different field name
                    enabled_plugins = [p.plugin_name for p in settings.plugins if getattr(p, 'enabled', False)]
                
            except Exception as e:
                self.logger.warning(f"Could not load plugin settings: {str(e)}")
                enabled_plugins = []
            
            # Always ensure core plugin is enabled
            if 'core' not in enabled_plugins:
                enabled_plugins.append('core')
            
            # Load plugins
            plugin_manager.load_enabled_plugins(enabled_plugins)
            
            # Get tools from plugins
            plugin_tools = plugin_manager.get_all_tools()
            
            for tool_name, tool_instance in plugin_tools.items():
                if tool_name not in self.tools:  # Avoid duplicates
                    self.tools[tool_name] = tool_instance
                    self.logger.debug(f"Loaded plugin tool: {tool_name}")
                else:
                    self.logger.warning(f"Duplicate tool name: {tool_name}")
                    
        except Exception as e:
            self.logger.error(f"Failed to discover plugin tools: {str(e)}")
    
    def _load_tools_from_module(self, module: Any, source: str):
        """Load all BaseTool subclasses from a module"""
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseTool) and 
                obj is not BaseTool):
                try:
                    tool_instance = obj()
                    if tool_instance.name:  # Only add tools with valid names
                        self.tools[tool_instance.name] = tool_instance
                        self.logger.debug(
                            f"Loaded {source} tool: {tool_instance.name}"
                        )
                    else:
                        self.logger.warning(
                            f"Tool {name} has no name defined"
                        )
                except Exception as e:
                    self.logger.error(
                        f"Failed to instantiate tool {name}: {str(e)}"
                    )
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(tool_name)
    
    def get_available_tools(self, user: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of available tools for user, filtered by enabled plugins.
        
        Args:
            user: Username to check permissions for
            
        Returns:
            List of tools in MCP format
        """
        if not user:
            user = frappe.session.user
        
        available_tools = []
        
        # Get enabled plugins from settings
        enabled_plugin_names = []
        has_plugin_configs = False
        try:
            settings = frappe.get_single("Assistant Core Settings")
            if hasattr(settings, 'enabled_plugins') and settings.enabled_plugins:
                has_plugin_configs = True
                enabled_plugin_names = [
                    p.plugin_name for p in settings.enabled_plugins 
                    if getattr(p, 'enabled', False)
                ]
        except Exception as e:
            self.logger.warning(f"Could not load plugin settings for filtering: {str(e)}")
        
        for tool in self.tools.values():
            try:
                # Check if user has permission for this tool
                if tool.requires_permission:
                    if not frappe.has_permission(
                        tool.requires_permission, 
                        "read", 
                        user=user
                    ):
                        continue
                
                # Plugin-based filtering
                if has_plugin_configs:
                    # Check if this is a plugin tool
                    tool_source_plugin = self._get_tool_source_plugin(tool.name)
                    
                    if tool_source_plugin and tool_source_plugin != 'core':
                        # This is a plugin tool - only include if plugin is enabled
                        if tool_source_plugin not in enabled_plugin_names:
                            self.logger.debug(f"Filtering out tool {tool.name} - plugin {tool_source_plugin} not enabled")
                            continue
                
                available_tools.append(tool.to_mcp_format())
                
            except Exception as e:
                self.logger.error(
                    f"Error checking permission for tool {tool.name}: {str(e)}"
                )
        
        self.logger.info(f"Available tools after plugin filtering: {len(available_tools)} tools")
        return available_tools
    
    def _get_tool_source_plugin(self, tool_name: str) -> str:
        """Get the source plugin for a tool from the database"""
        try:
            # Check if tool registry table exists
            if not frappe.db.table_exists("tabAssistant Tool Registry"):
                return 'core'
            
            # Get source_plugin from tool registry
            source_plugin = frappe.db.get_value(
                "Assistant Tool Registry", 
                {"tool_name": tool_name}, 
                "source_plugin"
            )
            
            return source_plugin or 'core'
            
        except Exception:
            return 'core'  # Fallback to core if there's an error
    
    def get_tool_list(self) -> List[str]:
        """Get list of all tool names"""
        return list(self.tools.keys())
    
    def get_tool_metadata(self) -> List[Dict[str, Any]]:
        """Get metadata for all tools"""
        metadata = []
        
        for tool in self.tools.values():
            try:
                metadata.append(tool.get_metadata())
            except Exception as e:
                self.logger.error(
                    f"Error getting metadata for tool {tool.name}: {str(e)}"
                )
        
        return metadata
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "error_type": "ToolNotFound"
            }
        
        return tool._safe_execute(arguments)
    
    def refresh(self):
        """Refresh tool registry"""
        self._discover_tools()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        core_tools = []
        plugin_tools = []
        
        for tool_name, tool in self.tools.items():
            # Check if this tool comes from the core plugin
            tool_source = self._get_tool_source_plugin(tool_name)
            if tool_source == 'core':
                core_tools.append(tool_name)
            else:
                plugin_tools.append(tool_name)
        
        return {
            "total_tools": len(self.tools),
            "core_tools": len(core_tools),
            "plugin_tools": len(plugin_tools),
            "core_tool_names": core_tools,
            "plugin_tool_names": plugin_tools
        }


# Global registry instance
_tool_registry = None


def get_tool_registry() -> ToolRegistry:
    """Get or create the global tool registry"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry


def refresh_tool_registry():
    """Refresh the global tool registry"""
    global _tool_registry
    _tool_registry = None
    return get_tool_registry()