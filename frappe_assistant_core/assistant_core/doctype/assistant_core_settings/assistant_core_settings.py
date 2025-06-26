

import frappe
from frappe.model.document import Document
from frappe import _
from frappe_assistant_core.assistant_core.server import assistantServer

class AssistantCoreSettings(Document):
    """assistant Server Settings DocType controller"""
    
    def validate(self):
        """Validate settings before saving"""
        # Validate max connections
        if self.max_connections < 1 or self.max_connections > 1000:
            frappe.throw("Max connections must be between 1 and 1000")
        
        # Validate rate limit
        if self.rate_limit < 1 or self.rate_limit > 10000:
            frappe.throw("Rate limit must be between 1 and 10000 requests per minute")
        
        # Validate SSL settings
        if self.ssl_enabled:
            if not self.ssl_cert_path or not self.ssl_key_path:
                frappe.throw("SSL certificate and key paths are required when SSL is enabled")
    
    def on_update(self):
        """Handle settings update"""
        from frappe_assistant_core.assistant_core.server import get_server_instance
        
        server = get_server_instance()
        server_was_enabled = self.has_value_changed('server_enabled')
        
        if self.server_enabled:
            if server_was_enabled or not server.running:
                # Start server if it was just enabled or not running
                frappe.enqueue('frappe_assistant_core.assistant_core.server.start_background_server', queue='short')
                frappe.msgprint("Assistant Server is starting...")
        else:
            if server_was_enabled and server.running:
                # Stop server if it was just disabled
                self.stop_assistant_core()
                frappe.msgprint("Assistant Server stopped")
    
    def restart_assistant_core(self):
        """Restart the assistant server with new settings"""
        try:
            # Stop existing server
            self.stop_assistant_core()
            
            # Start server with new settings
            self.start_assistant_core()
            
            frappe.msgprint("assistant Server restarted successfully")
            
        except Exception as e:
            frappe.log_error(f"Failed to restart assistant server: {str(e)}")
            frappe.throw(f"Failed to restart assistant server: {str(e)}")
    
    def start_assistant_core(self):
        """Start the assistant server"""
        try:
            server = assistantServer()
            server.start()
            
            # Log the server start (skip if DocType doesn't exist)
            try:
                if frappe.db.table_exists("tabAssistant Connection Log"):
                    frappe.get_doc({
                        "doctype": "Assistant Connection Log",
                        "action": "server_start",
                        "user": frappe.session.user,
                        "details": "assistant Server started (MCP API)"
                    }).insert(ignore_permissions=True)
            except:
                pass  # Don't fail server start if logging fails
            
        except Exception as e:
            frappe.log_error(f"Failed to start assistant server: {str(e)}")
            raise
    
    def stop_assistant_core(self):
        """Stop the assistant server"""
        try:
            server = assistantServer()
            server.stop()
            
            # Log the server stop (skip if DocType doesn't exist)
            try:
                if frappe.db.table_exists("tabAssistant Connection Log"):
                    frappe.get_doc({
                        "doctype": "Assistant Connection Log",
                        "action": "server_stop",
                        "user": frappe.session.user,
                        "details": "assistant Server stopped"
                    }).insert(ignore_permissions=True)
            except:
                pass  # Don't fail server stop if logging fails
            
        except Exception as e:
            frappe.log_error(f"Failed to stop assistant server: {str(e)}")
            raise

def get_context(context):
    context.title = _("assistant Server Settings")
    context.docs = _("Manage the settings for the assistant Server.")
    context.settings = frappe.get_doc("Assistant Core Settings")