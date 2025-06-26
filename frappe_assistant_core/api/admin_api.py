import frappe
from frappe import _

@frappe.whitelist()
def get_server_settings():
    """Fetch assistant Server Settings."""
    settings = frappe.get_single("Assistant Core Settings")
    return {
        "server_enabled": settings.server_enabled,
        "max_connections": settings.max_connections,
        "authentication_required": settings.authentication_required,
        "rate_limit": settings.rate_limit,
        "allowed_origins": settings.allowed_origins
    }

@frappe.whitelist()
def update_server_settings(server_enabled, max_connections, authentication_required, rate_limit, allowed_origins):
    """Update Assistant Core Settings."""
    settings = frappe.get_single("Assistant Core Settings")
    settings.server_enabled = server_enabled
    settings.max_connections = max_connections
    settings.authentication_required = authentication_required
    settings.rate_limit = rate_limit
    settings.allowed_origins = allowed_origins
    settings.save()
    return {"message": _("Assistant Core Settings updated successfully.")}

@frappe.whitelist()
def get_tool_registry():
    """Fetch assistant Tool Registry."""
    tools = frappe.get_all("assistant Tool Registry", filters={"enabled": 1}, fields=["tool_name", "tool_description"])
    return {"tools": tools}

@frappe.whitelist()
def toggle_tool(tool_name, enabled):
    """Enable or disable a tool in the assistant Tool Registry."""
    tool = frappe.get_doc("assistant Tool Registry", tool_name)
    tool.enabled = enabled
    tool.save()
    return {"message": _("Tool status updated successfully.")}