"""
Create KPI Card Tool - Metric cards with trend indicators

Creates professional KPI cards with trend analysis,
comparisons, and alert capabilities.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class CreateKpiCard(BaseTool):
    """
    Tool for creating KPI cards with trend analysis.
    
    Provides capabilities for:
    - Metric cards with trend indicators
    - Period-over-period comparisons
    - Alert thresholds and notifications
    - Professional styling and layouts
    """
    
    def __init__(self):
        super().__init__()
        self.name = "create_kpi_card"
        self.description = self._get_description()
        self.requires_permission = None  # Permission checked dynamically
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "KPI card title"
                },
                "doctype": {
                    "type": "string",
                    "description": "Data source DocType"
                },
                "metric_field": {
                    "type": "string",
                    "description": "Field to calculate metric from"
                },
                "aggregate": {
                    "type": "string",
                    "enum": ["sum", "count", "avg", "min", "max", "distinct"],
                    "default": "sum",
                    "description": "Aggregation method for metric"
                },
                "filters": {
                    "type": "object",
                    "description": "Data filters for metric calculation"
                },
                "comparison_period": {
                    "type": "string",
                    "enum": ["previous_month", "previous_quarter", "previous_year", "last_30_days", "none"],
                    "default": "previous_month",
                    "description": "Period for trend comparison"
                },
                "format_type": {
                    "type": "string",
                    "enum": ["number", "currency", "percentage", "duration", "custom"],
                    "default": "number",
                    "description": "Number formatting type"
                },
                "target_value": {
                    "type": "number",
                    "description": "Target value for progress tracking"
                },
                "alert_thresholds": {
                    "type": "object",
                    "properties": {
                        "critical_low": {"type": "number"},
                        "warning_low": {"type": "number"},
                        "warning_high": {"type": "number"},
                        "critical_high": {"type": "number"}
                    },
                    "description": "Alert threshold values"
                },
                "styling": {
                    "type": "object",
                    "properties": {
                        "color_scheme": {"type": "string"},
                        "icon": {"type": "string"},
                        "size": {"type": "string"},
                        "trend_display": {"type": "string"}
                    },
                    "description": "KPI card styling options"
                }
            },
            "required": ["title", "doctype", "metric_field"]
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Create professional KPI cards with trend analysis, alerts, and beautiful formatting.

📊 **KPI METRICS:**
• Revenue Metrics - Sales, profit, growth rates
• Performance Indicators - Efficiency, quality, productivity
• Operational Metrics - Volume, capacity, utilization
• Customer Metrics - Satisfaction, retention, acquisition

📈 **TREND ANALYSIS:**
• Period Comparisons - Month, quarter, year over year
• Trend Indicators - Up/down arrows with percentages
• Progress Tracking - Target vs actual performance
• Historical Context - Show recent performance patterns

⚠️ **SMART ALERTS:**
• Threshold Monitoring - Warning and critical levels
• Color Coding - Visual status indicators
• Performance Bands - Green/yellow/red zones
• Exception Highlighting - Flag unusual values

🎨 **PROFESSIONAL DESIGN:**
• Executive Ready - Corporate dashboard styling
• Mobile Optimized - Perfect on all devices
• Icon Integration - Meaningful visual symbols
• Number Formatting - Currency, percentages, units
• Compact Layout - Maximum information density"""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create KPI card"""
        try:
            # Import the actual KPI card creator
            from ..tools.chart_creator import CreateKPICard
            
            # Create KPI card creator and execute
            kpi_creator = CreateKPICard()
            return kpi_creator.execute(arguments)
            
        except Exception as e:
            frappe.log_error(
                title=_("KPI Card Creation Error"),
                message=f"Error creating KPI card: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
create_kpi_card = CreateKpiCard