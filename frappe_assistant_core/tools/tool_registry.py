"""
Auto-discovery tool registry that loads tools from code, not database
"""

import frappe
from typing import Dict, Any, List, Type

class AutoToolRegistry:
    """Auto-discovers and manages tools from code"""
    
    _tool_classes = None
    _tools_cache = None
    
    @classmethod
    def get_tool_classes(cls) -> List[Type]:
        """Get all tool classes"""
        if cls._tool_classes is None:
            cls._tool_classes = []
            
            try:
                # Import all tool classes
                frappe.log_error("🔧 Starting tool class imports", "Tool Registry Debug")
                
                from frappe_assistant_core.tools.analysis_tools import AnalysisTools
                frappe.log_error("✅ AnalysisTools imported", "Tool Registry Debug")
                
                # Test get_tools() immediately
                try:
                    analysis_tools_test = AnalysisTools.get_tools()
                    frappe.log_error(f"✅ AnalysisTools.get_tools() returned {len(analysis_tools_test)} tools", "Tool Registry Debug")
                except Exception as at_e:
                    frappe.log_error(f"❌ AnalysisTools.get_tools() failed: {at_e}", "Tool Registry Error")
                
                from frappe_assistant_core.tools.report_tools import ReportTools
                frappe.log_error("✅ ReportTools imported", "Tool Registry Debug")
                
                from frappe_assistant_core.tools.search_tools import SearchTools
                frappe.log_error("✅ SearchTools imported", "Tool Registry Debug")
                
                from frappe_assistant_core.tools.metadata_tools import MetadataTools
                frappe.log_error("✅ MetadataTools imported", "Tool Registry Debug")
                
                from frappe_assistant_core.tools.document_tools import DocumentTools
                frappe.log_error("✅ DocumentTools imported", "Tool Registry Debug")
                
                cls._tool_classes = [
                    AnalysisTools,
                    ReportTools, 
                    SearchTools,
                    MetadataTools,
                    DocumentTools
                ]
                
                frappe.log_error(f"✅ Tool classes array created with {len(cls._tool_classes)} classes", "Tool Registry Debug")
                
            except ImportError as e:
                frappe.log_error(f"❌ Error importing tool classes: {e}", "Tool Registry Error")
                cls._tool_classes = []
        
        return cls._tool_classes
    
    @classmethod
    def get_all_tools(cls) -> List[Dict[str, Any]]:
        """Get all available tools from all classes"""
        if cls._tools_cache is None:
            cls._tools_cache = []
            
            tool_classes = cls.get_tool_classes()
            frappe.log_error(f"🔧 get_all_tools: Found {len(tool_classes)} tool classes", "Tool Registry Debug")
            
            for tool_class in tool_classes:
                try:
                    class_tools = tool_class.get_tools()
                    frappe.log_error(f"✅ Loaded {len(class_tools)} tools from {tool_class.__name__}", "Tool Registry Debug")
                    cls._tools_cache.extend(class_tools)
                except Exception as e:
                    frappe.log_error(f"❌ Error loading tools from {tool_class.__name__}: {e}", "Tool Registry Error")
                    continue
            
            frappe.log_error(f"🔧 get_all_tools: Total cached tools: {len(cls._tools_cache)}", "Tool Registry Debug")
        
        return cls._tools_cache
    
    @classmethod
    def get_tools_for_user(cls, user: str = None) -> List[Dict[str, Any]]:
        """Get tools that the current user has permission to use"""
        user = user or frappe.session.user
        all_tools = cls.get_all_tools()
        accessible_tools = []
        
        frappe.log_error(f"🔧 get_tools_for_user: Found {len(all_tools)} total tools", "Tool Registry Debug")
        frappe.log_error(f"🔧 Tool names: {[t.get('name', 'unnamed') for t in all_tools]}", "Tool Registry Debug")
        
        for tool in all_tools:
            if cls._check_tool_permission(tool, user):
                accessible_tools.append(tool)
            else:
                frappe.log_error(f"❌ Tool {tool.get('name', 'unnamed')} filtered out by permissions", "Tool Registry Debug")
        
        frappe.log_error(f"🔧 get_tools_for_user: Returning {len(accessible_tools)} accessible tools", "Tool Registry Debug")
        return accessible_tools
    
    @classmethod
    def execute_tool(cls, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by finding the right class"""
        
        # Find the tool class that handles this tool
        for tool_class in cls.get_tool_classes():
            try:
                # Check if this class has this tool
                class_tools = tool_class.get_tools()
                tool_names = [t["name"] for t in class_tools]
                
                if tool_name in tool_names:
                    return tool_class.execute_tool(tool_name, arguments)
                    
            except Exception as e:
                frappe.log_error(f"Error checking tools in {tool_class.__name__}: {e}")
                continue
        
        # Tool not found in any class
        raise Exception(f"Unknown tool: {tool_name}")
    
    @classmethod
    def find_tool_by_name(cls, tool_name: str) -> Dict[str, Any]:
        """Find a tool definition by name"""
        all_tools = cls.get_all_tools()
        
        for tool in all_tools:
            if tool["name"] == tool_name:
                return tool
        
        return None
    
    @classmethod
    def _check_tool_permission(cls, tool: Dict[str, Any], user: str = None) -> bool:
        """Check if user has permission to use a tool"""
        try:
            user = user or frappe.session.user
            tool_name = tool.get("name", "")
            
            user_roles = frappe.get_roles(user)
            
            frappe.log_error(f"🔧 Checking permission for tool '{tool_name}' for user roles: {user_roles}", "Tool Registry Debug")
            
            # For System Managers and Administrators, allow ALL tools immediately
            if "System Manager" in user_roles or "Administrator" in user_roles or user == "Administrator":
                frappe.log_error(f"✅ Admin/System Manager has access to {tool_name}", "Tool Registry Debug")
                return True
            
            # Basic permission checks based on tool type for non-System Managers
            if tool_name.startswith("execute_") or tool_name.startswith("analyze_") or tool_name.startswith("query_"):
                # Analysis tools - require System Manager or System Settings access
                has_access = frappe.has_permission("System Settings", "read", user=user)
                print(f"🔧 Analysis tool {tool_name}: access = {has_access}")
                return has_access
            
            elif tool_name.startswith("report_"):
                # Report tools - check if user can access reports
                has_access = frappe.has_permission("Report", "read", user=user)
                print(f"🔧 Report tool {tool_name}: access = {has_access}")
                return has_access
            
            elif tool_name.startswith("search_") or tool_name.startswith("metadata_") or tool_name.startswith("get_"):
                # Search, metadata, and basic tools - available to most users
                print(f"✅ Basic tool {tool_name}: access granted")
                return True
            
            elif tool_name.startswith("document_"):
                # Document tools - basic document access (per-doctype checks during execution)
                print(f"✅ Document tool {tool_name}: access granted")
                return True
            
            else:
                # Unknown tools - allow for now
                print(f"✅ Unknown tool {tool_name}: access granted")
                return True
                
        except Exception as e:
            frappe.log_error(f"Error checking tool permission: {e}")
            print(f"❌ Permission check error for {tool_name}: {e}")
            return True  # Default to allowing access
    
    @classmethod
    def clear_cache(cls):
        """Clear the tools cache (useful for development/testing)"""
        cls._tools_cache = None
        cls._tool_classes = None
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get statistics about available tools"""
        tools = cls.get_all_tools()
        
        # Group by category
        categories = {}
        for tool in tools:
            tool_name = tool["name"]
            
            if tool_name.startswith("execute_") or tool_name.startswith("analyze_") or tool_name.startswith("query_") or tool_name.startswith("create_visualization"):
                category = "Analysis"
            elif tool_name.startswith("report_"):
                category = "Reports"
            elif tool_name.startswith("search_"):
                category = "Search"
            elif tool_name.startswith("metadata_"):
                category = "Metadata"
            elif tool_name.startswith("document_"):
                category = "Documents"
            else:
                category = "Basic"
            
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        return {
            "total_tools": len(tools),
            "categories": categories,
            "tool_classes": len(cls.get_tool_classes())
        }