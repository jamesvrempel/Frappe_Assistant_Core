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
    """Fetch assistant Tool Registry."""
    tools = frappe.get_all("assistant Tool Registry", filters={"enabled": 1}, fields=["tool_name", "tool_description"])
    return {"tools": tools}

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