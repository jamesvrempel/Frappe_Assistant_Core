"""
Document Listing Tool for Core Plugin.
Lists and searches Frappe documents with filtering capabilities.
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class DocumentList(BaseTool):
    """
    Tool for listing and searching Frappe documents.
    
    Provides capabilities for:
    - Searching documents with filters
    - Pagination support
    - Field selection
    - Permission checking
    """
    
    def __init__(self):
        super().__init__()
        self.name = "document_list"
        self.description = "Search and list Frappe documents with optional filtering. Use this when users want to find records, get lists of documents, or search for data. This is the primary tool for data exploration and discovery."
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "The Frappe DocType to search (e.g., 'Customer', 'Sales Invoice', 'Item', 'User'). Must match exact DocType name."
                },
                "filters": {
                    "type": "object",
                    "default": {},
                    "description": "Search filters as key-value pairs. Examples: {'status': 'Active'}, {'customer_type': 'Company'}, {'creation': ['>', '2024-01-01']}. Use empty {} to get all records."
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to retrieve. Examples: ['name', 'customer_name', 'email'], ['name', 'item_name', 'item_code']. Leave empty to get standard fields."
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "maximum": 1000,
                    "description": "Maximum number of records to return. Default is 20, maximum is 1000."
                },
                "order_by": {
                    "type": "string",
                    "description": "Order results by field. Examples: 'creation desc', 'name asc', 'modified desc'. Default is 'creation desc'."
                }
            },
            "required": ["doctype"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List documents with filters"""
        doctype = arguments.get("doctype")
        filters = arguments.get("filters", {})
        fields = arguments.get("fields", ["name", "creation", "modified"])
        limit = arguments.get("limit", 20)
        order_by = arguments.get("order_by", "creation desc")
        
        # Check permission for DocType
        if not frappe.has_permission(doctype, "read"):
            return {
                "success": False,
                "error": f"Insufficient permissions to read {doctype} documents"
            }
        
        try:
            # Get documents
            documents = frappe.get_all(
                doctype,
                filters=filters,
                fields=fields,
                limit=limit,
                order_by=order_by
            )
            
            # Get total count for pagination info
            total_count = frappe.db.count(doctype, filters)
            
            return {
                "success": True,
                "doctype": doctype,
                "data": documents,
                "count": len(documents),
                "total_count": total_count,
                "has_more": total_count > limit,
                "filters_applied": filters,
                "message": f"Found {len(documents)} {doctype} records"
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Document List Error"),
                message=f"Error listing {doctype}: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "doctype": doctype
            }


# Make sure class name matches file name for discovery
document_list = DocumentList