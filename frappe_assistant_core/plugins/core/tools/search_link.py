"""
Search Link Tool for Core Plugin.
Searches for link field values across DocTypes.
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class SearchLink(BaseTool):
    """
    Tool for searching link field values across DocTypes.
    
    Provides capabilities for:
    - Finding valid link values for Link fields
    - Searching for references to a document
    - Link validation
    """
    
    def __init__(self):
        super().__init__()
        self.name = "search_link"
        self.description = "Search for valid link field values or find references to a document. Use when users need to find valid options for Link fields or see where a document is referenced."
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "target_doctype": {
                    "type": "string",
                    "description": "The DocType to search for link values (e.g., 'Customer', 'Item', 'User')"
                },
                "search_text": {
                    "type": "string",
                    "description": "Text to search for in the target DocType"
                },
                "reference_doctype": {
                    "type": "string",
                    "description": "DocType to search for references in (optional)"
                },
                "reference_name": {
                    "type": "string",
                    "description": "Document name to find references to (optional)"
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Maximum number of results to return"
                }
            },
            "required": ["target_doctype"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search for link field values or references"""
        target_doctype = arguments.get("target_doctype")
        search_text = arguments.get("search_text")
        reference_doctype = arguments.get("reference_doctype")
        reference_name = arguments.get("reference_name")
        limit = arguments.get("limit", 20)
        
        # Check if target DocType exists
        if not frappe.db.exists("DocType", target_doctype):
            return {
                "success": False,
                "error": f"DocType '{target_doctype}' not found"
            }
        
        # Check permission for target DocType
        if not frappe.has_permission(target_doctype, "read"):
            return {
                "success": False,
                "error": f"Insufficient permissions to search {target_doctype} documents"
            }
        
        try:
            results = []
            
            if reference_doctype and reference_name:
                # Find references to a specific document
                results = self._find_references(reference_doctype, reference_name, limit)
            else:
                # Search for link values
                results = self._search_link_values(target_doctype, search_text, limit)
            
            return {
                "success": True,
                "target_doctype": target_doctype,
                "search_text": search_text,
                "reference_doctype": reference_doctype,
                "reference_name": reference_name,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Link Search Error"),
                message=f"Error searching links: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "target_doctype": target_doctype
            }
    
    def _search_link_values(self, doctype: str, search_text: str, limit: int) -> List[Dict]:
        """Search for valid link values in a DocType"""
        try:
            filters = {}
            if search_text:
                # Try to search in name and title fields
                filters = {
                    "name": ["like", f"%{search_text}%"]
                }
            
            results = frappe.get_all(
                doctype,
                filters=filters,
                fields=["name", "title", "creation", "modified"],
                limit=limit,
                order_by="modified desc"
            )
            
            return results
            
        except Exception:
            return []
    
    def _find_references(self, doctype: str, name: str, limit: int) -> List[Dict]:
        """Find references to a specific document"""
        try:
            # Get all DocTypes that have Link fields pointing to this DocType
            references = []
            
            # Use frappe's built-in method to find references
            ref_docs = frappe.get_all(
                "DocType",
                fields=["name"],
                filters={"istable": 0}
            )
            
            for ref_doc in ref_docs[:10]:  # Limit to avoid performance issues
                try:
                    meta = frappe.get_meta(ref_doc.name)
                    
                    for field in meta.fields:
                        if field.fieldtype == "Link" and field.options == doctype:
                            # Search for references in this field
                            refs = frappe.get_all(
                                ref_doc.name,
                                filters={field.fieldname: name},
                                fields=["name", "creation", "modified"],
                                limit=5
                            )
                            
                            for ref in refs:
                                references.append({
                                    "doctype": ref_doc.name,
                                    "name": ref.name,
                                    "field": field.fieldname,
                                    "creation": ref.creation,
                                    "modified": ref.modified
                                })
                                
                except Exception:
                    continue
            
            return references[:limit]
            
        except Exception:
            return []


# Make sure class name matches file name for discovery
search_link = SearchLink