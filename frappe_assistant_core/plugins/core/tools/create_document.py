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
        self.name = "create_document"
        self.description = "Create a new Frappe document (e.g., Customer, Sales Invoice, Item, etc.). Use this when users want to add new records to the system. Always check required fields for the doctype first."
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.inputSchema = {
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
            
            # Enhanced submit permission checking based on user role
            if submit:
                # Check if user has submit permission for this doctype
                if not frappe.has_permission(doctype, "submit"):
                    result = {
                        "success": False,
                        "error": f"Insufficient permissions to submit {doctype} documents. Current user: {frappe.session.user}"
                    }
                    audit_log_tool_access(frappe.session.user, self.name, arguments, result)
                    return result
                
                # Additional role-based restrictions
                if user_role in ["Assistant User", "Default"]:
                    # For basic users, check if they have explicit submit permission
                    # This allows proper role-based access while maintaining security
                    user_roles = frappe.get_roles(frappe.session.user)
                    meta = frappe.get_meta(doctype)
                    
                    # Check if any of the user's roles have submit permission
                    can_submit = False
                    for perm in meta.permissions:
                        if perm.role in user_roles and perm.submit:
                            can_submit = True
                            break
                    
                    if not can_submit:
                        result = {
                            "success": False,
                            "error": f"Your role does not have submit permission for {doctype} documents. Document will be saved as draft."
                        }
                        audit_log_tool_access(frappe.session.user, self.name, arguments, result)
                        # Don't return error, just disable submit
                        submit = False
            
            # Create document
            doc = frappe.new_doc(doctype)
            
            # Set field values
            for field, value in data.items():
                setattr(doc, field, value)
            
            # Save document
            doc.insert()
            
            # Initialize result with basic information
            result = {
                "success": True,
                "name": doc.name,
                "doctype": doctype,
                "docstatus": doc.docstatus,
                "owner": doc.owner,
                "creation": str(doc.creation),
                "submitted": False,
                "can_submit": False
            }
            
            # Submit if requested and allowed
            if submit and doc.docstatus == 0:
                try:
                    doc.submit()
                    result["submitted"] = True
                    result["docstatus"] = 1
                    result["message"] = f"{doctype} '{doc.name}' created and submitted successfully"
                except Exception as e:
                    result["message"] = f"{doctype} '{doc.name}' created as draft. Submit failed: {str(e)}"
                    result["submit_error"] = str(e)
            else:
                result["message"] = f"{doctype} '{doc.name}' created successfully as draft"
            
            # Check if user can submit this document later
            if doc.docstatus == 0:  # Only for draft documents
                try:
                    result["can_submit"] = frappe.has_permission(doctype, "submit", doc=doc.name)
                except Exception:
                    result["can_submit"] = False
            
            # Add workflow information if available
            if hasattr(doc, 'workflow_state') and doc.workflow_state:
                result["workflow_state"] = doc.workflow_state
            
            # Add useful next steps information
            if doc.docstatus == 0:
                result["next_steps"] = [
                    f"Document is in draft state",
                    f"You can update this document using document_update tool",
                    f"Submit permission: {'Available' if result['can_submit'] else 'Not available'}"
                ]
            else:
                result["next_steps"] = [
                    f"Document is submitted and cannot be modified",
                    f"Use document_get to view the submitted document"
                ]
            
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