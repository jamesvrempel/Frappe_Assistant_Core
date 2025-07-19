"""
Template Builder Tool - Business dashboard templates

Provides pre-built dashboard templates for common business scenarios.
Creates comprehensive dashboards using JSON template configurations.
"""

import frappe
from frappe import _
import json
import os
from typing import Dict, Any, List, Optional
from frappe_assistant_core.core.base_tool import BaseTool


class TemplateBuilder(BaseTool):
    """
    Pre-built business dashboard templates.
    
    Provides capabilities for:
    - Sales Performance Dashboard
    - Financial Performance Dashboard
    - Inventory Management Dashboard
    - HR Analytics Dashboard
    - Executive Summary Dashboard
    - Custom template creation
    """
    
    def __init__(self):
        super().__init__()
        self.name = "create_dashboard_from_template"
        self.description = self._get_description()
        self.requires_permission = None
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "template_type": {
                    "type": "string",
                    "enum": ["sales", "financial", "inventory", "hr", "executive", "custom"],
                    "description": "Type of dashboard template to create"
                },
                "dashboard_name": {
                    "type": "string",
                    "description": "Custom name for the dashboard"
                },
                "doctype_override": {
                    "type": "string",
                    "description": "Override the default doctype for the template"
                },
                "time_period": {
                    "type": "string",
                    "enum": ["current_month", "current_quarter", "current_year", "last_6_months", "last_12_months"],
                    "default": "current_quarter",
                    "description": "Default time period for dashboard data"
                },
                "customizations": {
                    "type": "object",
                    "properties": {
                        "filters": {"type": "object", "description": "Additional global filters"},
                        "chart_modifications": {"type": "array", "description": "Modify specific charts"},
                        "remove_charts": {"type": "array", "description": "Chart titles to remove"},
                        "add_charts": {"type": "array", "description": "Additional charts to add"}
                    },
                    "description": "Optional customizations to template"
                },
                "share_with": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Users/roles to share dashboard with"
                },
                "company": {
                    "type": "string",
                    "description": "Company filter (if applicable)"
                }
            },
            "required": ["template_type"]
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Create professional business dashboards from pre-built templates optimized for specific business functions and use cases.

🎯 **TEMPLATE TYPES:**

📊 **SALES TEMPLATE** - Complete sales performance analytics
• Revenue trends and forecasting
• Top customers and territory analysis
• Sales funnel conversion tracking
• Monthly target achievement gauges
• Recent high-value transactions
• Sales rep performance metrics

💰 **FINANCIAL TEMPLATE** - Comprehensive financial dashboard
• Revenue vs expenses analysis
• Net profit and cash flow tracking
• Budget vs actual performance
• Key financial ratios (ROA, Debt-to-Equity)
• Accounts receivable/payable metrics
• Expense breakdown and analysis

📦 **INVENTORY TEMPLATE** - Complete inventory management
• Stock levels and movement trends
• Low stock alerts and recommendations
• Warehouse utilization analysis
• ABC analysis for optimal inventory
• Seasonal stock patterns
• Stockout risk assessment

👥 **HR TEMPLATE** - Workforce analytics dashboard
• Employee headcount and demographics
• Attendance patterns and trends
• Performance tracking and ratings
• Recruitment funnel analysis
• Training completion rates
• Leave trend analysis

🏢 **EXECUTIVE TEMPLATE** - High-level business metrics
• Key performance indicators (KPIs)
• Revenue and profit trends
• Market share analysis
• Business unit performance
• Strategic metric tracking
• Board-ready presentations

🔧 **FEATURES:**
• One-click deployment - Instant dashboard creation
• Mobile optimized - Responsive design for all devices
• Auto-refresh - Real-time data updates
• Smart permissions - Role-based access control
• Export ready - PDF, Excel, PowerPoint formats
• Customizable - Modify colors, filters, and layouts

⚡ **SMART CAPABILITIES:**
• Auto-detects available data sources
• Intelligent field mapping
• Validates data compatibility
• Suggests optimal time periods
• Configures appropriate chart types

