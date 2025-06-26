"""
Script to register ALL tools in the Assistant Tool Registry
"""

import frappe
import json
from frappe_assistant_core.tools.analysis_tools import AnalysisTools
from frappe_assistant_core.tools.report_tools import ReportTools
from frappe_assistant_core.tools.search_tools import SearchTools
from frappe_assistant_core.tools.metadata_tools import MetadataTools
from frappe_assistant_core.tools.document_tools import DocumentTools

def register_all_tools():
    """Register all tools in the Assistant Tool Registry"""
    
    # Define all tool classes with their categories
    tool_classes = [
        (AnalysisTools, "Custom"),
        (ReportTools, "Reports"), 
        (SearchTools, "Search"),
        (MetadataTools, "Metadata"),
        (DocumentTools, "Document Operations")
    ]
    
    total_registered = 0
    
    for tool_class, category in tool_classes:
        print(f"\n=== Registering {category} Tools ===")
        
        try:
            # Get all tools from the class
            tools = tool_class.get_tools()
            
            for tool in tools:
                tool_name = tool["name"]
                
                # Check if tool already exists
                if frappe.db.exists("Assistant Tool Registry", tool_name):
                    print(f"Tool {tool_name} already exists, updating...")
                    tool_doc = frappe.get_doc("Assistant Tool Registry", tool_name)
                else:
                    print(f"Creating new tool: {tool_name}")
                    tool_doc = frappe.new_doc("Assistant Tool Registry")
                    tool_doc.tool_name = tool_name
                
                # Update tool details
                tool_doc.tool_description = tool["description"]
                tool_doc.enabled = 1
                tool_doc.category = category
                tool_doc.input_schema = json.dumps(tool["inputSchema"], indent=2)
                
                # Set appropriate permissions based on category
                if category == "Custom":
                    permissions = [{"doctype": "System Settings", "permission": "read"}]
                    timeout = 60
                elif category == "Reports":
                    permissions = [{"doctype": "Report", "permission": "read"}]
                    timeout = 30
                elif category == "Search":
                    permissions = [{"doctype": "System Settings", "permission": "read"}]
                    timeout = 15
                elif category == "Metadata":
                    permissions = [{"doctype": "DocType", "permission": "read"}]
                    timeout = 15
                elif category == "Document Operations":
                    permissions = [{"doctype": "System Settings", "permission": "read"}]
                    timeout = 30
                else:
                    permissions = []
                    timeout = 30
                
                tool_doc.required_permissions = json.dumps(permissions)
                tool_doc.execution_timeout = timeout
                
                # Save the tool
                tool_doc.save(ignore_permissions=True)
                print(f"✓ Registered tool: {tool_name}")
                total_registered += 1
            
            print(f"✓ Registered {len(tools)} {category.lower()} tools")
            
        except Exception as e:
            print(f"❌ Error registering {category} tools: {e}")
            continue
    
    frappe.db.commit()
    print(f"\n🎉 Successfully registered {total_registered} tools across all categories!")
    
    # Show summary of registered tools
    print("\n=== Tool Summary ===")
    registered_tools = frappe.get_all(
        "Assistant Tool Registry",
        filters={"enabled": 1},
        fields=["tool_name", "category"],
        order_by="category, tool_name"
    )
    
    categories = {}
    for tool in registered_tools:
        category = tool.category or "Uncategorized"
        if category not in categories:
            categories[category] = []
        categories[category].append(tool.tool_name)
    
    for category, tools in categories.items():
        print(f"\n{category}: {len(tools)} tools")
        for tool in tools:
            print(f"  • {tool}")

if __name__ == "__main__":
    register_all_tools()