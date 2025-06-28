

import frappe
from frappe import _
import json

from frappe_assistant_core.utils.logger import api_logger

def after_install():
    """Run after app installation"""
    
    api_logger.info("Installing Frappe assistant Server...")
    
    # First, make sure all DocTypes are synced
    frappe.db.commit()
    
    # Create default assistant Server Settings
    create_default_settings()
    
    # Create necessary roles first
    create_default_roles()
    
    # Create custom fields if needed
    create_custom_fields()
    
    # Setup permissions
    setup_permissions()
    
    # Register default tools (after DocTypes are available)
    register_default_tools()
    
    api_logger.info("Frappe assistant Server installed successfully!")
    api_logger.info("Please configure assistant Server Settings to enable the server.")

def create_default_settings():
    """Create default Assistant Core Settings"""
    try:
        # Ensure the DocType is properly loaded
        frappe.reload_doc("frappe_assistant_core", "doctype", "assistant_core_settings")
        
        if not frappe.db.exists("Assistant Core Settings", "Assistant Core Settings"):
            doc = frappe.get_doc({
                "doctype": "Assistant Core Settings",
                "server_enabled": 0,
                "max_connections": 100,
                "authentication_required": 1,
                "rate_limit": 60,
                "websocket_enabled": 1,
                "ssl_enabled": 0,
                "log_level": "INFO",
                "max_log_entries": 10000,
                "cleanup_logs_after_days": 30
            })
            doc.insert(ignore_permissions=True)
            api_logger.info("Created default Assistant Core Settings")
        else:
            api_logger.info("Assistant Core Settings already exists")
    except Exception as e:
        api_logger.warning(f"Could not create Assistant Core Settings: {e}")

def register_default_tools():
    """Register default assistant tools using the complete auto-registry"""
    try:
        # Import and run the complete tool registration
        from frappe_assistant_core.install_all_tools import register_all_tools
        register_all_tools()
        api_logger.info("Successfully registered all assistant tools")
        
    except Exception as e:
        api_logger.warning(f"Could not register tools: {e}")
        # Fallback to basic registration if the complete one fails
        try:
            api_logger.info("Attempting fallback tool registration...")
            register_basic_tools()
        except Exception as fallback_error:
            api_logger.error(f"Fallback tool registration also failed: {fallback_error}")

def register_basic_tools():
    """Fallback basic tool registration"""
    # Ensure the DocType is properly loaded
    frappe.reload_doc("frappe_assistant_core", "doctype", "assistant_tool_registry")
    
    # Check if Assistant Tool Registry DocType exists
    if not frappe.db.table_exists("tabAssistant Tool Registry"):
        api_logger.warning("Assistant Tool Registry table not found, skipping tool registration")
        return

    # Import tools with error handling
    tools_modules = [
        ("frappe_assistant_core.tools.analysis_tools", "AnalysisTools"),
        ("frappe_assistant_core.tools.document_tools", "DocumentTools"),
        ("frappe_assistant_core.tools.report_tools", "ReportTools"), 
        ("frappe_assistant_core.tools.search_tools", "SearchTools"),
        ("frappe_assistant_core.tools.metadata_tools", "MetadataTools")
    ]
    
    all_tools = []
    for module_path, class_name in tools_modules:
        try:
            module = frappe.get_module(module_path)
            tool_class = getattr(module, class_name)
            all_tools.extend(tool_class.get_tools())
        except Exception as e:
            api_logger.warning(f"Could not load tools from {module_path}: {e}")
            continue
    
    tools_created = 0
    for tool in all_tools:
        try:
            # Use raw SQL to check existence to avoid module issues
            exists = frappe.db.sql("""
                SELECT name FROM `tabAssistant Tool Registry` 
                WHERE tool_name = %s LIMIT 1
            """, (tool["name"],))
            
            if not exists:
                # Determine category based on tool name
                category = "Custom"
                if tool["name"].startswith("execute_") or tool["name"].startswith("analyze_") or tool["name"].startswith("query_") or tool["name"].startswith("create_"):
                    category = "Custom"
                elif tool["name"].startswith("document_"):
                    category = "Document Operations"
                elif tool["name"].startswith("report_"):
                    category = "Reports"
                elif tool["name"].startswith("search_"):
                    category = "Search"
                elif tool["name"].startswith("metadata_"):
                    category = "Metadata"
                
                # Set required permissions based on tool category
                required_permissions = []
                if category == "Document Operations":
                    required_permissions = [{"doctype": "DocType", "permission": "read"}]
                elif category == "Reports":
                    required_permissions = [{"doctype": "Report", "permission": "read"}]
                
                doc = frappe.get_doc({
                    "doctype": "Assistant Tool Registry",
                    "tool_name": tool["name"],
                    "tool_description": tool["description"],
                    "enabled": 1,
                    "category": category,
                    "input_schema": json.dumps(tool["inputSchema"]),
                    "required_permissions": json.dumps(required_permissions),
                    "execution_timeout": 30
                })
                doc.insert(ignore_permissions=True)
                tools_created += 1
        except Exception as e:
            api_logger.warning(f"Could not create tool {tool['name']}: {e}")
    
    api_logger.info(f"Registered {tools_created} assistant tools via fallback method")

