from frappe import get_doc, has_permission
import json
import frappe
from frappe import _

def check_tool_permissions(tool_name: str, user: str) -> bool:
    """Check if the user has permissions to access the specified tool."""
    tool = get_doc("assistant Tool Registry", tool_name)
    
    if not tool.enabled:
        return False
    
    required_permissions = json.loads(tool.required_permissions or "[]")
    
    for perm in required_permissions:
        if isinstance(perm, dict):
            doctype = perm.get("doctype")
            permission_type = perm.get("permission", "read")
            if not has_permission(doctype, permission_type, user=user):
                return False
        elif isinstance(perm, str):
            if perm not in get_roles(user):
                return False
    
    return True

def get_roles(user: str) -> list:
    """Retrieve roles for the specified user."""
    return [role.role for role in get_doc("User", user).roles] if user else []

def get_permission_query_conditions(user=None):
    """Permission query conditions for assistant Connection Log"""
    if not user:
        user = frappe.session.user
    
    # System Manager and assistant Admin can see all logs
    if "System Manager" in frappe.get_roles(user) or "assistant Admin" in frappe.get_roles(user):
        return ""
    
    # assistant Users can only see their own connection logs
    if "assistant User" in frappe.get_roles(user):
        return f"`tabassistant Connection Log`.user = '{user}'"
    
    # No access for others
    return "1=0"

def get_audit_permission_query_conditions(user=None):
    """Permission query conditions for assistant Audit Log"""
    if not user:
        user = frappe.session.user
    
    # System Manager and assistant Admin can see all audit logs
    if "System Manager" in frappe.get_roles(user) or "assistant Admin" in frappe.get_roles(user):
        return ""
    
    # assistant Users can only see their own audit logs
    if "assistant User" in frappe.get_roles(user):
        return f"`tabassistant Audit Log`.user = '{user}'"
    
    # No access for others
    return "1=0"

def check_assistant_permission(user=None):
    """Check if user has assistant access permission"""
    if not user:
        user = frappe.session.user
    
    user_roles = frappe.get_roles(user)
    assistant_roles = ["System Manager", "assistant Admin", "assistant User"]
    
    return any(role in user_roles for role in assistant_roles)