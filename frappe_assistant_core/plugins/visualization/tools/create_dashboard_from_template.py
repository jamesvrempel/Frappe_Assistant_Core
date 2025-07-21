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
        self.name = "build_dashboard_from_template"
        self.description = self._get_description()
        self.requires_permission = None  # Permission checked dynamically
        
        self.inputSchema = {
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
        return """Create professional business dashboards using pre-built industry templates (sales, financial, inventory, HR, executive). Features automatic data mapping, customizable branding, and instant deployment."""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create dashboard from template"""
        try:
            # Import the actual template builder
            from ..tools.template_builder import TemplateBuilder
            
            # Map parameters to match TemplateBuilder expectations
            template_builder_args = arguments.copy()
            
            # Map template_name to template_type
            if "template_name" in template_builder_args:
                template_builder_args["template_type"] = template_builder_args["template_name"]
                del template_builder_args["template_name"]
            
            # Map primary_doctype to doctype_override
            if "primary_doctype" in template_builder_args:
                template_builder_args["doctype_override"] = template_builder_args["primary_doctype"]
                del template_builder_args["primary_doctype"]
            
            # Create template builder and execute
            template_builder = TemplateBuilder()
            return template_builder.execute(template_builder_args)
            
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