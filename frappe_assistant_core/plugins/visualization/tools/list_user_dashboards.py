"""
List User Dashboards Tool - Display available dashboards for user

Provides comprehensive listing of user's dashboards with filtering and
search capabilities across Insights and Frappe Dashboard systems.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class ListUserDashboards(BaseTool):
    """
    Tool for listing user's dashboards with search and filtering.
    
    Provides capabilities for:
    - Listing dashboards from Insights app and Frappe Dashboard
    - Search and filtering options
    - Dashboard metadata and sharing info
    - Quick access actions
    """
    
    def __init__(self):
        super().__init__()
        self.name = "show_my_dashboards"
        self.description = self._get_description()
        self.requires_permission = None  # Permission checked dynamically
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "search_term": {
                    "type": "string",
                    "description": "Search term to filter dashboards by name"
                },
                "filter_by_owner": {
                    "type": "boolean",
                    "default": False,
                    "description": "Show only dashboards owned by current user"
                },
                "include_shared": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include dashboards shared with user"
                },
                "dashboard_type": {
                    "type": "string",
                    "enum": ["all", "insights", "frappe_dashboard"],
                    "default": "all",
                    "description": "Type of dashboards to list"
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Maximum number of dashboards to return"
                }
            }
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """List and search user's available dashboards with filtering by owner, type, and access level. Shows creation dates, chart counts, sharing status, and provides quick actions."""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List user dashboards"""
        try:
            # Import the actual dashboard manager
            from ..tools.dashboard_manager import ListUserDashboards as ListDashboardsImpl
            
            # Create dashboard lister and execute
            dashboard_lister = ListDashboardsImpl()
            return dashboard_lister.execute(arguments)
            
        except Exception as e:
            frappe.log_error(
                title=_("Dashboard Listing Error"),
                message=f"Error listing dashboards: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
list_user_dashboards = ListUserDashboards