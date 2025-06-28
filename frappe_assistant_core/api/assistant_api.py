"""
Clean refactored Assistant API with modular handlers and proper logging
"""

import frappe
import json
from typing import Dict, Any, Optional

from frappe_assistant_core.constants.definitions import (
    ErrorCodes, ErrorMessages, LogMessages, MCP_PROTOCOL_VERSION
)
from frappe_assistant_core.utils.logger import api_logger
from frappe_assistant_core.api.handlers import (
    handle_initialize, handle_tools_list, handle_tool_call,
    handle_prompts_list, handle_prompts_get
)


@frappe.whitelist(allow_guest=False, methods=["POST"])
def handle_assistant_request() -> Dict[str, Any]:
    """Handle assistant protocol requests"""
    
    # SECURITY: Validate user context immediately
    if not frappe.session.user or frappe.session.user == "Guest":
        api_logger.warning("Authentication attempt without valid session")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": ErrorCodes.AUTHENTICATION_REQUIRED,
                "message": ErrorMessages.AUTHENTICATION_REQUIRED
            }
        }
    
    # SECURITY: Check if user has assistant access
    from frappe_assistant_core.utils.permissions import check_assistant_permission
    if not check_assistant_permission(frappe.session.user):
        api_logger.warning(f"Access denied for user: {frappe.session.user}")
        return {
            "jsonrpc": "2.0", 
            "error": {
                "code": ErrorCodes.AUTHENTICATION_REQUIRED,
                "message": ErrorMessages.ACCESS_DENIED
            }
        }
    
    api_logger.info(LogMessages.API_AUTHENTICATED.format(frappe.session.user))
    
    try:
        # Log connection
        log_assistant_connection()
    except Exception as e:
        api_logger.debug(f"Connection logging failed: {e}")
        
    try:
        # Get request data
        data = _extract_request_data()
        api_logger.debug(LogMessages.API_RECEIVED_DATA.format(data))
        
        # Validate JSON-RPC 2.0 format
        validation_response = _validate_jsonrpc_request(data)
        if validation_response:
            return validation_response
        
        method = data.get("method")
        params = data.get("params", {})
        request_id = data.get("id")
        
        api_logger.debug(LogMessages.METHOD_PARAMS.format(method, params))
        
        # Handle different assistant methods using modular handlers
        if method == "initialize":
            response = handle_initialize(params, request_id)
            _log_assistant_audit("initialize", params, response, "Success")
            return response
        elif method == "tools/list":
            response = handle_tools_list(request_id)
            _log_assistant_audit("get_metadata", params, response, "Success")
            return response
        elif method == "tools/call":
            response = handle_tool_call(params, request_id)
            status = "Success" if "error" not in response else "Error"
            # Map tool call to appropriate action
            tool_name = params.get("name", "")
            if "create" in tool_name:
                action = "create_document"
            elif "get" in tool_name or "search" in tool_name:
                action = "get_document" 
            else:
                action = "custom_tool"
            _log_assistant_audit(action, params, response, status)
            return response
        elif method == "prompts/list":
            response = handle_prompts_list(request_id)
            _log_assistant_audit("get_prompts", params, response, "Success")
            return response
        elif method == "prompts/get":
            response = handle_prompts_get(params, request_id)
            _log_assistant_audit("get_prompt", params, response, "Success")
            return response
        elif method == "notifications/cancelled":
            from frappe_assistant_core.api.assistant_api_notification_handler import handle_notification_cancelled
            return handle_notification_cancelled(params, request_id)
        else:
            response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": ErrorCodes.METHOD_NOT_FOUND,
                    "message": ErrorMessages.METHOD_NOT_FOUND.format(method)
                }
            }
            
            # Only include id if it's not None
            if request_id is not None:
                response["id"] = request_id
                
            return response
            
    except Exception as e:
        api_logger.error(f"Assistant API Error: {str(e)}")
        
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": ErrorCodes.INTERNAL_ERROR,
                "message": ErrorMessages.INTERNAL_ERROR,
                "data": str(e)
            }
        }
        
        # Only include id if it's not None and we have access to data
        if 'data' in locals() and isinstance(data, dict) and data.get("id") is not None:
            response["id"] = data["id"]
            
        return response


