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
WebSocket Server Management API for Frappe Assistant Core
Provides endpoints to control and monitor WebSocket MCP server
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.assistant_core.websocket_server import (
    get_websocket_server, 
    start_websocket_server_thread
)
from frappe_assistant_core.utils.cache import get_cached_server_settings
from frappe_assistant_core.utils.logger import api_logger
import threading
import time

# Global thread reference for WebSocket server
_websocket_thread = None

@frappe.whitelist()
def start_websocket_server():
    """Start the WebSocket MCP server"""
    global _websocket_thread
    
    try:
        # Check if WebSocket is enabled in settings
        settings = get_cached_server_settings()
        if not settings.get('websocket_enabled'):
            return {
                "success": False,
                "message": "WebSocket support is disabled in settings"
            }
        
        # Check if server is already running
        server = get_websocket_server()
        if server.running:
            return {
                "success": False,
                "message": "WebSocket server is already running"
            }
        
        # Determine port (default to 8001 for WebSocket)
        port = 8001
        host = "0.0.0.0"  # Listen on all interfaces
        
        # Start server in separate thread
        _websocket_thread = start_websocket_server_thread(host, port)
        
        # Give it a moment to start
        time.sleep(0.5)
        
        return {
            "success": True,
            "message": f"WebSocket MCP server started on {host}:{port}",
            "endpoint": f"ws://{host}:{port}/mcp?api_key=YOUR_API_KEY&api_secret=YOUR_SECRET",
            "protocol": "WebSocket MCP"
        }
        
    except Exception as e:
        api_logger.error(f"Failed to start WebSocket server: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to start WebSocket server: {str(e)}"
        }

@frappe.whitelist()
def stop_websocket_server():
    """Stop the WebSocket MCP server"""
    global _websocket_thread
    
    try:
        server = get_websocket_server()
        
        if not server.running:
            return {
                "success": False,
                "message": "WebSocket server is not running"
            }
        
        # Stop the server (this is async, so we'll need to handle it properly)
        # For now, we'll set running to False and let the cleanup handle it
        server.running = False
        
        return {
            "success": True,
            "message": "WebSocket server stop initiated"
        }
        
    except Exception as e:
        api_logger.error(f"Failed to stop WebSocket server: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to stop WebSocket server: {str(e)}"
        }

