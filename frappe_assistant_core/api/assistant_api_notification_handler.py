"""
Notification handler for MCP API
"""

def handle_notification_cancelled(params, request_id):
    """Handle notifications/cancelled request"""
    try:
        print(f"🔧 Handling notification cancelled for request {params.get('requestId')}: {params.get('reason')}")
        
        # For notifications, we typically don't need to return anything special
        # Just acknowledge that we received the cancellation
        response = {
            "jsonrpc": "2.0",
            "result": {
                "acknowledged": True,
                "requestId": params.get("requestId"),
                "reason": params.get("reason")
            }
        }
        
        # Only include id if it's not None
        if request_id is not None:
            response["id"] = request_id
            
        return response
        
    except Exception as e:
        print(f"❌ Error in handle_notification_cancelled: {e}")
        
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Error handling notification",
                "data": str(e)
            }
        }
        
        # Only include id if it's not None
        if request_id is not None:
            response["id"] = request_id
            
        return response