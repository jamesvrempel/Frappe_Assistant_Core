"""
Workflow Action Tool for Core Plugin.
Executes workflow actions on documents.
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class WorkflowAction(BaseTool):
    """
    Tool for executing workflow actions on documents.
    
    Provides capabilities for:
    - Execute workflow transitions
    - Apply workflow actions
    - Handle workflow validation
    """
    
    def __init__(self):
        super().__init__()
        self.name = "workflow_action"
        self.description = "Execute a workflow action on a document. Use when users want to move a document through its workflow states."
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
                "action": {
                    "type": "string",
                    "description": "The workflow action to execute (e.g., 'Submit', 'Approve', 'Reject')"
                },
                "comment": {
                    "type": "string",
                    "description": "Optional comment for the workflow action"
                }
            },
            "required": ["doctype", "name", "action"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow action"""
        doctype = arguments.get("doctype")
        name = arguments.get("name")
        action = arguments.get("action")
        comment = arguments.get("comment", "")
        
        # Check permission for DocType
        if not frappe.has_permission(doctype, "write"):
            return {
                "success": False,
                "error": f"Insufficient permissions to execute workflow action on {doctype}"
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
            
            # Apply workflow action
            doc.add_comment("Workflow", f"Action: {action}" + (f" - {comment}" if comment else ""))
            
            # Execute the action
            if action.lower() == "submit" and hasattr(doc, "submit"):
                doc.submit()
            elif action.lower() == "cancel" and hasattr(doc, "cancel"):
                doc.cancel()
            elif action.lower() == "approve":
                # Find next state for approval
                next_state = self._get_next_workflow_state(workflow, current_state, action)
                if next_state:
                    doc.workflow_state = next_state
                    doc.save()
                else:
                    return {
                        "success": False,
                        "error": f"No valid transition found for action '{action}' from state '{current_state}'"
                    }
            elif action.lower() == "reject":
                # Find next state for rejection
                next_state = self._get_next_workflow_state(workflow, current_state, action)
                if next_state:
                    doc.workflow_state = next_state
                    doc.save()
                else:
                    return {
                        "success": False,
                        "error": f"No valid transition found for action '{action}' from state '{current_state}'"
                    }
            else:
                # Generic workflow action
                next_state = self._get_next_workflow_state(workflow, current_state, action)
                if next_state:
                    doc.workflow_state = next_state
                    doc.save()
                else:
                    return {
                        "success": False,
                        "error": f"Unknown workflow action '{action}' or no valid transition found"
                    }
            
            return {
                "success": True,
                "doctype": doctype,
                "name": name,
                "action": action,
                "previous_state": current_state,
                "current_state": doc.get("workflow_state"),
                "message": f"Workflow action '{action}' executed successfully"
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Workflow Action Error"),
                message=f"Error executing workflow action '{action}' on {doctype} '{name}': {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "doctype": doctype,
                "name": name,
                "action": action
            }
    
    def _get_next_workflow_state(self, workflow: str, current_state: str, action: str) -> str:
        """Get next workflow state for given action"""
        try:
            # Get workflow transitions
            transitions = frappe.get_all(
                "Workflow Transition",
                filters={
                    "parent": workflow,
                    "state": current_state,
                    "action": action
                },
                fields=["next_state"]
            )
            
            if transitions:
                return transitions[0].next_state
            
            return None
            
        except Exception:
            return None


# Make sure class name matches file name for discovery
workflow_action = WorkflowAction