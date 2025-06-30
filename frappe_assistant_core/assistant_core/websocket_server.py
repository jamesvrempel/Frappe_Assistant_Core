"""
WebSocket MCP Server for Frappe Assistant Core
Provides persistent WebSocket connections for enhanced MCP protocol support
"""

import frappe
import json
import asyncio
import websockets
import time
import uuid
from typing import Dict, Any, Optional, Set, List
from datetime import datetime, timedelta
from threading import Thread
import logging
from frappe.utils import cint
from frappe_assistant_core.assistant_core.protocol_handler import ProtocolHandler
from frappe_assistant_core.utils.auth import validate_api_credentials
from frappe_assistant_core.utils.logger import api_logger
from frappe_assistant_core.utils.cache import get_cached_server_settings

class WebSocketConnection:
    """Represents a single WebSocket connection with authentication and state"""
    
    def __init__(self, websocket, connection_id: str, user: str = None, api_key: str = None):
        self.websocket = websocket
        self.connection_id = connection_id
        self.user = user
        self.api_key = api_key
        self.connected_at = datetime.now()
        self.last_activity = datetime.now()
        self.message_count = 0
        self.active_operations: Set[str] = set()
        self.rate_limit_history: List[float] = []
        
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
        
    def add_operation(self, operation_id: str):
        """Track active operation"""
        self.active_operations.add(operation_id)
        
    def remove_operation(self, operation_id: str):
        """Remove completed operation"""
        self.active_operations.discard(operation_id)
        
    def check_rate_limit(self, rate_limit: int) -> bool:
        """Check if connection is within rate limits"""
        now = time.time()
        # Remove old entries (older than 1 minute)
        self.rate_limit_history = [t for t in self.rate_limit_history if now - t < 60]
        
        if len(self.rate_limit_history) >= rate_limit:
            return False
            
        self.rate_limit_history.append(now)
        return True
        
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        return {
            "connection_id": self.connection_id,
            "user": self.user,
            "connected_at": self.connected_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "message_count": self.message_count,
            "active_operations": len(self.active_operations),
            "uptime_seconds": (datetime.now() - self.connected_at).total_seconds()
        }

