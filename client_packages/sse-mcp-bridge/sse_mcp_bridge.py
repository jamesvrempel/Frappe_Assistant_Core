#!/usr/bin/env python3
"""
SSE MCP Bridge for Frappe MCP Server
This FastAPI app allows Claude API to communicate with your HTTP-based MCP server via SSE

Usage with Claude API:
```javascript
const response = await anthropic.beta.messages.create({
  model: "claude-sonnet-4-20250514",
  messages: [{ role: "user", content: "Get my sales data" }],
  mcp_servers: [{
    type: "url",
    url: "https://your-bridge.com/mcp/sse?server_url=https://your-frappe.com",
    name: "frappe-erp",
    authorization_token: "YOUR_FRAPPE_OAUTH_TOKEN"
  }],
  betas: ["mcp-client-2025-04-04"]
});
```

Features:
- Dynamic Frappe server URLs (multi-tenant support)
- OAuth token pass-through (same token for bridge and Frappe)
- No hardcoded credentials
- Compatible with Claude API MCP connector
"""

import json
import asyncio
import os
from typing import Dict, Any, Optional, AsyncGenerator
from contextlib import asynccontextmanager
import logging

import httpx
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Configure logging to stderr (important for production)
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

class SSEMCPBridge:
    def __init__(self):
        # Store active SSE connections and pending requests
        self.connections: Dict[str, asyncio.Queue] = {}
        self.pending_requests: Dict[str, asyncio.Queue] = {}
    
    def validate_oauth_token(self, authorization: Optional[str]) -> Optional[str]:
        """Validate OAuth Bearer token and return user context"""
        if not authorization or not authorization.startswith('Bearer '):
            return None
        
        token = authorization.split(' ')[1]
        
        # TODO: Implement actual OAuth token validation with Frappe
        # For now, just validate it's present
        # In production, you'd validate against Frappe's OAuth system
        
        logger.info(f"Validating OAuth token: {token[:10]}...")
        
        # Placeholder - replace with actual Frappe OAuth validation
        if len(token) > 10:  # Basic validation
            return "authenticated_user"  # Return user ID/context
        
        return None
    
    async def send_to_server(self, request_data: Dict[str, Any], server_url: str, oauth_token: str) -> Dict[str, Any]:
        """Send request to HTTP MCP server using OAuth token"""
        try:
            # Remove trailing slash if present
            server_url = server_url.rstrip('/')
            
            headers = {
                "Authorization": f"Bearer {oauth_token}",
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
                logger.debug(f"Received from server: {result}")
                
                # Frappe wraps responses in {"message": ...}
                # Extract the actual JSON-RPC response
                if isinstance(result, dict) and "message" in result:
                    extracted = result["message"]
                    return self.validate_jsonrpc_response(extracted, request_data.get("id"))
                else:
                    return self.validate_jsonrpc_response(result, request_data.get("id"))
            else:
                logger.error(f"Server returned status {response.status_code}: {response.text}")
                return self.format_error_response(
                    -32603, 
                    f"Server error: {response.status_code}",
                    response.text,
                    request_data.get("id")
                )
                
        except httpx.ConnectError:
            logger.error(f"Cannot connect to MCP server at {server_url}")
            return self.format_error_response(
                -32603,
                "Connection failed to MCP server",
                f"Make sure the server is running at {server_url}",
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
        """Validate and fix JSON-RPC response format (same as STDIO bridge)"""
        if not isinstance(response, dict):
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": response
            }
        
        if "jsonrpc" not in response:
            response["jsonrpc"] = "2.0"
        
        if request_id is not None and "id" not in response:
            response["id"] = request_id
        
        if "result" not in response and "error" not in response:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": response
            }
        
        return response
    
    def format_error_response(self, code: int, message: str, data: Any = None, request_id: Any = None) -> Dict[str, Any]:
        """Format a JSON-RPC error response (same as STDIO bridge)"""
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            }
        }
        
        if data is not None:
            response["error"]["data"] = data
        
        if request_id is not None:
            response["id"] = request_id
            
        return response
    
    def handle_initialization(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialization (same as STDIO bridge)"""
        response = {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {},
                    "prompts": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "frappe-mcp-sse-bridge",
                    "version": "1.0.0"
                }
            }
        }
        
        if "id" in request and request["id"] is not None:
            response["id"] = request["id"]
            
        return response
    
    def handle_resources_list(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request (same as STDIO bridge)"""
        response = {
            "jsonrpc": "2.0",
            "result": {
                "resources": []
            }
        }
        
        if "id" in request and request["id"] is not None:
            response["id"] = request["id"]
            
        return response
    
    async def process_mcp_request(self, request_data: Dict[str, Any], server_url: str, oauth_token: str) -> Dict[str, Any]:
        """Process MCP request (adapted from STDIO bridge logic)"""
        try:
            method = request_data.get("method")
            request_id = request_data.get("id")
            
            logger.info(f"Processing MCP request: {method} (id: {request_id}) for server: {server_url}")
            
            # Handle methods locally or forward to HTTP server
            if method == "initialize":
                response = self.handle_initialization(request_data)
            elif method == "resources/list":
                response = self.handle_resources_list(request_data)
            else:
                # Forward all other requests to HTTP server
                response = await self.send_to_server(request_data, server_url, oauth_token)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing MCP request: {e}")
            return self.format_error_response(
                -32603,
                "Internal error",
                str(e),
                request_data.get("id")
            )

# Initialize bridge
bridge = SSEMCPBridge()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting SSE MCP Bridge")
    yield
    logger.info("Shutting down SSE MCP Bridge")

# Create FastAPI app
app = FastAPI(
    title="Frappe MCP SSE Bridge",
    description="SSE bridge for Frappe MCP Server compatible with Claude API",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "frappe-mcp-sse-bridge"}

@app.post("/mcp/request")
async def handle_mcp_request(
    request: MCPRequest,
    server_url: str,  # Required parameter for Frappe server URL
    authorization: Optional[str] = Header(None)
):
    """Handle individual MCP requests (for testing or alternative access)"""
    
    # Validate OAuth token
    user_context = bridge.validate_oauth_token(authorization)
    if not user_context:
        raise HTTPException(status_code=401, detail="Invalid or missing authorization token")
    
    # Extract OAuth token
    oauth_token = authorization.split(' ')[1] if authorization and authorization.startswith('Bearer ') else None
    if not oauth_token:
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    # Process the request
    response = await bridge.process_mcp_request(request.dict(), server_url, oauth_token)
    return response

@app.get("/mcp/sse")
async def mcp_sse_endpoint(
    request: Request,
    server_url: str,  # Required parameter for Frappe server URL
    authorization: Optional[str] = Header(None)
):
    """
    SSE endpoint for Claude API MCP connector
    
    This is the main endpoint that Claude API will connect to.
    It streams MCP responses and handles the SSE protocol.
    
    Parameters:
    - server_url: The Frappe server URL to connect to
    - authorization: Bearer token for OAuth authentication
    """
    
    # Validate OAuth token
    user_context = bridge.validate_oauth_token(authorization)
    if not user_context:
        raise HTTPException(status_code=401, detail="Invalid or missing authorization token")
    
    # Extract OAuth token
    oauth_token = authorization.split(' ')[1] if authorization and authorization.startswith('Bearer ') else None
    if not oauth_token:
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    async def generate_sse_stream() -> AsyncGenerator[str, None]:
        """Generate SSE stream for MCP responses"""
        
        connection_id = f"{user_context}_{id(request)}"
        response_queue = asyncio.Queue()
        bridge.connections[connection_id] = response_queue
        
        try:
            logger.info(f"SSE connection established: {connection_id} for server: {server_url}")
            
            # Send initial capabilities as first event
            init_response = bridge.handle_initialization({"jsonrpc": "2.0", "method": "initialize", "id": 1})
            yield f"data: {json.dumps(init_response)}\n\n"
            
            # Keep connection alive and handle incoming requests
            while True:
                try:
                    # Wait for responses to send (with timeout for keepalive)
                    response = await asyncio.wait_for(response_queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(response)}\n\n"
                    
                except asyncio.TimeoutError:
                    # Send keepalive ping
                    yield f": keepalive\n\n"
                    
                except Exception as e:
                    logger.error(f"Error in SSE stream: {e}")
                    error_response = bridge.format_error_response(-32603, "Stream error", str(e))
                    yield f"data: {json.dumps(error_response)}\n\n"
                    break
                    
        except Exception as e:
            logger.error(f"SSE connection error: {e}")
            
        finally:
            # Cleanup connection
            if connection_id in bridge.connections:
                del bridge.connections[connection_id]
            logger.info(f"SSE connection closed: {connection_id}")
    
    return StreamingResponse(
        generate_sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Authorization",
        }
    )

