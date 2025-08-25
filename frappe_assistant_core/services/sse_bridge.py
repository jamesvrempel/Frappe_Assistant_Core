#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Frappe Assistant Core - SSE MCP Bridge Service
# Copyright (C) 2025 Paul Clinton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
SSE MCP Bridge Service for Frappe Assistant Core
"""

import json
import asyncio
import os
from typing import Dict, Any, Optional, AsyncGenerator, List
from contextlib import asynccontextmanager
import logging
import uuid
import time

try:
    import httpx
    from fastapi import FastAPI, HTTPException, Header, Request
    from fastapi.responses import StreamingResponse, JSONResponse
    from pydantic import BaseModel
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing required dependencies for SSE bridge: {e}")
    print("Please install with: pip install frappe_assistant_core[sse-bridge]")
    exit(1)

# Load environment variables from various sources
load_dotenv()  # Load from .env file if present
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class MCPRequest(BaseModel):
    """MCP request model"""
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Any] = None

class PendingRequest:
    """Represents a pending request waiting for SSE connection"""
    def __init__(self, request_data: Dict[str, Any], server_url: str, auth_token: str):
        self.request_data = request_data
        self.server_url = server_url
        self.auth_token = auth_token
        self.timestamp = time.time()

class SSEMCPBridge:
    def __init__(self):
        # Store active SSE connections mapped by user context
        self.connections: Dict[str, asyncio.Queue] = {}
        # Store connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        # Buffer for requests that arrive before SSE connection
        self.pending_requests: Dict[str, List[PendingRequest]] = {}
        # Grace period in seconds to wait for SSE connection
        self.connection_grace_period = 5.0
        # Maximum connection idle time before cleanup (in seconds)
        self.max_idle_time = 300.0  # 5 minutes
        # Connection heartbeat interval
        self.heartbeat_interval = 30.0  # 30 seconds
    
    async def validate_authorization(self, authorization: Optional[str], server_url: str) -> Optional[str]:
        """Validate authorization (Bearer token or API key) with Frappe and return user context"""
        logger.debug(f"Authorization header: {authorization[:50] if authorization else 'None'}...")
        
        if not authorization:
            logger.warning("Missing authorization header")
            return None
        
        try:
            frappe_server_url = server_url.rstrip('/')
            
            # Try OAuth Bearer token first
            if authorization.startswith('Bearer '):
                return await self._validate_auth_token(authorization, frappe_server_url)
            
            # Try API key:secret format (like stdio bridge)
            elif authorization.startswith('token '):
                return await self._validate_api_key(authorization, frappe_server_url)
            
            # Try as raw API key (assume it needs a secret from env)
            else:
                # Treat as API key, try to get secret from environment
                api_secret = os.environ.get("FRAPPE_API_SECRET")
                if api_secret:
                    token_auth = f"token {authorization}:{api_secret}"
                    return await self._validate_api_key(token_auth, frappe_server_url)
                else:
                    logger.warning("No FRAPPE_API_SECRET found for API key validation")
                    return None
                    
        except Exception as e:
            logger.error(f"Authorization validation error: {e}")
            return None
    
    async def _validate_auth_token(self, authorization: str, frappe_server_url: str) -> Optional[str]:
        """Validate OAuth Bearer token"""
        token = authorization.split(' ')[1]
        logger.info(f"Validating OAuth token: {token[:10]}...")
        
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{frappe_server_url}/api/method/frappe.auth.get_logged_user",
                headers=headers,
                timeout=10.0
            )
        
        if response.status_code == 200:
            result = response.json()
            user_email = None
            
            if isinstance(result, dict):
                if "message" in result:
                    user_email = result["message"]
                elif "user" in result:
                    user_email = result["user"]
            
            if user_email:
                user_context = f"user_{user_email.replace('@', '_').replace('.', '_')}"
                logger.info(f"OAuth validation successful for user: {user_context}")
                return user_context
            else:
                logger.warning("OAuth validation failed - no user in response")
                return None
        else:
            logger.warning(f"OAuth validation failed - status {response.status_code}: {response.text}")
            return None
    
    async def _validate_api_key(self, authorization: str, frappe_server_url: str) -> Optional[str]:
        """Validate API key:secret token (like stdio bridge)"""
        if authorization.startswith('token '):
            token_part = authorization.split(' ')[1]
            logger.info(f"Validating API key: {token_part.split(':')[0][:10]}...")
        else:
            logger.info(f"Validating API key: {authorization[:10]}...")
        
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json"
        }
        
        # Try the same endpoint as stdio bridge
        test_request = {
            "jsonrpc": "2.0",
            "method": "ping",
            "id": 1
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{frappe_server_url}/api/method/frappe_assistant_core.api.assistant_api.handle_assistant_request",
                headers=headers,
                json=test_request,
                timeout=10.0
            )
        
        if response.status_code == 200:
            # Extract user context from API key
            if authorization.startswith('token '):
                api_key = authorization.split(' ')[1].split(':')[0]
            else:
                api_key = authorization.split(':')[0]
            
            user_context = f"user_{api_key[:10]}"
            logger.info(f"API key validation successful for user: {user_context}")
            return user_context
        else:
            logger.warning(f"API key validation failed - status {response.status_code}: {response.text}")
            return None
    
    async def send_to_server(self, request_data: Dict[str, Any], server_url: str, authorization: str) -> Dict[str, Any]:
        """Send request to HTTP MCP server using authorization header"""
        try:
            server_url = server_url.rstrip('/')
            
            headers = {
                "Authorization": authorization,
                "Content-Type": "application/json"
            }
            
            logger.debug(f"Sending to server {server_url}: {request_data}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{server_url}/api/method/frappe_assistant_core.api.assistant_api.handle_assistant_request",
                    headers=headers,
                    json=request_data,
                    timeout=30.0
                )
            
            if response.status_code == 200:
                result = response.json()
                # logger.debug(f"Received from server: {result}")
                
                if isinstance(result, dict) and "message" in result:
                    extracted = result["message"]
                    final_response = self.validate_jsonrpc_response(extracted, request_data.get("id"))
                else:
                    final_response = self.validate_jsonrpc_response(result, request_data.get("id"))
                
                # Log the actual response being sent back
                if request_data.get("method") == "tools/list":
                    tools_count = 0
                    if isinstance(final_response, dict) and "result" in final_response:
                        if isinstance(final_response["result"], dict) and "tools" in final_response["result"]:
                            tools_count = len(final_response["result"]["tools"])
                    logger.info(f"tools/list response contains {tools_count} tools")
                
                return final_response
            else:
                logger.error(f"Server returned status {response.status_code}: {response.text}")
                return self.format_error_response(
                    -32603, 
                    f"Server error: {response.status_code}",
                    response.text,
                    request_data.get("id")
                )
                
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return self.format_error_response(
                -32603,
                "Internal error",
                str(e),
                request_data.get("id")
            )
    
    def validate_jsonrpc_response(self, response: Any, request_id: Any = None) -> Dict[str, Any]:
        """Validate and fix JSON-RPC response format"""
        if not isinstance(response, dict):
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": response
            }
        
        if "jsonrpc" not in response:
            response["jsonrpc"] = "2.0"
        
        # Always ensure id field is present for JSON-RPC compliance
        # This is especially important for error responses
        if "id" not in response:
            response["id"] = request_id
        
        if "result" not in response and "error" not in response:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": response
            }
        
        return response
    
    def format_error_response(self, code: int, message: str, data: Any = None, request_id: Any = None) -> Dict[str, Any]:
        """Format a JSON-RPC error response"""
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            # Always include id field, even if null, to comply with JSON-RPC spec
            "id": request_id
        }
        
        if data is not None:
            response["error"]["data"] = data
            
        return response
    
    async def handle_initialization(self, request: Dict[str, Any], server_url: str, auth_token: str) -> Dict[str, Any]:
        """Handle MCP initialization - fetch capabilities from actual server"""
        try:
            # Forward initialization to the actual Frappe server to get real capabilities
            server_response = await self.send_to_server(request, server_url, auth_token)
            
            # If server responded with capabilities, use them
            if (isinstance(server_response, dict) and 
                "result" in server_response and 
                isinstance(server_response["result"], dict) and
                "capabilities" in server_response["result"]):
                
                logger.info("Using capabilities from Frappe server")
                return server_response
            
        except Exception as e:
            logger.warning(f"Failed to get capabilities from server: {e}")
        
        # Fallback to default capabilities
        logger.info("Using default SSE bridge capabilities")
        response = {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    },
                    "prompts": {
                        "listChanged": True  
                    },
                    "resources": {
                        "listChanged": True
                    }
                },
                "serverInfo": {
                    "name": "frappe-mcp-sse-bridge",
                    "version": "2.0.0"
                }
            }
        }
        
        if "id" in request and request["id"] is not None:
            response["id"] = request["id"]
            
        return response
    
    def handle_resources_list(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request"""
        response = {
            "jsonrpc": "2.0",
            "result": {
                "resources": []
            }
        }
        
        if "id" in request and request["id"] is not None:
            response["id"] = request["id"]
            
        return response
    
    def handle_ping(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping request for connection testing"""
        response = {
            "jsonrpc": "2.0",
            "result": {
                "status": "ok",
                "timestamp": time.time(),
                "service": "frappe-mcp-sse-bridge",
                "message": "pong"
            }
        }
        
        if "id" in request and request["id"] is not None:
            response["id"] = request["id"]
            
        return response
    
    def handle_notifications_initialized(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle notifications/initialized - MCP protocol notification sent after initialization"""
        # This is a notification (no id field expected), just acknowledge it
        # Notifications don't require a response in MCP protocol
        logger.info("Client sent notifications/initialized - client is ready")
        
        # Since this is a notification (no id), we shouldn't send a response
        # But if it has an id (which would be non-standard), respond appropriately
        if "id" in request and request["id"] is not None:
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {"status": "acknowledged"}
            }
        
        # For standard notifications (no id), return empty response that won't be sent
        return None
    
    async def queue_response_for_connection(self, user_context: str, response: Dict[str, Any]):
        """Queue a response to be sent via SSE to the appropriate connection"""
        if user_context in self.connections:
            await self.connections[user_context].put(response)
            # Better logging for debugging
            response_id = response.get('id')
            if "result" in response and isinstance(response["result"], dict) and "tools" in response["result"]:
                tools_count = len(response["result"]["tools"])
                logger.info(f"Queued tools/list response for user {user_context}: id={response_id}, tools={tools_count}")
            else:
                logger.info(f"Queued response for user {user_context}: id={response_id}")
        else:
            logger.warning(f"No active SSE connection for user {user_context}")
    
    async def process_pending_requests(self, user_context: str):
        """Process any pending requests for a user once their SSE connection is established"""
        if user_context in self.pending_requests:
            pending = self.pending_requests.pop(user_context)
            logger.info(f"Processing {len(pending)} pending requests for user {user_context}")
            
            for req in pending:
                try:
                    await self.process_mcp_request(
                        req.request_data,
                        req.server_url,
                        req.auth_token,
                        user_context,
                        use_sse=True
                    )
                except Exception as e:
                    logger.error(f"Error processing pending request: {e}")
    
    async def cleanup_old_pending_requests(self):
        """Remove old pending requests that have exceeded the grace period"""
        current_time = time.time()
        for user_context in list(self.pending_requests.keys()):
            pending = self.pending_requests.get(user_context, [])
            # Remove requests older than grace period
            self.pending_requests[user_context] = [
                req for req in pending 
                if current_time - req.timestamp < self.connection_grace_period
            ]
            # Remove user entry if no pending requests
            if not self.pending_requests[user_context]:
                del self.pending_requests[user_context]
    
    async def process_mcp_request(self, request_data: Dict[str, Any], server_url: str, 
                                  auth_token: str, user_context: str, use_sse: bool = True) -> Dict[str, Any]:
        """Process MCP request and optionally queue response for SSE"""
        try:
            method = request_data.get("method")
            request_id = request_data.get("id")
            
            logger.info(f"Processing MCP request: {method} (id: {request_id}) for server: {server_url}")
            
            # Handle methods locally or forward to HTTP server
            if method == "initialize":
                response = await self.handle_initialization(request_data, server_url, auth_token)
            elif method == "resources/list":
                response = self.handle_resources_list(request_data)
            elif method == "ping":
                # Handle ping request - this is for JSON-RPC ping, not SSE keep-alive
                response = self.handle_ping(request_data)
            elif method == "notifications/initialized":
                # Handle MCP protocol notification - client is ready
                response = self.handle_notifications_initialized(request_data)
            else:
                # Forward all other requests to HTTP server
                response = await self.send_to_server(request_data, server_url, auth_token)
            
            # If using SSE, queue the response for the SSE stream
            if use_sse and user_context in self.connections:
                # Only queue response if it's not None (notifications may not need responses)
                if response is not None:
                    await self.queue_response_for_connection(user_context, response)
                # Return a simple acknowledgment for POST request
                return {"status": "accepted", "id": request_id}
            else:
                # Return response directly (for non-SSE requests)
                return response
            
        except Exception as e:
            logger.error(f"Error processing MCP request: {e}")
            error_response = self.format_error_response(
                -32603,
                "Internal error",
                str(e),
                request_data.get("id")
            )
            
            if use_sse and user_context in self.connections:
                await self.queue_response_for_connection(user_context, error_response)
                return {"status": "error", "id": request_id}
            else:
                return error_response

