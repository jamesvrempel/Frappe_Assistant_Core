"""
Assistant Plugin Repository DocType.
Manages the registry of all available plugins for the Assistant Core system.
"""

import frappe
import json
from frappe.model.document import Document
from frappe import _


class AssistantPluginRepository(Document):
    """Registry for all available Assistant plugins"""
    
    def validate(self):
        """Validate plugin repository entry"""
        # Validate plugin name format
        if not self.plugin_name.replace('_', '').replace('-', '').isalnum():
            frappe.throw(_("Plugin name can only contain letters, numbers, hyphens and underscores"))
        
        # Validate JSON fields
        self.validate_dependencies()
        self.validate_supported_tools()
        self.validate_plugin_info()
        
        # Set display name if not provided
        if not self.display_name:
            self.display_name = self.plugin_name.replace('_', ' ').title()
    
    def validate_dependencies(self):
        """Validate dependencies JSON"""
        if self.dependencies:
            try:
                deps = json.loads(self.dependencies)
                if not isinstance(deps, list):
                    frappe.throw(_("Dependencies must be a JSON array"))
            except json.JSONDecodeError:
                frappe.throw(_("Dependencies must be valid JSON"))
    
    def validate_supported_tools(self):
        """Validate supported tools JSON"""
        if self.supported_tools:
            try:
                tools = json.loads(self.supported_tools)
                if not isinstance(tools, list):
                    frappe.throw(_("Supported tools must be a JSON array"))
            except json.JSONDecodeError:
                frappe.throw(_("Supported tools must be valid JSON"))
    
    def validate_plugin_info(self):
        """Validate plugin info JSON"""
        if self.plugin_info:
            try:
                info = json.loads(self.plugin_info)
                if not isinstance(info, dict):
                    frappe.throw(_("Plugin info must be a JSON object"))
            except json.JSONDecodeError:
                frappe.throw(_("Plugin info must be valid JSON"))
    
    def update_usage_stats(self, success=True):
        """Update usage statistics for the plugin"""
        self.db_set("total_loads", self.total_loads + 1)
        self.db_set("last_loaded", frappe.utils.now())
        
        if success:
            self.db_set("successful_loads", self.successful_loads + 1)
        else:
            self.db_set("failed_loads", self.failed_loads + 1)
    
    def get_success_rate(self):
        """Calculate success rate percentage"""
        if self.total_loads == 0:
            return 0
        return round((self.successful_loads / self.total_loads) * 100, 2)
    
    def can_enable_plugin(self):
        """Check if plugin can be enabled"""
        return self.can_enable and not self.validation_error
    
    def get_plugin_details(self):
        """Get complete plugin details as a dictionary"""
        details = {
            "name": self.plugin_name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "module_path": self.module_path,
            "enabled": self.enabled,
            "can_enable": self.can_enable,
            "validation_error": self.validation_error,
            "dependencies": json.loads(self.dependencies) if self.dependencies else [],
            "supported_tools": json.loads(self.supported_tools) if self.supported_tools else [],
            "plugin_info": json.loads(self.plugin_info) if self.plugin_info else {},
            "usage_stats": {
                "total_loads": self.total_loads,
                "successful_loads": self.successful_loads,
                "failed_loads": self.failed_loads,
                "success_rate": self.get_success_rate(),
                "last_loaded": self.last_loaded
            }
        }
        return details


@frappe.whitelist()
def get_enabled_plugins():
    """Get list of enabled plugins"""
    plugins = frappe.get_all(
        "Assistant Plugin Repository",
        filters={"enabled": 1, "can_enable": 1},
        fields=["plugin_name", "display_name", "version", "description"]
    )
    return plugins


@frappe.whitelist()
def get_available_plugins():
    """Get list of all available plugins"""
    plugins = frappe.get_all(
        "Assistant Plugin Repository",
        fields=["plugin_name", "display_name", "version", "description", "enabled", "can_enable", "validation_error"]
    )
    return plugins


@frappe.whitelist()
def refresh_plugin_repository():
    """Refresh the plugin repository from discovered plugins"""
    try:
        from frappe_assistant_core.utils.plugin_manager import get_plugin_manager
        
        # Get plugin manager and refresh discovery
        plugin_manager = get_plugin_manager()
        plugin_manager.refresh_plugins()
        
        # Get discovered plugins
        discovered_plugins = plugin_manager.get_discovered_plugins()
        
        # Update repository
        plugins_updated = 0
        for plugin_info in discovered_plugins:
            plugin_name = plugin_info.get('name')
            if not plugin_name:
                continue
                
            # Check if plugin exists in repository
            if frappe.db.exists("Assistant Plugin Repository", plugin_name):
                # Update existing plugin
                doc = frappe.get_doc("Assistant Plugin Repository", plugin_name)
                doc.display_name = plugin_info.get('display_name', plugin_name)
                doc.description = plugin_info.get('description', '')
                doc.version = plugin_info.get('version', '')
                doc.module_path = plugin_info.get('module_path', '')
                doc.can_enable = plugin_info.get('can_enable', False)
                doc.validation_error = plugin_info.get('validation_error', '')
                doc.dependencies = json.dumps(plugin_info.get('dependencies', []))
                doc.supported_tools = json.dumps(plugin_info.get('tools', []))
                doc.plugin_info = json.dumps(plugin_info)
                doc.save(ignore_permissions=True)
            else:
                # Create new plugin entry
                doc = frappe.get_doc({
                    "doctype": "Assistant Plugin Repository",
                    "plugin_name": plugin_name,
                    "display_name": plugin_info.get('display_name', plugin_name),
                    "description": plugin_info.get('description', ''),
                    "version": plugin_info.get('version', ''),
                    "module_path": plugin_info.get('module_path', ''),
                    "enabled": False,  # Default to disabled
                    "can_enable": plugin_info.get('can_enable', False),
                    "validation_error": plugin_info.get('validation_error', ''),
                    "dependencies": json.dumps(plugin_info.get('dependencies', [])),
                    "supported_tools": json.dumps(plugin_info.get('tools', [])),
                    "plugin_info": json.dumps(plugin_info)
                })
                doc.insert(ignore_permissions=True)
            
            plugins_updated += 1
        
        frappe.msgprint(
            frappe._("Plugin repository refreshed. Updated {0} plugins.").format(plugins_updated)
        )
        
        return {"success": True, "plugins_updated": plugins_updated}
        
    except Exception as e:
        frappe.log_error(
            title=frappe._("Plugin Repository Refresh Error"),
            message=str(e)
        )
        frappe.throw(
            frappe._("Failed to refresh plugin repository: {0}").format(str(e))
        )


def get_context(context):
    """Get context for web view"""
    context.title = _("Assistant Plugin Repository")
    context.docs = _("Manage available plugins for the Assistant Core system.")
    context.plugins = get_available_plugins()