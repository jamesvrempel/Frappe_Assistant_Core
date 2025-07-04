"""
Report List Tool for Core Plugin.
Lists available reports with basic information.
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class ReportList(BaseTool):
    """
    Tool for listing available reports.
    
    Provides capabilities for:
    - List all available reports
    - Filter by module or type
    - Get basic report information
    """
    
    def __init__(self):
        super().__init__()
        self.name = "report_list"
        self.description = "List all available reports in the system. Use when users want to see what reports are available to run."
        self.requires_permission = None  # Permission checked per report
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "module": {
                    "type": "string",
                    "description": "Filter by specific module (e.g., 'Accounts', 'Stock', 'HR')"
                },
                "report_type": {
                    "type": "string",
                    "enum": ["Query Report", "Script Report", "Report Builder"],
                    "description": "Filter by report type"
                },
                "custom_only": {
                    "type": "boolean",
                    "default": False,
                    "description": "Only show custom reports"
                },
                "limit": {
                    "type": "integer",
                    "default": 50,
                    "description": "Maximum number of reports to return"
                }
            },
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List available reports"""
        module = arguments.get("module")
        report_type = arguments.get("report_type")
        custom_only = arguments.get("custom_only", False)
        limit = arguments.get("limit", 50)
        
        try:
            # Build filters
            filters = {}
            
            if module:
                filters["module"] = module
            
            if report_type:
                filters["report_type"] = report_type
            
            if custom_only:
                filters["is_standard"] = "No"
            
            # Get reports
            reports = frappe.get_all(
                "Report",
                filters=filters,
                fields=[
                    "name", "report_name", "report_type", "module", "is_standard",
                    "disabled", "ref_doctype", "creation", "modified"
                ],
                limit=limit,
                order_by="name"
            )
            
            # Filter by permissions
            accessible_reports = []
            for report in reports:
                try:
                    # Check if user has permission to access this report
                    if frappe.has_permission("Report", "read", report):
                        # Also check if not disabled
                        if not report.disabled:
                            accessible_reports.append(report)
                except Exception:
                    # Skip if there's an error checking permissions
                    continue
            
            # Add summary statistics
            summary = {
                "total_found": len(reports),
                "accessible": len(accessible_reports),
                "query_reports": len([r for r in accessible_reports if r.report_type == "Query Report"]),
                "script_reports": len([r for r in accessible_reports if r.report_type == "Script Report"]),
                "report_builder": len([r for r in accessible_reports if r.report_type == "Report Builder"]),
                "custom_reports": len([r for r in accessible_reports if r.is_standard == "No"]),
                "standard_reports": len([r for r in accessible_reports if r.is_standard == "Yes"])
            }
            
            return {
                "success": True,
                "reports": accessible_reports,
                "summary": summary,
                "filters_applied": {
                    "module": module,
                    "report_type": report_type,
                    "custom_only": custom_only,
                    "limit": limit
                }
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Report List Error"),
                message=f"Error listing reports: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
report_list = ReportList