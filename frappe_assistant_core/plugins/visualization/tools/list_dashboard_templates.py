"""
List Dashboard Templates Tool - Browse available business templates

Provides comprehensive listing of dashboard templates with previews
and compatibility information.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class ListDashboardTemplates(BaseTool):
    """
    Tool for browsing available dashboard templates.
    
    Provides capabilities for:
    - Template catalog browsing
    - Template preview and details
    - Compatibility checking
    - Usage recommendations
    """
    
    def __init__(self):
        super().__init__()
        self.name = "show_dashboard_templates"
        self.description = self._get_description()
        self.requires_permission = None
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "category_filter": {
                    "type": "string",
                    "enum": ["all", "sales", "financial", "operations", "hr", "executive"],
                    "default": "all",
                    "description": "Filter templates by business category"
                },
                "include_preview": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include template preview information"
                },
                "check_data_compatibility": {
                    "type": "boolean",
                    "default": True,
                    "description": "Check if templates are compatible with current data"
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["popularity", "name", "category", "compatibility"],
                    "default": "popularity",
                    "description": "Sort templates by specified criteria"
                }
            }
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Browse comprehensive catalog of business dashboard templates with previews and compatibility checking.

📋 **TEMPLATE CATALOG:**
• Sales Templates - Revenue, pipeline, customer analysis
• Financial Templates - P&L, cash flow, financial ratios
• Operations Templates - Inventory, supply chain, efficiency
• HR Templates - Employee metrics, performance, attendance
• Executive Templates - Strategic KPIs, high-level overview

🔍 **TEMPLATE DETAILS:**
• Preview Screenshots - Visual template samples
• Required Data - DocTypes and fields needed
• Chart Types - Visualizations included
• Customization Level - How flexible the template is

✅ **COMPATIBILITY CHECK:**
• Data Availability - Check if required data exists
• Permission Validation - Verify user access
• System Requirements - Ensure app compatibility
• Estimated Setup Time - Time to deploy template

🏆 **RECOMMENDATIONS:**
• Best Match - Templates suited to your data
• Popular Choices - Most used templates
• Industry Standards - Templates by business type
• Quick Start - Templates for immediate use"""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List available templates"""
        try:
            # Import the actual template builder
            from ..tools.template_builder import TemplateBuilder
            
            # Create template builder and get templates
            template_builder = TemplateBuilder()
            
            # Get templates based on filters
            category_filter = arguments.get("category_filter", "all")
            include_preview = arguments.get("include_preview", True)
            check_compatibility = arguments.get("check_data_compatibility", True)
            sort_by = arguments.get("sort_by", "popularity")
            
            templates = template_builder.list_available_templates(
                category_filter=category_filter,
                include_preview=include_preview,
                check_compatibility=check_compatibility,
                sort_by=sort_by
            )
            
            return {
                "success": True,
                "templates": templates,
                "total_count": len(templates),
                "categories_available": ["sales", "financial", "inventory", "hr", "executive"]
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Template Listing Error"),
                message=f"Error listing templates: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
list_dashboard_templates = ListDashboardTemplates