💡 **CUSTOMIZATION OPTIONS:**
• Override default doctypes
• Add/remove specific charts
• Modify filters and time periods
• Customize sharing permissions
• Brand with company colors"""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create dashboard from template"""
        try:
            template_type = arguments.get("template_type")
            dashboard_name = arguments.get("dashboard_name")
            doctype_override = arguments.get("doctype_override")
            time_period = arguments.get("time_period", "current_quarter")
            customizations = arguments.get("customizations", {})
            share_with = arguments.get("share_with", [])
            company = arguments.get("company")
            
            # Load template configuration
            template_config = self._load_template(template_type)
            if not template_config:
                return {
                    "success": False,
                    "error": f"Template '{template_type}' not found"
                }
            
            # Override dashboard name if provided
            if dashboard_name:
                template_config["name"] = dashboard_name
            
            # Override doctype if provided
            if doctype_override:
                template_config["doctype"] = doctype_override
            
            # Apply customizations
            template_config = self._apply_customizations(template_config, customizations, time_period, company)
            
            # Validate template compatibility
            validation_result = self._validate_template(template_config)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Template validation failed: {validation_result['error']}",
                    "missing_doctypes": validation_result.get("missing_doctypes", []),
                    "missing_fields": validation_result.get("missing_fields", [])
                }
            
            # Create dashboard using DashboardManager
            dashboard_result = self._create_template_dashboard(template_config, share_with)
            
            if dashboard_result["success"]:
                return {
                    "success": True,
                    "template_type": template_type,
                    "dashboard_name": template_config["name"],
                    "dashboard_id": dashboard_result["dashboard_id"],
                    "dashboard_url": dashboard_result["dashboard_url"],
                    "charts_created": dashboard_result["charts_created"],
                    "template_features": self._get_template_features(template_config),
                    "customizations_applied": len(customizations),
                    "sharing_info": dashboard_result.get("permissions", []),
                    "mobile_optimized": template_config.get("mobile_layout", {}).get("enabled", True),
                    "auto_refresh": template_config.get("auto_refresh", True),
                    "refresh_interval": template_config.get("refresh_interval", "1_hour")
                }
            else:
                return dashboard_result
                
        except Exception as e:
            frappe.log_error(
                title=_("Template Dashboard Creation Error"),
                message=f"Error creating template dashboard: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "template_type": template_type
            }
    
    def _load_template(self, template_type: str) -> Optional[Dict[str, Any]]:
        """Load template configuration from JSON file"""
        try:
            template_file = f"{template_type}_template.json"
            template_path = os.path.join(
                os.path.dirname(__file__), 
                "..", 
                "templates", 
                template_file
            )
            
            if not os.path.exists(template_path):
                frappe.logger("template_builder").error(f"Template file not found: {template_path}")
                return None
            
            with open(template_path, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            frappe.logger("template_builder").error(f"Failed to load template {template_type}: {str(e)}")
            return None
    
    def _apply_customizations(self, template_config: Dict, customizations: Dict, 
                            time_period: str, company: Optional[str]) -> Dict:
        """Apply customizations to template configuration"""
        try:
            # Apply time period override
            for chart in template_config.get("charts", []):
                if "time_span" not in chart or chart["time_span"] == "default":
                    chart["time_span"] = time_period
            
            # Apply company filter if provided
            if company:
                if "filters" not in template_config:
                    template_config["filters"] = {}
                template_config["filters"]["company"] = company
                
                # Add company filter to global filters if not present
                global_filters = template_config.get("global_filters", [])
                has_company_filter = any(f.get("field") == "company" for f in global_filters)
                if not has_company_filter:
                    global_filters.append({
                        "field": "company",
                        "type": "select",
                        "label": "Company",
                        "options_from": "company"
                    })
                    template_config["global_filters"] = global_filters
            
            # Apply additional filters
            if "filters" in customizations:
                template_config["filters"].update(customizations["filters"])
            
            # Remove charts if specified
            if "remove_charts" in customizations:
                charts_to_remove = customizations["remove_charts"]
                template_config["charts"] = [
                    chart for chart in template_config["charts"]
                    if chart.get("title") not in charts_to_remove
                ]
            
            # Modify existing charts
            if "chart_modifications" in customizations:
                for modification in customizations["chart_modifications"]:
                    chart_title = modification.get("chart_title")
                    for chart in template_config["charts"]:
                        if chart.get("title") == chart_title:
                            # Apply modifications to this chart
                            for key, value in modification.items():
                                if key != "chart_title":
                                    chart[key] = value
                            break
            
            # Add new charts
            if "add_charts" in customizations:
                template_config["charts"].extend(customizations["add_charts"])
            
            return template_config
            
        except Exception as e:
            frappe.logger("template_builder").error(f"Failed to apply customizations: {str(e)}")
            return template_config
    
    def _validate_template(self, template_config: Dict) -> Dict[str, Any]:
        """Validate template configuration against available data"""
        try:
            missing_doctypes = []
            missing_fields = []
            
            # Check primary doctype
            primary_doctype = template_config.get("doctype")
            if primary_doctype and not frappe.db.exists("DocType", primary_doctype):
                missing_doctypes.append(primary_doctype)
            
            # Check permission for primary doctype
            if primary_doctype and not frappe.has_permission(primary_doctype, "read"):
                return {
                    "valid": False,
                    "error": f"Insufficient permissions to access {primary_doctype} data"
                }
            
            # Check charts for doctype and field existence
            for chart in template_config.get("charts", []):
                chart_doctype = chart.get("doctype", primary_doctype)
                
                # Check if doctype exists
                if chart_doctype and not frappe.db.exists("DocType", chart_doctype):
                    if chart_doctype not in missing_doctypes:
                        missing_doctypes.append(chart_doctype)
                    continue
                
                # Check fields exist in doctype
                fields_to_check = [
                    chart.get("x_field"),
                    chart.get("y_field"),
                    chart.get("value_field"),
                    chart.get("group_by")
                ]
                
                for field in fields_to_check:
                    if field and chart_doctype:
                        if not self._field_exists(chart_doctype, field):
                            missing_fields.append(f"{chart_doctype}.{field}")
            
            if missing_doctypes or missing_fields:
                return {
                    "valid": False,
                    "error": "Template validation failed due to missing data sources",
                    "missing_doctypes": missing_doctypes,
                    "missing_fields": missing_fields
                }
            
            return {"valid": True}
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    def _field_exists(self, doctype: str, field: str) -> bool:
        """Check if field exists in doctype"""
        try:
            meta = frappe.get_meta(doctype)
            return meta.has_field(field)
        except:
            return False
    
    def _create_template_dashboard(self, template_config: Dict, share_with: List[str]) -> Dict[str, Any]:
        """Create dashboard using template configuration"""
        try:
            # Import DashboardManager
            from .dashboard_manager import DashboardManager
            
            dashboard_manager = DashboardManager()
            
            # Convert template config to dashboard manager arguments
            dashboard_args = {
                "dashboard_name": template_config["name"],
                "doctype": template_config["doctype"],
                "chart_configs": self._convert_template_charts(template_config["charts"]),
                "filters": template_config.get("filters", {}),
                "share_with": share_with,
                "auto_refresh": template_config.get("auto_refresh", True),
                "refresh_interval": template_config.get("refresh_interval", "1_hour"),
                "mobile_optimized": template_config.get("mobile_layout", {}).get("enabled", True),
                "template_type": template_config.get("category", "custom").lower()
            }
            
            return dashboard_manager.execute(dashboard_args)
            
        except Exception as e:
            frappe.logger("template_builder").error(f"Failed to create template dashboard: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _convert_template_charts(self, template_charts: List[Dict]) -> List[Dict]:
        """Convert template chart configurations to dashboard manager format"""
        converted_charts = []
        
        for chart in template_charts:
            # Convert template chart config to standard format
            converted_chart = {
                "chart_type": chart.get("type", "bar"),
                "title": chart.get("title", "Chart"),
                "x_field": chart.get("x_field"),
                "y_field": chart.get("y_field"),
                "aggregate": chart.get("aggregate", "sum"),
                "filters": chart.get("filters", {}),
                "time_span": chart.get("time_span")
            }
            
            # Add additional properties if present
            if "group_by" in chart:
                converted_chart["group_by"] = chart["group_by"]
            
            if "limit" in chart:
                converted_chart["limit"] = chart["limit"]
            
            if "order_by" in chart:
                converted_chart["order_by"] = chart["order_by"]
            
            # Handle special chart types
            if chart.get("type") == "kpi_card":
                converted_chart["chart_type"] = "kpi_card"
                converted_chart["field"] = chart.get("field", chart.get("y_field"))
                converted_chart["comparison"] = chart.get("comparison")
            
            elif chart.get("type") == "gauge":
                converted_chart["chart_type"] = "gauge"
                converted_chart["target_value"] = chart.get("target_value")
            
            elif chart.get("type") == "table":
                converted_chart["chart_type"] = "table"
                converted_chart["fields"] = chart.get("fields", [])
            
            converted_charts.append(converted_chart)
        
        return converted_charts
    
    def _get_template_features(self, template_config: Dict) -> List[str]:
        """Get list of features included in template"""
        features = []
        
        chart_types = set()
        for chart in template_config.get("charts", []):
            chart_types.add(chart.get("type", "bar"))
        
        # Map chart types to feature descriptions
        feature_mapping = {
            "line": "Trend Analysis",
            "bar": "Comparison Charts", 
            "pie": "Distribution Analysis",
            "kpi_card": "Key Performance Indicators",
            "gauge": "Target Achievement Tracking",
            "table": "Detailed Data Tables",
            "heatmap": "Pattern Recognition",
            "funnel": "Conversion Analysis",
            "scatter": "Correlation Analysis",
            "waterfall": "Flow Analysis"
        }
        
        for chart_type in chart_types:
            if chart_type in feature_mapping:
                features.append(feature_mapping[chart_type])
        
        # Add template-specific features
        if template_config.get("auto_refresh"):
            features.append("Auto-refresh Data")
        
        if template_config.get("mobile_layout", {}).get("enabled"):
            features.append("Mobile Optimized")
        
        if template_config.get("export_options"):
            features.append("Export Capabilities")
        
        return features


class ListDashboardTemplates(BaseTool):
    """List available dashboard templates"""
    
    def __init__(self):
        super().__init__()
        self.name = "list_dashboard_templates"
        self.description = "List all available dashboard templates with descriptions and features"
        self.requires_permission = None
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["sales", "financial", "inventory", "hr", "executive", "all"],
                    "default": "all",
                    "description": "Filter templates by category"
                },
                "include_details": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include detailed template information"
                }
            }
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List available templates"""
        try:
            category = arguments.get("category", "all")
            include_details = arguments.get("include_details", True)
            
            templates = []
            template_types = ["sales", "financial", "inventory", "hr", "executive"]
            
            if category != "all":
                template_types = [category]
            
            template_builder = TemplateBuilder()
            
            for template_type in template_types:
                template_config = template_builder._load_template(template_type)
                
                if template_config:
                    template_info = {
                        "template_type": template_type,
                        "name": template_config["name"],
                        "description": template_config["description"],
                        "category": template_config.get("category", template_type.title()),
                        "primary_doctype": template_config.get("doctype"),
                        "chart_count": len(template_config.get("charts", [])),
                        "tags": template_config.get("tags", [])
                    }
                    
                    if include_details:
                        template_info.update({
                            "features": template_builder._get_template_features(template_config),
                            "auto_refresh": template_config.get("auto_refresh", False),
                            "mobile_optimized": template_config.get("mobile_layout", {}).get("enabled", False),
                            "export_options": list(template_config.get("export_options", {}).keys()),
                            "default_sharing": template_config.get("sharing", {}).get("default_roles", [])
                        })
                    
                    templates.append(template_info)
            
            return {
                "success": True,
                "templates": templates,
                "total_count": len(templates),
                "category_filter": category
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Export tools for plugin discovery
__all__ = ["TemplateBuilder", "ListDashboardTemplates"]