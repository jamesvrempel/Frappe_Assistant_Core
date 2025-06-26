

import frappe
import json
from frappe.model.document import Document
from frappe import _

class AssistantToolRegistry(Document):
    """assistant Tool Registry DocType controller"""
    
    def validate(self):
        """Validate tool registry entry"""
        # Validate tool name format
        if not self.tool_name.replace('_', '').replace('-', '').isalnum():
            frappe.throw(_("Tool name can only contain letters, numbers, hyphens and underscores"))
        
        # Validate JSON schemas
        self.validate_input_schema()
        self.validate_output_schema()
        self.validate_required_permissions()
        
        # Validate execution timeout
        if self.execution_timeout < 1 or self.execution_timeout > 300:
            frappe.throw(_("Execution timeout must be between 1 and 300 seconds"))
    
    def validate_input_schema(self):
        """Validate input schema JSON"""
        if self.input_schema:
            try:
                schema = json.loads(self.input_schema)
                # Basic JSON schema validation
                if not isinstance(schema, dict):
                    frappe.throw(_("Input schema must be a valid JSON object"))
                if "type" not in schema:
                    frappe.throw(_("Input schema must have a 'type' property"))
            except json.JSONDecodeError:
                frappe.throw(_("Input schema must be valid JSON"))
    
    def validate_output_schema(self):
        """Validate output schema JSON"""
        if self.output_schema:
            try:
                schema = json.loads(self.output_schema)
                if not isinstance(schema, dict):
                    frappe.throw(_("Output schema must be a valid JSON object"))
            except json.JSONDecodeError:
                frappe.throw(_("Output schema must be valid JSON"))
    
    def validate_required_permissions(self):
        """Validate required permissions JSON"""
        if self.required_permissions:
            try:
                perms = json.loads(self.required_permissions)
                if not isinstance(perms, list):
                    frappe.throw(_("Required permissions must be a JSON array"))
                
                # Validate each permission entry
                for perm in perms:
                    if isinstance(perm, dict):
                        if "doctype" not in perm:
                            frappe.throw(_("Permission object must have 'doctype' property"))
                    elif not isinstance(perm, str):
                        frappe.throw(_("Permission entries must be strings (roles) or objects (doctype permissions)"))
                        
            except json.JSONDecodeError:
                frappe.throw(_("Required permissions must be valid JSON"))
    
    def update_usage_stats(self, success=True):
        """Update usage statistics for the tool"""
        self.db_set("total_calls", self.total_calls + 1)
        self.db_set("last_called", frappe.utils.now())
        
        if success:
            self.db_set("successful_calls", self.successful_calls + 1)
        else:
            self.db_set("failed_calls", self.failed_calls + 1)
    
    def get_success_rate(self):
        """Calculate success rate percentage"""
        if self.total_calls == 0:
            return 0
        return round((self.successful_calls / self.total_calls) * 100, 2)
    
    def can_execute(self, user=None):
        """Check if user can execute this tool"""
        if not self.enabled:
            return False
        
        if not user:
            user = frappe.session.user
        
        # Check required permissions
        if self.required_permissions:
            return self._check_permissions(user)
        
        return True
    
    def _check_permissions(self, user):
        """Check if user has required permissions"""
        try:
            perms = json.loads(self.required_permissions)
            user_roles = frappe.get_roles(user)
            
            for perm in perms:
                if isinstance(perm, dict):
                    # DocType permission check
                    doctype = perm.get("doctype")
                    ptype = perm.get("permission", "read")
                    if not frappe.has_permission(doctype, ptype, user=user):
                        return False
                elif isinstance(perm, str):
                    # Role-based permission check
                    if perm not in user_roles:
                        return False
            
            return True
            
        except Exception:
            return False

def get_context(context):
    context.title = _("assistant Tool Registry")
    context.docs = _("Manage the tools available for the assistant server.")
    context.tools = get_tools()

def get_tools():
    tools = frappe.get_all("assistant Tool Registry", filters={"enabled": 1}, fields=["tool_name", "tool_description"])
    return tools