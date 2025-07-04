"""
Search DocType Tool for Core Plugin.
Searches within a specific DocType.
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class SearchDoctype(BaseTool):
    """
    Tool for searching within a specific DocType.
    
    Provides capabilities for:
    - Text search within DocType fields
    - Filter-based search
    - Field-specific search
    """
    
    def __init__(self):
        super().__init__()
        self.name = "search_doctype"
        self.description = "Search within a specific DocType using text or field-based criteria. Use when users want to find documents within a particular document type."
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "The DocType to search within (e.g., 'Customer', 'Sales Invoice', 'Item')"
                },
                "search_text": {
                    "type": "string",
                    "description": "Text to search for across searchable fields in the DocType"
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to search in. Leave empty to search all searchable fields."
                },
                "filters": {
                    "type": "object",
                    "description": "Additional filters to apply to the search"
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Maximum number of results to return"
                }
            },
            "required": ["doctype", "search_text"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search within a specific DocType"""
        doctype = arguments.get("doctype")
        search_text = arguments.get("search_text")
        fields = arguments.get("fields", [])
        filters = arguments.get("filters", {})
        limit = arguments.get("limit", 20)
        
        # Check if DocType exists
        if not frappe.db.exists("DocType", doctype):
            return {
                "success": False,
                "error": f"DocType '{doctype}' not found"
            }
        
        # Check permission for DocType
        if not frappe.has_permission(doctype, "read"):
            return {
                "success": False,
                "error": f"Insufficient permissions to search {doctype} documents"
            }
        
        try:
            # Build search query
            search_fields = fields if fields else self._get_searchable_fields(doctype)
            
            # Perform search
            results = []
            
            if search_fields:
                # Use OR conditions for text search across fields
                or_filters = []
                for field in search_fields:
                    or_filters.append([doctype, field, "like", f"%{search_text}%"])
                
                # Combine with additional filters
                all_filters = [filters] if filters else []
                
                results = frappe.get_all(
                    doctype,
                    filters=all_filters,
                    or_filters=or_filters,
                    fields=["name", "creation", "modified"] + search_fields[:5],  # Limit fields
                    limit=limit,
                    order_by="modified desc"
                )
            
            return {
                "success": True,
                "doctype": doctype,
                "search_text": search_text,
                "results": results,
                "count": len(results),
                "searched_fields": search_fields
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("DocType Search Error"),
                message=f"Error searching {doctype}: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "doctype": doctype,
                "search_text": search_text
            }
    
    def _get_searchable_fields(self, doctype: str) -> List[str]:
        """Get searchable fields for a DocType"""
        try:
            meta = frappe.get_meta(doctype)
            searchable_fields = []
            
            for field in meta.fields:
                if field.fieldtype in ["Data", "Text", "Long Text", "Small Text", "Text Editor"]:
                    searchable_fields.append(field.fieldname)
            
            # Add standard fields - only add title if it exists
            searchable_fields.append("name")
            
            # Check if title field exists before adding
            if any(field.fieldname == "title" for field in meta.fields):
                searchable_fields.append("title")
            
            return searchable_fields
            
        except Exception:
            return ["name"]


# Make sure class name matches file name for discovery
search_doctype = SearchDoctype