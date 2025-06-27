"""
Initialize handler for MCP protocol
Handles server initialization and capability declaration
"""

import frappe
from typing import Dict, Any, Optional

from frappe_assistant_core.constants.definitions import (
    MCP_PROTOCOL_VERSION, SERVER_NAME, SERVER_VERSION, ErrorCodes, ErrorMessages
)
from frappe_assistant_core.utils.logger import api_logger

def handle_initialize(params: Dict[str, Any], request_id: Optional[Any]) -> Dict[str, Any]:
    """Handle MCP initialize request with prompts capabilities"""
    try:
        api_logger.debug(f"Handling initialize request with params: {params}")
        
        response = {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    },
                    "prompts": {},  # Declare prompts capability
                    "resources": {
                        "subscribe": True,
                        "listChanged": True
                    },
                    "logging": {}
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": frappe.get_version() if frappe else SERVER_VERSION
                }
            }
        }
        
        # Only include id if it's not None
        if request_id is not None:
            response["id"] = request_id
            
        api_logger.info("Initialize request completed successfully")
        return response
        
    except Exception as e:
        api_logger.error(f"Error in handle_initialize: {e}")
        
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": ErrorCodes.INTERNAL_ERROR,
                "message": ErrorMessages.INTERNAL_ERROR,
                "data": str(e)
            }
        }
        
        # Only include id if it's not None
        if request_id is not None:
            response["id"] = request_id
            
        return response