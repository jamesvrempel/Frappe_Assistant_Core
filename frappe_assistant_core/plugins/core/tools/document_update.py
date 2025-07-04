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
        
        # Check permission for DocType
        if not frappe.has_permission(doctype, "write"):
            return {
                "success": False,
                "error": f"Insufficient permissions to update {doctype} document"
            }
        
        try:
            # Check if document exists
            if not frappe.db.exists(doctype, name):
                return {
                    "success": False,
                    "error": f"{doctype} '{name}' not found"
                }
            
            # Get document
            doc = frappe.get_doc(doctype, name)
            
            # Update field values
            for field, value in data.items():
                setattr(doc, field, value)
            
            # Save document
            doc.save()
            
            return {
                "success": True,
                "name": doc.name,
                "doctype": doctype,
                "message": f"{doctype} '{doc.name}' updated successfully",
                "updated_fields": list(data.keys())
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Document Update Error"),
                message=f"Error updating {doctype} '{name}': {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "doctype": doctype,
                "name": name
            }


# Make sure class name matches file name for discovery
document_update = DocumentUpdate