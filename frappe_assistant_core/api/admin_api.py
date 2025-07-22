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

import frappe
from frappe import _

@frappe.whitelist()
def get_server_settings():
    """Fetch assistant Server Settings with caching."""
    from frappe_assistant_core.utils.cache import get_cached_server_settings
    
    return get_cached_server_settings()

@frappe.whitelist()
def update_server_settings(server_enabled, max_connections, authentication_required, rate_limit, allowed_origins):
    """Update Assistant Core Settings with cache invalidation."""
    from frappe_assistant_core.utils.cache import invalidate_settings_cache
    
    settings = frappe.get_single("Assistant Core Settings")
    settings.server_enabled = server_enabled
    settings.max_connections = max_connections
    settings.authentication_required = authentication_required
    settings.rate_limit = rate_limit
    settings.allowed_origins = allowed_origins
    settings.save()
    
    # Invalidate cached settings
    invalidate_settings_cache()
    
    return {"message": _("Assistant Core Settings updated successfully.")}

@frappe.whitelist()
def get_tool_registry():
    """Fetch assistant Tool Registry with plugin filtering."""
    # Use the core tool registry which handles plugin filtering properly
    from frappe_assistant_core.core.tool_registry import get_tool_registry
    
    registry = get_tool_registry()
    tools = registry.get_available_tools()
    
    # Convert to the expected format for backward compatibility
    formatted_tools = [
        {
            "tool_name": tool.get("name"),
            "tool_description": tool.get("description")
        }
        for tool in tools
    ]
    
    return {"tools": formatted_tools}

@frappe.whitelist()
def toggle_tool(tool_name, enabled):
    """Enable or disable a tool in the assistant Tool Registry."""
    from frappe_assistant_core.utils.cache import invalidate_tool_registry_cache
    
    tool = frappe.get_doc("Assistant Tool Registry", tool_name)
    tool.enabled = enabled
    tool.save()
    
    # Invalidate tool registry cache
    invalidate_tool_registry_cache()
    
    return {"message": _("Tool status updated successfully.")}

@frappe.whitelist()
def get_cache_status():
    """Get current cache status and statistics."""
    from frappe_assistant_core.utils.cache import get_cache_statistics
    
    try:
        cache_stats = get_cache_statistics()
        return {
            "success": True,
            "cache_info": cache_stats
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def clear_cache():
    """Clear all assistant-related caches."""
    from frappe_assistant_core.utils.cache import clear_all_assistant_cache
    
    try:
        clear_all_assistant_cache()
        return {
            "success": True,
            "message": _("All assistant caches cleared successfully.")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def warm_cache():
    """Warm up frequently used caches."""
    from frappe_assistant_core.utils.cache import warm_cache
    
    try:
        success = warm_cache()
        return {
            "success": success,
            "message": _("Cache warming completed.") if success else _("Cache warming failed.")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }