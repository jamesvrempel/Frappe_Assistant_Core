"""
Workflow List Tool for Core Plugin.
Lists all workflows and their configurations.
"""

import frappe
from frappe import _
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class WorkflowList(BaseTool):
    """
    Tool for listing all workflows and their configurations.
    
    Provides capabilities for:
    - List all workflows
    - Get workflow details
    - Filter workflows by DocType
    """
    
    def __init__(self):
        super().__init__()
        self.name = "workflow_list"
        self.description = "List all workflows in the system with their configurations. Use when users want to see available workflows and their details."
        self.requires_permission = None  # Permission checked per workflow
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "Filter workflows by specific DocType (e.g., 'Sales Invoice', 'Purchase Order')"
                },
                "include_details": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to include workflow states and transitions"
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Maximum number of workflows to return"
                }
            },
            "required": []
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List workflows"""
        doctype = arguments.get("doctype")
        include_details = arguments.get("include_details", True)
        limit = arguments.get("limit", 20)
        
        try:
            # Build filters
            filters = {}
            if doctype:
                filters["document_type"] = doctype
            
            # Get workflows
            workflows = frappe.get_all(
                "Workflow",
                filters=filters,
                fields=[
                    "name", "workflow_name", "document_type", "is_active",
                    "workflow_state_field", "send_email_alert",
                    "creation", "modified", "owner"
                ],
                limit=limit,
                order_by="name"
            )
            
            # Filter by permissions and add details
            accessible_workflows = []
            for workflow in workflows:
                try:
                    # Check if user has permission to access this workflow's DocType
                    if frappe.has_permission(workflow.document_type, "read"):
                        workflow_info = dict(workflow)
                        
                        # Add detailed information if requested
                        if include_details:
                            workflow_details = self._get_workflow_details(workflow.name)
                            workflow_info.update(workflow_details)
                        
                        accessible_workflows.append(workflow_info)
                except Exception:
                    # Skip if there's an error
                    continue
            
            # Add summary statistics
            summary = {
                "total_workflows": len(accessible_workflows),
                "active_workflows": len([w for w in accessible_workflows if w.get("is_active")]),
                "inactive_workflows": len([w for w in accessible_workflows if not w.get("is_active")]),
                "unique_doctypes": len(set(w.get("document_type") for w in accessible_workflows))
            }
            
            return {
                "success": True,
                "workflows": accessible_workflows,
                "summary": summary,
                "filters_applied": {
                    "doctype": doctype,
                    "include_details": include_details,
                    "limit": limit
                }
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Workflow List Error"),
                message=f"Error listing workflows: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_workflow_details(self, workflow_name: str) -> Dict:
        """Get detailed workflow information"""
        try:
            workflow_doc = frappe.get_doc("Workflow", workflow_name)
            
            # Get states
            states = []
            for state in workflow_doc.states:
                state_info = {
                    "state": state.state,
                    "doc_status": state.doc_status,
                    "update_field": state.update_field,
                    "update_value": state.update_value,
                    "is_optional_state": state.is_optional_state,
                    "allow_edit": state.allow_edit,
                    "message": state.message
                }
                states.append(state_info)
            
            # Get transitions
            transitions = []
            for transition in workflow_doc.transitions:
                transition_info = {
                    "state": transition.state,
                    "action": transition.action,
                    "next_state": transition.next_state,
                    "allowed": transition.allowed,
                    "condition": transition.condition,
                    "allow_self_approval": transition.allow_self_approval
                }
                transitions.append(transition_info)
            
            return {
                "states": states,
                "transitions": transitions,
                "state_count": len(states),
                "transition_count": len(transitions)
            }
            
        except Exception:
            return {
                "states": [],
                "transitions": [],
                "state_count": 0,
                "transition_count": 0
            }


# Make sure class name matches file name for discovery
workflow_list = WorkflowList