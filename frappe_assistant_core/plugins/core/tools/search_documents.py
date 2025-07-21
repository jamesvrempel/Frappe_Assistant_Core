"""
Search Documents Tool for Core Plugin.
Global search across all accessible documents.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class SearchDocuments(BaseTool):
    """
    Tool for global search across all accessible documents.
    
    Provides capabilities for:
    - Global search across common DocTypes
    - Permission-aware results
    - Structured result formatting
    """
    
    def __init__(self):
        super().__init__()
        self.name = "search_documents"
        self.description = "Global search across all accessible documents"
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Maximum results"
                }
            },
            "required": ["query"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute global search"""
        try:
            # Import the search implementation
            from .search_tools import SearchTools
            
            # Execute search using existing implementation
            return SearchTools.global_search(
                query=arguments.get("query"),
                limit=arguments.get("limit", 20)
            )
            
        except Exception as e:
            frappe.log_error(
                title=_("Search Documents Error"),
                message=f"Error searching documents: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
search_documents = SearchDocuments