"""
Base class for all MCP tools following Frappe standards.
"""

import frappe
from frappe import _
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json


class BaseTool(ABC):
    """
    Base class for all Frappe Assistant Core tools.
    
    Attributes:
        name: Tool identifier used in MCP protocol
        description: Human-readable description
        input_schema: JSON schema for tool inputs
        requires_permission: DocType permission required
    """
    
    def __init__(self):
        self.name: str = ""
        self.description: str = ""
        self.input_schema: Dict[str, Any] = {}
        self.requires_permission: Optional[str] = None
        self.logger = frappe.logger(self.__class__.__module__)
    
    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with given arguments.
        
        Args:
            arguments: Tool-specific arguments
            
        Returns:
            Tool execution result
            
        Raises:
            frappe.PermissionError: If user lacks permission
            frappe.ValidationError: If arguments are invalid
        """
        pass
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> None:
        """
        Validate arguments against input schema.
        
        Args:
            arguments: Arguments to validate
            
        Raises:
            frappe.ValidationError: If validation fails
        """
        # Implement JSON schema validation
        required_fields = self.input_schema.get("required", [])
        properties = self.input_schema.get("properties", {})
        
        # Check required fields
        for field in required_fields:
            if field not in arguments:
                frappe.throw(
                    _("Missing required field: {0}").format(field),
                    frappe.ValidationError
                )
        
        # Validate field types
        for field, value in arguments.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if not self._validate_type(value, expected_type):
                    frappe.throw(
                        _("Invalid type for field {0}: expected {1}").format(
                            field, expected_type
                        ),
                        frappe.ValidationError
                    )
    
    def check_permission(self) -> None:
        """
        Check if current user has required permissions.
        
        Raises:
            frappe.PermissionError: If permission check fails
        """
        if self.requires_permission:
            if not frappe.has_permission(self.requires_permission, "read"):
                frappe.throw(
                    _("Insufficient permissions to execute {0}").format(self.name),
                    frappe.PermissionError
                )
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value matches expected JSON schema type"""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        if expected_type in type_map:
            return isinstance(value, type_map[expected_type])
        return True
    
    def to_mcp_format(self) -> Dict[str, Any]:
        """Convert tool to MCP protocol format"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }
    
    def _safe_execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safely execute tool with error handling and logging.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Execution result with success/error status
        """
        try:
            # Check permissions
            self.check_permission()
            
            # Validate arguments
            self.validate_arguments(arguments)
            
            # Execute tool
            result = self.execute(arguments)
            
            # Log success
            self.logger.info(f"Successfully executed {self.name}")
            
            return {
                "success": True,
                "result": result
            }
            
        except frappe.PermissionError as e:
            # Log permission error
            frappe.log_error(
                title=_("Permission Error"),
                message=f"{self.name}: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "error_type": "PermissionError"
            }
            
        except frappe.ValidationError as e:
            # Log validation error
            frappe.log_error(
                title=_("Validation Error"),
                message=f"{self.name}: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "error_type": "ValidationError"
            }
            
        except Exception as e:
            # Log unexpected error
            frappe.log_error(
                title=_("Tool Execution Error"),
                message=f"{self.name}: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "error_type": "ExecutionError"
            }
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get tool metadata for admin/debugging purposes.
        
        Returns:
            Tool metadata including class info, permissions, etc.
        """
        return {
            "name": self.name,
            "description": self.description,
            "class": self.__class__.__name__,
            "module": self.__class__.__module__,
            "requires_permission": self.requires_permission,
            "input_schema": self.input_schema
        }