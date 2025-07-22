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
Script to register ALL tools in the Assistant Tool Registry using plugin architecture
"""

import frappe
import json
from frappe_assistant_core.utils.logger import api_logger

def register_all_tools():
    """Register all tools from plugins in the Assistant Tool Registry"""
    
    try:
        # Use the plugin manager to discover and register all tools
        from frappe_assistant_core.utils.plugin_manager import get_plugin_manager
        from frappe_assistant_core.core.tool_registry import get_tool_registry
        
        # Get plugin manager and discover plugins
        plugin_manager = get_plugin_manager()
        discovered_plugins = plugin_manager.get_discovered_plugins()
        
        api_logger.info(f"Discovered {len(discovered_plugins)} plugins for tool registration")
        
        # Load all discovered plugins to get their tools
        plugin_names = [p.get('name') for p in discovered_plugins if p.get('name')]
        plugin_manager.load_enabled_plugins(plugin_names)
        
        # Get tool registry with all tools loaded
        registry = get_tool_registry()
        available_tools = registry.get_available_tools()
        
        api_logger.info(f"Found {len(available_tools)} tools from plugins")
        
        total_registered = 0
        total_updated = 0
        
        # Register each tool in the database
        for tool_info in available_tools:
            tool_name = tool_info["name"]
            
            try:
                # Check if tool already exists
                if frappe.db.exists("Assistant Tool Registry", tool_name):
                    api_logger.debug(f"Tool {tool_name} already exists, updating...")
                    tool_doc = frappe.get_doc("Assistant Tool Registry", tool_name)
                    total_updated += 1
                else:
                    api_logger.debug(f"Creating new tool: {tool_name}")
                    tool_doc = frappe.new_doc("Assistant Tool Registry")
                    tool_doc.tool_name = tool_name
                    total_registered += 1
                
                # Determine category and source plugin
                category = _determine_tool_category(tool_name)
                source_plugin = _determine_tool_source_plugin(tool_name)
                
                # Update tool details
                tool_doc.tool_description = tool_info["description"]
                tool_doc.enabled = 1
                tool_doc.category = category
                tool_doc.source_plugin = source_plugin
                tool_doc.inputSchema = json.dumps(tool_info["inputSchema"], indent=2)
                
                # Set appropriate permissions based on category
                permissions = _get_permissions_for_category(category)
                timeout = _get_timeout_for_category(category)
                
                tool_doc.required_permissions = json.dumps(permissions)
                tool_doc.execution_timeout = timeout
                
                # Save the tool
                tool_doc.save(ignore_permissions=True)
                api_logger.debug(f"✓ Registered tool: {tool_name}")
                
            except Exception as e:
                api_logger.error(f"❌ Error registering tool {tool_name}: {e}")
                continue
        
        frappe.db.commit()
        api_logger.info(f"Successfully registered {total_registered} new tools and updated {total_updated} existing tools!")
        
        # Show summary
        _print_tool_summary()
        
    except Exception as e:
        api_logger.error(f"Failed to register tools: {str(e)}")
        frappe.throw(f"Failed to register tools: {str(e)}")

def _determine_tool_category(tool_name: str) -> str:
    """Determine tool category based on tool name"""
    if tool_name.startswith(("execute_", "analyze_", "query_", "create_")):
        return "Custom"
    elif tool_name.startswith("document_"):
        return "Document Operations"
    elif tool_name.startswith("report_"):
        return "Reports"
    elif tool_name.startswith("search_"):
        return "Search"
    elif tool_name.startswith("metadata_"):
        return "Metadata"
    elif tool_name.startswith("workflow_"):
        return "Workflow"
    else:
        return "Uncategorized"

def _determine_tool_source_plugin(tool_name: str) -> str:
    """Determine which plugin a tool belongs to"""
    # Import from install.py to maintain consistency
    from frappe_assistant_core.install import determine_tool_source_plugin
    return determine_tool_source_plugin(tool_name)

def _get_permissions_for_category(category: str) -> list:
    """Get default permissions for tool category"""
    permission_map = {
        "Custom": [{"doctype": "System Settings", "permission": "read"}],
        "Reports": [{"doctype": "Report", "permission": "read"}],
        "Search": [{"doctype": "System Settings", "permission": "read"}],
        "Metadata": [{"doctype": "DocType", "permission": "read"}],
        "Document Operations": [{"doctype": "System Settings", "permission": "read"}],
        "Workflow": [{"doctype": "System Settings", "permission": "read"}]
    }
    return permission_map.get(category, [])

def _get_timeout_for_category(category: str) -> int:
    """Get default timeout for tool category"""
    timeout_map = {
        "Custom": 60,
        "Reports": 30,
        "Search": 15,
        "Metadata": 15,
        "Document Operations": 30,
        "Workflow": 30
    }
    return timeout_map.get(category, 30)

def _print_tool_summary():
    """Print summary of registered tools"""
    try:
        registered_tools = frappe.get_all(
            "Assistant Tool Registry",
            filters={"enabled": 1},
            fields=["tool_name", "category", "source_plugin"],
            order_by="category, tool_name"
        )
        
        categories = {}
        for tool in registered_tools:
            category = tool.category or "Uncategorized"
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'name': tool.tool_name,
                'plugin': tool.source_plugin or 'core'
            })
        
        api_logger.info("=== Tool Registration Summary ===")
        for category, tools in categories.items():
            api_logger.info(f"{category}: {len(tools)} tools")
            for tool in tools:
                api_logger.info(f"  • {tool['name']} (plugin: {tool['plugin']})")
    
    except Exception as e:
        api_logger.warning(f"Could not generate tool summary: {e}")

if __name__ == "__main__":
    register_all_tools()