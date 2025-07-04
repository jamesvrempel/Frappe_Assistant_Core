

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
    
    def get_streaming_protocol(self):
        """Get current streaming protocol configuration"""
        # Check if streaming-related fields exist in the DocType
        streaming_config = {
            "artifact_streaming_enforced": True,  # Default to enforced
            "protocol_status": "active",
            "limit_prevention_active": True,
            "streaming_behavior_instructions": """
Always create analysis workspace artifacts before performing data analysis.
Stream all detailed work to artifacts to prevent response limits.
Keep responses minimal with artifact references.
Build unlimited analysis depth via progressive artifact updates.
            """
        }
        
        # If fields exist in DocType, use their values
        if hasattr(self, "enforce_artifact_streaming"):
            streaming_config["artifact_streaming_enforced"] = self.enforce_artifact_streaming
            streaming_config["protocol_status"] = "active" if self.enforce_artifact_streaming else "optional"
        
        if hasattr(self, "response_limit_prevention"):
            streaming_config["limit_prevention_active"] = self.response_limit_prevention
            
        if hasattr(self, "streaming_behavior_instructions"):
            streaming_config["custom_instructions"] = self.streaming_behavior_instructions
        
        return streaming_config
    
    def get_enhanced_settings(self):
        """Get all settings including streaming protocol"""
        settings = self.as_dict()
        settings["streaming_protocol"] = self.get_streaming_protocol()
        return settings
    
    @frappe.whitelist()
    def refresh_plugins(self):
        """Refresh plugin repository and update plugin table"""
        try:
            # First refresh the plugin repository
            from frappe_assistant_core.assistant_core.doctype.assistant_plugin_repository.assistant_plugin_repository import refresh_plugin_repository
            refresh_plugin_repository()
            
            # Clear existing plugin configs
            self.enabled_plugins = []
            
            # Get all plugins from repository
            plugins = frappe.get_all(
                "Assistant Plugin Repository",
                fields=["plugin_name", "display_name", "description", "version", "can_enable", "validation_error"]
            )
            
            # Add plugins to the table
            for plugin in plugins:
                self.append('enabled_plugins', {
                    'plugin_name': plugin['plugin_name'],
                    'display_name': plugin.get('display_name', plugin['plugin_name']),
                    'description': plugin.get('description', ''),
                    'version': plugin.get('version', ''),
                    'can_enable': plugin.get('can_enable', False),
                    'validation_error': plugin.get('validation_error', ''),
                    'enabled': False  # Default to disabled
                })
            
            # Save changes
            self.save()
            
            # Clear relevant caches
            frappe.clear_cache()
            
            frappe.msgprint(
                frappe._("Plugin discovery completed. Found {0} plugins.").format(
                    len(plugins)
                )
            )
            
        except Exception as e:
            frappe.log_error(
                title=frappe._("Plugin Refresh Error"),
                message=str(e)
            )
            frappe.throw(
                frappe._("Failed to refresh plugins: {0}").format(str(e))
            )
    
    @frappe.whitelist()
    def refresh_tool_registry(self):
        """Refresh tool registry with source plugin information"""
        try:
            from frappe_assistant_core.install import determine_tool_source_plugin
            
            # Debug: Check plugin discovery
            try:
                from frappe_assistant_core.utils.plugin_manager import get_plugin_manager
                plugin_manager = get_plugin_manager()
                discovered_plugins = plugin_manager.get_discovered_plugins()
                frappe.logger().info(f"DEBUG: Found {len(discovered_plugins)} plugins during tool registry refresh")
                for plugin in discovered_plugins:
                    tools_count = len(plugin.get('tools', []))
                    frappe.logger().info(f"DEBUG: Plugin {plugin.get('name')} has {tools_count} tools")
            except Exception as debug_e:
                frappe.logger().error(f"DEBUG: Plugin discovery error: {debug_e}")
            
            # Get all tools from registry
            tools = frappe.get_all(
                "Assistant Tool Registry", 
                fields=["name", "tool_name", "source_plugin"]
            )
            
            debug_info = []
            updated_count = 0
            for tool in tools:
                # Determine the source plugin for this tool
                source_plugin = determine_tool_source_plugin(tool["tool_name"])
                
                debug_info.append(f"{tool['tool_name']} -> {source_plugin or 'core'}")
                
                # Update only if source_plugin is different
                current_source = tool.get("source_plugin")
                if current_source != source_plugin:
                    frappe.db.set_value(
                        "Assistant Tool Registry", 
                        tool["name"], 
                        "source_plugin", 
                        source_plugin
                    )
                    updated_count += 1
            
            # Commit the changes
            frappe.db.commit()
            
            # Refresh tool registry to clear cache and reload tools
            from frappe_assistant_core.core.tool_registry import refresh_tool_registry
            refresh_tool_registry()
            
            # Show debug info in the message
            debug_summary = "<br>".join(debug_info[:10])  # Show first 10 mappings
            if len(debug_info) > 10:
                debug_summary += f"<br>... and {len(debug_info)-10} more tools"
            
            frappe.msgprint(
                frappe._("Tool registry updated. {0} tools updated with source plugin information.<br><br>Tool mappings:<br>{1}").format(
                    updated_count, debug_summary
                )
            )
            
        except Exception as e:
            frappe.log_error(
                title=frappe._("Tool Registry Refresh Error"),
                message=str(e)
            )
            frappe.throw(
                frappe._("Failed to refresh tool registry: {0}").format(str(e))
            )
    
    def on_update(self):
        """Handle settings update including plugin changes"""
        from frappe_assistant_core.assistant_core.server import get_server_instance
        from frappe_assistant_core.utils.plugin_manager import get_plugin_manager
        
        server = get_server_instance()
        server_was_enabled = self.has_value_changed('server_enabled')
        
        # Handle server enable/disable
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
        
        # Handle plugin changes
        if hasattr(self, 'enabled_plugins') and self.enabled_plugins:
            try:
                # Get enabled plugin names
                enabled_plugin_names = [
                    p.plugin_name for p in self.enabled_plugins if p.enabled
                ]
                
                # Load enabled plugins
                plugin_manager = get_plugin_manager()
                plugin_manager.load_enabled_plugins(enabled_plugin_names)
                
                # Refresh tool registry if plugins changed
                from frappe_assistant_core.core.tool_registry import refresh_tool_registry
                refresh_tool_registry()
                
            except Exception as e:
                frappe.log_error(
                    title=frappe._("Plugin Load Error"),
                    message=str(e)
                )
                frappe.msgprint(
                    frappe._("Warning: Some plugins failed to load: {0}").format(str(e)),
                    indicator='orange'
                )



def get_context(context):
    context.title = _("assistant Server Settings")
    context.docs = _("Manage the settings for the assistant Server.")
    context.settings = frappe.get_doc("Assistant Core Settings")