#!/usr/bin/env python3
"""
Debug script for document_list tool issue
"""

import sys
import os

# Add the current directory to path so we can import frappe
sys.path.insert(0, '/Users/clinton/frappe/bench/frappe-bench')

def debug_document_list():
    """Debug the document_list functionality"""
    
    print("🔍 Starting document_list debug...")
    
    try:
        # Import and initialize frappe
        import frappe
        print("✅ Frappe imported successfully")
        
        # Initialize with a site
        frappe.init(site="codevantage.pilot")
        frappe.connect()
        print("✅ Frappe initialized and connected")
        
        # Test basic database connectivity
        print(f"📊 Current user: {frappe.session.user}")
        print(f"📊 Current site: {frappe.local.site}")
        print(f"📊 Database connected: {bool(frappe.db)}")
        
        # Test basic counts
        try:
            user_count = frappe.db.count("User")
            print(f"📊 User records in DB: {user_count}")
        except Exception as e:
            print(f"❌ Error counting users: {e}")
        
        try:
            doctype_count = frappe.db.count("DocType")
            print(f"📊 DocType records in DB: {doctype_count}")
        except Exception as e:
            print(f"❌ Error counting doctypes: {e}")
        
        # Test direct frappe.get_all
        try:
            users = frappe.get_all("User", fields=["name", "email"], limit=3)
            print(f"📊 Direct frappe.get_all User result: {len(users)} users")
            for user in users:
                print(f"   - {user}")
        except Exception as e:
            print(f"❌ Error with direct frappe.get_all Users: {e}")
            
        # Test importing DocumentTools
        try:
            from frappe_assistant_core.tools.document_tools import DocumentTools
            print("✅ DocumentTools imported successfully")
        except Exception as e:
            print(f"❌ Error importing DocumentTools: {e}")
            return
        
        # Test calling document_list
        try:
            print("\n🔧 Testing DocumentTools.list_documents...")
            result = DocumentTools.list_documents("User", {}, ["name", "email"], 5, debug=True)
            print(f"📊 DocumentTools.list_documents result:")
            print(f"   Success: {result.get('success', 'Unknown')}")
            print(f"   Count: {result.get('count', 'Unknown')}")
            print(f"   Total in DB: {result.get('total_in_db', 'Unknown')}")
            print(f"   Documents: {len(result.get('documents', []))}")
            
            if result.get('debug_info'):
                print(f"🔍 Debug info:")
                debug_info = result['debug_info']
                print(f"   Permission check passed: {debug_info.get('permission_check_passed')}")
                print(f"   Errors encountered: {debug_info.get('errors_encountered')}")
                print(f"   Query attempts: {debug_info.get('query_attempts')}")
                
            if result.get('warning'):
                print(f"⚠️  Warning: {result['warning']}")
                
        except Exception as e:
            print(f"❌ Error calling DocumentTools.list_documents: {e}")
            import traceback
            traceback.print_exc()
        
        # Test with DocType 
        try:
            print("\n🔧 Testing DocumentTools.list_documents with DocType...")
            result2 = DocumentTools.list_documents("DocType", {}, ["name", "module"], 5, debug=True)
            print(f"📊 DocType query result:")
            print(f"   Success: {result2.get('success', 'Unknown')}")
            print(f"   Count: {result2.get('count', 'Unknown')}")
            print(f"   Total in DB: {result2.get('total_in_db', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error with DocType query: {e}")
        
        # Test AutoToolRegistry
        try:
            print("\n🔧 Testing AutoToolRegistry...")
            from frappe_assistant_core.tools.tool_registry import AutoToolRegistry
            
            # Get all tools
            all_tools = AutoToolRegistry.get_all_tools()
            print(f"📊 AutoToolRegistry found {len(all_tools)} tools")
            
            # Look for document_list tool
            document_tools = [t for t in all_tools if 'document' in t.get('name', '')]
            print(f"📊 Document-related tools: {len(document_tools)}")
            for tool in document_tools:
                print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            
            # Test executing document_list via AutoToolRegistry
            try:
                print("\n🔧 Testing AutoToolRegistry.execute_tool('document_list')...")
                auto_result = AutoToolRegistry.execute_tool("document_list", {
                    "doctype": "User", 
                    "filters": {}, 
                    "fields": ["name", "email"], 
                    "limit": 5,
                    "debug": True
                })
                print(f"📊 AutoToolRegistry result:")
                print(f"   Success: {auto_result.get('success', 'Unknown')}")
                print(f"   Count: {auto_result.get('count', 'Unknown')}")
                
            except Exception as e:
                print(f"❌ Error with AutoToolRegistry execution: {e}")
                import traceback
                traceback.print_exc()
        
        except Exception as e:
            print(f"❌ Error importing/testing AutoToolRegistry: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            frappe.destroy()
            print("✅ Frappe destroyed")
        except:
            pass

if __name__ == "__main__":
    debug_document_list()