"""
Create Dashboard from Template Tool - Business-ready dashboard creation

Creates professional dashboards using pre-built business templates
with industry-specific metrics and layouts.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class CreateDashboardFromTemplate(BaseTool):
    """
    Tool for creating dashboards from business templates.
    
    Provides capabilities for:
    - Business-specific dashboard templates
    - Template customization and adaptation
    - Data source mapping
    - Professional layouts and styling
    """
    
    def __init__(self):
        super().__init__()
        self.name = "create_dashboard_from_template"
        self.description = self._get_description()
        self.requires_permission = None  # Permission checked dynamically
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "template_name": {
                    "type": "string",
                    "enum": ["sales", "financial", "inventory", "hr", "executive"],
                    "description": "Business template to use"
                },
                "dashboard_name": {
                    "type": "string",
                    "description": "Name for the new dashboard"
                },
                "primary_doctype": {
                    "type": "string",
                    "description": "Main DocType for dashboard data"
                },
                "customizations": {
                    "type": "object",
                    "properties": {
                        "company_filter": {"type": "string"},
                        "date_range": {"type": "string"},
                        "currency": {"type": "string"},
                        "custom_fields": {"type": "array"},
                        "color_scheme": {"type": "string"}
                    },
                    "description": "Template customization options"
                },
                "include_sample_data": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include sample data for demo purposes"
                },
                "auto_refresh_interval": {
                    "type": "integer",
                    "default": 300,
                    "description": "Auto-refresh interval in seconds"
                }
            },
            "required": ["template_name", "dashboard_name"]
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Create professional business dashboards using pre-built industry templates with minimal setup.

🎨 **BUSINESS TEMPLATES:**
• Sales Dashboard - Revenue, pipeline, customer metrics
• Financial Dashboard - P&L, cash flow, budget analysis
• Inventory Dashboard - Stock levels, movements, ABC analysis
• HR Dashboard - Employee metrics, attendance, performance
• Executive Dashboard - High-level KPIs and strategic metrics

🔧 **TEMPLATE FEATURES:**
• Industry Best Practices - Proven dashboard layouts
• Smart Data Mapping - Auto-connects to your data
• Professional Design - Corporate-ready styling
• Mobile Optimized - Responsive across devices

⚙️ **CUSTOMIZATION OPTIONS:**
• Company Branding - Apply your colors and logos
• Field Mapping - Connect to your specific fields
• Date Ranges - Set default time periods
• Currency Settings - Localize for your region
• Additional Metrics - Add custom KPIs

🚀 **INSTANT DEPLOYMENT:**
• One-Click Setup - Dashboard ready in seconds
• Sample Data - Preview with demo data
• Auto-Configuration - Smart defaults for quick start
• Validation Checks - Ensures data compatibility"""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create dashboard from template"""
        try:
            # Import the actual template builder
            from ..tools.template_builder import TemplateBuilder
            
            # Create template builder and execute
            template_builder = TemplateBuilder()
            return template_builder.execute(arguments)
            
        except Exception as e:
            frappe.log_error(
                title=_("Template Dashboard Creation Error"),
                message=f"Error creating dashboard from template: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
create_dashboard_from_template = CreateDashboardFromTemplate