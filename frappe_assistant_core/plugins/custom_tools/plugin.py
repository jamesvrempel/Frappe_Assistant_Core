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
Custom Tools Plugin for external app integration.

This plugin discovers and manages tools from external Frappe apps
using the hooks-based discovery system.
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.plugins.base_plugin import BasePlugin


class CustomToolsPlugin(BasePlugin):
    """
    Plugin that aggregates tools from external Frappe apps.
    
    This plugin serves as a bridge between the enhanced tool registry
    and the existing plugin system, allowing external apps to contribute
    tools through the hooks mechanism.
    """
    
    def __init__(self):
        super().__init__()
        self._external_tools = []
        self._discovery_stats = {}
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            "name": "custom_tools",
            "display_name": "Custom Tools",
            "description": "External app tool integration and management",
            "version": "1.0.0",
            "author": "Frappe Assistant Core Team",
            "category": "Integration",
            "dependencies": [],
            "requires_restart": False,
            "external_integration": True
        }
    
    def get_tools(self) -> List[str]:
        """
        Get list of tools from external apps.
        
        This method discovers tools from external apps using the
        enhanced tool registry and returns their names.
        """
        try:
            from frappe_assistant_core.core.enhanced_tool_registry import get_tool_registry
            
            registry = get_tool_registry()
            
            # Get tools from non-core apps
            external_tools = []
            for tool_name, tool in registry.get_all_tools().items():
                # Skip core app tools
                if tool.source_app != "frappe_assistant_core":
                    external_tools.append(tool_name)
            
            self._external_tools = external_tools
            self._update_discovery_stats(registry)
            
            return external_tools
            
        except Exception as e:
            frappe.logger("custom_tools_plugin").error(f"Failed to discover external tools: {str(e)}")
            return []
    
    def _update_discovery_stats(self, registry):
        """Update discovery statistics"""
        try:
            stats = registry.get_registry_stats()
            
            # Calculate external app statistics
            external_apps = [app for app in stats.get("source_apps", []) 
                           if app != "frappe_assistant_core"]
            
            self._discovery_stats = {
                "external_apps": external_apps,
                "external_app_count": len(external_apps),
                "external_tool_count": len(self._external_tools),
                "total_apps_scanned": len(stats.get("source_apps", [])),
                "discovery_errors": stats.get("discovery_errors", 0)
            }
            
        except Exception as e:
            frappe.logger("custom_tools_plugin").warning(f"Failed to update discovery stats: {str(e)}")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get plugin capabilities"""
        return {
            "external_discovery": {
                "hooks_based": True,
                "automatic_refresh": True,
                "multi_app_support": True,
                "dependency_validation": True
            },
            "tool_management": {
                "dynamic_loading": True,
                "configuration_support": True,
                "audit_logging": True,
                "performance_monitoring": True
            },
            "integration": {
                "cache_integration": True,
                "migration_hooks": True,
                "error_handling": True,
                "statistics_tracking": True
            }
        }
    
    def validate_environment(self) -> tuple[bool, str]:
        """Validate plugin environment"""
        try:
            # Check if enhanced tool registry is available
            from frappe_assistant_core.core.enhanced_tool_registry import get_tool_registry
            
            registry = get_tool_registry()
            
            # Check if discovery is working
            tools = registry.get_all_tools()
            
            if not tools:
                return False, "No tools discovered - registry may not be functioning"
            
            # Check cache availability
            from frappe_assistant_core.utils.tool_cache import get_tool_cache
            
            cache = get_tool_cache()
            cache_stats = cache.get_cache_stats()
            
            if not cache_stats.get("redis_available", False):
                return False, "Redis cache not available - performance may be degraded"
            
            return True, None
            
        except ImportError as e:
            return False, f"Enhanced tool registry not available: {str(e)}"
        except Exception as e:
            return False, f"Environment validation failed: {str(e)}"
    
    def on_enable(self):
        """Called when plugin is enabled"""
        try:
            frappe.logger("custom_tools_plugin").info("Custom Tools plugin enabled")
            
            # Trigger tool discovery to populate cache
            from frappe_assistant_core.utils.tool_cache import refresh_tool_cache
            
            result = refresh_tool_cache(force=True)
            if result.get("success"):
                frappe.logger("custom_tools_plugin").info("Tool cache refreshed on plugin enable")
            else:
                frappe.logger("custom_tools_plugin").warning("Tool cache refresh failed on plugin enable")
                
        except Exception as e:
            frappe.logger("custom_tools_plugin").error(f"Error enabling plugin: {str(e)}")
    
    def on_disable(self):
        """Called when plugin is disabled"""
        try:
            frappe.logger("custom_tools_plugin").info("Custom Tools plugin disabled")
            
            # Clear external tool cache
            from frappe_assistant_core.utils.tool_cache import get_tool_cache
            
            cache = get_tool_cache()
            cache.invalidate_cache()
            
            frappe.logger("custom_tools_plugin").info("Tool cache cleared on plugin disable")
            
        except Exception as e:
            frappe.logger("custom_tools_plugin").error(f"Error disabling plugin: {str(e)}")
    
    def get_external_app_summary(self) -> Dict[str, Any]:
        """
        Get summary of external apps and their tools.
        
        Returns:
            Summary dictionary with app and tool information
        """
        try:
            from frappe_assistant_core.core.enhanced_tool_registry import get_tool_registry
            
            registry = get_tool_registry()
            all_tools = registry.get_all_tools()
            
            # Group tools by external apps
            external_apps = {}
            for tool_name, tool in all_tools.items():
                if tool.source_app != "frappe_assistant_core":
                    app_name = tool.source_app
                    if app_name not in external_apps:
                        external_apps[app_name] = {
                            "app_name": app_name,
                            "tools": [],
                            "tool_count": 0,
                            "categories": set()
                        }
                    
                    external_apps[app_name]["tools"].append({
                        "name": tool_name,
                        "category": tool.category,
                        "description": tool.description[:100] + "..." if len(tool.description) > 100 else tool.description
                    })
                    external_apps[app_name]["tool_count"] += 1
                    external_apps[app_name]["categories"].add(tool.category)
            
            # Convert categories to lists for JSON serialization
            for app_data in external_apps.values():
                app_data["categories"] = list(app_data["categories"])
            
            return {
                "external_apps": list(external_apps.values()),
                "total_external_apps": len(external_apps),
                "total_external_tools": sum(app["tool_count"] for app in external_apps.values()),
                "discovery_stats": self._discovery_stats
            }
            
        except Exception as e:
            frappe.logger("custom_tools_plugin").error(f"Failed to get external app summary: {str(e)}")
            return {
                "external_apps": [],
                "total_external_apps": 0,
                "total_external_tools": 0,
                "error": str(e)
            }
    
    def refresh_external_tools(self) -> Dict[str, Any]:
        """
        Manually refresh external tool discovery.
        
        Returns:
            Refresh operation results
        """
        try:
            from frappe_assistant_core.core.enhanced_tool_registry import get_tool_registry
            
            registry = get_tool_registry()
            result = registry.refresh_tools(force=True)
            
            if result.get("success"):
                # Update our tool list
                self.get_tools()
                
                return {
                    "success": True,
                    "message": "External tools refreshed successfully",
                    "external_tools": len(self._external_tools),
                    "discovery_stats": self._discovery_stats,
                    "registry_result": result
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "registry_result": result
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }