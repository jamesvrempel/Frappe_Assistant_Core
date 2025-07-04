"""
Plugin discovery and management following Frappe standards.
"""

import os
import importlib
import inspect
import frappe
from frappe import _
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
from frappe_assistant_core.plugins.base_plugin import BasePlugin


class PluginManager:
    """
    Manages plugin discovery, loading, and lifecycle.
    Follows Frappe's module loading patterns.
    """
    
    def __init__(self):
        self.discovered_plugins: Dict[str, Type[BasePlugin]] = {}
        self.loaded_plugins: Dict[str, BasePlugin] = {}
        self.plugin_tools: Dict[str, List[Any]] = {}
        self.logger = frappe.logger("frappe_assistant_core.plugin_manager")
        self._discover_plugins()
    
    def _discover_plugins(self):
        """Auto-discover all plugins in the plugins directory"""
        plugins_dir = Path(__file__).parent.parent / "plugins"
        
        if not plugins_dir.exists():
            self.logger.warning(f"Plugins directory not found: {plugins_dir}")
            return
        
        # Clear existing discoveries
        self.discovered_plugins.clear()
        
        # Scan for plugin directories
        for item in plugins_dir.iterdir():
            if item.is_dir() and not item.name.startswith(('_', '.')):
                self._discover_plugin(item)
    
    def _discover_plugin(self, plugin_dir: Path):
        """Discover a single plugin"""
        try:
            # Check if plugin.py exists
            plugin_file = plugin_dir / "plugin.py"
            if not plugin_file.exists():
                self.logger.debug(f"No plugin.py found in {plugin_dir.name}")
                return
            
            # Import plugin module
            module_name = f"frappe_assistant_core.plugins.{plugin_dir.name}.plugin"
            module = importlib.import_module(module_name)
            
            # Find BasePlugin subclass
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BasePlugin) and 
                    attr is not BasePlugin):
                    
                    plugin_instance = attr()
                    info = plugin_instance.get_info()
                    self.discovered_plugins[info['name']] = attr
                    self.logger.info(
                        _("Discovered plugin: {0}").format(info['name'])
                    )
                    break
                    
        except Exception as e:
            frappe.log_error(
                title=_("Plugin Discovery Error"),
                message=f"Failed to discover plugin in {plugin_dir.name}: {str(e)}"
            )
    
    def get_discovered_plugins(self) -> List[Dict[str, Any]]:
        """Get list of all discovered plugins with their info"""
        plugins = []
        
        for name, plugin_class in self.discovered_plugins.items():
            try:
                instance = plugin_class()
                info = instance.get_info()
                can_enable, error = instance.validate_environment()
                
                plugins.append({
                    **info,
                    'discovered': True,
                    'can_enable': can_enable,
                    'validation_error': error,
                    'loaded': name in self.loaded_plugins
                })
            except Exception as e:
                frappe.log_error(
                    title=_("Plugin Info Error"),
                    message=f"Failed to get info for plugin {name}: {str(e)}"
                )
                plugins.append({
                    'name': name,
                    'error': str(e),
                    'discovered': False,
                    'loaded': False
                })
        
        return plugins
    
    def load_enabled_plugins(self, enabled_plugin_names: List[str]):
        """Load plugins that are enabled in settings"""
        # Unload previously loaded plugins
        for plugin_name, plugin in list(self.loaded_plugins.items()):
            if plugin_name not in enabled_plugin_names:
                self._unload_plugin(plugin_name)
        
        # Load enabled plugins
        for plugin_name in enabled_plugin_names:
            if plugin_name not in self.loaded_plugins:
                self._load_plugin(plugin_name)
    
    def _load_plugin(self, plugin_name: str):
        """Load a single plugin"""
        if plugin_name not in self.discovered_plugins:
            self.logger.warning(
                _("Plugin {0} not found in discovered plugins").format(plugin_name)
            )
            return
        
        try:
            # Create plugin instance
            plugin_class = self.discovered_plugins[plugin_name]
            plugin = plugin_class()
            
            # Validate environment
            can_enable, error = plugin.validate_environment()
            if not can_enable:
                frappe.msgprint(
                    _("Cannot enable plugin {0}: {1}").format(plugin_name, error),
                    indicator='red'
                )
                return
            
            # Load plugin
            plugin.on_enable()
            self.loaded_plugins[plugin_name] = plugin
            
            # Load plugin tools
            self._load_plugin_tools(plugin_name, plugin)
            
            self.logger.info(
                _("Loaded plugin: {0}").format(plugin_name)
            )
            
        except Exception as e:
            frappe.log_error(
                title=_("Plugin Load Error"),
                message=f"Failed to load plugin {plugin_name}: {str(e)}"
            )
    
    def _unload_plugin(self, plugin_name: str):
        """Unload a plugin"""
        if plugin_name in self.loaded_plugins:
            try:
                plugin = self.loaded_plugins[plugin_name]
                plugin.on_disable()
                del self.loaded_plugins[plugin_name]
                
                # Remove plugin tools
                if plugin_name in self.plugin_tools:
                    del self.plugin_tools[plugin_name]
                
                self.logger.info(
                    _("Unloaded plugin: {0}").format(plugin_name)
                )
                
            except Exception as e:
                frappe.log_error(
                    title=_("Plugin Unload Error"),
                    message=f"Error unloading plugin {plugin_name}: {str(e)}"
                )
    
    def _load_plugin_tools(self, plugin_name: str, plugin: BasePlugin):
        """Load tools provided by a plugin"""
        tools = []
        tool_names = plugin.get_tools()
        
        for tool_name in tool_names:
            try:
                # Import tool module
                module_name = (
                    f"frappe_assistant_core.plugins.{plugin_name}"
                    f".tools.{tool_name}"
                )
                module = importlib.import_module(module_name)
                
                # Get tool class - try both PascalCase and snake_case
                tool_class = None
                possible_names = [
                    tool_name,  # exact match
                    tool_name.title().replace('_', ''),  # PascalCase
                    ''.join(word.capitalize() for word in tool_name.split('_'))  # Another PascalCase variant
                ]
                
                for name in possible_names:
                    if hasattr(module, name):
                        tool_class = getattr(module, name)
                        break
                
                if tool_class:
                    tools.append(tool_class)
                    self.logger.debug(f"Loaded tool: {tool_name} from plugin {plugin_name}")
                else:
                    self.logger.error(
                        f"Tool class not found for {tool_name} in {module_name}"
                    )
                
            except Exception as e:
                frappe.log_error(
                    title=_("Tool Load Error"),
                    message=(
                        f"Failed to load tool {tool_name} "
                        f"from plugin {plugin_name}: {str(e)}"
                    )
                )
        
        self.plugin_tools[plugin_name] = tools
    
    def get_all_tools(self) -> Dict[str, Any]:
        """Get all available tools from loaded plugins"""
        all_tools = {}
        
        for plugin_name, tools in self.plugin_tools.items():
            for tool_class in tools:
                try:
                    tool_instance = tool_class()
                    all_tools[tool_instance.name] = tool_instance
                    self.logger.debug(f"Added tool: {tool_instance.name}")
                except Exception as e:
                    frappe.log_error(
                        title=_("Tool Instantiation Error"),
                        message=(
                            f"Failed to instantiate tool "
                            f"from {plugin_name}: {str(e)}"
                        )
                    )
        
        return all_tools
    
    def get_plugin_capabilities(self) -> Dict[str, Any]:
        """Get combined capabilities from all loaded plugins"""
        capabilities = {}
        
        for plugin in self.loaded_plugins.values():
            plugin_caps = plugin.get_capabilities()
            # Merge capabilities
            for key, value in plugin_caps.items():
                if key in capabilities and isinstance(value, dict):
                    capabilities[key].update(value)
                else:
                    capabilities[key] = value
        
        return capabilities
    
    def refresh_plugins(self):
        """Refresh plugin discovery"""
        self._discover_plugins()
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific plugin"""
        if plugin_name not in self.discovered_plugins:
            return None
            
        try:
            plugin_class = self.discovered_plugins[plugin_name]
            plugin = plugin_class()
            info = plugin.get_info()
            can_enable, error = plugin.validate_environment()
            
            return {
                **info,
                'can_enable': can_enable,
                'validation_error': error,
                'loaded': plugin_name in self.loaded_plugins,
                'tools': plugin.get_tools(),
                'capabilities': plugin.get_capabilities()
            }
        except Exception as e:
            frappe.log_error(
                title=_("Plugin Info Error"),
                message=f"Failed to get info for plugin {plugin_name}: {str(e)}"
            )
            return None


# Global plugin manager instance
_plugin_manager = None


def get_plugin_manager() -> PluginManager:
    """Get or create the global plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


def refresh_plugin_manager():
    """Refresh the global plugin manager"""
    global _plugin_manager
    _plugin_manager = None
    return get_plugin_manager()