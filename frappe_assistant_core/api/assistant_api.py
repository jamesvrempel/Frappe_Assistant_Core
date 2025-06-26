

import frappe
import json

@frappe.whitelist(allow_guest=False, methods=["POST"])
def handle_assistant_request():
    """Handle assistant protocol requests"""
    
    # SECURITY: Validate user context immediately
    if not frappe.session.user or frappe.session.user == "Guest":
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": "Authentication required: No valid user session"
            }
        }
    
    # SECURITY: Check if user has assistant access
    from frappe_assistant_core.utils.permissions import check_assistant_permission
    if not check_assistant_permission(frappe.session.user):
        return {
            "jsonrpc": "2.0", 
            "error": {
                "code": -32000,
                "message": "Access denied: User does not have assistant permissions"
            }
        }
    
    print(f"🔐 assistant API authenticated user: {frappe.session.user}")
    
    try:
        # Log connection
        log_assistant_connection()
        
    except Exception as e:
        pass  # Don't fail request due to logging
        
    try:
        # Get request data
        if hasattr(frappe.local, 'form_dict') and frappe.local.form_dict:
            data = frappe.local.form_dict
        elif hasattr(frappe, 'request') and frappe.request.data:
            data = json.loads(frappe.request.data.decode('utf-8'))
        else:
            data = {}
        
        print(f"🔧 assistant API received data: {data}")
        
        # Validate JSON-RPC 2.0 format
        if not isinstance(data, dict) or data.get("jsonrpc") != "2.0":
            response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Invalid Request - Not JSON-RPC 2.0 format"
                }
            }
            
            # Only include id if it exists and is not None
            if isinstance(data, dict) and data.get("id") is not None:
                response["id"] = data["id"]
                
            return response
        
        method = data.get("method")
        params = data.get("params", {})
        request_id = data.get("id")
        
        print(f"🔧 assistant Method: {method}, Params: {params}")
        
        # Handle different assistant methods
        if method == "tools/list":
            response = handle_tools_list(request_id)
            log_assistant_audit("get_metadata", params, response, "Success")
            return response
        elif method == "tools/call":
            response = handle_tool_call(params, request_id)
            status = "Success" if "error" not in response else "Error"
            # Map tool call to appropriate action
            tool_name = params.get("name", "")
            if "create" in tool_name:
                action = "create_document"
            elif "get" in tool_name or "search" in tool_name:
                action = "get_document" 
            else:
                action = "custom_tool"
            log_assistant_audit(action, params, response, status)
            return response
        elif method == "notifications/cancelled":
            from frappe_assistant_core.api.assistant_api_notification_handler import handle_notification_cancelled
            return handle_notification_cancelled(params, request_id)
        else:
            response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }
            
            # Only include id if it's not None
            if request_id is not None:
                response["id"] = request_id
                
            return response
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ assistant API Error: {error_msg}")
        
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": error_msg
            }
        }
        
        # Only include id if it's not None and we have access to data
        if 'data' in locals() and isinstance(data, dict) and data.get("id") is not None:
            response["id"] = data["id"]
            
        return response

