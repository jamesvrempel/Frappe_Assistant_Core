"""
Clone Dashboard Tool - Create copy of existing dashboard

Allows users to duplicate dashboards for customization while preserving
original layouts and configurations.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class CloneDashboard(BaseTool):
    """
    Tool for cloning existing dashboards.
    
    Provides capabilities for:
    - Duplicating dashboard structure and charts
    - Customizing cloned dashboard properties
    - Preserving or modifying permissions
    - Template creation from existing dashboards
    """
    
    def __init__(self):
        super().__init__()
        self.name = "clone_dashboard"
        self.description = self._get_description()
        self.requires_permission = None  # Permission checked dynamically
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "source_dashboard_name": {
                    "type": "string",
                    "description": "Name of dashboard to clone"
                },
                "new_dashboard_name": {
                    "type": "string",
                    "description": "Name for the cloned dashboard"
                },
                "copy_permissions": {
                    "type": "boolean",
                    "default": False,
                    "description": "Copy sharing permissions from source"
                },
                "customize_on_clone": {
                    "type": "boolean",
                    "default": True,
                    "description": "Allow immediate customization after cloning"
                },
                "clone_data_filters": {
                    "type": "boolean",
                    "default": True,
                    "description": "Clone dashboard-level filters"
                },
                "update_chart_titles": {
                    "type": "boolean",
                    "default": False,
                    "description": "Update chart titles to reflect new dashboard"
                }
            },
            "required": ["source_dashboard_name", "new_dashboard_name"]
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Clone existing dashboards to create customized copies while preserving layouts and functionality.

🔄 **CLONING CAPABILITIES:**
• Full Dashboard Copy - All charts, filters, and layouts
• Partial Cloning - Select specific components
• Template Creation - Convert dashboard to reusable template
• Cross-System Clone - Between Insights and Frappe Dashboard

🎨 **CUSTOMIZATION OPTIONS:**
• Rename Dashboard - Give cloned dashboard new identity
• Update Chart Titles - Reflect new context/purpose
• Modify Permissions - Set new sharing rules
• Adjust Filters - Change default filter values

🔒 **PERMISSION HANDLING:**
• Copy Permissions - Inherit sharing from source
• Reset Permissions - Start with private dashboard
• Custom Permissions - Set specific access rules
• Owner Transfer - Assign to different user

⚙️ **ADVANCED FEATURES:**
• Smart Renaming - Auto-update related references
• Data Source Mapping - Connect to different data
• Layout Preservation - Maintain visual structure
• Dependency Tracking - Handle linked components"""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Clone dashboard"""
        try:
            # Import the actual dashboard manager
            from ..tools.dashboard_manager import CloneDashboard as CloneDashboardImpl
            
            # Create dashboard cloner and execute
            dashboard_cloner = CloneDashboardImpl()
            return dashboard_cloner.execute(arguments)
            
        except Exception as e:
            frappe.log_error(
                title=_("Dashboard Cloning Error"),
                message=f"Error cloning dashboard: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
clone_dashboard = CloneDashboard