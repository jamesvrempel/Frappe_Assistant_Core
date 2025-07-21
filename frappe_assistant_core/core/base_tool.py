"""
Base class for all MCP tools with configuration and dependency management.
"""

import frappe
from frappe import _
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import json
import time


class BaseTool(ABC):
    """
    Base class for all Frappe Assistant Core tools.
    
    Attributes:
        name: Tool identifier used in MCP protocol
        description: Human-readable description
        inputSchema: JSON schema for tool inputs
        requires_permission: DocType permission required
        category: Tool category for organization
        source_app: App that provides this tool
        dependencies: List of required dependencies
        default_config: Default configuration values
    """
    
    def __init__(self):
        self.name: str = ""
        self.description: str = ""
        self.inputSchema: Dict[str, Any] = {}
        self.requires_permission: Optional[str] = None
        self.category: str = "Custom"
        self.source_app: str = "frappe_assistant_core"
        self.dependencies: List[str] = []
        self.default_config: Dict[str, Any] = {}
        self.logger = frappe.logger(self.__class__.__module__)
        self._config_cache: Optional[Dict[str, Any]] = None
    
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
        required_fields = self.inputSchema.get("required", [])
        properties = self.inputSchema.get("properties", {})
        
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
            "inputSchema": self.inputSchema
        }
    
    def _safe_execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safely execute tool with error handling, timing, and audit logging.
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Execution result with success/error status
        """
        start_time = time.time()
        
        try:
            # Check dependencies
            deps_valid, deps_error = self.validate_dependencies()
            if not deps_valid:
                return {
                    "success": False,
                    "error": deps_error,
                    "error_type": "DependencyError"
                }
            
            # Check permissions
            self.check_permission()
            
            # Validate arguments
            self.validate_arguments(arguments)
            
            # Execute tool
            result = self.execute(arguments)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Prepare success response
            response = {
                "success": True,
                "result": result,
                "execution_time": execution_time
            }
            
            # Log execution
            self.log_execution(arguments, response, execution_time)
            
            # Log success
            self.logger.info(f"Successfully executed {self.name} in {execution_time:.3f}s")
            
            return response
            
        except frappe.PermissionError as e:
            execution_time = time.time() - start_time
            response = {
                "success": False,
                "error": str(e),
                "error_type": "PermissionError",
                "execution_time": execution_time
            }
            
            # Log execution
            self.log_execution(arguments, response, execution_time)
            
            # Log permission error
            frappe.log_error(
                title=_("Permission Error"),
                message=f"{self.name}: {str(e)}"
            )
            
            return response
            
        except frappe.ValidationError as e:
            execution_time = time.time() - start_time
            response = {
                "success": False,
                "error": str(e),
                "error_type": "ValidationError",
                "execution_time": execution_time
            }
            
            # Log execution
            self.log_execution(arguments, response, execution_time)
            
            # Log validation error
            frappe.log_error(
                title=_("Validation Error"),
                message=f"{self.name}: {str(e)}"
            )
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            response = {
                "success": False,
                "error": str(e),
                "error_type": "ExecutionError",
                "execution_time": execution_time
            }
            
            # Log execution
            self.log_execution(arguments, response, execution_time)
            
            # Log unexpected error
            frappe.log_error(
                title=_("Tool Execution Error"),
                message=f"{self.name}: {str(e)}"
            )
            
            return response
    
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
            "source_app": self.source_app,
            "category": self.category,
            "requires_permission": self.requires_permission,
            "dependencies": self.dependencies,
            "inputSchema": self.inputSchema,
            "default_config": self.default_config
        }
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get effective configuration using hierarchy: site > app > tool defaults.
        
        Returns:
            Merged configuration dictionary
        """
        if self._config_cache is not None:
            return self._config_cache
        
        # Start with tool defaults
        config = self.default_config.copy()
        
        # Apply app-level configuration from hooks
        app_config = self._get_app_config()
        if app_config:
            config.update(app_config)
        
        # Apply site-level configuration
        site_config = self._get_site_config()
        if site_config:
            config.update(site_config)
        
        # Cache the result
        self._config_cache = config
        return config
    
    def _get_app_config(self) -> Dict[str, Any]:
        """Get app-level configuration from hooks"""
        try:
            from frappe.utils import get_hooks
            tool_configs = get_hooks("assistant_tool_configs") or {}
            return tool_configs.get(self.name, {})
        except Exception:
            return {}
    
    def _get_site_config(self) -> Dict[str, Any]:
        """Get site-level configuration from site_config.json"""
        try:
            site_config = frappe.conf.get("assistant_tools", {})
            return site_config.get(self.name, {})
        except Exception:
            return {}
    
    def validate_dependencies(self) -> Tuple[bool, Optional[str]]:
        """
        Check if all tool dependencies are available.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.dependencies:
            return True, None
        
        missing_deps = []
        for dep in self.dependencies:
            try:
                # Try to import the dependency
                __import__(dep)
            except ImportError:
                missing_deps.append(dep)
        
        if missing_deps:
            return False, f"Missing dependencies: {', '.join(missing_deps)}"
        
        return True, None
    
    def clear_config_cache(self):
        """Clear cached configuration to force reload"""
        self._config_cache = None
    
    def log_execution(self, arguments: Dict[str, Any], result: Dict[str, Any], 
                     execution_time: float):
        """
        Log tool execution for audit purposes.
        
        Args:
            arguments: Tool arguments (sensitive data will be sanitized)
            result: Execution result
            execution_time: Time taken in seconds
        """
        try:
            from frappe_assistant_core.utils.audit_trail import log_tool_execution
            
            log_tool_execution(
                tool_name=self.name,
                user=frappe.session.user,
                arguments=self._sanitize_arguments(arguments),
                success=result.get("success", False),
                execution_time=execution_time,
                source_app=self.source_app,
                error_message=result.get("error") if not result.get("success") else None
            )
        except Exception as e:
            # Don't fail tool execution due to logging issues
            self.logger.warning(f"Failed to log execution for {self.name}: {str(e)}")
    
    def _sanitize_arguments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from arguments for logging"""
        sensitive_keys = ['password', 'api_key', 'secret', 'token', 'auth']
        sanitized = {}
        
        for key, value in arguments.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        
        return sanitized