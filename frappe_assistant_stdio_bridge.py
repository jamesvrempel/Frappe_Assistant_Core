#!/usr/bin/env python3
"""
Stdio assistant Wrapper for Frappe MCP Server
This wrapper allows Claude Desktop to communicate with your HTTP-based MCP server
"""

import json
import sys
import requests
import os
from typing import Dict, Any

class StdioMCPWrapper:
    def __init__(self):
        self.server_url = "http://127.0.0.1:8000"
        self.api_key = os.environ.get("FRAPPE_API_KEY")
        self.api_secret = os.environ.get("FRAPPE_API_SECRET")
        
        if not self.api_key or not self.api_secret:
            self.log_error("Missing FRAPPE_API_KEY or FRAPPE_API_SECRET environment variables")
            sys.exit(1)
        
        self.headers = {
            "Authorization": f"token {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json"
        }
    
    def log_error(self, message: str):
        """Log error to stderr"""
        print(f"ERROR: {message}", file=sys.stderr, flush=True)
    
    def log_debug(self, message: str):
        """Log debug info to stderr"""
        if os.environ.get("MCP_DEBUG"):
            print(f"DEBUG: {message}", file=sys.stderr, flush=True)
    
    def send_to_server(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to HTTP assistant server"""
        try:
            self.log_debug(f"Sending to server: {request_data}")
            
            response = requests.post(
                f"{self.server_url}/api/method/frappe_assistant_core.api.assistant_api.handle_assistant_request",
                headers=self.headers,
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log_debug(f"Received from server: {result}")
                
                # Frappe wraps responses in {"message": ...}
                # Extract the actual JSON-RPC response
                if isinstance(result, dict) and "message" in result:
                    extracted = result["message"]
                    # Validate and fix JSON-RPC format
                    return self.validate_jsonrpc_response(extracted, request_data.get("id"))
                else:
                    return self.validate_jsonrpc_response(result, request_data.get("id"))
            else:
                self.log_error(f"Server returned status {response.status_code}: {response.text}")
                return self.format_error_response(
                    -32603, 
                    f"Server error: {response.status_code}",
                    response.text,
                    request_data.get("id")
                )
                
        except requests.exceptions.ConnectionError:
            self.log_error("Cannot connect to assistant server. Make sure it's running on http://127.0.0.1:8000")
            return self.format_error_response(
                -32603,
                "Connection failed to assistant server",
                "Make sure the server is running on http://127.0.0.1:8000",
                request_data.get("id")
            )
        except Exception as e:
            self.log_error(f"Request failed: {e}")
            return self.format_error_response(
                -32603,
                "Internal error",
                str(e),
                request_data.get("id")
            )
    
    def validate_jsonrpc_response(self, response: Any, request_id: Any = None) -> Dict[str, Any]:
        """Validate and fix JSON-RPC response format"""
        if not isinstance(response, dict):
            # Convert non-dict responses to proper JSON-RPC format
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": response
            }
        
        # Ensure jsonrpc field is present
        if "jsonrpc" not in response:
            response["jsonrpc"] = "2.0"
        
        # Ensure id field is present if request had one
        if request_id is not None and "id" not in response:
            response["id"] = request_id
        
        # Validate that response has either result or error
        if "result" not in response and "error" not in response:
            # Wrap the entire response as result
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
            }
        }
        
        if data is not None:
            response["error"]["data"] = data
        
        # Only include id if it was present in request and not null
        if request_id is not None:
            response["id"] = request_id
            
        return response
    
    def handle_initialization(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle assistant initialization"""
        response = {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "prompts": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "frappe-assistant-core",
                    "version": "1.0.0"
                }
            }
        }
        
        # Only include id if it was present in request
        if "id" in request and request["id"] is not None:
            response["id"] = request["id"]
            
        return response
    
    def handle_resources_list(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request"""
        response = {
            "jsonrpc": "2.0",
            "result": {
                "resources": []  # Empty for now, can add resources later
            }
        }
        
        # Only include id if it was present in request
        if "id" in request and request["id"] is not None:
            response["id"] = request["id"]
            
        return response
    
    def run(self):
        """Main stdio loop"""
        self.log_debug("Starting Frappe assistant Stdio Wrapper")
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    self.log_debug(f"Received request: {request}")
                    
                    method = request.get("method")
                    request_id = request.get("id")
                    
                    # Handle methods locally or forward to HTTP server
                    if method == "initialize":
                        response = self.handle_initialization(request)
                    elif method == "resources/list":
                        response = self.handle_resources_list(request)
                    else:
                        # Forward all other requests (including prompts/*) to HTTP server
                        response = self.send_to_server(request)
                    
                    # Only send response if request had an id (notifications don't get responses)
                    if request_id is not None:
                        print(json.dumps(response), flush=True)
                    else:
                        self.log_debug(f"Notification processed: {method}")
                    
                except json.JSONDecodeError as e:
                    self.log_error(f"Invalid JSON received: {e}")
                    error_response = self.format_error_response(
                        -32700,
                        "Parse error",
                        str(e),
                        None
                    )
                    print(json.dumps(error_response), flush=True)
                
                except Exception as e:
                    self.log_error(f"Error processing request: {e}")
                    error_response = self.format_error_response(
                        -32603,
                        "Internal error",
                        str(e),
                        None
                    )
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            self.log_debug("Wrapper stopped by user")
        except Exception as e:
            self.log_error(f"Fatal error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    wrapper = StdioMCPWrapper()
    wrapper.run()