"""
Document Retrieval Tool for Core Plugin.
Retrieves detailed information about specific Frappe documents.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class DocumentGet(BaseTool):
    """
    Tool for retrieving Frappe documents.
    
    Provides capabilities for:
    - Fetching complete document data
    - Checking permissions
    - Handling non-existent documents
    """
    
    def __init__(self):
        super().__init__()
        self.name = "document_get"
        self.description = "Retrieve detailed information about a specific Frappe document. Use when users ask for details about a particular record they know the name/ID of."
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
                    "description": "The document name/ID (e.g., 'CUST-00001', 'SINV-00001'). This is the unique identifier for the document."
                }
            },
            "required": ["doctype", "name"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a specific document"""
        doctype = arguments.get("doctype")
        name = arguments.get("name")
        
        # Check permission for DocType
        if not frappe.has_permission(doctype, "read"):
            return {
                "success": False,
                "error": f"Insufficient permissions to read {doctype} document"
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
            
            # Convert to dict
            doc_dict = doc.as_dict()
            
            return {
                "success": True,
                "doctype": doctype,
                "name": name,
                "data": doc_dict,
                "message": f"{doctype} '{name}' retrieved successfully"
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Document Retrieval Error"),
                message=f"Error retrieving {doctype} '{name}': {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "doctype": doctype,
                "name": name
            }


# Make sure class name matches file name for discovery
document_get = DocumentGet