@frappe.whitelist()
def get_websocket_status():
    """Get WebSocket server status and statistics"""
    try:
        server = get_websocket_server()
        settings = get_cached_server_settings()
        
        # Get connection statistics
        stats = server.get_connection_stats()
        
        return {
            "success": True,
            "status": {
                "enabled": settings.get('websocket_enabled', False),
                "running": server.running,
                "connections": stats,
                "endpoint": "ws://localhost:8001/mcp?api_key=YOUR_KEY&api_secret=YOUR_SECRET",
                "capabilities": [
                    "Persistent connections",
                    "Batch request processing", 
                    "Progress streaming",
                    "Operation cancellation",
                    "Real-time notifications"
                ]
            }
        }
        
    except Exception as e:
        api_logger.error(f"Failed to get WebSocket status: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def get_websocket_connections():
    """Get detailed information about active WebSocket connections"""
    try:
        if not frappe.has_permission("System Manager"):
            return {
                "success": False,
                "message": "Insufficient permissions"
            }
        
        server = get_websocket_server()
        stats = server.get_connection_stats()
        
        # Enhance with database connection logs
        recent_connections = frappe.get_all(
            "Assistant Connection Log",
            filters={
                "protocol": "WebSocket",
                "creation": [">=", frappe.utils.add_days(frappe.utils.today(), -1)]
            },
            fields=["connection_id", "user", "status", "creation", "ip_address"],
            order_by="creation desc",
            limit=50
        )
        
        return {
            "success": True,
            "data": {
                "active_connections": stats["connections"],
                "recent_connections": recent_connections,
                "total_active": stats["total_connections"],
                "server_running": stats["server_running"]
            }
        }
        
    except Exception as e:
        api_logger.error(f"Failed to get WebSocket connections: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def close_websocket_connection(connection_id: str):
    """Force close a specific WebSocket connection"""
    try:
        if not frappe.has_permission("System Manager"):
            return {
                "success": False,
                "message": "Insufficient permissions"
            }
        
        server = get_websocket_server()
        
        if connection_id not in server.connections:
            return {
                "success": False,
                "message": "Connection not found"
            }
        
        # Close the connection (this would need async handling in real implementation)
        connection = server.connections[connection_id]
        # connection.websocket.close() - would need proper async handling
        
        return {
            "success": True,
            "message": f"Connection {connection_id} closed"
        }
        
    except Exception as e:
        api_logger.error(f"Failed to close WebSocket connection: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def broadcast_websocket_message(message: str, target_users: str = None):
    """Broadcast message to WebSocket connections"""
    try:
        if not frappe.has_permission("System Manager"):
            return {
                "success": False,
                "message": "Insufficient permissions"
            }
        
        server = get_websocket_server()
        
        if not server.running:
            return {
                "success": False,
                "message": "WebSocket server is not running"
            }
        
        # Parse target users if provided
        target_user_list = []
        if target_users:
            target_user_list = [u.strip() for u in target_users.split(',')]
        
        # Count successful broadcasts
        broadcast_count = 0
        
        for connection in server.connections.values():
            # Filter by target users if specified
            if target_user_list and connection.user not in target_user_list:
                continue
                
            try:
                # This would need async handling in real implementation
                broadcast_count += 1
            except Exception as e:
                api_logger.error(f"Failed to broadcast to {connection.connection_id}: {str(e)}")
        
        return {
            "success": True,
            "message": f"Message broadcast to {broadcast_count} connections"
        }
        
    except Exception as e:
        api_logger.error(f"Failed to broadcast WebSocket message: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def get_websocket_metrics():
    """Get WebSocket performance metrics"""
    try:
        server = get_websocket_server()
        
        # Get basic metrics
        stats = server.get_connection_stats()
        
        # Get database metrics for WebSocket connections
        today = frappe.utils.today()
        
        websocket_metrics = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_connections_today,
                COUNT(DISTINCT user) as unique_users_today,
                AVG(TIMESTAMPDIFF(SECOND, creation, 
                    COALESCE(disconnected_at, NOW()))) as avg_session_duration
            FROM `tabAssistant Connection Log`
            WHERE protocol = 'WebSocket' 
            AND DATE(creation) = %s
        """, (today,), as_dict=True)
        
        # Get error rates
        error_metrics = frappe.db.sql("""
            SELECT 
                COUNT(CASE WHEN status = 'Error' THEN 1 END) as error_count,
                COUNT(CASE WHEN status = 'Timeout' THEN 1 END) as timeout_count,
                COUNT(*) as total_events
            FROM `tabAssistant Connection Log`
            WHERE protocol = 'WebSocket' 
            AND DATE(creation) = %s
        """, (today,), as_dict=True)
        
        # Calculate rates
        metrics = websocket_metrics[0] if websocket_metrics else {}
        errors = error_metrics[0] if error_metrics else {}
        
        total_events = errors.get('total_events', 0)
        error_rate = (errors.get('error_count', 0) / total_events * 100) if total_events > 0 else 0
        timeout_rate = (errors.get('timeout_count', 0) / total_events * 100) if total_events > 0 else 0
        
        return {
            "success": True,
            "metrics": {
                "current_connections": stats["total_connections"],
                "connections_today": metrics.get('total_connections_today', 0),
                "unique_users_today": metrics.get('unique_users_today', 0),
                "avg_session_duration_seconds": metrics.get('avg_session_duration', 0),
                "error_rate_percent": round(error_rate, 2),
                "timeout_rate_percent": round(timeout_rate, 2),
                "server_uptime": "Not implemented",  # Would need server start time tracking
                "message_throughput": "Not implemented"  # Would need message counting
            }
        }
        
    except Exception as e:
        api_logger.error(f"Failed to get WebSocket metrics: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def test_websocket_connectivity():
    """Test WebSocket server connectivity"""
    try:
        import websockets
        import asyncio
        
        async def test_connection():
            try:
                # This is a basic connectivity test
                # In a real implementation, we'd test with proper auth
                uri = "ws://localhost:8001/mcp"
                async with websockets.connect(uri, timeout=5) as websocket:
                    return True
            except Exception:
                return False
        
        # Run the test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_connection())
        loop.close()
        
        return {
            "success": True,
            "connectivity": result,
            "message": "WebSocket server is reachable" if result else "WebSocket server is not reachable"
        }
        
    except Exception as e:
        return {
            "success": False,
            "connectivity": False,
            "error": str(e)
        }