class WebSocketMCPServer:
    """Enhanced WebSocket MCP Server with Frappe integration"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.protocol_handler = ProtocolHandler()
        self.server = None
        self.running = False
        self.cleanup_task = None
        
    async def authenticate_connection(self, websocket, path: str) -> Optional[WebSocketConnection]:
        """Authenticate WebSocket connection using query parameters"""
        try:
            # Parse query parameters from path
            if '?' not in path:
                await websocket.close(code=1008, reason="Missing authentication parameters")
                return None
                
            query_string = path.split('?', 1)[1]
            params = {}
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
            
            api_key = params.get('api_key')
            api_secret = params.get('api_secret')
            
            if not api_key or not api_secret:
                await websocket.close(code=1008, reason="Missing API credentials")
                return None
            
            # Validate credentials using existing auth system
            user = validate_api_credentials(api_key, api_secret)
            if not user:
                await websocket.close(code=1008, reason="Invalid API credentials")
                return None
                
            # Check origin validation
            origin = websocket.request_headers.get('Origin')
            if not self._validate_origin(origin):
                await websocket.close(code=1008, reason="Origin not allowed")
                return None
            
            # Create connection
            connection_id = str(uuid.uuid4())
            connection = WebSocketConnection(websocket, connection_id, user, api_key)
            
            # Log connection
            self._log_connection(connection, "Connected")
            
            return connection
            
        except Exception as e:
            api_logger.error(f"Authentication error: {str(e)}")
            await websocket.close(code=1011, reason="Authentication failed")
            return None
    
    def _validate_origin(self, origin: str) -> bool:
        """Validate WebSocket origin"""
        try:
            settings = get_cached_server_settings()
            allowed_origins = settings.get('allowed_origins', '')
            
            if not allowed_origins:
                return True  # Allow all origins if not configured
                
            allowed_list = [o.strip() for o in allowed_origins.split(',')]
            return origin in allowed_list or '*' in allowed_list
            
        except Exception:
            return True  # Default to allow if settings unavailable
    
    def _log_connection(self, connection: WebSocketConnection, event: str):
        """Log connection events to database"""
        try:
            log_doc = frappe.get_doc({
                "doctype": "Assistant Connection Log",
                "connection_id": connection.connection_id,
                "user": connection.user,
                "event": event,
                "protocol": "WebSocket",
                "ip_address": getattr(connection.websocket, 'remote_address', ['unknown'])[0],
                "status": "Connected" if event == "Connected" else "Disconnected"
            })
            log_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            
        except Exception as e:
            api_logger.error(f"Failed to log connection: {str(e)}")
    
    async def handle_connection(self, websocket, path):
        """Handle individual WebSocket connection"""
        connection = await self.authenticate_connection(websocket, path)
        if not connection:
            return
            
        try:
            # Add to active connections
            self.connections[connection.connection_id] = connection
            api_logger.info(f"WebSocket connection established: {connection.connection_id}")
            
            # Send initial capabilities
            await self._send_capabilities(connection)
            
            # Message handling loop
            async for message in websocket:
                await self._handle_message(connection, message)
                
        except websockets.exceptions.ConnectionClosed:
            api_logger.info(f"WebSocket connection closed: {connection.connection_id}")
        except Exception as e:
            api_logger.error(f"WebSocket error: {str(e)}")
        finally:
            # Cleanup connection
            if connection.connection_id in self.connections:
                del self.connections[connection.connection_id]
            self._log_connection(connection, "Disconnected")
    
    async def _send_capabilities(self, connection: WebSocketConnection):
        """Send server capabilities to client"""
        capabilities = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True, "listChanged": True},
                    "prompts": {"listChanged": True},
                    "experimental": {
                        "batch_processing": True,
                        "progress_streaming": True,
                        "operation_cancellation": True
                    }
                },
                "serverInfo": {
                    "name": "Frappe Assistant Core WebSocket",
                    "version": "1.0.0",
                    "protocol_version": "2024-11-05"
                }
            }
        }
        
        await self._send_message(connection, capabilities)
    
    async def _handle_message(self, connection: WebSocketConnection, message: str):
        """Handle incoming WebSocket message"""
        try:
            connection.update_activity()
            connection.message_count += 1
            
            # Check rate limiting
            settings = get_cached_server_settings()
            rate_limit = settings.get('rate_limit', 60)
            
            if not connection.check_rate_limit(rate_limit):
                await self._send_error(connection, None, -32000, "Rate limit exceeded")
                return
            
            # Parse JSON-RPC message
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                await self._send_error(connection, None, -32700, "Parse error")
                return
            
            # Handle batch requests
            if isinstance(data, list):
                await self._handle_batch_request(connection, data)
                return
            
            # Handle single request
            await self._handle_single_request(connection, data)
            
        except Exception as e:
            api_logger.error(f"Message handling error: {str(e)}")
            await self._send_error(connection, None, -32603, "Internal error")
    
    async def _handle_single_request(self, connection: WebSocketConnection, request: Dict[str, Any]):
        """Handle single JSON-RPC request"""
        request_id = request.get('id')
        method = request.get('method')
        params = request.get('params', {})
        
        try:
            # Set user context for Frappe operations
            frappe.set_user(connection.user)
            
            # Handle different methods
            if method == "tools/call":
                await self._handle_tool_call(connection, request_id, params)
            elif method == "tools/list":
                await self._handle_tools_list(connection, request_id, params)
            elif method == "resources/list":
                await self._handle_resources_list(connection, request_id, params)
            elif method == "resources/read":
                await self._handle_resource_read(connection, request_id, params)
            elif method.startswith("batch/"):
                await self._handle_batch_method(connection, request_id, method, params)
            else:
                await self._send_error(connection, request_id, -32601, f"Method not found: {method}")
                
        except Exception as e:
            api_logger.error(f"Request handling error: {str(e)}")
            await self._send_error(connection, request_id, -32603, "Internal error")
    
    async def _handle_batch_request(self, connection: WebSocketConnection, requests: List[Dict[str, Any]]):
        """Handle batch JSON-RPC requests with parallel processing"""
        try:
            # Create tasks for parallel execution
            tasks = []
            for request in requests:
                task = asyncio.create_task(self._handle_single_request(connection, request))
                tasks.append(task)
            
            # Execute all requests in parallel
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            api_logger.error(f"Batch request error: {str(e)}")
    
    async def _handle_tool_call(self, connection: WebSocketConnection, request_id: str, params: Dict[str, Any]):
        """Handle tool execution with progress streaming"""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        if not tool_name:
            await self._send_error(connection, request_id, -32602, "Missing tool name")
            return
        
        # Generate operation ID for tracking
        operation_id = str(uuid.uuid4())
        connection.add_operation(operation_id)
        
        try:
            # Send progress start notification
            await self._send_progress(connection, operation_id, "started", f"Executing {tool_name}")
            
            # Execute tool using existing protocol handler
            result = self.protocol_handler.handle_tools_call({
                'name': tool_name,
                'arguments': arguments
            })
            
            # Send progress completion
            await self._send_progress(connection, operation_id, "completed", f"Tool {tool_name} completed")
            
            # Send result
            await self._send_result(connection, request_id, result)
            
        except Exception as e:
            await self._send_progress(connection, operation_id, "failed", f"Tool {tool_name} failed: {str(e)}")
            await self._send_error(connection, request_id, -32603, str(e))
        finally:
            connection.remove_operation(operation_id)
    
    async def _handle_tools_list(self, connection: WebSocketConnection, request_id: str, params: Dict[str, Any]):
        """Handle tools list request"""
        try:
            result = self.protocol_handler.handle_tools_list(params)
            await self._send_result(connection, request_id, result)
        except Exception as e:
            await self._send_error(connection, request_id, -32603, str(e))
    
    async def _handle_resources_list(self, connection: WebSocketConnection, request_id: str, params: Dict[str, Any]):
        """Handle resources list request"""
        try:
            result = self.protocol_handler.handle_resources_list(params)
            await self._send_result(connection, request_id, result)
        except Exception as e:
            await self._send_error(connection, request_id, -32603, str(e))
    
    async def _handle_resource_read(self, connection: WebSocketConnection, request_id: str, params: Dict[str, Any]):
        """Handle resource read request"""
        try:
            result = self.protocol_handler.handle_resources_read(params)
            await self._send_result(connection, request_id, result)
        except Exception as e:
            await self._send_error(connection, request_id, -32603, str(e))
    
    async def _handle_batch_method(self, connection: WebSocketConnection, request_id: str, method: str, params: Dict[str, Any]):
        """Handle batch-specific methods"""
        if method == "batch/cancel":
            operation_id = params.get('operation_id')
            if operation_id in connection.active_operations:
                connection.remove_operation(operation_id)
                await self._send_result(connection, request_id, {"cancelled": True})
            else:
                await self._send_error(connection, request_id, -32602, "Operation not found")
        else:
            await self._send_error(connection, request_id, -32601, f"Unknown batch method: {method}")
    
    async def _send_message(self, connection: WebSocketConnection, message: Dict[str, Any]):
        """Send message to WebSocket connection"""
        try:
            await connection.websocket.send(json.dumps(message))
        except Exception as e:
            api_logger.error(f"Failed to send message: {str(e)}")
    
    async def _send_result(self, connection: WebSocketConnection, request_id: str, result: Any):
        """Send JSON-RPC result"""
        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        await self._send_message(connection, message)
    
    async def _send_error(self, connection: WebSocketConnection, request_id: str, code: int, message: str):
        """Send JSON-RPC error"""
        error_message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        await self._send_message(connection, error_message)
    
    async def _send_progress(self, connection: WebSocketConnection, operation_id: str, status: str, message: str):
        """Send progress notification"""
        progress_message = {
            "jsonrpc": "2.0",
            "method": "notifications/progress",
            "params": {
                "operation_id": operation_id,
                "status": status,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        }
        await self._send_message(connection, progress_message)
    
    async def _cleanup_connections(self):
        """Periodic cleanup of stale connections"""
        while self.running:
            try:
                current_time = datetime.now()
                stale_connections = []
                
                for conn_id, connection in self.connections.items():
                    # Check for timeout (1 hour of inactivity)
                    if current_time - connection.last_activity > timedelta(hours=1):
                        stale_connections.append(conn_id)
                
                # Remove stale connections
                for conn_id in stale_connections:
                    if conn_id in self.connections:
                        connection = self.connections[conn_id]
                        await connection.websocket.close(code=1001, reason="Connection timeout")
                        del self.connections[conn_id]
                        self._log_connection(connection, "Timeout")
                
                # Wait 5 minutes before next cleanup
                await asyncio.sleep(300)
                
            except Exception as e:
                api_logger.error(f"Cleanup error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def start_server(self, host: str = "localhost", port: int = 8001):
        """Start the WebSocket server"""
        try:
            self.running = True
            
            # Start cleanup task
            self.cleanup_task = asyncio.create_task(self._cleanup_connections())
            
            # Start WebSocket server
            self.server = await websockets.serve(
                self.handle_connection,
                host,
                port,
                ping_interval=30,
                ping_timeout=10,
                max_size=1024*1024,  # 1MB max message size
                compression="deflate"
            )
            
            api_logger.info(f"WebSocket MCP server started on {host}:{port}")
            
            # Keep server running
            await self.server.wait_closed()
            
        except Exception as e:
            api_logger.error(f"WebSocket server error: {str(e)}")
            raise
        finally:
            self.running = False
            if self.cleanup_task:
                self.cleanup_task.cancel()
    
    async def stop_server(self):
        """Stop the WebSocket server"""
        try:
            self.running = False
            
            # Close all connections
            for connection in self.connections.values():
                await connection.websocket.close(code=1001, reason="Server shutdown")
            
            # Stop server
            if self.server:
                self.server.close()
                await self.server.wait_closed()
            
            # Cancel cleanup task
            if self.cleanup_task:
                self.cleanup_task.cancel()
            
            api_logger.info("WebSocket MCP server stopped")
            
        except Exception as e:
            api_logger.error(f"Error stopping WebSocket server: {str(e)}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get current connection statistics"""
        return {
            "total_connections": len(self.connections),
            "connections": [conn.get_connection_info() for conn in self.connections.values()],
            "server_running": self.running
        }

# Global WebSocket server instance
_websocket_server: Optional[WebSocketMCPServer] = None

def get_websocket_server() -> WebSocketMCPServer:
    """Get or create the global WebSocket server instance"""
    global _websocket_server
    if _websocket_server is None:
        _websocket_server = WebSocketMCPServer()
    return _websocket_server

def start_websocket_server_thread(host: str = "localhost", port: int = 8001):
    """Start WebSocket server in a separate thread"""
    def run_server():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        server = get_websocket_server()
        loop.run_until_complete(server.start_server(host, port))
    
    thread = Thread(target=run_server, daemon=True)
    thread.start()
    return thread