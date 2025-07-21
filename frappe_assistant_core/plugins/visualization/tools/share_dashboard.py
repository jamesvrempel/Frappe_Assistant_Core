"""
Share Dashboard Tool - Dashboard collaboration and permissions

Manages dashboard sharing with users, roles, and public access
with granular permission controls.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class ShareDashboard(BaseTool):
    """
    Tool for managing dashboard sharing and permissions.
    
    Provides capabilities for:
    - User and role-based sharing
    - Public link generation
    - Permission level control
    - Access tracking and audit
    """
    
    def __init__(self):
        super().__init__()
        self.name = "share_dashboard"
        self.description = self._get_description()
        self.requires_permission = None  # Permission checked dynamically
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "dashboard_name": {
                    "type": "string",
                    "description": "Name of dashboard to share"
                },
                "share_with": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["user", "role"]},
                            "name": {"type": "string"},
                            "permission_level": {"type": "string", "enum": ["read", "write", "admin"]}
                        },
                        "required": ["type", "name", "permission_level"]
                    },
                    "description": "List of users/roles to share with"
                },
                "public_access": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "require_login": {"type": "boolean"},
                        "expiry_date": {"type": "string"},
                        "allowed_domains": {"type": "array"}
                    },
                    "description": "Public access settings"
                },
                "notification_settings": {
                    "type": "object",
                    "properties": {
                        "notify_shared_users": {"type": "boolean"},
                        "email_message": {"type": "string"},
                        "include_instructions": {"type": "boolean"}
                    },
                    "description": "Notification preferences"
                },
                "access_restrictions": {
                    "type": "object",
                    "properties": {
                        "ip_whitelist": {"type": "array"},
                        "time_restrictions": {"type": "object"},
                        "download_permissions": {"type": "boolean"}
                    },
                    "description": "Additional security restrictions"
                }
            },
            "required": ["dashboard_name"]
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Share dashboards with users, roles, or public access. Configure granular permissions (read/write/admin), create public links with expiry controls, and track access logs."""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Share dashboard"""
        try:
            # Import the actual sharing manager
            from ..tools.sharing_manager import SharingManager
            
            # Create sharing manager and execute
            sharing_manager = SharingManager()
            return sharing_manager.execute(arguments)
            
        except Exception as e:
            frappe.log_error(
                title=_("Dashboard Sharing Error"),
                message=f"Error sharing dashboard: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
share_dashboard = ShareDashboard