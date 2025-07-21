"""
List Dashboard Templates Tool - List available dashboard templates

List all available dashboard templates with descriptions and features.
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class ListDashboardTemplates(BaseTool):
    """List available dashboard templates"""
    
    def __init__(self):
        super().__init__()
        self.name = "list_dashboard_templates"
        self.description = "List all available dashboard templates with descriptions and features"
        self.requires_permission = None
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "template_category": {
                    "type": "string",
                    "enum": ["all", "business", "technical", "custom"],
                    "default": "all",
                    "description": "Filter templates by category"
                },
                "include_details": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include detailed template configuration"
                }
            }
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List dashboard templates"""
        try:
            template_category = arguments.get("template_category", "all")
            include_details = arguments.get("include_details", False)
            
            # Get template list from template builder
            from .create_dashboard_from_template import TemplateBuilder
            
            template_builder = TemplateBuilder()
            templates = template_builder.list_available_templates()
            
            # Add additional template information
            for template in templates:
                template["category"] = self._get_template_category(template["template_type"])
                template["permissions_required"] = [template["primary_doctype"]]
                template["features"] = self._get_template_features(template["template_type"])
                
                if include_details:
                    # Load full template config
                    template_config = template_builder._load_template(template["template_type"])
                    if template_config:
                        template["chart_details"] = template_config.get("charts", [])
                        template["global_filters"] = template_config.get("global_filters", {})
            
            # Filter by category if specified
            if template_category != "all":
                templates = [t for t in templates if t["category"] == template_category]
            
            return {
                "success": True,
                "templates": templates,
                "total_count": len(templates),
                "category_filter": template_category,
                "details_included": include_details,
                "available_categories": ["business", "technical", "custom"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_template_category(self, template_type: str) -> str:
        """Get template category"""
        categories = {
            "sales": "business",
            "financial": "business", 
            "inventory": "business",
            "hr": "business",
            "executive": "business",
            "custom": "custom"
        }
        return categories.get(template_type, "business")
    
    def _get_template_features(self, template_type: str) -> List[str]:
        """Get template features"""
        features = {
            "sales": [
                "Revenue tracking",
                "Customer analysis", 
                "Territory performance",
                "Monthly trend analysis",
                "KPI cards"
            ],
            "financial": [
                "P&L tracking",
                "Cash flow analysis",
                "Expense categorization",
                "Budget vs actual",
                "Financial KPIs"
            ],
            "inventory": [
                "Stock level monitoring",
                "Item movement tracking",
                "Inventory valuation",
                "Stock alerts",
                "Warehouse analysis"
            ],
            "hr": [
                "Employee metrics",
                "Department analysis",
                "Attendance tracking",
                "Performance indicators",
                "Headcount reporting"
            ],
            "executive": [
                "High-level KPIs",
                "Growth tracking",
                "Executive summaries",
                "Performance dashboards",
                "Strategic metrics"
            ]
        }
        return features.get(template_type, [])