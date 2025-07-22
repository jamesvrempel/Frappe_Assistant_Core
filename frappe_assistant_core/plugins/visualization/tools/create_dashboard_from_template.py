# -*- coding: utf-8 -*-
# Frappe Assistant Core - AI Assistant integration for Frappe Framework
# Copyright (C) 2025 Paul Clinton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
        self.description = "Create professional business dashboards from pre-built templates for sales, financial, inventory, HR, and executive analytics"
        self.requires_permission = None
        
        self.inputSchema = {
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
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create dashboard from template"""
        try:
            template_type = arguments.get("template_type")
            dashboard_name = arguments.get("dashboard_name") or f"{template_type.title()} Dashboard"
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
            
            # Override doctype if specified
            if doctype_override:
                template_config["primary_doctype"] = doctype_override
            
            # Check permissions for primary doctype
            primary_doctype = template_config.get("primary_doctype", "Sales Invoice")
            if not frappe.has_permission(primary_doctype, "read"):
                return {
                    "success": False,
                    "error": f"Insufficient permissions to access {primary_doctype} data"
                }
            
            # Apply customizations
            chart_configs = self._apply_template_customizations(
                template_config.get("charts", []), 
                customizations, 
                time_period, 
                company
            )
            
            # Create dashboard using the insights dashboard tool
            from .create_insights_dashboard import DashboardManager
            
            dashboard_manager = DashboardManager()
            result = dashboard_manager.execute({
                "dashboard_name": dashboard_name,
                "doctype": primary_doctype,
                "chart_configs": chart_configs,
                "filters": template_config.get("global_filters", {}),
                "share_with": share_with,
                "template_type": template_type,
                "mobile_optimized": True
            })
            
            if result["success"]:
                result["template_used"] = template_type
                result["template_config"] = template_config
                result["customizations_applied"] = len(customizations) > 0
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_template(self, template_type: str) -> Optional[Dict]:
        """Load template configuration"""
        try:
            # Define built-in templates
            templates = {
                "sales": {
                    "name": "Sales Performance Dashboard",
                    "description": "Complete sales analytics with revenue, customers, and performance metrics",
                    "primary_doctype": "Sales Invoice",
                    "global_filters": {"docstatus": 1},
                    "charts": [
                        {
                            "chart_type": "kpi_card",
                            "title": "Total Revenue",
                            "y_field": "grand_total",
                            "aggregate": "sum",
                            "time_span": "current_quarter"
                        },
                        {
                            "chart_type": "line",
                            "title": "Monthly Revenue Trend",
                            "x_field": "posting_date",
                            "y_field": "grand_total",
                            "aggregate": "sum",
                            "time_span": "last_12_months"
                        },
                        {
                            "chart_type": "bar",
                            "title": "Top Customers",
                            "x_field": "customer",
                            "y_field": "grand_total",
                            "aggregate": "sum",
                            "time_span": "current_quarter"
                        },
                        {
                            "chart_type": "pie",
                            "title": "Sales by Territory",
                            "x_field": "territory",
                            "y_field": "grand_total",
                            "aggregate": "sum"
                        }
                    ]
                },
                "financial": {
                    "name": "Financial Performance Dashboard",
                    "description": "Financial metrics with P&L, cash flow, and budget analysis",
                    "primary_doctype": "GL Entry",
                    "global_filters": {"is_cancelled": 0},
                    "charts": [
                        {
                            "chart_type": "kpi_card",
                            "title": "Net Income",
                            "y_field": "debit",
                            "aggregate": "sum",
                            "time_span": "current_quarter"
                        },
                        {
                            "chart_type": "line",
                            "title": "Monthly Cash Flow",
                            "x_field": "posting_date",
                            "y_field": "debit",
                            "aggregate": "sum",
                            "time_span": "last_12_months"
                        },
                        {
                            "chart_type": "bar",
                            "title": "Expenses by Account",
                            "x_field": "account",
                            "y_field": "debit",
                            "aggregate": "sum"
                        }
                    ]
                },
                "inventory": {
                    "name": "Inventory Management Dashboard",
                    "description": "Stock levels, movements, and inventory analysis",
                    "primary_doctype": "Stock Entry",
                    "global_filters": {"docstatus": 1},
                    "charts": [
                        {
                            "chart_type": "kpi_card",
                            "title": "Total Stock Value",
                            "y_field": "total_outgoing_value",
                            "aggregate": "sum"
                        },
                        {
                            "chart_type": "bar",
                            "title": "Stock Movement by Item",
                            "x_field": "item_code",
                            "y_field": "qty",
                            "aggregate": "sum"
                        }
                    ]
                },
                "hr": {
                    "name": "HR Analytics Dashboard", 
                    "description": "Employee metrics, attendance, and HR analytics",
                    "primary_doctype": "Employee",
                    "global_filters": {"status": "Active"},
                    "charts": [
                        {
                            "chart_type": "kpi_card",
                            "title": "Total Employees",
                            "aggregate": "count"
                        },
                        {
                            "chart_type": "pie",
                            "title": "Employees by Department",
                            "x_field": "department",
                            "aggregate": "count"
                        }
                    ]
                },
                "executive": {
                    "name": "Executive Summary Dashboard",
                    "description": "High-level KPIs and executive metrics",
                    "primary_doctype": "Sales Invoice",
                    "global_filters": {"docstatus": 1},
                    "charts": [
                        {
                            "chart_type": "kpi_card",
                            "title": "Monthly Revenue",
                            "y_field": "grand_total",
                            "aggregate": "sum",
                            "time_span": "current_month"
                        },
                        {
                            "chart_type": "line",
                            "title": "Growth Trend",
                            "x_field": "posting_date",
                            "y_field": "grand_total", 
                            "aggregate": "sum",
                            "time_span": "last_6_months"
                        }
                    ]
                }
            }
            
            return templates.get(template_type)
            
        except Exception as e:
            frappe.logger("template_builder").error(f"Failed to load template {template_type}: {str(e)}")
            return None
    
    def _apply_template_customizations(self, chart_configs: List[Dict], 
                                     customizations: Dict, time_period: str, 
                                     company: Optional[str]) -> List[Dict]:
        """Apply customizations to template"""
        try:
            # Apply time period to all charts
            for chart in chart_configs:
                if not chart.get("time_span"):
                    chart["time_span"] = time_period
                
                # Add company filter if specified
                if company:
                    chart.setdefault("filters", {})["company"] = company
                
                # Apply global customization filters
                if "filters" in customizations:
                    chart.setdefault("filters", {}).update(customizations["filters"])
            
            # Remove charts if specified
            if "remove_charts" in customizations:
                chart_configs = [
                    chart for chart in chart_configs 
                    if chart.get("title") not in customizations["remove_charts"]
                ]
            
            # Add additional charts if specified
            if "add_charts" in customizations:
                chart_configs.extend(customizations["add_charts"])
            
            return chart_configs
            
        except Exception as e:
            frappe.logger("template_builder").error(f"Failed to apply customizations: {str(e)}")
            return chart_configs
    
    def list_available_templates(self) -> List[Dict[str, Any]]:
        """List all available dashboard templates"""
        templates = [
            {
                "template_type": "sales",
                "name": "Sales Performance Dashboard",
                "description": "Complete sales analytics with revenue, customers, and performance metrics",
                "primary_doctype": "Sales Invoice",
                "charts_count": 4
            },
            {
                "template_type": "financial", 
                "name": "Financial Performance Dashboard",
                "description": "Financial metrics with P&L, cash flow, and budget analysis",
                "primary_doctype": "GL Entry",
                "charts_count": 3
            },
            {
                "template_type": "inventory",
                "name": "Inventory Management Dashboard",
                "description": "Stock levels, movements, and inventory analysis", 
                "primary_doctype": "Stock Entry",
                "charts_count": 2
            },
            {
                "template_type": "hr",
                "name": "HR Analytics Dashboard",
                "description": "Employee metrics, attendance, and HR analytics",
                "primary_doctype": "Employee", 
                "charts_count": 2
            },
            {
                "template_type": "executive",
                "name": "Executive Summary Dashboard",
                "description": "High-level KPIs and executive metrics",
                "primary_doctype": "Sales Invoice",
                "charts_count": 2
            }
        ]
        return templates