import frappe
from frappe import _

def get_assistant_status():
    """Template helper to get assistant server status"""
    try:
        from frappe_assistant_core.assistant_core.server import get_server_status
        return get_server_status()
    except Exception:
        return {"running": False, "enabled": False}

def get_tool_count():
    """Template helper to get count of enabled tools"""
    try:
        return frappe.db.count("Assistant Tool Registry", {"enabled": 1})
    except Exception:
        return 0

def format_execution_time(seconds):
    """Format execution time for display"""
    if not seconds:
        return "N/A"
    
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    else:
        return f"{seconds:.2f}s"

def get_connection_status_color(status):
    """Get color for connection status"""
    colors = {
        "Connected": "green",
        "Disconnected": "gray", 
        "Error": "red",
        "Timeout": "orange"
    }
    return colors.get(status, "gray")