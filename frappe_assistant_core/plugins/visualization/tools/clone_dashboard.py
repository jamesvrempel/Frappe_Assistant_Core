"""
Clone Dashboard Tool - Clone existing dashboard with optional modifications

Duplicate an existing dashboard with optional modifications.
"""

import frappe
from frappe import _
import json
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class CloneDashboard(BaseTool):
    """Clone existing dashboard with optional modifications"""
    
    def __init__(self):
        super().__init__()
        self.name = "clone_dashboard"
        self.description = "Duplicate an existing dashboard with optional modifications"
        self.requires_permission = None
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "source_dashboard": {
                    "type": "string",
                    "description": "Name/ID of dashboard to clone"
                },
                "new_dashboard_name": {
                    "type": "string",
                    "description": "Name for the cloned dashboard"
                },
                "copy_charts": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to copy all charts from source dashboard"
                },
                "copy_permissions": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to copy sharing permissions"
                },
                "modify_filters": {
                    "type": "object",
                    "description": "New filters to apply to cloned dashboard"
                }
            },
            "required": ["source_dashboard", "new_dashboard_name"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Clone dashboard"""
        try:
            source_dashboard = arguments.get("source_dashboard")
            new_dashboard_name = arguments.get("new_dashboard_name")
            copy_charts = arguments.get("copy_charts", True)
            copy_permissions = arguments.get("copy_permissions", False)
            modify_filters = arguments.get("modify_filters", {})
            
            # Check if source dashboard exists and user has access
            if not frappe.has_permission("Dashboard", "read", source_dashboard):
                return {
                    "success": False,
                    "error": f"Dashboard '{source_dashboard}' not found or access denied"
                }
            
            # Get source dashboard
            source_doc = frappe.get_doc("Dashboard", source_dashboard)
            
            # Create new dashboard
            new_dashboard = frappe.get_doc({
                "doctype": "Dashboard",
                "dashboard_name": new_dashboard_name,
                "module": source_doc.module,
                "is_standard": 0,
                "charts": []
            })
            new_dashboard.insert()
            
            cloned_charts = []
            
            # Clone charts if requested
            if copy_charts and hasattr(source_doc, 'charts') and source_doc.charts:
                for chart_link in source_doc.charts:
                    try:
                        # Get original chart
                        original_chart = frappe.get_doc("Dashboard Chart", chart_link.chart)
                        
                        # Create new chart name
                        new_chart_name = f"{original_chart.chart_name} - Cloned"
                        
                        # Clone chart
                        new_chart = frappe.get_doc({
                            "doctype": "Dashboard Chart",
                            "chart_name": new_chart_name,
                            "chart_type": original_chart.chart_type,
                            "document_type": original_chart.document_type,
                            "based_on": original_chart.based_on,
                            "value_based_on": original_chart.value_based_on,
                            "type": original_chart.type,
                            "timeseries": original_chart.get("timeseries", 0),
                            "filters_json": self._modify_chart_filters(
                                original_chart.get("filters_json", "{}"), 
                                modify_filters
                            )
                        })
                        new_chart.insert()
                        
                        # Link to new dashboard
                        new_dashboard.append("charts", {
                            "chart": new_chart.name,
                            "width": chart_link.get("width", "Half")
                        })
                        
                        cloned_charts.append(new_chart.name)
                        
                    except Exception as e:
                        frappe.logger("clone_dashboard").error(f"Failed to clone chart {chart_link.chart}: {str(e)}")
                        continue
                
                # Save dashboard with charts
                if cloned_charts:
                    new_dashboard.save()
            
            # Copy permissions if requested
            if copy_permissions:
                self._copy_dashboard_permissions(source_dashboard, new_dashboard.name)
            
            return {
                "success": True,
                "source_dashboard": source_dashboard,
                "new_dashboard_name": new_dashboard_name,
                "new_dashboard_id": new_dashboard.name,
                "dashboard_url": f"/app/dashboard/{new_dashboard.name}",
                "charts_cloned": len(cloned_charts),
                "cloned_charts": cloned_charts,
                "permissions_copied": copy_permissions
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _modify_chart_filters(self, original_filters_json: str, modify_filters: Dict) -> str:
        """Modify chart filters with new values"""
        try:
            original_filters = json.loads(original_filters_json or "{}")
            
            # Update filters
            updated_filters = {**original_filters, **modify_filters}
            
            return json.dumps(updated_filters)
            
        except Exception:
            return original_filters_json
    
    def _copy_dashboard_permissions(self, source_dashboard: str, new_dashboard: str):
        """Copy sharing permissions from source to new dashboard"""
        try:
            # Get all shares for source dashboard
            shares = frappe.get_all("DocShare",
                filters={"share_name": source_dashboard, "share_doctype": "Dashboard"},
                fields=["user", "read", "write", "share", "everyone"]
            )
            
            # Copy shares to new dashboard
            for share in shares:
                frappe.share.add(
                    "Dashboard", 
                    new_dashboard, 
                    share.user,
                    read=share.read,
                    write=share.write,
                    share=share.share
                )
                
        except Exception as e:
            frappe.logger("clone_dashboard").error(f"Failed to copy permissions: {str(e)}")