# Initialize bridge
bridge = SSEMCPBridge()

# Background task to cleanup old pending requests
async def cleanup_task():
    """Periodically cleanup old pending requests"""
    while True:
        await asyncio.sleep(10)  # Run every 10 seconds
        await bridge.cleanup_old_pending_requests()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Frappe Assistant Core SSE MCP Bridge")
    # Start cleanup task
    cleanup = asyncio.create_task(cleanup_task())
    yield
    # Cancel cleanup task
    cleanup.cancel()
    logger.info("Shutting down Frappe Assistant Core SSE MCP Bridge")

# Create FastAPI app
def create_app():
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Frappe Assistant Core SSE Bridge",
        description="SSE bridge for Frappe Assistant Core MCP integration",
        version="2.0.0",
        lifespan=lifespan
    )

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy", 
            "service": "frappe-assistant-core-sse-bridge",
            "active_connections": len(bridge.connections),
            "pending_requests": sum(len(reqs) for reqs in bridge.pending_requests.values())
        }

    @app.get("/mcp/sse")
    async def mcp_sse_endpoint_get(
        request: Request,
        server_url: str,
        authorization: Optional[str] = Header(None)
    ):
        """SSE endpoint for MCP - establishes SSE stream and provides endpoint URL"""
        
        # Validate authorization (OAuth or API key)
        user_context = await bridge.validate_authorization(authorization, server_url)
        if not user_context:
            raise HTTPException(status_code=401, detail="Invalid or missing authorization token")
        
        # Store the full authorization header for later use
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing authorization header")
        
        async def generate_sse_stream() -> AsyncGenerator[str, None]:
            """Generate SSE stream for MCP responses"""
            
            connection_id = f"{user_context}_{uuid.uuid4().hex[:8]}"
            response_queue = asyncio.Queue()
            
            # Store connection info
            bridge.connections[user_context] = response_queue
            bridge.connection_metadata[user_context] = {
                "connection_id": connection_id,
                "server_url": server_url,
                "auth_token": authorization
            }
            
            try:
                logger.info(f"SSE connection established: {connection_id} for user: {user_context}")
                
                # Send endpoint event - tells client where to send POST messages
                endpoint_url = f"/mcp/messages?session_id={connection_id}"
                yield f"event: endpoint\n"
                yield f"data: {endpoint_url}\n\n"
                
                # Give the connection a moment to stabilize
                await asyncio.sleep(0.1)
                
                # Process any pending requests
                await bridge.process_pending_requests(user_context)
                
                # Keep connection alive and send queued responses
                ping_counter = 0
                while True:
                    try:
                        # Wait for responses to send (with timeout for ping)
                        response = await asyncio.wait_for(response_queue.get(), timeout=5.0)
                        yield f"event: message\n"
                        yield f"data: {json.dumps(response)}\n\n"
                        logger.info(f"Sent SSE response: {response.get('id')} to {connection_id}")
                        
                    except asyncio.TimeoutError:
                        # Send periodic ping as a comment to keep connection alive
                        # SSE comments start with ':' and don't trigger events in clients
                        ping_counter += 1
                        ping_timestamp = time.time()
                        # Send as SSE comment - this keeps the connection alive without triggering unknown event warnings
                        yield f": ping {ping_counter} at {ping_timestamp}\n\n"
                        
                    except Exception as e:
                        logger.error(f"Error in SSE stream: {e}")
                        # Include a null id for stream errors to comply with JSON-RPC spec
                        error_response = bridge.format_error_response(-32603, "Stream error", str(e), request_id=None)
                        yield f"event: error\n"
                        yield f"data: {json.dumps(error_response)}\n\n"
                        break
                        
            except Exception as e:
                logger.error(f"SSE connection error: {e}")
                
            finally:
                # Cleanup connection
                if user_context in bridge.connections:
                    del bridge.connections[user_context]
                if user_context in bridge.connection_metadata:
                    del bridge.connection_metadata[user_context]
                logger.info(f"SSE connection closed: {connection_id}")
        
        return StreamingResponse(
            generate_sse_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Authorization",
            }
        )

    @app.post("/mcp/messages")
    async def mcp_messages_endpoint(
        request: Request,
        session_id: str,
        authorization: Optional[str] = Header(None)
    ):
        """MCP message endpoint - handles POST messages from client"""
        
        # Find the user context and server URL from session_id
        user_context = None
        server_url = None
        
        for ctx, meta in bridge.connection_metadata.items():
            if session_id in meta.get("connection_id", ""):
                user_context = ctx
                server_url = meta.get("server_url")
                break
        
        if not user_context or not server_url:
            raise HTTPException(status_code=400, detail="Invalid session ID or no active connection")
        
        # Validate authorization (OAuth or API key) - this ensures the token is still valid
        validated_user = await bridge.validate_authorization(authorization, server_url)
        if not validated_user or validated_user != user_context:
            raise HTTPException(status_code=401, detail="Invalid or missing authorization token")
        
        # Double-check connection exists
        if user_context not in bridge.connections:
            raise HTTPException(status_code=400, detail="No active SSE connection")
        
        try:
            # Read the MCP request from POST body
            body = await request.body()
            mcp_request = json.loads(body.decode('utf-8'))
            
            logger.info(f"Received MCP message: {mcp_request.get('method')} (id: {mcp_request.get('id')}) from {user_context}")
            
            # Get auth token from connection metadata (we already have server_url from above)
            metadata = bridge.connection_metadata.get(user_context, {})
            auth_token = metadata.get("auth_token")
            
            if not auth_token:
                raise HTTPException(status_code=500, detail="Connection metadata missing auth token")
            
            # Process the MCP request and queue response for SSE
            await bridge.process_mcp_request(
                mcp_request, 
                server_url, 
                auth_token, 
                user_context,
                use_sse=True
            )
            
            # Return simple acknowledgment
            return JSONResponse(
                content={"status": "accepted"},
                status_code=202  # Accepted
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in POST request: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON in request body")
        
        except Exception as e:
            logger.error(f"Error processing MCP message: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    # Add other endpoints...
    return app

def main():
    """Main entry point for the SSE bridge service"""
    import uvicorn
    
    # Get configuration from environment
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting Frappe Assistant Core SSE MCP Bridge on {host}:{port}")
    logger.info("Bridge configured to handle race conditions")
    logger.info("POST requests are buffered if SSE connection not established")
    logger.info(f"Grace period for pending requests: {bridge.connection_grace_period}s")
    
    # Create app
    app = create_app()
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )

if __name__ == "__main__":
    main()

# Make this module executable via python -m
def __main__():
    main()