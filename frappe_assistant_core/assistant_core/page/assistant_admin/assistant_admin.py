import frappe
from frappe import _

def get_context(context):
    context.title = _("assistant Server Management")
    context.description = _("Manage the assistant Server settings and tools.")
    
    # Fetch assistant Server Settings
    context.settings = frappe.get_single("assistant Server Settings")
    
    # Fetch assistant Tool Registry
    context.tools = frappe.get_all("assistant Tool Registry", filters={"enabled": 1}, fields=["tool_name", "tool_description"])