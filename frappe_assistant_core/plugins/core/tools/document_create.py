"""
Document Creation Tool for Core Plugin.
Creates new Frappe documents with validation and permissions.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class DocumentCreate(BaseTool):
    """
    Tool for creating new Frappe documents.
    
    Provides capabilities for:
    - Creating documents with field validation
    - Checking required fields
    - Handling permissions
    - Optional document submission
    """
    
    def __init__(self):
        super().__init__()
        self.name = "document_create"
        self.description = "Create a new Frappe document (e.g., Customer, Sales Invoice, Item, etc.). Use this when users want to add new records to the system. Always check required fields for the doctype first."
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "The Frappe DocType name (e.g., 'Customer', 'Sales Invoice', 'Item', 'User'). Must match exact DocType name in system."
                },
                "data": {
                    "type": "object",
                    "description": "Document field data as key-value pairs. Include all required fields for the doctype. Example: {'customer_name': 'ABC Corp', 'customer_type': 'Company'}"
                },
                "submit": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to submit the document after creation (for submittable doctypes like Sales Invoice). Use true only when explicitly requested."
                }
            },
            "required": ["doctype", "data"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document"""
        doctype = arguments.get("doctype")
        data = arguments.get("data", {})
        submit = arguments.get("submit", False)
        
        # Check permission for DocType
        if not frappe.has_permission(doctype, "create"):
            return {
                "success": False,
                "error": f"Insufficient permissions to create {doctype} document"
            }
        
        try:
            # Create document
            doc = frappe.new_doc(doctype)
            
            # Set field values
            for field, value in data.items():
                setattr(doc, field, value)
            
            # Save document
            doc.insert()
            
            # Submit if requested
            if submit and doc.docstatus == 0:
                doc.submit()
            
            return {
                "success": True,
                "name": doc.name,
                "doctype": doctype,
                "message": f"{doctype} '{doc.name}' created successfully",
                "submitted": doc.docstatus == 1 if submit else False
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Document Creation Error"),
                message=f"Error creating {doctype}: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "doctype": doctype
            }


# Make sure class name matches file name for discovery
document_create = DocumentCreate