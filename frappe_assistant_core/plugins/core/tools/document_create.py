"""
Document Creation Tool for Core Plugin.
Creates new Frappe documents with validation and permissions.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class DocumentCreate(BaseTool):
    """
    Tool for creating new Frappe documents.
    
    Provides capabilities for:
    - Creating documents with field validation
    - Checking required fields
    - Handling permissions
    - Optional document submission
    """
    
    def __init__(self):
        super().__init__()
        self.name = "document_create"
        self.description = "Create a new Frappe document (e.g., Customer, Sales Invoice, Item, etc.). Use this when users want to add new records to the system. Always check required fields for the doctype first."
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "The Frappe DocType name (e.g., 'Customer', 'Sales Invoice', 'Item', 'User'). Must match exact DocType name in system."
                },
                "data": {
                    "type": "object",
                    "description": "Document field data as key-value pairs. Include all required fields for the doctype. Example: {'customer_name': 'ABC Corp', 'customer_type': 'Company'}"
                },
                "submit": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to submit the document after creation (for submittable doctypes like Sales Invoice). Use true only when explicitly requested."
                }
            },
            "required": ["doctype", "data"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document"""
        doctype = arguments.get("doctype")
        data = arguments.get("data", {})
        submit = arguments.get("submit", False)
        
        # Import security validation
        from frappe_assistant_core.core.security_config import validate_document_access, filter_sensitive_fields, audit_log_tool_access
        
        # Validate document access with comprehensive permission checking
        validation_result = validate_document_access(
            user=frappe.session.user,
            doctype=doctype,
            name=None,  # No specific document for create operation
            perm_type="create"
        )
        
        if not validation_result["success"]:
            audit_log_tool_access(frappe.session.user, self.name, arguments, validation_result)
            return validation_result
        
        user_role = validation_result["role"]
        
        try:
            # Filter out sensitive fields that user shouldn't be able to set
            from frappe_assistant_core.core.security_config import SENSITIVE_FIELDS, ADMIN_ONLY_FIELDS
            
            # Get restricted fields for this role and doctype
            restricted_fields = set()
            restricted_fields.update(SENSITIVE_FIELDS.get("all_doctypes", []))
            restricted_fields.update(SENSITIVE_FIELDS.get(doctype, []))
            
            if user_role == "Assistant User":
                restricted_fields.update(ADMIN_ONLY_FIELDS.get("all_doctypes", []))
                doctype_admin_fields = ADMIN_ONLY_FIELDS.get(doctype, [])
                if doctype_admin_fields != "*":
                    restricted_fields.update(doctype_admin_fields)
            
            # Check for attempts to set restricted fields
            restricted_fields_attempted = [field for field in data.keys() if field in restricted_fields]
            if restricted_fields_attempted:
                result = {
                    "success": False,
                    "error": f"Cannot set restricted fields: {', '.join(restricted_fields_attempted)}. These fields require higher privileges."
                }
                audit_log_tool_access(frappe.session.user, self.name, arguments, result)
                return result
            
            # Check submit permission for Assistant Users
            if submit and user_role == "Assistant User":
                # Assistant Users typically shouldn't be able to submit documents directly
                if not frappe.has_permission(doctype, "submit"):
                    result = {
                        "success": False,
                        "error": f"Insufficient permissions to submit {doctype} documents"
                    }
                    audit_log_tool_access(frappe.session.user, self.name, arguments, result)
                    return result
            
            # Create document
            doc = frappe.new_doc(doctype)
            
            # Set field values
            for field, value in data.items():
                setattr(doc, field, value)
            
            # Save document
            doc.insert()
            
            # Submit if requested
            if submit and doc.docstatus == 0:
                doc.submit()
            
            result = {
                "success": True,
                "name": doc.name,
                "doctype": doctype,
                "message": f"{doctype} '{doc.name}' created successfully",
                "submitted": doc.docstatus == 1 if submit else False
            }
            
            # Log successful creation
            audit_log_tool_access(frappe.session.user, self.name, arguments, result)
            return result
            
        except Exception as e:
            frappe.log_error(
                title=_("Document Creation Error"),
                message=f"Error creating {doctype}: {str(e)}"
            )
            
            result = {
                "success": False,
                "error": str(e),
                "doctype": doctype
            }
            
            # Log failed creation
            audit_log_tool_access(frappe.session.user, self.name, arguments, result)
            return result


# Make sure class name matches file name for discovery
document_create = DocumentCreate