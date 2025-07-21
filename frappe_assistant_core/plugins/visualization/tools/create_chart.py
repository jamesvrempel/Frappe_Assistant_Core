"""
Create Chart Tool - Individual chart creation

Creates standalone charts with advanced visualization options
and modern styling capabilities.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class CreateChart(BaseTool):
    """
    Tool for creating individual charts and visualizations.
    
    Provides capabilities for:
    - 13+ chart types with modern styling
    - Advanced aggregation and filtering
    - Interactive features and animations
    - Export and sharing options
    """
    
    def __init__(self):
        super().__init__()
        self.name = "create_chart"
        self.description = self._get_description()
        self.requires_permission = None  # Permission checked dynamically
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "chart_type": {
                    "type": "string",
                    "enum": [
                        "bar", "line", "area", "pie", "donut", "gauge", "kpi_card", 
                        "table", "funnel", "heatmap", "scatter", "waterfall", 
                        "treemap", "histogram", "box"
                    ],
                    "description": "Type of chart to create"
                },
                "title": {
                    "type": "string",
                    "description": "Chart title"
                },
                "doctype": {
                    "type": "string",
                    "description": "Data source DocType"
                },
                "x_field": {
                    "type": "string",
                    "description": "X-axis field"
                },
                "y_field": {
                    "type": "string",
                    "description": "Y-axis field"
                },
                "aggregate": {
                    "type": "string",
                    "enum": ["sum", "count", "avg", "min", "max", "distinct"],
                    "default": "sum",
                    "description": "Aggregation method"
                },
                "filters": {
                    "type": "object",
                    "description": "Data filters"
                },
                "time_span": {
                    "type": "string",
                    "enum": ["current_month", "current_quarter", "current_year", "last_6_months", "last_12_months", "custom"],
                    "description": "Time span for date-based data"
                },
                "styling": {
                    "type": "object",
                    "properties": {
                        "color_scheme": {"type": "string"},
                        "theme": {"type": "string"},
                        "animation": {"type": "boolean"},
                        "show_legend": {"type": "boolean"},
                        "show_grid": {"type": "boolean"}
                    },
                    "description": "Chart styling options"
                },
                "interactive_features": {
                    "type": "object",
                    "properties": {
                        "drill_down": {"type": "boolean"},
                        "zoom": {"type": "boolean"},
                        "tooltips": {"type": "boolean"},
                        "click_actions": {"type": "array"}
                    },
                    "description": "Interactive chart features"
                }
            },
            "required": ["chart_type", "title", "doctype"]
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Create professional charts from Frappe data with 15+ chart types including bar, line, pie, gauge, funnel, and KPI cards. Supports advanced styling and interactive features."""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create chart"""
        try:
            # Import the actual chart creator
            from ..tools.chart_creator import ChartCreator
            
            # Create chart creator and execute
            chart_creator = ChartCreator()
            return chart_creator.execute(arguments)
            
        except Exception as e:
            frappe.log_error(
                title=_("Chart Creation Error"),
                message=f"Error creating chart: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
create_chart = CreateChart