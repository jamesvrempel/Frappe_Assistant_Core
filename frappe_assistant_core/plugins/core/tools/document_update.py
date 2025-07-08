"""
Document Update Tool for Core Plugin.
Updates existing Frappe documents.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class DocumentUpdate(BaseTool):
    """
    Tool for updating existing Frappe documents.
    
    Provides capabilities for:
    - Updating document field values
    - Checking permissions
    - Handling validation errors
    """
    
    def __init__(self):
        super().__init__()
        self.name = "document_update"
        self.description = "Update/modify an existing Frappe document. Use when users want to change field values in an existing record. Always fetch the document first to understand current values."
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "The Frappe DocType name (e.g., 'Customer', 'Sales Invoice', 'Item')"
                },
                "name": {
                    "type": "string",
                    "description": "The document name/ID to update (e.g., 'CUST-00001', 'SINV-00001')"
                },
                "data": {
                    "type": "object",
                    "description": "Field updates as key-value pairs. Only include fields that need to be changed. Example: {'customer_name': 'Updated Corp Name', 'phone': '+1234567890'}"
                }
            },
            "required": ["doctype", "name", "data"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing document"""
        doctype = arguments.get("doctype")
        name = arguments.get("name")
        data = arguments.get("data", {})
        
        # Import security validation
        from frappe_assistant_core.core.security_config import validate_document_access, filter_sensitive_fields, audit_log_tool_access
        
        # Validate document access with comprehensive permission checking
        validation_result = validate_document_access(
            user=frappe.session.user,
            doctype=doctype,
            name=name,
            perm_type="write"
        )
        
        if not validation_result["success"]:
            audit_log_tool_access(frappe.session.user, self.name, arguments, validation_result)
            return validation_result
        
        user_role = validation_result["role"]
        
        try:
            # Check if document exists
            if not frappe.db.exists(doctype, name):
                result = {
                    "success": False,
                    "error": f"{doctype} '{name}' not found"
                }
                audit_log_tool_access(frappe.session.user, self.name, arguments, result)
                return result
            
            # Get document
            doc = frappe.get_doc(doctype, name)
            
            # Check if document is submitted (protection against editing submitted docs)
            if hasattr(doc, 'docstatus') and doc.docstatus == 1:
                result = {
                    "success": False,
                    "error": f"Cannot modify submitted document {doctype} '{name}'. Submitted documents are read-only."
                }
                audit_log_tool_access(frappe.session.user, self.name, arguments, result)
                return result
            
            # Filter out sensitive fields that user shouldn't be able to update
            from frappe_assistant_core.core.security_config import SENSITIVE_FIELDS, ADMIN_ONLY_FIELDS
            
            # Get restricted fields for this role and doctype
            restricted_fields = set()
            restricted_fields.update(SENSITIVE_FIELDS.get("all_doctypes", []))
            restricted_fields.update(SENSITIVE_FIELDS.get(doctype, []))
            
            if user_role == "Assistant User":
                restricted_fields.update(ADMIN_ONLY_FIELDS.get("all_doctypes", []))
                doctype_admin_fields = ADMIN_ONLY_FIELDS.get(doctype, [])
                if doctype_admin_fields != "*":
                    restricted_fields.update(doctype_admin_fields)
            
            # Check for attempts to update restricted fields
            restricted_updates = [field for field in data.keys() if field in restricted_fields]
            if restricted_updates:
                result = {
                    "success": False,
                    "error": f"Cannot update restricted fields: {', '.join(restricted_updates)}. These fields require higher privileges."
                }
                audit_log_tool_access(frappe.session.user, self.name, arguments, result)
                return result
            
            # Update field values
            for field, value in data.items():
                setattr(doc, field, value)
            
            # Save document
            doc.save()
            
            result = {
                "success": True,
                "name": doc.name,
                "doctype": doctype,
                "message": f"{doctype} '{doc.name}' updated successfully",
                "updated_fields": list(data.keys())
            }
            
            # Log successful update
            audit_log_tool_access(frappe.session.user, self.name, arguments, result)
            return result
            
        except Exception as e:
            frappe.log_error(
                title=_("Document Update Error"),
                message=f"Error updating {doctype} '{name}': {str(e)}"
            )
            
            result = {
                "success": False,
                "error": str(e),
                "doctype": doctype,
                "name": name
            }
            
            # Log failed update
            audit_log_tool_access(frappe.session.user, self.name, arguments, result)
            return result


# Make sure class name matches file name for discovery
document_update = DocumentUpdate