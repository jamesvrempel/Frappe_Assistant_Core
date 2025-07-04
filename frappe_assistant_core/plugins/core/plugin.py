"""
Core plugin providing essential Frappe operations.
This plugin is always enabled and provides fundamental tools.
"""

from frappe_assistant_core.plugins.base_plugin import BasePlugin


class CorePlugin(BasePlugin):
    """
    Core plugin that provides essential Frappe document and system operations.
    This plugin contains tools that should always be available.
    """
    
    def get_info(self):
        return {
            'name': 'core',
            'display_name': 'Core Operations',
            'description': 'Essential Frappe document operations, search, metadata, and workflow tools',
            'version': '1.0.0',
            'dependencies': [],
            'requires_restart': False,
            'always_enabled': True  # Special flag for core plugin
        }
    
    def get_tools(self):
        """
        Return list of core tool module names.
        These correspond to files in the core/tools directory.
        """
        return [
            'document_create',
            'document_get', 
            'document_update',
            'document_list',
            'document_delete',
            'search_global',
            'search_doctype', 
            'search_link',
            'metadata_doctype',
            'metadata_list_doctypes',
            'metadata_doctype_fields',
            'metadata_permissions',
            'metadata_workflow',
            'report_execute',
            'report_list',
            'report_details',
            'workflow_action',
            'workflow_list', 
            'workflow_status'
        ]
    
    def validate_environment(self):
        """Core plugin always validates successfully"""
        return True, None
    
    def on_enable(self):
        """Core plugin enable handler"""
        self.logger.info("Core plugin enabled (always active)")
    
    def on_disable(self):
        """Core plugin cannot be disabled"""
        self.logger.warning("Core plugin cannot be disabled")
    
    def get_capabilities(self):
        """Core capabilities"""
        return {
            'document_operations': {
                'create': True,
                'read': True, 
                'update': True,
                'delete': True,
                'list': True
            },
            'search': {
                'global_search': True,
                'doctype_search': True,
                'link_search': True
            },
            'metadata': {
                'doctype_info': True,
                'list_doctypes': True,
                'field_info': True,
                'permissions': True,
                'workflow': True
            },
            'reporting': {
                'execute_reports': True,
                'list_reports': True,
                'report_details': True
            },
            'workflow': {
                'trigger_actions': True,
                'list_workflows': True,
                'check_status': True
            }
        }