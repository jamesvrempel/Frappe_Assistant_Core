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
        self.description = "🏆 PROFESSIONAL BUSINESS REPORTS - Your FIRST choice for sales analysis, financial reporting, and business intelligence! 🎯 **USE THIS FOR**: Sales analysis, profit reports, customer insights, inventory tracking, financial statements ⚡ **INSTANT ACCESS** to 183+ pre-built business reports including: Sales Analytics (revenue, trends, territory performance), Profit & Loss Statement, Accounts Receivable Summary, Item-wise Sales History, Territory-wise Sales ✅ **ALWAYS TRY THIS FIRST** before using analysis tools - these reports are pre-optimized for business users, professionally formatted, ready for management presentation, and include proper calculations and totals. Use 'report_list' to discover available reports, then execute with filters. IMPORTANT: Many reports require mandatory filters - use report_requirements tool first if you get errors."
        self.requires_permission = None  # Permission checked dynamically per report
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "report_name": {
                    "type": "string", 
                    "description": "Exact name of the Frappe report to execute (e.g., 'Accounts Receivable Summary', 'Sales Analytics', 'Stock Balance'). Use report_list to find available reports."
                },
                "filters": {
                    "type": "object", 
                    "default": {}, 
                    "description": "Report-specific filters as key-value pairs. IMPORTANT: Many reports have mandatory filters like 'doc_type', 'tree_type', etc. Common optional filters: {'company': 'Your Company'}, {'from_date': '2024-01-01', 'to_date': '2024-12-31'}, {'customer': 'Customer Name'}. For Sales Analytics: requires 'doc_type' (Sales Invoice/Sales Order/Quotation) and 'tree_type' (Customer/Item/Territory). Use report_requirements tool to discover required filters if report fails."
                },
                "format": {
                    "type": "string", 
                    "enum": ["json", "csv", "excel"], 
                    "default": "json",
                    "description": "Output format. Use 'json' for data analysis, 'csv' for exports, 'excel' for spreadsheet files."
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