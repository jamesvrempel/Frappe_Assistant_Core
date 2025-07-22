# -*- coding: utf-8 -*-
# Frappe Assistant Core - AI Assistant integration for Frappe Framework
# Copyright (C) 2025 Paul Clinton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Dict, Any, List
import frappe

class WorkflowTools:
    """assistant tools for managing workflows in Frappe"""

    @staticmethod
    def get_tools() -> List[Dict]:
        """Return list of workflow-related assistant tools"""
        return [
            {
                "name": "run_workflow",
                "description": "Start a workflow for a specific document",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doctype": {"type": "string", "description": "Document type"},
                        "name": {"type": "string", "description": "Document name"},
                        "workflow": {"type": "string", "description": "Workflow name"},
                        "action": {"type": "string", "description": "Action to perform"}
                    },
                    "required": ["doctype", "name", "workflow", "action"]
                }
            },
            {
                "name": "get_workflow_state",
                "description": "Get the current state of a workflow for a document",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doctype": {"type": "string"},
                        "name": {"type": "string"}
                    },
                    "required": ["doctype", "name"]
                }
            },
            {
                "name": "get_workflow_actions",
                "description": "Get available actions for a document in a workflow",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doctype": {"type": "string"},
                        "name": {"type": "string"}
                    },
                    "required": ["doctype", "name"]
                }
            }
        ]

    @staticmethod
    def start_workflow(doctype: str, name: str, workflow: str, action: str) -> Dict[str, Any]:
        """Start a workflow for a specific document"""
        try:
            doc = frappe.get_doc(doctype, name)
            if not doc:
                return {"success": False, "error": f"Document '{doctype}' with name '{name}' not found."}

            # Check if the workflow exists
            if not frappe.db.exists("Workflow", workflow):
                return {"success": False, "error": f"Workflow '{workflow}' does not exist."}

            # Start the workflow
            doc.workflow_state = action
            doc.save()

            return {"success": True, "message": f"Workflow '{workflow}' started for '{doctype}' '{name}'."}

        except Exception as e:
            frappe.log_error(f"Workflow Start Error: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_workflow_state(doctype: str, name: str) -> Dict[str, Any]:
        """Get the current state of a workflow for a document"""
        try:
            doc = frappe.get_doc(doctype, name)
            if not doc:
                return {"success": False, "error": f"Document '{doctype}' with name '{name}' not found."}

            return {
                "success": True,
                "workflow_state": doc.workflow_state
            }

        except Exception as e:
            frappe.log_error(f"Get Workflow State Error: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_workflow_actions(doctype: str, name: str) -> Dict[str, Any]:
        """Get available actions for a document in a workflow"""
        try:
            doc = frappe.get_doc(doctype, name)
            if not doc:
                return {"success": False, "error": f"Document '{doctype}' with name '{name}' not found."}

            # Assuming the workflow is defined in the document
            workflow = frappe.get_doc("Workflow", doc.workflow)
            actions = workflow.get_available_actions(doc)

            return {
                "success": True,
                "actions": actions
            }

        except Exception as e:
            frappe.log_error(f"Get Workflow Actions Error: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a workflow tool by name"""
        try:
            if tool_name == "run_workflow":
                result = WorkflowTools.start_workflow(
                    arguments.get("doctype"),
                    arguments.get("name"),
                    arguments.get("workflow"),
                    arguments.get("action")
                )
            elif tool_name == "get_workflow_state":
                result = WorkflowTools.get_workflow_state(
                    arguments.get("doctype"),
                    arguments.get("name")
                )
            elif tool_name == "get_workflow_actions":
                result = WorkflowTools.get_workflow_actions(
                    arguments.get("doctype"),
                    arguments.get("name")
                )
            else:
                return f"Unknown workflow tool: {tool_name}"
                
            return frappe.as_json(result, indent=2)
            
        except Exception as e:
            frappe.log_error(f"Workflow tool execution error: {e}")
            return f"Error executing {tool_name}: {str(e)}"