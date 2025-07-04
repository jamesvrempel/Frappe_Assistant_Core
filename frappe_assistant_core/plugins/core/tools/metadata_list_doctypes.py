"""
Metadata List DocTypes Tool for Core Plugin.
Lists all available DocTypes with basic metadata.
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class MetadataListDoctypes(BaseTool):
    """
    Tool for listing all available DocTypes with basic metadata.
    
    Provides capabilities for:
    - List all DocTypes
    - Filter by module or custom
    - Get basic DocType information
    """
    
    def __init__(self):
        super().__init__()
        self.name = "metadata_list_doctypes"
        self.description = "List all available DocTypes in the system with basic metadata. Use when users need to know what document types are available."
        self.requires_permission = None  # DocType list is generally accessible
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "module": {
                    "type": "string",
                    "description": "Filter by specific module (e.g., 'Core', 'Accounts', 'Stock')"
                },
                "custom_only": {
                    "type": "boolean",
                    "default": False,
                    "description": "Only show custom DocTypes"
                },
                "standard_only": {
                    "type": "boolean",
                    "default": False,
                    "description": "Only show standard (non-custom) DocTypes"
                },
                "include_child_tables": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include child table DocTypes"
                },
                "limit": {
                    "type": "integer",
                    "default": 50,
                    "description": "Maximum number of DocTypes to return"
                }
            },
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List DocTypes with metadata"""
        module = arguments.get("module")
        custom_only = arguments.get("custom_only", False)
        standard_only = arguments.get("standard_only", False)
        include_child_tables = arguments.get("include_child_tables", False)
        limit = arguments.get("limit", 50)
        
        try:
            # Build filters
            filters = {}
            
            if module:
                filters["module"] = module
            
            if custom_only:
                filters["custom"] = 1
            elif standard_only:
                filters["custom"] = 0
            
            if not include_child_tables:
                filters["istable"] = 0
            
            # Get DocTypes - only use fields that definitely exist
            doctypes = frappe.get_all(
                "DocType",
                filters=filters,
                fields=[
                    "name", "module", "custom", "istable", "is_submittable",
                    "has_web_view", "allow_copy", "allow_rename",
                    "track_changes", "autoname", "naming_rule", "creation", "modified"
                ],
                limit=limit,
                order_by="name"
            )
            
            # Filter by permissions
            accessible_doctypes = []
            for doctype in doctypes:
                try:
                    # Check if user has any permission on this DocType
                    if frappe.has_permission(doctype.name, "read"):
                        accessible_doctypes.append(doctype)
                except Exception:
                    # Skip if there's an error checking permissions
                    continue
            
            # Add summary statistics
            summary = {
                "total_found": len(doctypes),
                "accessible": len(accessible_doctypes),
                "custom": len([d for d in accessible_doctypes if d.custom]),
                "standard": len([d for d in accessible_doctypes if not d.custom]),
                "submittable": len([d for d in accessible_doctypes if d.is_submittable]),
                "child_tables": len([d for d in accessible_doctypes if d.istable])
            }
            
            return {
                "success": True,
                "doctypes": accessible_doctypes,
                "summary": summary,
                "filters_applied": {
                    "module": module,
                    "custom_only": custom_only,
                    "standard_only": standard_only,
                    "include_child_tables": include_child_tables,
                    "limit": limit
                }
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("DocType List Error"),
                message=f"Error listing DocTypes: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
metadata_list_doctypes = MetadataListDoctypes