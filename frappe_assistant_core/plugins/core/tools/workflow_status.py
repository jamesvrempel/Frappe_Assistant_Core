"""
Workflow Status Tool for Core Plugin.
Gets current workflow status and available actions for a document.
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class WorkflowStatus(BaseTool):
    """
    Tool for getting workflow status and available actions.
    
    Provides capabilities for:
    - Get current workflow state
    - List available workflow actions
    - Get workflow history
    """
    
    def __init__(self):
        super().__init__()
        self.name = "workflow_status"
        self.description = "Get current workflow status and available actions for a document. Use when users want to see the workflow state and possible next steps."
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "The DocType of the document (e.g., 'Sales Invoice', 'Purchase Order')"
                },
                "name": {
                    "type": "string",
                    "description": "The document name/ID"
                },
                "include_history": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to include workflow history"
                }
            },
            "required": ["doctype", "name"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get workflow status"""
        doctype = arguments.get("doctype")
        name = arguments.get("name")
        include_history = arguments.get("include_history", True)
        
        # Check permission for DocType
        if not frappe.has_permission(doctype, "read"):
            return {
                "success": False,
                "error": f"Insufficient permissions to access {doctype} workflow status"
            }
        
        try:
            # Check if document exists
            if not frappe.db.exists(doctype, name):
                return {
                    "success": False,
                    "error": f"{doctype} '{name}' not found"
                }
            
            # Get document
            doc = frappe.get_doc(doctype, name)
            
            # Check if document has workflow
            workflow = frappe.get_value("DocType", doctype, "workflow")
            if not workflow:
                return {
                    "success": False,
                    "error": f"No workflow configured for {doctype}"
                }
            
            # Get current workflow state
            current_state = doc.get("workflow_state")
            
            # Get workflow information
            workflow_doc = frappe.get_doc("Workflow", workflow)
            
            # Get available actions
            available_actions = self._get_available_actions(workflow, current_state)
            
            # Build status response
            status = {
                "doctype": doctype,
                "name": name,
                "workflow": workflow,
                "current_state": current_state,
                "available_actions": available_actions,
                "workflow_states": [state.state for state in workflow_doc.states],
                "is_final_state": self._is_final_state(workflow, current_state)
            }
            
            # Add workflow history if requested
            if include_history:
                history = self._get_workflow_history(doctype, name)
                status["history"] = history
            
            return {
                "success": True,
                "workflow_status": status
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Workflow Status Error"),
                message=f"Error getting workflow status for {doctype} '{name}': {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "doctype": doctype,
                "name": name
            }
    
    def _get_available_actions(self, workflow: str, current_state: str) -> List[Dict]:
        """Get available workflow actions from current state"""
        try:
            transitions = frappe.get_all(
                "Workflow Transition",
                filters={
                    "parent": workflow,
                    "state": current_state
                },
                fields=["action", "next_state", "allowed"]
            )
            
            available_actions = []
            for transition in transitions:
                action_info = {
                    "action": transition.action,
                    "next_state": transition.next_state,
                    "allowed_roles": transition.allowed.split(",") if transition.allowed else []
                }
                available_actions.append(action_info)
            
            return available_actions
            
        except Exception:
            return []
    
    def _is_final_state(self, workflow: str, current_state: str) -> bool:
        """Check if current state is a final state"""
        try:
            # Check if there are any transitions from current state
            transitions = frappe.get_all(
                "Workflow Transition",
                filters={
                    "parent": workflow,
                    "state": current_state
                },
                limit=1
            )
            
            return len(transitions) == 0
            
        except Exception:
            return False
    
    def _get_workflow_history(self, doctype: str, name: str) -> List[Dict]:
        """Get workflow history from comments"""
        try:
            history = frappe.get_all(
                "Comment",
                filters={
                    "reference_doctype": doctype,
                    "reference_name": name,
                    "comment_type": "Workflow"
                },
                fields=["content", "creation", "owner"],
                order_by="creation desc"
            )
            
            return history
            
        except Exception:
            return []


# Make sure class name matches file name for discovery
workflow_status = WorkflowStatus