def handle_tools_list(request_id):
    """Handle tools/list request"""
    try:
        print(f"🔧 Handling tools/list request")
        
        # Auto-discover tools from code (no database dependency)
        tools = []
        try:
            from frappe_assistant_core.tools.tool_registry import AutoToolRegistry
            frappe.log_error(f"🔧 Loading tools for user: {frappe.session.user}", "Assistant API Debug")
            
            # Clear cache to force fresh loading
            AutoToolRegistry.clear_cache()
            
            # Get all tools first to debug
            all_tools = AutoToolRegistry.get_all_tools()
            frappe.log_error(f"🔧 Found {len(all_tools)} total tools in registry", "Assistant API Debug")
            
            # Get filtered tools for user
            tools = AutoToolRegistry.get_tools_for_user()
            frappe.log_error(f"🔧 User {frappe.session.user} has access to {len(tools)} tools", "Assistant API Debug")
            
            # Debug: Print tool names
            tool_names = [t.get('name', 'unnamed') for t in tools]
            frappe.log_error(f"🔧 Available tools: {tool_names}", "Assistant API Debug")
            
        except Exception as e:
            print(f"❌ Error auto-discovering tools: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            tools = []
        
        # FORCE manual loading regardless to ensure all tools are loaded
        print("🔧 FORCING manual tool loading...")
        manual_tools = []
        
        # Manually import and get tools from each class - FORCE LOADING
        try:
            from frappe_assistant_core.tools.document_tools import DocumentTools
            doc_tools = DocumentTools.get_tools()
            manual_tools.extend(doc_tools)
            print(f"✅ FORCE: Loaded {len(doc_tools)} document tools")
        except Exception as e:
            print(f"❌ FORCE: Failed to load document tools: {e}")
        
        try:
            print("🔧 FORCE: Importing AnalysisTools...")
            from frappe_assistant_core.tools.analysis_tools import AnalysisTools
            print("🔧 FORCE: AnalysisTools imported successfully")
            
            print("🔧 FORCE: Calling AnalysisTools.get_tools()...")
            analysis_tools = AnalysisTools.get_tools()
            print(f"🔧 FORCE: get_tools() returned {len(analysis_tools)} tools")
            
            manual_tools.extend(analysis_tools)
            print(f"✅ FORCE: Loaded {len(analysis_tools)} analysis tools")
            
            # Debug: print tool names
            if analysis_tools:
                tool_names = [t.get('name', 'unnamed') for t in analysis_tools]
                print(f"🔧 FORCE: Analysis tool names: {tool_names}")
            else:
                print("🔧 FORCE: Analysis tools list is empty!")
                
        except Exception as e:
            print(f"❌ FORCE: Failed to load analysis tools: {e}")
            import traceback
            print(f"❌ FORCE: Analysis tools traceback: {traceback.format_exc()}")
            
            # Try to get specific error info
            print(f"❌ FORCE: Exception type: {type(e).__name__}")
            print(f"❌ FORCE: Exception args: {e.args}")
            
            # Try importing just the module
            try:
                import frappe_assistant_core.tools.analysis_tools
                print("✅ FORCE: Module import successful")
            except Exception as import_e:
                print(f"❌ FORCE: Module import failed: {import_e}")
        
        try:
            from frappe_assistant_core.tools.report_tools import ReportTools
            report_tools = ReportTools.get_tools()
            manual_tools.extend(report_tools)
            print(f"✅ FORCE: Loaded {len(report_tools)} report tools")
        except Exception as e:
            print(f"❌ FORCE: Failed to load report tools: {e}")
        
        try:
            from frappe_assistant_core.tools.search_tools import SearchTools
            search_tools = SearchTools.get_tools()
            manual_tools.extend(search_tools)
            print(f"✅ FORCE: Loaded {len(search_tools)} search tools")
        except Exception as e:
            print(f"❌ FORCE: Failed to load search tools: {e}")
        
        try:
            from frappe_assistant_core.tools.metadata_tools import MetadataTools
            metadata_tools = MetadataTools.get_tools()
            manual_tools.extend(metadata_tools)
            print(f"✅ FORCE: Loaded {len(metadata_tools)} metadata tools")
        except Exception as e:
            print(f"❌ FORCE: Failed to load metadata tools: {e}")
        
        print(f"🔧 FORCE: Manual loading complete. Total manual tools: {len(manual_tools)}")
        
        # Use manual tools if they loaded successfully, otherwise use auto-discovered tools
        if manual_tools:
            tools = manual_tools
            print(f"🔧 Using manually loaded tools: {len(tools)} total")
        else:
            print(f"🔧 Using auto-discovered tools: {len(tools)} total")
        
        # Add basic metadata tools if they weren't loaded manually
        if not any(t.get('name') == 'get_user_info' for t in tools):
            tools.extend([
                {
                    "name": "get_user_info",
                    "description": "Get current user information and session details",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                {
                    "name": "get_doctypes", 
                    "description": "List all available document types with descriptions",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "default": 50, "description": "Maximum number of doctypes to return"}
                        }
                    }
                }
            ])
            print(f"✅ Added basic metadata tools")
        
        # Final fallback to minimal hardcoded tools if everything fails
        if not tools:
            tools = [
                {
                    "name": "get_user_info",
                    "description": "Get current user information",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "get_doctypes",
                    "description": "List all available document types",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "default": 50, "description": "Maximum number of doctypes to return"}
                        }
                    }
                },
                {
                    "name": "create_document",
                    "description": "Create a new document",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "doctype": {"type": "string", "description": "Document type to create"},
                            "data": {"type": "object", "description": "Document data"}
                        },
                        "required": ["doctype", "data"]
                    }
                },
                {
                    "name": "get_document",
                    "description": "Get a specific document",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "doctype": {"type": "string", "description": "Document type"},
                            "name": {"type": "string", "description": "Document name"}
                        },
                        "required": ["doctype", "name"]
                    }
                },
                {
                    "name": "search_documents",
                    "description": "Search documents with filters",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "doctype": {"type": "string", "description": "Document type to search"},
                            "filters": {"type": "object", "default": {}, "description": "Search filters"},
                            "fields": {"type": "array", "items": {"type": "string"}, "description": "Fields to return"},
                            "limit": {"type": "integer", "default": 20, "description": "Maximum results"}
                        },
                        "required": ["doctype"]
                    }
                }
            ]
        
        response = {
            "jsonrpc": "2.0",
            "result": {
                "tools": tools
            }
        }
        
        # Only include id if it's not None
        if request_id is not None:
            response["id"] = request_id
            
        return response
        
    except Exception as e:
        print(f"❌ Error in handle_tools_list: {e}")
        
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Error listing tools",
                "data": str(e)
            }
        }
        
        # Only include id if it's not None
        if request_id is not None:
            response["id"] = request_id
            
        return response

