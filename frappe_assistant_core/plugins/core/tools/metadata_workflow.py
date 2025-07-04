"""
Metadata Workflow Tool for Core Plugin.
Retrieves workflow information for Frappe DocTypes.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class MetadataWorkflow(BaseTool):
    """
    Tool for retrieving DocType workflow information.
    
    Provides capabilities for:
    - Checking if a DocType has a workflow
    - Getting workflow states and transitions
    - Getting workflow approval rules
    """
    
    def __init__(self):
        super().__init__()
        self.name = "metadata_workflow"
        self.description = "Get workflow information for a DocType including states, transitions, and approval rules. Shows if a DocType has workflow enabled and what actions are available."
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "The Frappe DocType name to get workflow information for (e.g., 'Sales Invoice', 'Purchase Order')"
                }
            },
            "required": ["doctype"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get DocType workflow information"""
        doctype = arguments.get("doctype")
        
        # Check if DocType exists
        if not frappe.db.exists("DocType", doctype):
            return {
                "success": False,
                "error": f"DocType '{doctype}' not found"
            }
        
        try:
            # Check if workflow exists for this DocType
            workflow_name = frappe.db.get_value("Workflow", {"document_type": doctype})
            
            if not workflow_name:
                return {
                    "success": True,
                    "doctype": doctype,
                    "has_workflow": False,
                    "message": f"No workflow defined for DocType '{doctype}'"
                }
            
            # Get workflow document
            workflow_doc = frappe.get_doc("Workflow", workflow_name)
            
            # Process workflow states
            states = []
            for state in workflow_doc.states:
                states.append({
                    "state": state.state,
                    "doc_status": state.doc_status,
                    "allow_edit": state.allow_edit,
                    "message": state.message or "",
                    "next_action_email_template": state.next_action_email_template or "",
                    "is_optional_state": state.is_optional_state or 0
                })
            
            # Process workflow transitions
            transitions = []
            for transition in workflow_doc.transitions:
                transitions.append({
                    "state": transition.state,
                    "action": transition.action,
                    "next_state": transition.next_state,
                    "allowed": transition.allowed,
                    "allow_self_approval": transition.allow_self_approval or 0,
                    "condition": transition.condition or ""
                })
            
            return {
                "success": True,
                "doctype": doctype,
                "has_workflow": True,
                "workflow_name": workflow_name,
                "workflow_state_field": workflow_doc.workflow_state_field,
                "is_active": workflow_doc.is_active,
                "send_email_alerts": workflow_doc.send_email_alerts or 0,
                "states": states,
                "transitions": transitions,
                "state_count": len(states),
                "transition_count": len(transitions)
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Metadata Workflow Error"),
                message=f"Error getting workflow for {doctype}: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "doctype": doctype
            }


# Make sure class name matches file name for discovery
metadata_workflow = MetadataWorkflow