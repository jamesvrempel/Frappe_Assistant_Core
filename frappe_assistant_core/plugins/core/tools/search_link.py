"""
Search Link Tool for Core Plugin.
Search for link field options with filtering.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class SearchLink(BaseTool):
    """
    Tool for searching link field options.
    
    Provides capabilities for:
    - Link field value search
    - Filter-based search
    - Permission-aware results
    """
    
    def __init__(self):
        super().__init__()
        self.name = "search_link"
        self.description = "Search for link field options"
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "Target DocType for link"
                },
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "filters": {
                    "type": "object",
                    "default": {},
                    "description": "Additional filters"
                }
            },
            "required": ["doctype", "query"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute link search"""
        try:
            # Import the search implementation
            from .search_tools import SearchTools
            
            # Execute search using existing implementation
            return SearchTools.search_link(
                doctype=arguments.get("doctype"),
                query=arguments.get("query"),
                filters=arguments.get("filters", {})
            )
            
        except Exception as e:
            frappe.log_error(
                title=_("Search Link Error"),
                message=f"Error searching link options: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
search_link = SearchLink