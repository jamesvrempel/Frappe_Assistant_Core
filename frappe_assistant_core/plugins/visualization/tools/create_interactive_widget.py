"""
Create Interactive Widget Tool - Dynamic dashboard components

Creates interactive widgets with drill-down, filtering,
and dynamic data refresh capabilities.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class CreateInteractiveWidget(BaseTool):
    """
    Tool for creating interactive dashboard widgets.
    
    Provides capabilities for:
    - Interactive charts with drill-down
    - Dynamic filters and controls
    - Real-time data refresh
    - Cross-widget interactions
    """
    
    def __init__(self):
        super().__init__()
        self.name = "create_interactive_widget"
        self.description = self._get_description()
        self.requires_permission = None  # Permission checked dynamically
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "widget_type": {
                    "type": "string",
                    "enum": [
                        "drill_down_chart", "filter_control", "dynamic_table", 
                        "real_time_metric", "alert_widget", "action_button"
                    ],
                    "description": "Type of interactive widget"
                },
                "title": {
                    "type": "string",
                    "description": "Widget title"
                },
                "data_source": {
                    "type": "object",
                    "properties": {
                        "doctype": {"type": "string"},
                        "fields": {"type": "array"},
                        "filters": {"type": "object"},
                        "refresh_interval": {"type": "integer"}
                    },
                    "description": "Widget data configuration"
                },
                "interactions": {
                    "type": "object",
                    "properties": {
                        "drill_down_levels": {"type": "array"},
                        "click_actions": {"type": "array"},
                        "filter_targets": {"type": "array"},
                        "hover_behaviors": {"type": "object"}
                    },
                    "description": "Interactive behavior configuration"
                },
                "appearance": {
                    "type": "object",
                    "properties": {
                        "size": {"type": "string"},
                        "position": {"type": "object"},
                        "theme": {"type": "string"},
                        "animation": {"type": "boolean"}
                    },
                    "description": "Widget appearance settings"
                },
                "real_time_settings": {
                    "type": "object",
                    "properties": {
                        "auto_refresh": {"type": "boolean"},
                        "refresh_interval": {"type": "integer"},
                        "alert_thresholds": {"type": "object"},
                        "notification_settings": {"type": "object"}
                    },
                    "description": "Real-time behavior configuration"
                }
            },
            "required": ["widget_type", "title", "data_source"]
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Create dynamic interactive widgets that enhance dashboard user experience with real-time capabilities.

🔄 **INTERACTIVE WIDGETS:**
• Drill-Down Charts - Click to explore deeper levels
• Filter Controls - Dynamic dashboard filtering
• Dynamic Tables - Sortable, searchable data grids
• Real-Time Metrics - Live updating KPIs
• Alert Widgets - Threshold-based notifications
• Action Buttons - Trigger workflows or actions

⚡ **REAL-TIME FEATURES:**
• Auto-Refresh - Automatic data updates
• Live Monitoring - Real-time metric tracking
• Threshold Alerts - Instant notifications
• Status Indicators - Visual health monitoring

🔗 **CROSS-WIDGET INTERACTIONS:**
• Filter Propagation - One widget filters others
• Selection Linking - Coordinate multiple views
• Data Synchronization - Maintain consistency
• Event Broadcasting - Widget-to-widget communication

🎨 **CUSTOMIZATION:**
• Flexible Sizing - Responsive widget dimensions
• Position Control - Exact placement on dashboard
• Theme Integration - Match dashboard styling
• Animation Effects - Smooth transitions and updates

🔍 **DRILL-DOWN CAPABILITIES:**
• Multi-Level Exploration - Navigate data hierarchies
• Breadcrumb Navigation - Track exploration path
• Context Preservation - Maintain filter state
• Quick Return - Easy navigation back to overview"""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create interactive widget"""
        try:
            # Import the actual interactive widgets manager
            from ..tools.interactive_widgets import InteractiveWidgets
            
            # Create interactive widgets manager and execute
            widget_manager = InteractiveWidgets()
            return widget_manager.execute(arguments)
            
        except Exception as e:
            frappe.log_error(
                title=_("Interactive Widget Creation Error"),
                message=f"Error creating interactive widget: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
create_interactive_widget = CreateInteractiveWidget