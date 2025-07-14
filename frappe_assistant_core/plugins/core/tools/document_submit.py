"""
Document Submit Tool for Core Plugin.
Submits draft documents after validation.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class DocumentSubmit(BaseTool):
    """
    Tool for submitting draft documents.
    
    Provides capabilities for:
    - Submitting draft documents
    - Validating submission permissions
    - Providing workflow guidance
    """
    
    def __init__(self):
        super().__init__()
        self.name = "document_submit"
        self.description = "Submit a draft document after validation. Only works with documents in draft state (docstatus=0). Use when users want to finalize a document."
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "The Frappe DocType name (e.g., 'Customer', 'Sales Invoice', 'Item')"
                },
                "name": {
                    "type": "string",
                    "description": "The document name/ID to submit (e.g., 'CUST-00001', 'SINV-00001')"
                }
            },
            "required": ["doctype", "name"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a draft document"""
        doctype = arguments.get("doctype")
        name = arguments.get("name")
        
        # Import security validation
        from frappe_assistant_core.core.security_config import validate_document_access, audit_log_tool_access
        
        # Validate document access with comprehensive permission checking
        validation_result = validate_document_access(
            user=frappe.session.user,
            doctype=doctype,
            name=name,
            perm_type="submit"
        )
        
        if not validation_result["success"]:
            audit_log_tool_access(frappe.session.user, self.name, arguments, validation_result)
            return validation_result
        
        user_role = validation_result["role"]
        
        try:
            # Check if document exists
            if not frappe.db.exists(doctype, name):
                result = {
                    "success": False,
                    "error": f"{doctype} '{name}' not found"
                }
                audit_log_tool_access(frappe.session.user, self.name, arguments, result)
                return result
            
            # Get document
            doc = frappe.get_doc(doctype, name)
            
            # Check document state
            current_docstatus = getattr(doc, 'docstatus', 0)
            current_workflow_state = getattr(doc, 'workflow_state', None)
            
            # Validate document is in draft state
            if current_docstatus != 0:
                state_description = {
                    1: "submitted",
                    2: "cancelled"
                }.get(current_docstatus, "unknown")
                
                result = {
                    "success": False,
                    "error": f"Cannot submit {state_description} document {doctype} '{name}'. Only draft documents can be submitted.",
                    "docstatus": current_docstatus,
                    "workflow_state": current_workflow_state,
                    "suggestion": f"Document is already {state_description}. Use document_get to view its current state."
                }
                audit_log_tool_access(frappe.session.user, self.name, arguments, result)
                return result
            
            # Check if DocType is submittable
            meta = frappe.get_meta(doctype)
            if not getattr(meta, 'is_submittable', False):
                result = {
                    "success": False,
                    "error": f"{doctype} is not a submittable DocType",
                    "suggestion": f"Only submittable DocTypes can be submitted. {doctype} doesn't support submission."
                }
                audit_log_tool_access(frappe.session.user, self.name, arguments, result)
                return result
            
            # Perform submission
            doc.submit()
            
            # Get updated document state
            doc.reload()
            updated_docstatus = getattr(doc, 'docstatus', 0)
            updated_workflow_state = getattr(doc, 'workflow_state', None)
            
            result = {
                "success": True,
                "name": doc.name,
                "doctype": doctype,
                "docstatus": updated_docstatus,
                "state_description": "Submitted" if updated_docstatus == 1 else "Unknown",
                "workflow_state": updated_workflow_state,
                "owner": doc.owner,
                "modified": str(doc.modified),
                "modified_by": doc.modified_by,
                "message": f"{doctype} '{doc.name}' submitted successfully"
            }
            
            # Add next steps information
            if updated_docstatus == 1:
                result["next_steps"] = [
                    f"Document is now submitted and read-only",
                    f"Use document_get to view the submitted document",
                    f"Submit permissions: {'Available' if frappe.has_permission(doctype, 'cancel') else 'Not available'} for cancellation"
                ]
                
                # Add workflow information
                if updated_workflow_state:
                    result["next_steps"].append(f"Current workflow state: {updated_workflow_state}")
            else:
                result["next_steps"] = [
                    f"Submission may have failed - document status: {updated_docstatus}",
                    f"Check document validation errors or permissions"
                ]
            
            # Log successful submission
            audit_log_tool_access(frappe.session.user, self.name, arguments, result)
            return result
            
        except Exception as e:
            frappe.log_error(
                title=_("Document Submit Error"),
                message=f"Error submitting {doctype} '{name}': {str(e)}"
            )
            
            result = {
                "success": False,
                "error": str(e),
                "doctype": doctype,
                "name": name,
                "suggestion": "Check if the document has all required fields filled and passes validation."
            }
            
            # Log failed submission
            audit_log_tool_access(frappe.session.user, self.name, arguments, result)
            return result


# Make sure class name matches file name for discovery
document_submit = DocumentSubmit