@app.post("/mcp/tools/call")
async def handle_tool_call(
    request: MCPRequest,
    server_url: str,  # Required parameter for Frappe server URL
    authorization: Optional[str] = Header(None)
):
    """
    Handle MCP tool calls (if Claude API sends them separately)
    
    This might be needed if Claude API separates tool calls from the SSE stream
    """
    
    # Validate OAuth token
    user_context = bridge.validate_oauth_token(authorization)
    if not user_context:
        raise HTTPException(status_code=401, detail="Invalid or missing authorization token")
    
    # Extract OAuth token
    oauth_token = authorization.split(' ')[1] if authorization and authorization.startswith('Bearer ') else None
    if not oauth_token:
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    # Process the tool call
    response = await bridge.process_mcp_request(request.dict(), server_url, oauth_token)
    
    # Send response via SSE if connection exists
    connection_id = f"{user_context}_active"  # You'd need to track this properly
    if connection_id in bridge.connections:
        await bridge.connections[connection_id].put(response)
    
    return response

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting SSE MCP Bridge on {host}:{port}")
    logger.info("Bridge configured for dynamic Frappe server URLs via parameters")
    
    uvicorn.run(
        "sse_mcp_bridge:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug"
    )

# Environment Variables:
# HOST=0.0.0.0                    # Server host (optional)
# PORT=8000                       # Server port (optional) 
# DEBUG=false                     # Debug mode (optional)
#
# No Frappe credentials needed - passed via OAuth tokens and URL parameters!