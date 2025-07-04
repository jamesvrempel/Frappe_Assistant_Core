"""
Report Execute Tool for Core Plugin.
Executes reports and returns results.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class ReportExecute(BaseTool):
    """
    Tool for executing reports and returning results.
    
    Provides capabilities for:
    - Execute Query Reports
    - Execute Script Reports
    - Apply filters and parameters
    """
    
    def __init__(self):
        super().__init__()
        self.name = "report_execute"
        self.description = "Execute a report and return the results. Use when users want to run reports and get data output."
        self.requires_permission = None  # Permission checked dynamically per report
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "report_name": {
                    "type": "string",
                    "description": "The name of the report to execute"
                },
                "filters": {
                    "type": "object",
                    "description": "Report filters as key-value pairs"
                },
                "limit": {
                    "type": "integer",
                    "default": 100,
                    "description": "Maximum number of rows to return"
                }
            },
            "required": ["report_name"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a report"""
        report_name = arguments.get("report_name")
        filters = arguments.get("filters", {})
        limit = arguments.get("limit", 100)
        
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
                    "error": f"Insufficient permissions to execute report '{report_name}'"
                }
            
            # Execute report based on type
            if report.report_type == "Query Report":
                # Execute query report
                result = self._execute_query_report(report, filters, limit)
            elif report.report_type == "Script Report":
                # Execute script report  
                result = self._execute_script_report(report, filters, limit)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported report type: {report.report_type}"
                }
            
            return {
                "success": True,
                "report_name": report_name,
                "report_type": report.report_type,
                "data": result.get("data", []),
                "columns": result.get("columns", []),
                "filters_applied": filters,
                "count": len(result.get("data", []))
            }
                
        except Exception as e:
            frappe.log_error(
                title=_("Report Execute Error"),
                message=f"Error executing report '{report_name}': {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "report_name": report_name
            }
    
    def _execute_query_report(self, report, filters, limit):
        """Execute a query report"""
        try:
            # Use Frappe's built-in query report execution
            from frappe.desk.query_report import run
            
            result = run(
                report_name=report.name,
                filters=filters,
                ignore_prepared_report=1
            )
            
            # Handle different result formats
            if isinstance(result, dict):
                return {
                    "data": result.get("result", [])[:limit],
                    "columns": result.get("columns", [])
                }
            else:
                # If result is a list, assume it's data
                return {
                    "data": (result or [])[:limit],
                    "columns": []
                }
        except Exception as e:
            return {
                "data": [],
                "columns": [],
                "error": str(e)
            }
    
    def _execute_script_report(self, report, filters, limit):
        """Execute a script report"""
        try:
            # Use Frappe's built-in script report execution
            from frappe.desk.query_report import run
            
            result = run(
                report_name=report.name,
                filters=filters,
                ignore_prepared_report=1
            )
            
            # Handle different result formats
            if isinstance(result, dict):
                return {
                    "data": result.get("result", [])[:limit],
                    "columns": result.get("columns", [])
                }
            else:
                # If result is a list, assume it's data
                return {
                    "data": (result or [])[:limit],
                    "columns": []
                }
        except Exception as e:
            return {
                "data": [],
                "columns": [],
                "error": str(e)
            }


# Make sure class name matches file name for discovery
report_execute = ReportExecute