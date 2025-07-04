"""
Metadata DocType Fields Tool for Core Plugin.
Gets detailed field information for a specific DocType.
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class MetadataDoctypeFields(BaseTool):
    """
    Tool for getting detailed field information for a specific DocType.
    
    Provides capabilities for:
    - Detailed field metadata
    - Field validation rules
    - Field relationships and dependencies
    """
    
    def __init__(self):
        super().__init__()
        self.name = "metadata_doctype_fields"
        self.description = "Get detailed field information for a specific DocType including validation rules, options, and relationships. Use when users need to understand specific field properties."
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "The DocType name to get field information for (e.g., 'Customer', 'Sales Invoice', 'Item')"
                },
                "field_name": {
                    "type": "string",
                    "description": "Specific field name to get information for (optional)"
                },
                "field_type": {
                    "type": "string",
                    "description": "Filter by field type (e.g., 'Data', 'Link', 'Select')"
                },
                "required_only": {
                    "type": "boolean",
                    "default": False,
                    "description": "Only show required fields"
                },
                "include_hidden": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include hidden fields"
                }
            },
            "required": ["doctype"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get DocType field information"""
        doctype = arguments.get("doctype")
        field_name = arguments.get("field_name")
        field_type = arguments.get("field_type")
        required_only = arguments.get("required_only", False)
        include_hidden = arguments.get("include_hidden", False)
        
        # Check permission for DocType
        if not frappe.has_permission(doctype, "read"):
            return {
                "success": False,
                "error": f"Insufficient permissions to access {doctype} field information"
            }
        
        try:
            # Get DocType metadata
            meta = frappe.get_meta(doctype)
            
            # Filter fields based on criteria
            fields = []
            for field in meta.fields:
                # Apply filters
                if field_name and field.fieldname != field_name:
                    continue
                    
                if field_type and field.fieldtype != field_type:
                    continue
                    
                if required_only and not field.reqd:
                    continue
                    
                if not include_hidden and field.hidden:
                    continue
                
                # Build detailed field information
                field_info = {
                    "fieldname": field.fieldname,
                    "label": field.label,
                    "fieldtype": field.fieldtype,
                    "options": field.options,
                    "reqd": field.reqd,
                    "unique": field.unique,
                    "read_only": field.read_only,
                    "hidden": field.hidden,
                    "description": field.description,
                    "default": field.default,
                    "length": field.length,
                    "precision": field.precision,
                    "in_list_view": field.in_list_view,
                    "in_standard_filter": field.in_standard_filter,
                    "search_index": field.search_index,
                    "allow_bulk_edit": field.allow_bulk_edit,
                    "allow_in_quick_entry": field.allow_in_quick_entry,
                    "bold": field.bold,
                    "collapsible": field.collapsible,
                    "depends_on": field.depends_on,
                    "mandatory_depends_on": field.mandatory_depends_on,
                    "read_only_depends_on": field.read_only_depends_on,
                    "fetch_from": field.fetch_from,
                    "fetch_if_empty": field.fetch_if_empty,
                    "permlevel": field.permlevel,
                    "report_hide": field.report_hide,
                    "translatable": field.translatable,
                    "width": field.width
                }
                
                # Add field-type specific information
                if field.fieldtype == "Link":
                    field_info["link_doctype"] = field.options
                    field_info["ignore_user_permissions"] = field.ignore_user_permissions
                elif field.fieldtype == "Select":
                    field_info["select_options"] = field.options.split('\n') if field.options else []
                elif field.fieldtype in ["Int", "Float", "Currency"]:
                    field_info["non_negative"] = field.non_negative
                elif field.fieldtype == "Date":
                    field_info["ignore_user_permissions"] = field.ignore_user_permissions
                elif field.fieldtype == "Table":
                    field_info["child_doctype"] = field.options
                
                fields.append(field_info)
            
            # Summary statistics
            summary = {
                "total_fields": len(fields),
                "required_fields": len([f for f in fields if f["reqd"]]),
                "hidden_fields": len([f for f in fields if f["hidden"]]),
                "unique_fields": len([f for f in fields if f["unique"]]),
                "link_fields": len([f for f in fields if f["fieldtype"] == "Link"]),
                "select_fields": len([f for f in fields if f["fieldtype"] == "Select"]),
                "table_fields": len([f for f in fields if f["fieldtype"] == "Table"])
            }
            
            return {
                "success": True,
                "doctype": doctype,
                "fields": fields,
                "summary": summary,
                "filters_applied": {
                    "field_name": field_name,
                    "field_type": field_type,
                    "required_only": required_only,
                    "include_hidden": include_hidden
                }
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("DocType Fields Error"),
                message=f"Error getting field information for {doctype}: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "doctype": doctype
            }


# Make sure class name matches file name for discovery
metadata_doctype_fields = MetadataDoctypeFields