def create_default_roles():
    """Create default roles for assistant Server"""
    try:
        roles_to_create = [
            {
                "role_name": "assistant User",
                "description": "Can use assistant tools and view connection logs"
            },
            {
                "role_name": "assistant Admin", 
                "description": "Full access to assistant Server configuration and management"
            }
        ]
        
        for role_config in roles_to_create:
            if not frappe.db.exists("Role", role_config["role_name"]):
                # Create role
                role_doc = frappe.get_doc({
                    "doctype": "Role",
                    "role_name": role_config["role_name"],
                    "description": role_config["description"]
                })
                role_doc.insert(ignore_permissions=True)
        
        api_logger.info("Created default assistant roles")
        
    except Exception as e:
        api_logger.warning(f"Could not create default roles: {e}")

def create_custom_fields():
    """Create any necessary custom fields"""
    try:
        # Add assistant-related fields to User doctype if needed
        custom_fields = [
            {
                "doctype": "Custom Field",
                "dt": "User",
                "fieldname": "assistant_enabled",
                "label": "assistant Access Enabled",
                "fieldtype": "Check",
                "insert_after": "enabled",
                "description": "Allow this user to access assistant tools"
            }
        ]
        
        for field_config in custom_fields:
            if not frappe.db.exists("Custom Field", {"dt": field_config["dt"], "fieldname": field_config["fieldname"]}):
                frappe.get_doc(field_config).insert(ignore_permissions=True)
        
        api_logger.info("Created custom fields")
        
    except Exception as e:
        api_logger.warning(f"Could not create custom fields: {e}")

def setup_permissions():
    """Setup default permissions"""
    try:
        # Give System Manager role full access to assistant
        system_manager_perms = [
            "Assistant Core Settings",
            "Assistant Tool Registry", 
            "Assistant Connection Log",
            "Assistant Audit Log"
        ]
        
        for doctype in system_manager_perms:
            if frappe.db.table_exists(f"tab{doctype}"):
                existing_perm = frappe.db.sql("""
                    SELECT name FROM `tabCustom DocPerm` 
                    WHERE parent = %s AND role = 'System Manager'
                    LIMIT 1
                """, (doctype,))
                
                if not existing_perm:
                    frappe.get_doc({
                        "doctype": "Custom DocPerm",
                        "parent": doctype,
                        "parenttype": "DocType",
                        "parentfield": "permissions",
                        "role": "System Manager",
                        "read": 1,
                        "write": 1,
                        "create": 1,
                        "delete": 1,
                        "submit": 0,
                        "cancel": 0,
                        "amend": 0
                    }).insert(ignore_permissions=True)
        
        api_logger.info("Setup default permissions")
        
    except Exception as e:
        api_logger.warning(f"Could not setup permissions: {e}")