def _extract_request_data() -> Dict[str, Any]:
    """Extract request data from Frappe request context"""
    if hasattr(frappe.local, 'form_dict') and frappe.local.form_dict:
        return frappe.local.form_dict
    elif hasattr(frappe, 'request') and frappe.request.data:
        return json.loads(frappe.request.data.decode('utf-8'))
    else:
        return {}


def _validate_jsonrpc_request(data: Any) -> Optional[Dict[str, Any]]:
    """Validate JSON-RPC 2.0 request format"""
    if not isinstance(data, dict) or data.get("jsonrpc") != "2.0":
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": ErrorCodes.INVALID_REQUEST,
                "message": ErrorMessages.INVALID_REQUEST_FORMAT
            }
        }
        
        # Only include id if it exists and is not None
        if isinstance(data, dict) and data.get("id") is not None:
            response["id"] = data["id"]
            
        return response
    
    return None


def _log_assistant_audit(action: str, params: Dict[str, Any], response: Dict[str, Any], status: str):
    """Log assistant action for audit purposes"""
    try:
        log_assistant_audit(action, params, response, status)
    except Exception as e:
        api_logger.debug(f"Audit logging failed: {e}")


def log_assistant_connection():
    """Log assistant connection for monitoring purposes"""
    try:
        # Create a log entry for connection tracking
        user = frappe.session.user
        user_ip = frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else 'Unknown'
        
        api_logger.info(f"Assistant connection established - User: {user}, IP: {user_ip}")
        
        # You can extend this to create database logs if needed
        # For now, just log to the application log
        
    except Exception as e:
        api_logger.error(f"Error logging connection: {e}")


def log_assistant_audit(action: str, params: Dict[str, Any], response: Dict[str, Any], status: str):
    """Log assistant actions for audit and compliance"""
    try:
        user = frappe.session.user
        
        # Log the action
        api_logger.info(f"Assistant Audit - User: {user}, Action: {action}, Status: {status}")
        
        # For detailed audit logs, you can extend this to create database records
        # This is particularly useful for compliance and monitoring
        audit_data = {
            "user": user,
            "action": action,
            "status": status,
            "timestamp": frappe.utils.now(),
            "params_summary": str(params)[:500] if params else "",  # Truncate for storage
            "has_error": "error" in response if response else False
        }
        
        api_logger.debug(f"Assistant Audit Details: {audit_data}")
        
    except Exception as e:
        api_logger.error(f"Error in audit logging: {e}")


