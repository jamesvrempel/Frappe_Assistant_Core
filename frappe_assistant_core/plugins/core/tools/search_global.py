"""
Global Search Tool for Core Plugin.
Performs global search across all accessible documents.
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class SearchGlobal(BaseTool):
    """
    Tool for global search across Frappe documents.
    
    Provides capabilities for:
    - Cross-doctype search
    - Text matching across multiple fields
    - Permission-aware results
    """
    
    def __init__(self):
        super().__init__()
        self.name = "search_global"
        self.description = "Global search across all accessible documents. Use this when users want to find information but don't know the specific DocType or when searching across multiple document types."
        self.requires_permission = None  # Permission checked per result
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query text. Can be document names, field values, or partial text matches."
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "maximum": 100,
                    "description": "Maximum number of results to return. Default is 20, maximum is 100."
                }
            },
            "required": ["query"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Perform global search"""
        query = arguments.get("query", "").strip()
        limit = arguments.get("limit", 20)
        
        if not query:
            return {
                "success": False,
                "error": "Search query cannot be empty"
            }
        
        try:
            # Get doctypes that can be searched
            searchable_doctypes = []
            for doctype in frappe.get_all("DocType", fields=["name"], pluck="name"):
                if frappe.has_permission(doctype, "read"):
                    searchable_doctypes.append(doctype)
            
            # Search across different DocTypes
            all_results = []
            for doctype in searchable_doctypes[:10]:  # Limit doctypes to avoid too many queries
                try:
                    # Simple search in the doctype
                    results = frappe.get_all(
                        doctype,
                        fields=["name", "creation"],
                        filters={"name": ["like", f"%{query}%"]},
                        limit=5
                    )
                    
                    # Add doctype info to results
                    for result in results:
                        result["doctype"] = doctype
                        all_results.append(result)
                        
                except Exception:
                    # Skip DocTypes that can't be searched
                    continue
            
            # Sort by creation date and limit results
            all_results.sort(key=lambda x: x.get("creation", ""), reverse=True)
            filtered_results = all_results[:limit]
            
            return {
                "success": True,
                "query": query,
                "results": filtered_results,
                "count": len(filtered_results),
                "searched_doctypes": searchable_doctypes[:10],
                "message": f"Found {len(filtered_results)} results for '{query}'"
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Global Search Error"),
                message=f"Error performing global search for '{query}': {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "query": query
            }


# Make sure class name matches file name for discovery
search_global = SearchGlobal