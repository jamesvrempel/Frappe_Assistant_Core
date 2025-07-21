"""
Run Workflow Tool for Core Plugin.
Start and manage workflows for documents.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class RunWorkflow(BaseTool):
    """
    Tool for starting workflows for documents.
    
    Provides capabilities for:
    - Workflow initiation
    - State management
    - Action execution
    """
    
    def __init__(self):
        super().__init__()
        self.name = "run_workflow"
        self.description = "Start a workflow for a specific document"
        self.requires_permission = None  # Permission checked dynamically per document
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "Document type"
                },
                "name": {
                    "type": "string",
                    "description": "Document name"
                },
                "workflow": {
                    "type": "string",
                    "description": "Workflow name"
                },
                "action": {
                    "type": "string",
                    "description": "Action to perform"
                }
            },
            "required": ["doctype", "name", "workflow", "action"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow start"""
        try:
            # Import the workflow implementation
            from .workflow_tools import WorkflowTools
            
            # Execute workflow using existing implementation
            return WorkflowTools.start_workflow(
                doctype=arguments.get("doctype"),
                name=arguments.get("name"),
                workflow=arguments.get("workflow"),
                action=arguments.get("action")
            )
            
        except Exception as e:
            frappe.log_error(
                title=_("Run Workflow Error"),
                message=f"Error running workflow: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
run_workflow = RunWorkflow