@frappe.whitelist(allow_guest=False, methods=["GET", "POST"])
def get_usage_statistics() -> Dict[str, Any]:
    """Get usage statistics for the assistant"""
    try:
        # SECURITY: Validate user context
        if not frappe.session.user or frappe.session.user == "Guest":
            api_logger.warning("Usage statistics requested without valid session")
            frappe.throw("Authentication required")
        
        # SECURITY: Check if user has assistant access
        from frappe_assistant_core.utils.permissions import check_assistant_permission
        user_roles = frappe.get_roles(frappe.session.user)
        api_logger.debug(f"User {frappe.session.user} has roles: {user_roles}")
        
        if not check_assistant_permission(frappe.session.user):
            api_logger.warning(f"Access denied for user: {frappe.session.user} with roles: {user_roles}")
            frappe.throw("Access denied - insufficient permissions")
        
        api_logger.info(f"Usage statistics requested by user: {frappe.session.user}")
        api_logger.info(f"Current site: {frappe.local.site}")
        
        # Get actual usage statistics
        today = frappe.utils.today()
        week_start = frappe.utils.add_days(today, -7)
        
        # Connection statistics with error handling
        try:
            total_connections = frappe.db.count("Assistant Connection Log") or 0
            today_connections = frappe.db.count("Assistant Connection Log", {"creation": (">=", today)}) or 0
            week_connections = frappe.db.count("Assistant Connection Log", {"creation": (">=", week_start)}) or 0
        except Exception as e:
            api_logger.warning(f"Connection stats error: {e}")
            total_connections = today_connections = week_connections = 0
        
        # Audit log statistics with error handling
        try:
            total_audit = frappe.db.count("Assistant Audit Log") or 0
            today_audit = frappe.db.count("Assistant Audit Log", {"creation": (">=", today)}) or 0
            week_audit = frappe.db.count("Assistant Audit Log", {"creation": (">=", week_start)}) or 0
        except Exception as e:
            api_logger.warning(f"Audit stats error: {e}")
            total_audit = today_audit = week_audit = 0
        
        # Tool statistics with error handling
        try:
            # Skip table existence check and just query directly
            total_tools = frappe.db.count("Assistant Tool Registry") or 0
            enabled_tools = frappe.db.count("Assistant Tool Registry", {"enabled": 1}) or 0
            api_logger.debug(f"Tool stats: total={total_tools}, enabled={enabled_tools}")
        except Exception as e:
            api_logger.warning(f"Tool stats error: {e}")
            total_tools = enabled_tools = 0
        
        # Recent activity with error handling
        try:
            recent_activity = frappe.db.get_list(
                "Assistant Audit Log",
                fields=["action", "tool_name", "user", "status", "timestamp"],
                order_by="timestamp desc",
                limit=10
            ) or []
        except Exception as e:
            api_logger.warning(f"Recent activity error: {e}")
            recent_activity = []
        
        # Return statistics in the format expected by frontend
        result = {
            "success": True,
            "data": {
                "connections": {
                    "total": total_connections,
                    "today": today_connections,
                    "this_week": week_connections
                },
                "audit_logs": {
                    "total": total_audit,
                    "today": today_audit,
                    "this_week": week_audit
                },
                "tools": {
                    "total": total_tools,
                    "enabled": enabled_tools
                },
                "recent_activity": recent_activity
            }
        }
        
        api_logger.debug(f"Usage statistics result: {result}")
        return result
        
    except Exception as e:
        api_logger.error(f"Error getting usage statistics: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist(allow_guest=False, methods=["GET", "POST"])
def ping() -> Dict[str, Any]:
    """Ping endpoint for testing connectivity"""
    try:
        # SECURITY: Validate user context
        if not frappe.session.user or frappe.session.user == "Guest":
            frappe.throw("Authentication required")
        
        # SECURITY: Check if user has assistant access
        from frappe_assistant_core.utils.permissions import check_assistant_permission
        if not check_assistant_permission(frappe.session.user):
            frappe.throw("Access denied")
        
        return {
            "success": True,
            "message": "pong",
            "timestamp": frappe.utils.now(),
            "user": frappe.session.user
        }
        
    except Exception as e:
        api_logger.error(f"Error in ping: {e}")
        return {
            "success": False,
            "message": f"Ping failed: {str(e)}"
        }


@frappe.whitelist(allow_guest=False, methods=["GET", "POST"])
def force_test_logging() -> Dict[str, Any]:
    """Force test logging for debugging purposes"""
    try:
        # SECURITY: Validate user context
        if not frappe.session.user or frappe.session.user == "Guest":
            frappe.throw("Authentication required")
        
        # SECURITY: Check if user has assistant access
        from frappe_assistant_core.utils.permissions import check_assistant_permission
        if not check_assistant_permission(frappe.session.user):
            frappe.throw("Access denied")
        
        # Force a test log entry
        api_logger.info(f"Force test logging triggered by user: {frappe.session.user}")
        
        return {
            "success": True,
            "message": "Test logging completed",
            "timestamp": frappe.utils.now(),
            "user": frappe.session.user
        }
        
    except Exception as e:
        api_logger.error(f"Error in force test logging: {e}")
        return {
            "success": False,
            "message": f"Force test logging failed: {str(e)}"
        }