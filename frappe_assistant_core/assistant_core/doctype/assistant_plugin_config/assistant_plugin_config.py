"""
Assistant Plugin Config DocType.
Child table for configuring plugins in Assistant Core Settings.
"""

import frappe
from frappe.model.document import Document


class AssistantPluginConfig(Document):
    """Configuration for a single plugin"""
    
    def validate(self):
        """Validate plugin configuration"""
        # Auto-populate fields from plugin repository when plugin_name is set
        if self.plugin_name and frappe.db.exists("Assistant Plugin Repository", self.plugin_name):
            self.populate_from_repository()
        
        if self.enabled and not self.can_enable:
            frappe.throw(
                frappe._("Cannot enable plugin {0}: {1}").format(
                    self.plugin_name, 
                    self.validation_error or "Validation failed"
                )
            )
    
    def populate_from_repository(self):
        """Populate fields from the plugin repository"""
        try:
            plugin_repo = frappe.get_doc("Assistant Plugin Repository", self.plugin_name)
            self.display_name = plugin_repo.display_name
            self.description = plugin_repo.description
            self.version = plugin_repo.version
            self.can_enable = plugin_repo.can_enable
            self.validation_error = plugin_repo.validation_error
        except Exception as e:
            frappe.log_error(f"Error populating plugin config from repository: {e}")
            self.validation_error = f"Error loading plugin info: {str(e)}"
            self.can_enable = False