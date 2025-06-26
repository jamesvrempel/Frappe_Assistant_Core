import frappe

def boot_session(bootinfo):
    """Add assistant server information to boot session"""
    try:
        if frappe.session.user != "Guest":
            # Check if user has assistant access
            from frappe_assistant_core.utils.permissions import check_assistant_permission
            
            if check_assistant_permission():
                bootinfo.assistant_enabled = True
                
                # Add server status for admin users
                if "System Manager" in frappe.get_roles() or "assistant Admin" in frappe.get_roles():
                    from frappe_assistant_core.assistant_core.server import get_server_status
                    bootinfo.assistant_core_status = get_server_status()
    except Exception:
        pass  # Ignore errors during boot