def handle_tool_call(params, request_id):
    """Handle tools/call request"""
    try:
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        print(f"🔧 Executing tool: {tool_name} with args: {arguments}")
        
        if not tool_name:
            response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32602,
                    "message": "Missing tool name"
                }
            }
        else:
            # SECURITY: Validate user has assistant access
            from frappe_assistant_core.utils.permissions import check_assistant_permission
            if not check_assistant_permission(frappe.session.user):
                response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32000,
                        "message": "Access denied: User does not have assistant permissions"
                    }
                }
            # SECURITY: Additional validation for high-privilege tools
            elif tool_name in ["execute_python_code", "query_and_analyze"]:
                # These tools are now role-restricted (System Manager only) rather than disabled
                user_roles = frappe.get_roles(frappe.session.user)
                if "System Manager" not in user_roles:
                    response = {
                        "jsonrpc": "2.0", 
                        "error": {
                            "code": -32000,
                            "message": f"Tool '{tool_name}' requires System Manager role. Current roles: {', '.join(user_roles)}"
                        }
                    }
                else:
                    # Execute the tool and get raw result
                    raw_result = execute_tool(tool_name, arguments)
            else:
                # Execute the tool and get raw result
                raw_result = execute_tool(tool_name, arguments)
            
            # Format as assistant content blocks
            if raw_result.get("success", True):  # Success case
                # Convert result to readable text
                if tool_name == "get_user_info":
                    text = f"**User Information:**\n" \
                           f"• User: {raw_result.get('user', 'Unknown')}\n" \
                           f"• Full Name: {raw_result.get('full_name', 'Unknown')}\n" \
                           f"• Email: {raw_result.get('email', 'Unknown')}\n" \
                           f"• Site: {raw_result.get('site', 'Unknown')}\n" \
                           f"• Roles: {', '.join(raw_result.get('roles', []))}\n" \
                           f"• Timestamp: {raw_result.get('timestamp', 'Unknown')}"
                
                elif tool_name == "get_doctypes":
                    doctypes = raw_result.get('doctypes', [])
                    count = raw_result.get('count', 0)
                    text = f"**Available Document Types ({count} found):**\n\n"
                    for doctype in doctypes[:10]:  # Show first 10
                        text += f"• **{doctype.get('name', 'Unknown')}**"
                        if doctype.get('description'):
                            text += f" - {doctype['description']}"
                        text += f" (Module: {doctype.get('module', 'Unknown')})\n"
                    if count > 10:
                        text += f"\n... and {count - 10} more document types"
                
                elif tool_name == "create_document":
                    text = f"**Document Created Successfully:**\n" \
                           f"• Document Type: {raw_result.get('doctype', 'Unknown')}\n" \
                           f"• Document Name: {raw_result.get('name', 'Unknown')}\n" \
                           f"• Created By: {raw_result.get('created_by', 'Unknown')}\n" \
                           f"• Timestamp: {raw_result.get('timestamp', 'Unknown')}"
                
                elif tool_name == "get_document":
                    doc_data = raw_result.get('data', {})
                    text = f"**Document Details:**\n" \
                           f"• Document Type: {raw_result.get('doctype', 'Unknown')}\n" \
                           f"• Document Name: {raw_result.get('name', 'Unknown')}\n" \
                           f"• Creation: {doc_data.get('creation', 'Unknown')}\n" \
                           f"• Modified: {doc_data.get('modified', 'Unknown')}\n" \
                           f"• Owner: {doc_data.get('owner', 'Unknown')}\n\n" \
                           f"**Key Fields:**\n"
                    
                    # Show some key fields (limit to important ones)
                    important_fields = ['name', 'title', 'subject', 'description', 'status', 'enabled']
                    for field in important_fields:
                        if field in doc_data and doc_data[field]:
                            text += f"• {field.title()}: {doc_data[field]}\n"
                
                elif tool_name == "search_documents":
                    results = raw_result.get('results', [])
                    count = raw_result.get('count', 0)
                    text = f"**Search Results ({count} found):**\n\n"
                    for result in results[:5]:  # Show first 5
                        text += f"• **{result.get('name', 'Unknown')}**\n"
                        if result.get('creation'):
                            text += f"  Created: {result['creation']}\n"
                        if result.get('modified'):
                            text += f"  Modified: {result['modified']}\n"
                        text += "\n"
                    if count > 5:
                        text += f"... and {count - 5} more results"
                
                # Handle analysis tools
                elif tool_name.startswith("execute_python"):
                    text = f"**Python Code Execution Result:**\n"
                    if raw_result.get('output'):
                        text += f"**Output:**\n```\n{raw_result['output']}\n```\n"
                    if raw_result.get('variables'):
                        text += f"\n**Variables Created:** {len(raw_result['variables'])}\n"
                        for var_name, var_value in raw_result['variables'].items():
                            text += f"• {var_name}: {str(var_value)[:100]}...\n" if len(str(var_value)) > 100 else f"• {var_name}: {var_value}\n"
                    if raw_result.get('errors'):
                        text += f"\n**Warnings/Errors:**\n```\n{raw_result['errors']}\n```"
                
                elif tool_name.startswith("analyze_frappe"):
                    analysis = raw_result.get('analysis', {})
                    text = f"**Data Analysis Results:**\n"
                    text += f"• Analysis Type: {analysis.get('type', 'Unknown')}\n"
                    text += f"• DocType: {analysis.get('doctype', 'Unknown')}\n"
                    if analysis.get('numerical_summary'):
                        text += f"\n**Numerical Summary:**\n"
                        for field, stats in analysis['numerical_summary'].items():
                            text += f"• {field}: Count={stats.get('count', 0)}, Mean={stats.get('mean', 0):.2f}\n"
                    if analysis.get('categorical_summary'):
                        text += f"\n**Categorical Summary:**\n"
                        for field, counts in analysis['categorical_summary'].items():
                            text += f"• {field}: {len(counts)} unique values\n"
                
                elif tool_name.startswith("query_and"):
                    text = f"**Query Results:**\n"
                    text += f"• Rows Returned: {raw_result.get('row_count', 0)}\n"
                    if raw_result.get('columns'):
                        text += f"• Columns: {', '.join(raw_result['columns'])}\n"
                    if raw_result.get('analysis_output'):
                        text += f"\n**Analysis Output:**\n```\n{raw_result['analysis_output']}\n```"
                
                elif tool_name.startswith("create_visualization"):
                    text = f"**Visualization Created:**\n"
                    config = raw_result.get('chart_config', {})
                    text += f"• Chart Type: {config.get('type', 'Unknown')}\n"
                    text += f"• Title: {config.get('title', 'Unknown')}\n"
                    
                    # Show inline chart if base64 is available
                    if raw_result.get('chart_base64'):
                        text += f"• Chart created successfully!\n\n"
                        text += f"📊 **Chart Preview:** Chart should be displayed below\n"
                        
                    if raw_result.get('chart_saved'):
                        text += f"• Chart also saved to: {raw_result.get('chart_url', 'Unknown')}\n"
                        
                    if raw_result.get('data_summary'):
                        summary = raw_result['data_summary']
                        text += f"• Data Records: {summary.get('records', 0)}\n"
                        text += f"• Fields Used: {', '.join(summary.get('fields', []))}\n"
                        
                    if raw_result.get('save_error'):
                        text += f"⚠️ **Error:** {raw_result['save_error']}\n"
                        if raw_result.get('error_details'):
                            error_details = raw_result['error_details']
                            text += f"**Error Type:** {error_details.get('error_type', 'Unknown')}\n"
                            
                    # Debug info will be added later in the general section for visualizations
                        
                    if raw_result.get('visualization_code') and not raw_result.get('chart_base64'):
                        text += f"\n**Generated Code (fallback):**\n```python\n{raw_result['visualization_code'][:500]}...\n```"
                
                # Handle report tools
                elif tool_name == "report_execute":
                    text = f"**Report Execution Results:**\n"
                    text += f"• Report: {raw_result.get('report_name', 'Unknown')}\n"
                    text += f"• Type: {raw_result.get('report_type', 'Unknown')}\n"
                    data = raw_result.get('data', [])
                    text += f"• Records: {len(data)}\n"
                    if raw_result.get('columns'):
                        text += f"• Columns: {len(raw_result['columns'])}\n"
                    if data and len(data) > 0:
                        text += f"\n**Sample Data (first 3 rows):**\n"
                        for i, row in enumerate(data[:3]):
                            text += f"Row {i+1}: {str(row)[:100]}...\n" if len(str(row)) > 100 else f"Row {i+1}: {row}\n"
                    if raw_result.get('message'):
                        text += f"\n**Message:** {raw_result['message']}\n"
                
                elif tool_name == "report_list":
                    reports = raw_result.get('reports', [])
                    text = f"**Available Reports ({len(reports)} found):**\n\n"
                    for report in reports[:10]:  # Show first 10
                        text += f"• **{report.get('report_name', 'Unknown')}**\n"
                        text += f"  Type: {report.get('report_type', 'Unknown')}\n"
                        text += f"  Module: {report.get('module', 'Unknown')}\n"
                        if not report.get('is_standard'):
                            text += f"  (Custom Report)\n"
                        text += "\n"
                    if len(reports) > 10:
                        text += f"... and {len(reports) - 10} more reports\n"
                
                elif tool_name == "report_columns":
                    text = f"**Report Column Information:**\n"
                    text += f"• Report: {raw_result.get('report_name', 'Unknown')}\n"
                    text += f"• Type: {raw_result.get('report_type', 'Unknown')}\n"
                    columns = raw_result.get('columns', [])
                    text += f"• Total Columns: {len(columns)}\n\n"
                    if columns:
                        text += f"**Columns:**\n"
                        for col in columns[:15]:  # Show first 15 columns
                            if isinstance(col, dict):
                                label = col.get('label', col.get('fieldname', 'Unknown'))
                                fieldtype = col.get('fieldtype', 'Unknown')
                                text += f"• {label} ({fieldtype})\n"
                            else:
                                text += f"• {str(col)}\n"
                        if len(columns) > 15:
                            text += f"... and {len(columns) - 15} more columns\n"
                
                # Handle search tools
                elif tool_name.startswith("search_"):
                    text = f"**Search Results:**\n"
                    if tool_name == "search_global":
                        text += f"• Query: '{raw_result.get('query', 'Unknown')}'\n"
                        results = raw_result.get('results', [])
                        text += f"• Found: {len(results)} results\n\n"
                        for result in results[:5]:
                            text += f"• **{result.get('title', result.get('name', 'Unknown'))}**\n"
                            text += f"  Type: {result.get('doctype', 'Unknown')}\n"
                            if result.get('content'):
                                text += f"  Preview: {result['content'][:100]}...\n"
                            text += "\n"
                    else:
                        # search_doctype, search_link
                        results = raw_result.get('results', [])
                        text += f"• Found: {len(results)} results in {raw_result.get('doctype', 'Unknown')}\n\n"
                        for result in results[:5]:
                            text += f"• {result.get('name', result.get('title', 'Unknown'))}\n"
                
                # Handle metadata tools  
                elif tool_name.startswith("metadata_"):
                    if tool_name == "metadata_doctype":
                        text = f"**DocType Metadata:**\n"
                        text += f"• DocType: {raw_result.get('doctype', 'Unknown')}\n"
                        text += f"• Module: {raw_result.get('module', 'Unknown')}\n"
                        text += f"• Is Custom: {raw_result.get('custom', False)}\n"
                        fields = raw_result.get('fields', [])
                        text += f"• Total Fields: {len(fields)}\n\n"
                        if fields:
                            text += "**Key Fields:**\n"
                            for field in fields[:10]:
                                text += f"• {field.get('label', field.get('fieldname', 'Unknown'))} ({field.get('fieldtype', 'Unknown')})\n"
                    
                    elif tool_name == "metadata_list_doctypes":
                        doctypes = raw_result.get('doctypes', [])
                        text = f"**Available DocTypes ({len(doctypes)} found):**\n\n"
                        for dt in doctypes[:10]:
                            text += f"• **{dt.get('name', 'Unknown')}**\n"
                            text += f"  Module: {dt.get('module', 'Unknown')}\n"
                            if dt.get('custom'):
                                text += f"  (Custom DocType)\n"
                            text += "\n"
                    
                    elif tool_name == "metadata_permissions":
                        text = f"**Permission Information:**\n"
                        text += f"• DocType: {raw_result.get('doctype', 'Unknown')}\n"
                        perms = raw_result.get('permissions', [])
                        text += f"• Permission Rules: {len(perms)}\n"
                        user_perms = raw_result.get('user_permissions', {})
                        text += f"• User Can Read: {user_perms.get('read', False)}\n"
                        text += f"• User Can Write: {user_perms.get('write', False)}\n"
                        text += f"• User Can Create: {user_perms.get('create', False)}\n"
                    
                    else:
                        # Generic metadata formatting
                        text = f"**Metadata Result:**\n"
                        text += f"```json\n{json.dumps(raw_result, indent=2)[:500]}...\n```"
                
                # Handle document tools
                elif tool_name.startswith("document_"):
                    if tool_name == "document_create":
                        text = f"**Document Created:**\n"
                        text += f"• DocType: {raw_result.get('doctype', 'Unknown')}\n"
                        text += f"• Name: {raw_result.get('name', 'Unknown')}\n"
                        text += f"• Status: {raw_result.get('status', 'Unknown')}\n"
                    
                    elif tool_name == "document_get":
                        text = f"**Document Retrieved:**\n"
                        text += f"• DocType: {raw_result.get('doctype', 'Unknown')}\n"
                        text += f"• Name: {raw_result.get('name', 'Unknown')}\n"
                        doc_data = raw_result.get('data', {})
                        text += f"• Modified: {doc_data.get('modified', 'Unknown')}\n"
                        text += f"• Owner: {doc_data.get('owner', 'Unknown')}\n"
                    
                    elif tool_name == "document_list":
                        results = raw_result.get('results', [])
                        text = f"**Document List:**\n"
                        text += f"• DocType: {raw_result.get('doctype', 'Unknown')}\n"
                        text += f"• Found: {len(results)} documents\n\n"
                        for doc in results[:5]:
                            text += f"• {doc.get('name', 'Unknown')}\n"
                    
                    elif tool_name == "document_update":
                        text = f"**Document Updated:**\n"
                        text += f"• DocType: {raw_result.get('doctype', 'Unknown')}\n"
                        text += f"• Name: {raw_result.get('name', 'Unknown')}\n"
                        text += f"• Updated By: {raw_result.get('updated_by', 'Unknown')}\n"
                    
                    else:
                        text = f"**Document Operation Result:**\n"
                        text += f"```json\n{json.dumps(raw_result, indent=2)[:300]}...\n```"
                
                else:
                    # Generic formatting for unknown tools
                    text = f"**Tool Result ({tool_name}):**\n"
                    text += f"```json\n{json.dumps(raw_result, indent=2)}\n```"
                
                # Add image data to text BEFORE creating content blocks
                if tool_name.startswith("create_visualization") and raw_result.get('chart_base64'):
                    chart_base64 = raw_result['chart_base64']
                    
                    # Try embedding the image as markdown in the text content
                    if isinstance(chart_base64, str) and chart_base64:
                        # Add debug info first
                        text += f"\n\n**Chart Details:**\n"
                        text += f"• Base64 Data Length: {len(chart_base64)} characters\n"
                        text += f"• Data URL Format: {chart_base64[:50]}...\n\n"
                        
                        # Try markdown image embedding with data URL
                        text += f"📊 **Chart Visualization:**\n"
                        text += f"![Generated Chart]({chart_base64})\n\n"
                        
                        # Add alternative access
                        text += f"*If chart doesn't display above, use the file URL provided earlier.*\n"
                
                # Return formatted content
                content_blocks = [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
                
                response = {
                    "jsonrpc": "2.0",
                    "result": {
                        "content": content_blocks
                    }
                }
            else:
                # Error case
                error_msg = raw_result.get('error', 'Unknown error occurred')
                response = {
                    "jsonrpc": "2.0",
                    "result": {
                        "content": [
                            {
                                "type": "text", 
                                "text": f"❌ **Error executing {tool_name}:**\n{error_msg}"
                            }
                        ]
                    }
                }
        
        # Only include id if it's not None
        if request_id is not None:
            response["id"] = request_id
            
        return response
        
    except Exception as e:
        print(f"❌ Error in handle_tool_call: {e}")
        
        response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Error executing tool",
                "data": str(e)
            }
        }
        
        # Only include id if it's not None
        if request_id is not None:
            response["id"] = request_id
            
        return response

