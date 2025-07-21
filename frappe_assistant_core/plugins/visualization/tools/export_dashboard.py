"""
Export Dashboard Tool - Dashboard export in multiple formats

Exports dashboards to PDF, Excel, PowerPoint, and image formats
with professional formatting and customization options.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class ExportDashboard(BaseTool):
    """
    Tool for exporting dashboards in various formats.
    
    Provides capabilities for:
    - Multi-format export (PDF, Excel, PNG, PowerPoint)
    - Professional formatting and styling
    - Scheduled report generation
    - Bulk export operations
    """
    
    def __init__(self):
        super().__init__()
        self.name = "export_dashboard"
        self.description = self._get_description()
        self.requires_permission = None  # Permission checked dynamically
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "dashboard_name": {
                    "type": "string",
                    "description": "Name of dashboard to export"
                },
                "export_format": {
                    "type": "string",
                    "enum": ["pdf", "excel", "png", "powerpoint", "csv", "json"],
                    "description": "Export format"
                },
                "include_data": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include underlying data in export"
                },
                "layout_options": {
                    "type": "object",
                    "properties": {
                        "page_orientation": {"type": "string", "enum": ["portrait", "landscape"]},
                        "page_size": {"type": "string", "enum": ["A4", "A3", "Letter", "Legal"]},
                        "include_header": {"type": "boolean"},
                        "include_footer": {"type": "boolean"},
                        "charts_per_page": {"type": "integer"}
                    },
                    "description": "Layout and formatting options"
                },
                "branding": {
                    "type": "object",
                    "properties": {
                        "company_logo": {"type": "boolean"},
                        "watermark": {"type": "string"},
                        "custom_header": {"type": "string"},
                        "custom_footer": {"type": "string"}
                    },
                    "description": "Branding and customization options"
                },
                "filters": {
                    "type": "object",
                    "description": "Apply filters before export"
                },
                "schedule": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "frequency": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
                        "recipients": {"type": "array"},
                        "email_subject": {"type": "string"}
                    },
                    "description": "Scheduled export settings"
                }
            },
            "required": ["dashboard_name", "export_format"]
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Export dashboards in multiple formats (PDF, Excel, PowerPoint, PNG, CSV, JSON) with professional formatting, company branding, and automated scheduling for regular report delivery."""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Export dashboard"""
        try:
            # Import the actual export manager
            from ..tools.sharing_manager import ExportDashboard as ExportDashboardImpl
            
            # Create export manager and execute
            export_manager = ExportDashboardImpl()
            return export_manager.execute(arguments)
            
        except Exception as e:
            frappe.log_error(
                title=_("Dashboard Export Error"),
                message=f"Error exporting dashboard: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
export_dashboard = ExportDashboard