

import frappe
import json
from typing import Dict, Any, List
from frappe import _

class ReportTools:
    """assistant tools for Frappe report operations"""
    
    @staticmethod
    def get_tools() -> List[Dict]:
        """Return list of report-related assistant tools"""
        return [
            {
                "name": "report_execute",
                "description": "Execute a Frappe report to get business data and analytics. Use this for financial reports, sales analysis, inventory reports, etc. Always check available reports first using report_list if unsure of report names.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "report_name": {
                            "type": "string", 
                            "description": "Exact name of the Frappe report to execute (e.g., 'Accounts Receivable Summary', 'Sales Analytics', 'Stock Balance'). Use report_list to find available reports."
                        },
                        "filters": {
                            "type": "object", 
                            "default": {}, 
                            "description": "Report-specific filters as key-value pairs. Common filters: {'company': 'Your Company'}, {'from_date': '2024-01-01', 'to_date': '2024-12-31'}, {'customer': 'Customer Name'}. Use empty {} for no filters."
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
            },
            {
                "name": "report_list",
                "description": "Discover available Frappe reports for data analysis and business intelligence. Use this to find reports when users ask for financial data, sales analysis, inventory reports, etc. Essential for report discovery.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "module": {
                            "type": "string", 
                            "description": "Filter by Frappe module (e.g., 'Accounts', 'Selling', 'Stock', 'HR', 'CRM'). Leave empty to see all modules."
                        },
                        "report_type": {
                            "type": "string", 
                            "enum": ["Report Builder", "Query Report", "Script Report"], 
                            "description": "Filter by report type. Script Reports are usually the most powerful for analytics. Leave empty to see all types."
                        }
                    }
                }
            },
            {
                "name": "report_columns",
                "description": "Get detailed column information and structure for a specific report. Use this to understand what data fields are available in a report before executing it, especially for data analysis and visualization.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "report_name": {
                            "type": "string", 
                            "description": "Exact name of the Frappe report to analyze (e.g., 'Sales Analytics', 'Accounts Receivable Summary'). This helps understand available fields for filtering and visualization."
                        }
                    },
                    "required": ["report_name"]
                }
            }
        ]
    
    @staticmethod
    def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a report tool with given arguments"""
        if tool_name == "report_execute":
            return ReportTools.execute_report(**arguments)
        elif tool_name == "report_list":
            return ReportTools.list_reports(**arguments)
        elif tool_name == "report_columns":
            return ReportTools.get_report_columns(**arguments)
        else:
            raise Exception(f"Unknown report tool: {tool_name}")
    
    @staticmethod
    def execute_report(report_name: str, filters: Dict[str, Any] = None, format: str = "json") -> Dict[str, Any]:
        """Execute a Frappe report"""
        try:
            # Check if report exists
            if not frappe.db.exists("Report", report_name):
                return {"success": False, "error": f"Report '{report_name}' not found"}
            
            # Check permissions
            if not frappe.has_permission("Report", "read", report_name):
                return {"success": False, "error": f"No permission to access report '{report_name}'"}
            
            # Get report document
            report_doc = frappe.get_doc("Report", report_name)
            
            # Execute report based on type
            if report_doc.report_type == "Query Report":
                result = ReportTools._execute_query_report(report_doc, filters or {})
            elif report_doc.report_type == "Script Report":
                result = ReportTools._execute_script_report(report_doc, filters or {})
            elif report_doc.report_type == "Report Builder":
                result = ReportTools._execute_report_builder(report_doc, filters or {})
            else:
                return {"success": False, "error": f"Unsupported report type: {report_doc.report_type}"}
            
            # Add debug information for troubleshooting
            data = result.get("result", [])
            debug_info = {
                "success": True,
                "report_name": report_name,
                "report_type": report_doc.report_type,
                "data": data,
                "columns": result.get("columns", []),
                "message": result.get("message"),
                "filters_applied": filters or {},
                "raw_result_keys": list(result.keys()) if result else [],
                "data_count": len(data) if data else 0,
                "result_type": type(result).__name__ if result else "None"
            }
            
            # Add debug info if no data found
            if not data or len(data) == 0:
                debug_info["debug_info"] = {
                    "filters_used": filters,
                    "result_structure": result,
                    "error_from_result": result.get("error") if result else None
                }
            
            return debug_info
            
        except Exception as e:
            frappe.log_error(f"assistant Execute Report Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def list_reports(module: str = None, report_type: str = None) -> Dict[str, Any]:
        """Get list of available reports"""
        try:
            filters = {}
            if module:
                filters["module"] = module
            if report_type:
                filters["report_type"] = report_type
            
            reports = frappe.get_all(
                "Report",
                filters=filters,
                fields=["name", "report_name", "report_type", "module", "is_standard", "disabled"],
                order_by="report_name"
            )
            
            # Filter by permissions
            accessible_reports = []
            for report in reports:
                if frappe.has_permission("Report", "read", report.name):
                    accessible_reports.append(report)
            
            return {
                "success": True,
                "reports": accessible_reports,
                "count": len(accessible_reports),
                "filters_applied": {"module": module, "report_type": report_type}
            }
            
        except Exception as e:
            frappe.log_error(f"assistant List Reports Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_report_columns(report_name: str) -> Dict[str, Any]:
        """Get column information for a report"""
        try:
            if not frappe.db.exists("Report", report_name):
                return {"success": False, "error": f"Report '{report_name}' not found"}
            
            if not frappe.has_permission("Report", "read", report_name):
                return {"success": False, "error": f"No permission to access report '{report_name}'"}
            
            report_doc = frappe.get_doc("Report", report_name)
            columns = []
            
            if report_doc.report_type == "Query Report":
                # Try to get columns from query execution with minimal filters
                try:
                    # Try with empty filters first
                    result = ReportTools._execute_query_report(report_doc, {}, get_columns_only=True)
                    columns = result.get("columns", [])
                except Exception as e:
                    # If that fails, try with default company
                    try:
                        default_company = frappe.db.get_single_value("Global Defaults", "default_company")
                        if default_company:
                            result = ReportTools._execute_query_report(report_doc, {"company": default_company}, get_columns_only=True)
                            columns = result.get("columns", [])
                    except Exception:
                        frappe.log_error(f"Error getting columns from query report: {str(e)}")
                        # Return basic info if column extraction fails
                        columns = [{"label": "Data not available - requires filters", "fieldname": "info", "fieldtype": "Data"}]
            elif report_doc.report_type == "Report Builder":
                # Get columns from report builder configuration
                for col in report_doc.columns:
                    columns.append({
                        "fieldname": col.fieldname,
                        "label": col.label,
                        "fieldtype": col.fieldtype,
                        "width": col.width
                    })
            
            return {
                "success": True,
                "report_name": report_name,
                "report_type": report_doc.report_type,
                "columns": columns
            }
            
        except Exception as e:
            frappe.log_error(f"assistant Get Report Columns Error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def _execute_query_report(report_doc, filters, get_columns_only=False):
        """Execute a Query Report"""
        from frappe.desk.query_report import run
        
        try:
            # Add default filters for common requirements
            if not filters:
                filters = {}
            
            # Add company filter if required and not provided
            if "company" not in filters and frappe.db.exists("Company"):
                default_company = frappe.db.get_single_value("Global Defaults", "default_company")
                if default_company:
                    filters["company"] = default_company
            
            return run(
                report_name=report_doc.name,
                filters=filters,
                user=frappe.session.user,
                is_tree=report_doc.is_tree,
                parent_field=report_doc.parent_field
            )
        except Exception as e:
            # If execution fails, try to get just column info
            if "company" in str(e).lower() and "required" in str(e).lower():
                return {
                    "result": [],
                    "columns": [],
                    "message": f"Report requires filters: {str(e)}",
                    "error": "missing_required_filters"
                }
            raise e
    
    @staticmethod
    def _execute_script_report(report_doc, filters):
        """Execute a Script Report"""
        from frappe.desk.query_report import run
        
        try:
            # Ensure filters is a proper dict
            if not isinstance(filters, dict):
                filters = {}
            
            # For Accounts Receivable Summary, ensure company is set
            if report_doc.name == "Accounts Receivable Summary" and not filters.get("company"):
                default_company = frappe.db.get_single_value("Global Defaults", "default_company")
                if default_company:
                    filters["company"] = default_company
            
            return run(
                report_name=report_doc.name,
                filters=filters,
                user=frappe.session.user
            )
            
        except Exception as e:
            frappe.log_error(f"Script report execution error for {report_doc.name}: {str(e)}")
            return {
                "result": [],
                "columns": [],
                "message": f"Script report execution failed: {str(e)}",
                "error": str(e)
            }
    
    @staticmethod
    def _execute_report_builder(report_doc, filters):
        """Execute a Report Builder report"""
        from frappe.desk.reportview import execute
        
        return execute(
            doctype=report_doc.ref_doctype,
            filters=filters,
            fields=[col.fieldname for col in report_doc.columns],
            order_by=report_doc.sort_by,
            limit_page_length=1000
        )