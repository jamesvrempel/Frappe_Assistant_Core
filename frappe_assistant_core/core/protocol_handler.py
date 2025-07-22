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

"""
Protocol Handler for Frappe Assistant Core.
Handles MCP (Model Context Protocol) communication and message processing.
"""

import frappe
from frappe import _
import json
import time
from typing import Dict, Any, Optional, List, Union
from frappe_assistant_core.core.constants import (
    MCP_PROTOCOL_VERSION, MCP_JSONRPC_VERSION, ERROR_CODES,
    SERVER_NAME, DEFAULT_SERVER_VERSION, MCP_CONTENT_TYPES
)
from frappe_assistant_core.core.tool_registry import get_tool_registry
from frappe_assistant_core.utils.validators import validate_json_rpc
from frappe_assistant_core.utils.logger import get_logger


class MCPProtocolHandler:
    """
    Handles MCP protocol communication between AI assistants and Frappe.
    
    Implements JSON-RPC 2.0 specification with MCP-specific extensions.
    """
    
    def __init__(self):
        self.logger = get_logger("protocol_handler")
        self.protocol_version = MCP_PROTOCOL_VERSION
        self.server_name = SERVER_NAME
        self.server_version = frappe.get_app_version("frappe_assistant_core") or DEFAULT_SERVER_VERSION
        
        # Performance tracking
        self.request_count = 0
        self.total_processing_time = 0.0
        
    def handle_request(self, request_data: str) -> str:
        """
        Handle incoming MCP request.
        
        Args:
            request_data: JSON-RPC 2.0 request string
            
        Returns:
            JSON-RPC 2.0 response string
        """
        start_time = time.time()
        request_id = None
        
        try:
            # Parse JSON request
            try:
                request = json.loads(request_data)
                request_id = request.get("id")
            except json.JSONDecodeError as e:
                self.logger.warning(f"Invalid JSON received: {str(e)}")
                return self._create_error_response(
                    None, 
                    ERROR_CODES["PARSE_ERROR"],
                    "Parse error",
                    f"Invalid JSON: {str(e)}"
                )
            
            # Validate JSON-RPC structure
            validation_error = validate_json_rpc(request)
            if validation_error:
                self.logger.warning(f"Invalid JSON-RPC request: {validation_error}")
                return self._create_error_response(
                    request_id,
                    ERROR_CODES["INVALID_REQUEST"],
                    "Invalid Request",
                    validation_error
                )
            
            # Log request (without sensitive data)
            self.logger.debug(f"Processing MCP request: {request.get('method')} (ID: {request_id})")
            
            # Route to appropriate handler
            response = self._route_request(request)
            
            # Update performance metrics
            processing_time = time.time() - start_time
            self._update_metrics(request.get("method"), processing_time, True)
            
            return response
            
        except frappe.PermissionError as e:
            self.logger.warning(f"Permission denied for request {request_id}: {str(e)}")
            processing_time = time.time() - start_time
            self._update_metrics(request.get("method") if "request" in locals() else "unknown", processing_time, False)
            
            return self._create_error_response(
                request_id,
                ERROR_CODES["PERMISSION_DENIED"],
                "Permission denied",
                str(e)
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error processing request {request_id}: {str(e)}")
            frappe.log_error(
                title=_("MCP Protocol Error"),
                message=f"Error processing MCP request: {str(e)}"
            )
            
            processing_time = time.time() - start_time
            self._update_metrics(request.get("method") if "request" in locals() else "unknown", processing_time, False)
            
            return self._create_error_response(
                request_id,
                ERROR_CODES["INTERNAL_ERROR"],
                "Internal error",
                "An internal error occurred"
            )
    
    def _route_request(self, request: Dict[str, Any]) -> str:
        """Route request to appropriate handler based on method"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        # MCP protocol methods
        if method == "initialize":
            result = self._handle_initialize(params)
        elif method == "initialized":
            result = self._handle_initialized(params)
        elif method == "tools/list":
            result = self._handle_tools_list(params)
        elif method == "tools/call":
            result = self._handle_tools_call(params)
        elif method == "ping":
            result = self._handle_ping(params)
        elif method == "notifications/initialized":
            result = self._handle_notifications_initialized(params)
        else:
            return self._create_error_response(
                request_id,
                ERROR_CODES["METHOD_NOT_FOUND"],
                "Method not found",
                f"Unknown method: {method}"
            )
        
        return self._create_success_response(request_id, result)
    
    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        # Validate protocol version
        client_version = params.get("protocolVersion", "")
        if not client_version:
            raise ValueError("Protocol version is required")
        
        if client_version != self.protocol_version:
            self.logger.warning(f"Protocol version mismatch: client={client_version}, server={self.protocol_version}")
        
        # Get client capabilities
        client_capabilities = params.get("capabilities", {})
        
        # Return server capabilities
        server_capabilities = {
            "tools": {
                "listChanged": True
            },
            "experimental": {
                "performance_monitoring": True,
                "batch_processing": True,
                "streaming_responses": False
            }
        }
        
        # Add plugin-specific capabilities
        server_capabilities.update(self._get_plugin_capabilities())
        
        return {
            "protocolVersion": self.protocol_version,
            "capabilities": server_capabilities,
            "serverInfo": {
                "name": self.server_name,
                "version": self.server_version
            }
        }
    
    def _handle_initialized(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialized notification"""
        self.logger.info("MCP connection initialized successfully")
        return {}
    
    def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tools/list request"""
        try:
            # Get tool registry
            registry = get_tool_registry()
            
            # Get available tools for current user
            tools = registry.get_available_tools()
            
            # Convert to MCP format
            mcp_tools = []
            for tool in tools:
                try:
                    mcp_tool = self._tool_to_mcp_format(tool)
                    mcp_tools.append(mcp_tool)
                except Exception as e:
                    self.logger.warning(f"Failed to convert tool {tool.name} to MCP format: {str(e)}")
            
            self.logger.debug(f"Returning {len(mcp_tools)} tools to client")
            return {"tools": mcp_tools}
            
        except Exception as e:
            self.logger.error(f"Error listing tools: {str(e)}")
            raise
    
    def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            raise ValueError("Tool name is required")
        
        self.logger.debug(f"Executing tool: {tool_name}")
        
        try:
            # Get tool registry
            registry = get_tool_registry()
            
            # Get tool instance
            tool = registry.get_tool(tool_name)
            if not tool:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            # Execute tool with error handling
            start_time = time.time()
            result = tool.execute(arguments)
            execution_time = time.time() - start_time
            
            self.logger.debug(f"Tool {tool_name} executed in {execution_time:.2f}s")
            
            # Convert result to MCP content format
            content = self._result_to_mcp_content(result, tool_name)
            
            return {"content": content}
            
        except Exception as e:
            self.logger.error(f"Error executing tool '{tool_name}': {str(e)}")
            frappe.log_error(
                title=_("Tool Execution Error"),
                message=f"Error executing tool '{tool_name}': {str(e)}"
            )
            raise
    
    def _handle_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping request for connection testing"""
        return {
            "status": "ok",
            "timestamp": frappe.utils.now(),
            "server": self.server_name,
            "uptime": self._get_server_uptime()
        }
    
    def _handle_notifications_initialized(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle notifications/initialized request"""
        self.logger.debug("Notifications initialized")
        return {}
    
    def _tool_to_mcp_format(self, tool) -> Dict[str, Any]:
        """Convert tool instance to MCP format"""
        mcp_tool = {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.inputSchema
        }
        
        # Add optional metadata
        if hasattr(tool, "requires_permission") and tool.requires_permission:
            mcp_tool["metadata"] = {
                "requires_permission": tool.requires_permission
            }
        
        if hasattr(tool, "plugin_name"):
            mcp_tool["metadata"] = mcp_tool.get("metadata", {})
            mcp_tool["metadata"]["plugin"] = tool.plugin_name
        
        return mcp_tool
    
    def _result_to_mcp_content(self, result: Any, tool_name: str) -> List[Dict[str, Any]]:
        """Convert tool execution result to MCP content format"""
        content = []
        
        if isinstance(result, dict):
            if "success" in result:
                if result["success"]:
                    # Success response - extract meaningful content
                    content_data = self._extract_content_from_result(result)
                    
                    # Handle different content types
                    if isinstance(content_data, str):
                        content.append({
                            "type": MCP_CONTENT_TYPES["TEXT"],
                            "text": content_data
                        })
                    elif isinstance(content_data, dict) or isinstance(content_data, list):
                        content.append({
                            "type": MCP_CONTENT_TYPES["TEXT"],
                            "text": json.dumps(content_data, indent=2, default=str)
                        })
                    else:
                        content.append({
                            "type": MCP_CONTENT_TYPES["TEXT"],
                            "text": str(content_data)
                        })
                    
                    # Add metadata if available
                    if "metadata" in result:
                        content.append({
                            "type": MCP_CONTENT_TYPES["TEXT"],
                            "text": f"Metadata: {json.dumps(result['metadata'], indent=2)}"
                        })
                else:
                    # Error response
                    error_msg = result.get("error", "Tool execution failed")
                    raise ValueError(f"Tool execution failed: {error_msg}")
            else:
                # Direct result without success flag
                content.append({
                    "type": MCP_CONTENT_TYPES["TEXT"],
                    "text": json.dumps(result, indent=2, default=str)
                })
        else:
            # Non-dict result
            content.append({
                "type": MCP_CONTENT_TYPES["TEXT"],
                "text": str(result)
            })
        
        return content
    
    def _extract_content_from_result(self, result: Dict[str, Any]) -> Any:
        """Extract meaningful content from tool result"""
        # Priority order for content extraction
        content_keys = ["data", "result", "content", "output", "response"]
        
        for key in content_keys:
            if key in result:
                return result[key]
        
        # If no standard content keys, return filtered result
        filtered_result = {k: v for k, v in result.items() 
                          if k not in ["success", "timestamp", "execution_time"]}
        
        return filtered_result if filtered_result else result
    
    def _get_plugin_capabilities(self) -> Dict[str, Any]:
        """Get capabilities from enabled plugins"""
        capabilities = {}
        
        try:
            from frappe_assistant_core.utils.plugin_manager import get_plugin_manager
            plugin_manager = get_plugin_manager()
            
            for plugin_name in plugin_manager.get_enabled_plugins():
                try:
                    plugin = plugin_manager.get_plugin(plugin_name)
                    if plugin and hasattr(plugin, "get_capabilities"):
                        plugin_caps = plugin.get_capabilities()
                        if plugin_caps:
                            capabilities[f"plugin_{plugin_name}"] = plugin_caps
                except Exception as e:
                    self.logger.warning(f"Failed to get capabilities from plugin {plugin_name}: {str(e)}")
        
        except Exception as e:
            self.logger.warning(f"Failed to get plugin capabilities: {str(e)}")
        
        return capabilities
    
    def _get_server_uptime(self) -> float:
        """Get server uptime in seconds"""
        try:
            # This is a simplified uptime calculation
            # In a real implementation, you might track server start time
            return frappe.utils.time_diff_in_seconds(frappe.utils.now(), frappe.utils.today())
        except Exception:
            return 0.0
    
    def _update_metrics(self, method: str, processing_time: float, success: bool):
        """Update performance metrics"""
        try:
            self.request_count += 1
            self.total_processing_time += processing_time
            
            # Update cached metrics
            metrics = frappe.cache().hget("assistant_metrics", "protocol_handler") or {}
            
            # Update method-specific metrics
            method_metrics = metrics.get(method, {"count": 0, "total_time": 0, "errors": 0})
            method_metrics["count"] += 1
            method_metrics["total_time"] += processing_time
            
            if not success:
                method_metrics["errors"] += 1
            
            metrics[method] = method_metrics
            
            # Update overall metrics
            metrics["total_requests"] = self.request_count
            metrics["avg_processing_time"] = self.total_processing_time / self.request_count
            metrics["last_updated"] = frappe.utils.now()
            
            frappe.cache().hset("assistant_metrics", "protocol_handler", metrics)
            
        except Exception as e:
            self.logger.warning(f"Failed to update metrics: {str(e)}")
    
    def _create_success_response(self, request_id: Any, result: Dict[str, Any]) -> str:
        """Create JSON-RPC 2.0 success response"""
        response = {
            "jsonrpc": MCP_JSONRPC_VERSION,
            "result": result,
            "id": request_id
        }
        return json.dumps(response)
    
    def _create_error_response(self, request_id: Any, code: int, message: str, data: Any = None) -> str:
        """Create JSON-RPC 2.0 error response"""
        error = {
            "code": code,
            "message": message
        }
        
        if data is not None:
            error["data"] = data
        
        response = {
            "jsonrpc": MCP_JSONRPC_VERSION,
            "error": error,
            "id": request_id
        }
        
        return json.dumps(response)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get handler performance metrics"""
        cached_metrics = frappe.cache().hget("assistant_metrics", "protocol_handler") or {}
        
        return {
            "request_count": self.request_count,
            "avg_processing_time": self.total_processing_time / max(self.request_count, 1),
            "cached_metrics": cached_metrics,
            "server_info": {
                "name": self.server_name,
                "version": self.server_version,
                "protocol_version": self.protocol_version
            }
        }


# Global handler instance
_protocol_handler = None


def get_protocol_handler() -> MCPProtocolHandler:
    """Get or create global protocol handler instance"""
    global _protocol_handler
    
    if _protocol_handler is None:
        _protocol_handler = MCPProtocolHandler()
    
    return _protocol_handler


def handle_mcp_request(request_data: str) -> str:
    """
    Global function for handling MCP requests.
    
    Args:
        request_data: JSON-RPC 2.0 request string
        
    Returns:
        JSON-RPC 2.0 response string
    """
    handler = get_protocol_handler()
    return handler.handle_request(request_data)