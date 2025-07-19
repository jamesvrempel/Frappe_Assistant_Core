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
        self.name = "list_user_dashboards"
        self.description = self._get_description()
        self.requires_permission = None  # Permission checked dynamically
        
        self.input_schema = {
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
        return """List and search through user's available dashboards with comprehensive filtering options.

📋 **DASHBOARD LISTING:**
• Personal Dashboards - Created by current user
• Shared Dashboards - Shared with user or role
• Public Dashboards - Available to all users
• Template Dashboards - Business-ready templates

🔍 **SEARCH & FILTER:**
• Text Search - Find dashboards by name/description
• Owner Filter - Show only own dashboards
• Type Filter - Insights vs Frappe Dashboard
• Access Filter - Personal vs shared dashboards

📊 **DASHBOARD INFO:**
• Creation Date - When dashboard was created
• Last Modified - Recent update information
• Chart Count - Number of visualizations
• Sharing Status - Who has access
• Performance - Load time and data freshness

⚡ **QUICK ACTIONS:**
• View Dashboard - Direct access link
• Clone Dashboard - Create copy for editing
• Share Dashboard - Manage permissions
• Export Dashboard - Download in various formats"""
    
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