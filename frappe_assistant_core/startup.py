import frappe

def startup():
    """App startup initialization"""
    try:
        # Initialize assistant server if enabled
        settings = frappe.get_single("Assistant Core Settings")
        if settings and settings.server_enabled:
            from frappe_assistant_core.assistant_core.server import start_server
            start_server()
    except Exception:
        pass  # Ignore startup errors