def execute_tool(tool_name, arguments):
    """Execute a specific assistant tool"""
    try:
        print(f"🔧 Executing tool: {tool_name}")
        
        if tool_name == "get_user_info":
            return {
                "user": frappe.session.user,
                "full_name": frappe.session.get('user_name', 'Unknown'),
                "email": frappe.session.user,
                "roles": frappe.get_roles(),
                "site": frappe.local.site,
                "timestamp": frappe.utils.now()
            }
        
        elif tool_name == "get_doctypes":
            limit = arguments.get("limit", 50)
            doctypes = frappe.get_all(
                "DocType",
                filters={"istable": 0, "issingle": 0, "custom": 0},
                fields=["name", "module", "description"],
                limit=limit,
                order_by="name"
            )
            return {
                "doctypes": doctypes,
                "count": len(doctypes),
                "limit_applied": limit
            }
        
        elif tool_name == "create_document":
            doctype = arguments.get("doctype")
            data = arguments.get("data", {})
            
            print(f"🔧 Creating document: {doctype}")
            print(f"🔧 Data: {data}")
            
            if not doctype:
                raise Exception("Missing doctype parameter")
            
            # Check if doctype exists
            if not frappe.db.exists("DocType", doctype):
                raise Exception(f"DocType '{doctype}' does not exist")
            
            # Check permissions
            if not frappe.has_permission(doctype, "create"):
                raise Exception(f"No create permission for {doctype}")
            
            try:
                # Ensure data has doctype
                data["doctype"] = doctype
                
                print(f"🔧 Creating document with data: {data}")
                
                # Create document
                doc = frappe.get_doc(data)
                
                print(f"🔧 Document object created: {doc.name}")
                
                # Insert document (this saves to database)
                doc.insert()
                
                print(f"🔧 Document inserted with name: {doc.name}")
                
                # Commit the transaction
                frappe.db.commit()
                
                print(f"🔧 Database committed")
                
                # Verify document was created
                if frappe.db.exists(doctype, doc.name):
                    print(f"✅ Document {doc.name} verified in database")
                    
                    return {
                        "success": True,
                        "name": doc.name,
                        "doctype": doctype,
                        "created_by": frappe.session.user,
                        "timestamp": frappe.utils.now(),
                        "status": "Draft" if doc.docstatus == 0 else "Submitted"
                    }
                else:
                    raise Exception(f"Document was not saved to database")
                    
            except frappe.ValidationError as e:
                print(f"❌ Validation error: {e}")
                raise Exception(f"Validation failed: {str(e)}")
                
            except frappe.DuplicateEntryError as e:
                print(f"❌ Duplicate entry error: {e}")
                raise Exception(f"Duplicate entry: {str(e)}")
                
            except Exception as e:
                print(f"❌ Document creation error: {e}")
                # Rollback in case of error
                frappe.db.rollback()
                raise Exception(f"Failed to create document: {str(e)}")
        
        elif tool_name == "get_document":
            doctype = arguments.get("doctype")
            name = arguments.get("name")
            
            if not doctype or not name:
                raise Exception("Missing doctype or name parameter")
            
            # Check if document exists
            if not frappe.db.exists(doctype, name):
                raise Exception(f"Document {doctype} '{name}' not found")
            
            # Check permissions
            if not frappe.has_permission(doctype, "read", name):
                raise Exception(f"No read permission for {doctype} {name}")
            
            doc = frappe.get_doc(doctype, name)
            return {
                "success": True,
                "doctype": doctype,
                "name": name,
                "data": doc.as_dict(),
                "retrieved_by": frappe.session.user,
                "timestamp": frappe.utils.now()
            }
        
        elif tool_name == "search_documents":
            doctype = arguments.get("doctype")
            filters = arguments.get("filters", {})
            fields = arguments.get("fields", ["name", "creation", "modified"])
            limit = arguments.get("limit", 20)
            
            if not doctype:
                raise Exception("Missing doctype parameter")
            
            # Check permissions
            if not frappe.has_permission(doctype, "read"):
                raise Exception(f"No read permission for {doctype}")
            
            # Search documents
            results = frappe.get_all(
                doctype,
                filters=filters,
                fields=fields,
                limit=limit,
                order_by="modified desc"
            )
            
            return {
                "success": True,
                "doctype": doctype,
                "results": results,
                "count": len(results),
                "filters_applied": filters,
                "searched_by": frappe.session.user,
                "timestamp": frappe.utils.now()
            }
        
        # Use auto-discovery system to execute tools
        else:
            try:
                from frappe_assistant_core.tools.tool_registry import AutoToolRegistry
                return AutoToolRegistry.execute_tool(tool_name, arguments)
            except Exception as e:
                print(f"Auto-discovery failed for {tool_name}: {e}")
                raise Exception(f"Unknown tool: {tool_name}")
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Tool execution error: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "tool": tool_name,
            "arguments": arguments
        }

