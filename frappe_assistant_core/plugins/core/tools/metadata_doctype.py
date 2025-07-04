"""
Metadata DocType Tool for Core Plugin.
Gets metadata information about a specific DocType.
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class MetadataDoctype(BaseTool):
    """
    Tool for getting metadata information about a specific DocType.
    
    Provides capabilities for:
    - DocType field information
    - Permissions and roles
    - DocType properties and settings
    """
    
    def __init__(self):
        super().__init__()
        self.name = "metadata_doctype"
        self.description = "Get detailed metadata information about a specific DocType including fields, permissions, and properties. Use when users need to understand the structure of a DocType."
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "The DocType name to get metadata for (e.g., 'Customer', 'Sales Invoice', 'Item')"
                },
                "include_fields": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to include detailed field information"
                },
                "include_permissions": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to include permission information"
                }
            },
            "required": ["doctype"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get DocType metadata"""
        doctype = arguments.get("doctype")
        include_fields = arguments.get("include_fields", True)
        include_permissions = arguments.get("include_permissions", True)
        
        # Check permission for DocType
        if not frappe.has_permission(doctype, "read"):
            return {
                "success": False,
                "error": f"Insufficient permissions to access {doctype} metadata"
            }
        
        try:
            # Get DocType metadata
            meta = frappe.get_meta(doctype)
            
            # Build metadata response - handle missing attributes gracefully
            metadata = {
                "doctype": doctype,
                "title": getattr(meta, 'title', doctype),
                "description": getattr(meta, 'description', ''),
                "module": getattr(meta, 'module', ''),
                "is_submittable": getattr(meta, 'is_submittable', False),
                "is_child_table": getattr(meta, 'is_child_table', False),
                "is_custom": getattr(meta, 'custom', False),
                "is_table": getattr(meta, 'istable', False),
                "autoname": getattr(meta, 'autoname', ''),
                "naming_rule": getattr(meta, 'naming_rule', ''),
                "has_web_view": getattr(meta, 'has_web_view', False),
                "allow_copy": getattr(meta, 'allow_copy', False),
                "allow_rename": getattr(meta, 'allow_rename', False),
                "allow_import": getattr(meta, 'allow_import', False),
                "track_changes": getattr(meta, 'track_changes', False),
                "search_fields": getattr(meta, 'search_fields', ''),
                "title_field": getattr(meta, 'title_field', ''),
                "sort_field": getattr(meta, 'sort_field', 'creation'),
                "sort_order": getattr(meta, 'sort_order', 'desc'),
                "default_print_format": getattr(meta, 'default_print_format', '')
            }
            
            # Add field information
            if include_fields:
                fields = []
                for field in meta.fields:
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
                        "length": field.length
                    }
                    fields.append(field_info)
                
                metadata["fields"] = fields
                metadata["field_count"] = len(fields)
                
                # Add link fields information
                link_fields = []
                for field in meta.get_link_fields():
                    link_fields.append({
                        "fieldname": field.fieldname,
                        "label": field.label,
                        "options": field.options
                    })
                metadata["link_fields"] = link_fields
            
            # Add permission information
            if include_permissions:
                permissions = []
                for perm in meta.permissions:
                    perm_info = {
                        "role": perm.role,
                        "read": perm.read,
                        "write": perm.write,
                        "create": perm.create,
                        "delete": perm.delete,
                        "submit": perm.submit,
                        "cancel": perm.cancel,
                        "amend": perm.amend,
                        "report": perm.report,
                        "export": perm.export,
                        "import": perm.import_,
                        "share": perm.share,
                        "print": perm.print_,
                        "email": perm.email
                    }
                    permissions.append(perm_info)
                
                metadata["permissions"] = permissions
            
            return {
                "success": True,
                "metadata": metadata
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("DocType Metadata Error"),
                message=f"Error getting metadata for {doctype}: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "doctype": doctype
            }


# Make sure class name matches file name for discovery
metadata_doctype = MetadataDoctype