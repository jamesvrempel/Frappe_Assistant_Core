"""
Notification handler for MCP protocol
Handles notification requests like cancelled operations
"""

import frappe
from typing import Dict, Any, Optional

from frappe_assistant_core.constants.definitions import (
    ErrorCodes, ErrorMessages, LogMessages
)
from frappe_assistant_core.utils.logger import api_logger


def handle_notification_cancelled(params: Dict[str, Any], request_id: Optional[Any]) -> Dict[str, Any]:
    """
    Handle notification/cancelled requests
    
    This is sent when the client cancels an operation
    """
    try:
        api_logger.debug(f"Handling notification/cancelled with params: {params}")
        
        # Extract notification details
        request_id_to_cancel = params.get("requestId")
        reason = params.get("reason", "User cancelled")
        
        # Log the cancellation
        api_logger.info(f"Request cancelled - ID: {request_id_to_cancel}, Reason: {reason}")
        
        # Here you could implement cancellation logic:
        # - Stop running operations
        # - Clean up resources
        # - Update operation status
        
        # For now, just acknowledge the cancellation
        response = {
            "jsonrpc": "2.0",
            "result": {
                "cancelled": True,
                "requestId": request_id_to_cancel
            }
        }
        
        # Only include id if it's not None
        if request_id is not None:
            response["id"] = request_id
            
        api_logger.info(f"Cancellation acknowledged for request: {request_id_to_cancel}")
        return response
        
    except Exception as e:
        api_logger.error(f"Error in handle_notification_cancelled: {e}")
        
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