def _check_tool_permission(tool):
    """Check if current user has permission to use a tool"""
    try:
        tool_name = tool.get("name", "")
        
        # Basic permission checks based on tool type
        if tool_name.startswith("execute_") or tool_name.startswith("analyze_") or tool_name.startswith("query_"):
            # Analysis tools - require System Manager or basic read access
            return frappe.has_permission("System Settings", "read") or "System Manager" in frappe.get_roles()
        
        elif tool_name.startswith("report_"):
            # Report tools - check if user can access reports
            return frappe.has_permission("Report", "read")
        
        elif tool_name.startswith("search_") or tool_name.startswith("metadata_"):
            # Search and metadata tools - basic access
            return True  # Most users should be able to search and view metadata
        
        elif tool_name.startswith("document_"):
            # Document tools - basic document access
            return True  # Will be checked per-doctype during execution
        
        else:
            # Basic tools - always available
            return True
            
    except Exception as e:
        print(f"Error checking tool permission: {e}")
        return True  # Default to allowing access

# Additional utility endpoints
@frappe.whitelist(allow_guest=True)
def ping():
    """Simple ping endpoint for testing"""
    try:
        return {
            "status": "ok",
            "site": frappe.local.site if hasattr(frappe.local, 'site') else "unknown",
            "db_connected": bool(frappe.db),
            "message": "assistant Server API is working",
            "timestamp": frappe.utils.now()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@frappe.whitelist(allow_guest=False)
def test_auth():
    """Test authenticated endpoint"""
    try:
        return {
            "status": "authenticated",
            "site": frappe.local.site,
            "user": frappe.session.user,
            "user_name": frappe.session.get('user_name', 'Unknown'),
            "roles": frappe.get_roles(),
            "db_connected": bool(frappe.db),
            "timestamp": frappe.utils.now()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def log_assistant_connection():
    """Log assistant connection (only once per session)"""
    try:
        if frappe.db.table_exists("Assistant Connection Log"):
            client_id = frappe.session.get("sid", "unknown")
            
            # Check if we already logged this session today
            existing = frappe.db.exists("Assistant Connection Log", {
                "client_id": client_id,
                "connected_at": [">=", frappe.utils.today()]
            })
            
            if not existing:
                frappe.get_doc({
                    "doctype": "Assistant Connection Log",
                    "client_id": client_id,
                    "user": frappe.session.user,
                    "connected_at": frappe.utils.now(),
                    "connection_type": "HTTP",
                    "status": "Connected",
                    "ip_address": frappe.local.request_ip if hasattr(frappe.local, "request_ip") else None,
                    "user_agent": frappe.local.request.headers.get("User-Agent", "") if hasattr(frappe.local, "request") else ""
                }).insert(ignore_permissions=True)
                frappe.db.commit()
    except Exception as e:
        print(f"Failed to log connection: {e}")

def log_assistant_audit(action, params, response, status):
    """Log assistant audit trail"""
    try:
        if frappe.db.table_exists("Assistant Audit Log"):
            audit_doc = frappe.get_doc({
                "doctype": "Assistant Audit Log",
                "action": action,
                "user": frappe.session.user,
                "timestamp": frappe.utils.now(),
                "status": status,
                "ip_address": frappe.local.request_ip if hasattr(frappe.local, "request_ip") else None,
                "request_data": json.dumps(params) if params else None,
                "response_data": json.dumps(response) if response else None,
                "execution_time": 0
            })
            
            if action == "tools/call" and params:
                audit_doc.tool_name = params.get("name")
                if "arguments" in params:
                    audit_doc.tool_arguments = json.dumps(params["arguments"])
            
            audit_doc.insert(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        print(f"Failed to log audit: {e}")

@frappe.whitelist()
def populate_tool_registry():
    """Populate Assistant Tool Registry with available tools"""
    try:
        if not frappe.db.table_exists("Assistant Tool Registry"):
            return {"success": False, "message": "Assistant Tool Registry table not found"}
            
        tools = [
            {
                "tool_name": "get_user_info", 
                "tool_description": "Get current user information", 
                "input_schema": '{"type": "object", "properties": {}}',
                "enabled": 1, 
                "required_permissions": '["System Manager"]', 
                "category": "Metadata"
            },
            {
                "tool_name": "get_doctypes", 
                "tool_description": "List all available document types", 
                "input_schema": '{"type": "object", "properties": {"limit": {"type": "integer", "default": 50}}}',
                "enabled": 1, 
                "required_permissions": '["System Manager"]', 
                "category": "Metadata"
            },
            {
                "tool_name": "create_document", 
                "tool_description": "Create a new document", 
                "input_schema": '{"type": "object", "properties": {"doctype": {"type": "string"}, "data": {"type": "object"}}, "required": ["doctype", "data"]}',
                "enabled": 1, 
                "required_permissions": '["System User"]', 
                "category": "Document Operations"
            },
            {
                "tool_name": "get_document", 
                "tool_description": "Get a specific document", 
                "input_schema": '{"type": "object", "properties": {"doctype": {"type": "string"}, "name": {"type": "string"}}, "required": ["doctype", "name"]}',
                "enabled": 1, 
                "required_permissions": '["System User"]', 
                "category": "Document Operations"
            },
            {
                "tool_name": "search_documents", 
                "tool_description": "Search documents with filters", 
                "input_schema": '{"type": "object", "properties": {"doctype": {"type": "string"}, "filters": {"type": "object"}, "fields": {"type": "array"}, "limit": {"type": "integer"}}, "required": ["doctype"]}',
                "enabled": 1, 
                "required_permissions": '["System User"]', 
                "category": "Search"
            }
        ]
        
        created = 0
        for tool in tools:
            if not frappe.db.exists("Assistant Tool Registry", tool["tool_name"]):
                frappe.get_doc({
                    "doctype": "Assistant Tool Registry",
                    "name": tool["tool_name"],
                    **tool
                }).insert(ignore_permissions=True)
                created += 1
        
        frappe.db.commit()
        return {"success": True, "message": f"Created {created} tool registry entries"}
        
    except Exception as e:
        return {"success": False, "message": f"Failed to populate tool registry: {e}"}

@frappe.whitelist()
def get_usage_statistics():
    """Get usage statistics for the admin dashboard"""
    try:
        stats = {
            "connections": {
                "total": frappe.db.count("Assistant Connection Log"),
                "today": frappe.db.count("Assistant Connection Log", {
                    "connected_at": [">=", frappe.utils.today()]
                }),
                "this_week": frappe.db.count("Assistant Connection Log", {
                    "connected_at": [">=", frappe.utils.add_days(frappe.utils.today(), -7)]
                })
            },
            "audit_logs": {
                "total": frappe.db.count("Assistant Audit Log"),
                "today": frappe.db.count("Assistant Audit Log", {
                    "timestamp": [">=", frappe.utils.today()]
                }),
                "this_week": frappe.db.count("Assistant Audit Log", {
                    "timestamp": [">=", frappe.utils.add_days(frappe.utils.today(), -7)]
                })
            },
            "tools": {
                "total": frappe.db.count("Assistant Tool Registry"),
                "enabled": frappe.db.count("Assistant Tool Registry", {"enabled": 1})
            },
            "recent_activity": frappe.get_all("Assistant Audit Log", 
                fields=["action", "user", "timestamp", "status", "tool_name"],
                limit=10,
                order_by="timestamp desc"
            )
        }
        
        return {"success": True, "data": stats}
        
    except Exception as e:
        return {"success": False, "message": f"Failed to get usage statistics: {e}"}

@frappe.whitelist()
def force_test_logging():
    """Force create test log entries for debugging"""
    try:
        # Test connection log
        if frappe.db.table_exists("Assistant Connection Log"):
            frappe.get_doc({
                "doctype": "Assistant Connection Log",
                "client_id": "test-" + frappe.utils.random_string(8),
                "user": frappe.session.user,
                "connected_at": frappe.utils.now(),
                "connection_type": "HTTP",
                "status": "Connected",
                "ip_address": "127.0.0.1",
                "user_agent": "Test Agent"
            }).insert(ignore_permissions=True)
        
        # Test audit log
        if frappe.db.table_exists("Assistant Audit Log"):
            frappe.get_doc({
                "doctype": "Assistant Audit Log",
                "action": "get_metadata",
                "user": frappe.session.user,
                "timestamp": frappe.utils.now(),
                "status": "Success",
                "ip_address": "127.0.0.1",
                "request_data": '{"test": true}',
                "response_data": '{"result": "test"}',
                "execution_time": 150
            }).insert(ignore_permissions=True)
        
        frappe.db.commit()
        return {"success": True, "message": "Test log entries created"}
        
    except Exception as e:
        return {"success": False, "message": f"Failed to create test logs: {e}"}
