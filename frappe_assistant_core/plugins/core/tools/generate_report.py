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
Generate Report Tool for Core Plugin.
Execute Frappe reports for business data and analytics.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class GenerateReport(BaseTool):
    """
    Tool for executing Frappe reports.
    
    Provides capabilities for:
    - Query Report execution
    - Script Report execution  
    - Report Builder execution
    - Automatic filter handling
    """
    
    def __init__(self):
        super().__init__()
        self.name = "generate_report"
        self.description = "Execute a Frappe report to get business data and analytics"
        self.requires_permission = None  # Permission checked dynamically per report
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "report_name": {
                    "type": "string",
                    "description": "Exact name of the Frappe report to execute"
                },
                "filters": {
                    "type": "object",
                    "default": {},
                    "description": "Report-specific filters as key-value pairs"
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "csv", "excel"],
                    "default": "json",
                    "description": "Output format"
                }
            },
            "required": ["report_name"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute report generation"""
        try:
            # Import the report implementation
            from .report_tools import ReportTools
            
            # Execute report using existing implementation
            return ReportTools.execute_report(
                report_name=arguments.get("report_name"),
                filters=arguments.get("filters", {}),
                format=arguments.get("format", "json")
            )
            
        except Exception as e:
            frappe.log_error(
                title=_("Generate Report Error"),
                message=f"Error generating report: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
generate_report = GenerateReport