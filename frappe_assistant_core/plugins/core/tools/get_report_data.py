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
Report Details Tool for Core Plugin.
Gets detailed information about a specific report.
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class ReportDetails(BaseTool):
    """
    Tool for getting detailed information about a specific report.
    
    Provides capabilities for:
    - Report metadata and configuration
    - Available filters and parameters
    - Column information
    """
    
    def __init__(self):
        super().__init__()
        self.name = "get_report_data"
        self.description = "Get detailed information about a specific report including filters, columns, and configuration. Use when users need to understand a report's structure before running it."
        self.requires_permission = None  # Permission checked per report
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "report_name": {
                    "type": "string",
                    "description": "The name of the report to get details for"
                },
                "include_filters": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to include filter information"
                },
                "include_columns": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to include column information"
                }
            },
            "required": ["report_name"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed report information"""
        report_name = arguments.get("report_name")
        include_filters = arguments.get("include_filters", True)
        include_columns = arguments.get("include_columns", True)
        
        try:
            # Check if report exists
            if not frappe.db.exists("Report", report_name):
                return {
                    "success": False,
                    "error": f"Report '{report_name}' not found"
                }
            
            # Get report document
            report = frappe.get_doc("Report", report_name)
            
            # Check permission
            if not frappe.has_permission("Report", "read", report):
                return {
                    "success": False,
                    "error": f"Insufficient permissions to access report '{report_name}'"
                }
            
            # Build report details
            details = {
                "name": getattr(report, 'name', ''),
                "report_name": getattr(report, 'report_name', ''),
                "report_type": getattr(report, 'report_type', ''),
                "module": getattr(report, 'module', ''),
                "is_standard": getattr(report, 'is_standard', False),
                "disabled": getattr(report, 'disabled', False),
                "description": getattr(report, 'description', ''),
                "ref_doctype": getattr(report, 'ref_doctype', ''),
                "creation": getattr(report, 'creation', None),
                "modified": getattr(report, 'modified', None),
                "owner": getattr(report, 'owner', ''),
                "modified_by": getattr(report, 'modified_by', '')
            }
            
            # Add type-specific information
            report_type = getattr(report, 'report_type', '')
            if report_type == "Query Report":
                details["query"] = getattr(report, 'query', '')
                details["prepared_report"] = getattr(report, 'prepared_report', False)
                details["disable_prepared_report"] = getattr(report, 'disable_prepared_report', False)
            elif report_type == "Script Report":
                details["javascript"] = getattr(report, 'javascript', '')
                details["json"] = getattr(report, 'json', '')
                
            # Add filters information
            if include_filters:
                filters = []
                
                # For Query Reports, try to extract filters from JSON
                if report_type == "Query Report" and getattr(report, 'json', ''):
                    try:
                        import json
                        report_config = json.loads(report.json)
                        if "filters" in report_config:
                            filters = report_config["filters"]
                    except Exception:
                        pass
                
                # For Script Reports, try to get filters from module
                elif report_type == "Script Report":
                    try:
                        module_name = report.module
                        report_module = frappe.get_module(f"{module_name}.report.{report.name.lower().replace(' ', '_')}")
                        
                        if hasattr(report_module, 'get_filters'):
                            filters = report_module.get_filters()
                        elif hasattr(report_module, 'filters'):
                            filters = report_module.filters
                    except Exception:
                        pass
                
                details["filters"] = filters
            
            # Add columns information
            if include_columns:
                columns = []
                
                # For Query Reports, try to get columns from first execution
                if report.report_type == "Query Report" and report.query:
                    try:
                        # Execute query with limit 1 to get column structure
                        query = report.query
                        if "limit" not in query.lower():
                            query = query.rstrip(';') + " LIMIT 1"
                        
                        result = frappe.db.sql(query, as_dict=True)
                        if result:
                            columns = [{"fieldname": key, "label": key.replace("_", " ").title()} 
                                     for key in result[0].keys()]
                    except Exception:
                        pass
                
                # For Script Reports, try to get columns from module
                elif report.report_type == "Script Report":
                    try:
                        module_name = report.module
                        report_module = frappe.get_module(f"{module_name}.report.{report.name.lower().replace(' ', '_')}")
                        
                        if hasattr(report_module, 'get_columns'):
                            columns = report_module.get_columns()
                        elif hasattr(report_module, 'columns'):
                            columns = report_module.columns
                    except Exception:
                        pass
                
                details["columns"] = columns
            
            return {
                "success": True,
                "report_details": details
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Report Details Error"),
                message=f"Error getting details for report '{report_name}': {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "report_name": report_name
            }


# Make sure class name matches file name for discovery
report_details = ReportDetails