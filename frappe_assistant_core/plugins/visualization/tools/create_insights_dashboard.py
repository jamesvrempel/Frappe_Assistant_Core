"""
Create Insights Dashboard Tool - Core dashboard creation

Creates comprehensive dashboards in Insights app with fallback to Frappe Dashboard.
Main tool for dashboard creation with professional layouts and features.
"""

import frappe
from frappe import _
import json
from typing import Dict, Any, List, Optional
from frappe_assistant_core.core.base_tool import BaseTool


class CreateInsightsDashboard(BaseTool):
    """
    Core dashboard creation and management tool.
    
    Provides capabilities for:
    - Creating dashboards in Insights app (primary)
    - Fallback to Frappe Dashboard
    - Dashboard listing and management
    - Professional chart layouts
    - Mobile optimization
    """
    
    def __init__(self):
        super().__init__()
        self.name = "create_dashboard"
        self.description = self._get_description()
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "dashboard_name": {
                    "type": "string",
                    "description": "Dashboard title/name"
                },
                "doctype": {
                    "type": "string", 
                    "description": "Primary data source DocType"
                },
                "chart_configs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "chart_type": {
                                "type": "string",
                                "enum": ["bar", "line", "pie", "gauge", "kpi_card", "table", "funnel", "heatmap"],
                                "description": "Type of chart/widget"
                            },
                            "title": {"type": "string", "description": "Chart title"},
                            "x_field": {"type": "string", "description": "X-axis field"},
                            "y_field": {"type": "string", "description": "Y-axis field"},
                            "aggregate": {
                                "type": "string",
                                "enum": ["sum", "count", "avg", "min", "max"],
                                "default": "sum"
                            },
                            "filters": {"type": "object", "description": "Chart-specific filters"},
                            "time_span": {
                                "type": "string", 
                                "enum": ["current_month", "current_quarter", "current_year", "last_6_months", "last_12_months"],
                                "description": "Time span for date-based data"
                            }
                        },
                        "required": ["chart_type", "title"]
                    },
                    "description": "Array of chart configurations"
                },
                "filters": {
                    "type": "object",
                    "description": "Global dashboard filters"
                },
                "share_with": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of users/roles to share dashboard with"
                },
                "auto_refresh": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable auto refresh"
                },
                "template_type": {
                    "type": "string",
                    "enum": ["sales", "financial", "inventory", "hr", "executive", "custom"],
                    "default": "custom",
                    "description": "Dashboard template type"
                }
            },
            "required": ["dashboard_name", "doctype", "chart_configs"]
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Create comprehensive business dashboards with multiple charts, KPI cards, and interactive widgets. Supports Insights app integration with Frappe Dashboard fallback."""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive dashboard"""
        try:
            # Import the actual dashboard manager
            from ..tools.dashboard_manager import DashboardManager
            
            # Create dashboard manager and execute
            dashboard_manager = DashboardManager()
            return dashboard_manager.execute(arguments)
            
        except Exception as e:
            frappe.log_error(
                title=_("Dashboard Creation Error"),
                message=f"Error creating dashboard: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }