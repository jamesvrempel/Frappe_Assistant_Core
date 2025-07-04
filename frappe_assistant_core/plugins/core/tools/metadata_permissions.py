"""
Metadata Permissions Tool for Core Plugin.
Retrieves permission information for Frappe DocTypes.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class MetadataPermissions(BaseTool):
    """
    Tool for retrieving DocType permission information.
    
    Provides capabilities for:
    - Getting user permissions for a DocType
    - Checking specific user permissions
    - Getting user roles and permission rules
    """
    
    def __init__(self):
        super().__init__()
        self.name = "metadata_permissions"
        self.description = "Get permission information for a DocType including user roles and permission rules. Shows what actions (read, write, create, delete, etc.) are allowed for the current or specified user."
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "The Frappe DocType name to get permissions for (e.g., 'User', 'Customer', 'Sales Invoice')"
                },
                "user": {
                    "type": "string",
                    "description": "Specific user email to check permissions for. If not provided, checks permissions for current user."
                }
            },
            "required": ["doctype"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get DocType permissions information"""
        doctype = arguments.get("doctype")
        user = arguments.get("user", frappe.session.user)
        
        # Check if DocType exists
        if not frappe.db.exists("DocType", doctype):
            return {
                "success": False,
                "error": f"DocType '{doctype}' not found"
            }
        
        try:
            # Get user roles
            user_roles = frappe.get_roles(user)
            
            # Get meta information
            meta = frappe.get_meta(doctype)
            
            # Check various permissions
            permissions = {
                "read": frappe.has_permission(doctype, "read", user=user),
                "write": frappe.has_permission(doctype, "write", user=user),
                "create": frappe.has_permission(doctype, "create", user=user),
                "delete": frappe.has_permission(doctype, "delete", user=user),
                "submit": frappe.has_permission(doctype, "submit", user=user),
                "cancel": frappe.has_permission(doctype, "cancel", user=user),
                "amend": frappe.has_permission(doctype, "amend", user=user),
                "report": frappe.has_permission(doctype, "report", user=user),
                "import": frappe.has_permission(doctype, "import", user=user),
                "export": frappe.has_permission(doctype, "export", user=user),
                "print": frappe.has_permission(doctype, "print", user=user),
                "email": frappe.has_permission(doctype, "email", user=user)
            }
            
            # Get permission rules from meta
            permission_rules = []
            for perm in meta.permissions:
                permission_rules.append(perm.as_dict())
            
            return {
                "success": True,
                "doctype": doctype,
                "user": user,
                "user_roles": user_roles,
                "permissions": permissions,
                "permission_rules": permission_rules,
                "is_submittable": meta.is_submittable,
                "has_workflow": bool(frappe.db.get_value("Workflow", {"document_type": doctype}))
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Metadata Permissions Error"),
                message=f"Error getting permissions for {doctype}: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "doctype": doctype
            }


# Make sure class name matches file name for discovery
metadata_permissions = MetadataPermissions