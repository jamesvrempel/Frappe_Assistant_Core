import frappe
from frappe_assistant_core.utils.logger import api_logger

def startup():
    """App startup initialization"""
    try:
        # Check and populate tool registry if empty
        ensure_tools_registered()
        
        # Initialize assistant server if enabled
        settings = frappe.get_single("Assistant Core Settings")
        if settings and settings.server_enabled:
            from frappe_assistant_core.assistant_core.server import start_server
            start_server()
    except Exception as e:
        api_logger.debug(f"Startup error (non-critical): {e}")

def ensure_tools_registered():
    """Ensure tools are registered in the database registry"""
    try:
        # Check if Assistant Tool Registry table exists and has tools
        if frappe.db.table_exists("tabAssistant Tool Registry"):
            tool_count = frappe.db.count("Assistant Tool Registry")
            
            if tool_count == 0:
                api_logger.info("Assistant Tool Registry is empty, auto-registering tools...")
                from frappe_assistant_core.install import register_default_tools
                register_default_tools()
            else:
                api_logger.debug(f"Assistant Tool Registry has {tool_count} tools")
        else:
            api_logger.debug("Assistant Tool Registry table not found during startup")
    except Exception as e:
        api_logger.debug(f"Error checking tool registry during startup: {e}")