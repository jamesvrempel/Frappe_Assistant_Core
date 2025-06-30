"""
[Tool Category] Tools Template
Template for creating new tool categories in Frappe Assistant Core

Instructions:
1. Replace [ToolCategory] with your tool category name (e.g., "Analytics", "Reporting")
2. Replace [tool_category] with lowercase version (e.g., "analytics", "reporting") 
3. Implement the helper functions at the bottom
4. Update the MCP schema in get_tools() method
5. Add proper error handling and validation
6. Create corresponding test file using test_template.py
"""

import frappe
import json
from typing import Dict, Any, List, Optional
from frappe_assistant_core.utils.permissions import check_user_permission
from frappe_assistant_core.utils.response_builder import build_response
from frappe_assistant_core.utils.validation import validate_doctype_access
from frappe_assistant_core.utils.enhanced_error_handling import handle_tool_error

class [ToolCategory]Tools:
    """[Tool category] operations for Frappe Assistant Core"""
    
    @staticmethod
    def get_tools() -> List[Dict[str, Any]]:
        """Get available [tool category] tools with MCP schema"""
        return [
            {
                "name": "[tool_category]_operation_1",
                "description": "Brief description of what this tool does",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doctype": {
                            "type": "string",
                            "description": "Name of the DocType to operate on"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name/ID of the specific document"
                        },
                        "optional_param": {
                            "type": "string",
                            "description": "Optional parameter description",
                            "optional": True
                        }
                    },
                    "required": ["doctype", "name"]
                }
            },
            {
                "name": "[tool_category]_operation_2",
                "description": "Description of second tool operation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doctype": {
                            "type": "string",
                            "description": "DocType name for the operation"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Filter criteria for the operation",
                            "default": {}
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of records to return",
                            "default": 20
                        }
                    },
                    "required": ["doctype"]
                }
            }
        ]
    
    @staticmethod  
    def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool by name"""
        if tool_name == "[tool_category]_operation_1":
            return [ToolCategory]Tools.operation_1(**arguments)
        elif tool_name == "[tool_category]_operation_2":
            return [ToolCategory]Tools.operation_2(**arguments)
        else:
            raise Exception(f"Unknown tool: {tool_name}")
    
    @staticmethod
    def operation_1(doctype: str, name: str, optional_param: Optional[str] = None) -> Dict[str, Any]:
        """
        [Description of what this operation does]
        
        Args:
            doctype (str): Name of the DocType
            name (str): Name/ID of the document
            optional_param (str, optional): Description of optional parameter
            
        Returns:
            Dict[str, Any]: Response with operation results
        """
        try:
            # Validate DocType exists
            if not frappe.db.exists("DocType", doctype):
                return {"success": False, "error": f"DocType '{doctype}' does not exist"}
            
            # Permission check
            if not frappe.has_permission(doctype, "read"):
                return {"success": False, "error": f"No read permission for {doctype}"}
            
            # Input validation
            if not name or not name.strip():
                return {"success": False, "error": "name is required and cannot be empty"}
            
            # Check if document exists
            if not frappe.db.exists(doctype, name):
                return {"success": False, "error": f"Document {name} does not exist in {doctype}"}
            
            # Main operation logic - replace with actual implementation
            result = perform_operation_1_logic(doctype, name, optional_param)
            
            # IMPORTANT: This response structure is verified by tests
            # Always return: success, doctype, name, data (NOT "document")
            return {
                "success": True,
                "doctype": doctype,
                "name": name,
                "data": result,  # Use "data" key, NOT "document"
                "optional_param_used": optional_param
            }
            
        except Exception as e:
            frappe.log_error(f"Error in operation_1: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def operation_2(doctype: str, filters: Optional[Dict] = None, limit: int = 20) -> Dict[str, Any]:
        """
        [Description of what this operation does]
        
        Args:
            doctype (str): Name of the DocType
            filters (dict, optional): Filter criteria
            limit (int): Maximum number of records to return
            
        Returns:
            Dict[str, Any]: Response with operation results
        """
        try:
            # Validate DocType exists
            if not frappe.db.exists("DocType", doctype):
                return {"success": False, "error": f"DocType '{doctype}' does not exist"}
            
            # Permission check
            if not frappe.has_permission(doctype, "read"):
                return {"success": False, "error": f"No read permission for {doctype}"}
            
            # Validate limit
            if limit <= 0 or limit > 1000:
                return {"success": False, "error": "Limit must be between 1 and 1000"}
            
            # Main operation logic - replace with actual implementation
            results = perform_operation_2_logic(doctype, filters or {}, limit)
            
            # IMPORTANT: This response structure is verified by tests
            # Always return: success, doctype, results, filters_applied, limit_used, total_count
            return {
                "success": True,
                "doctype": doctype,
                "results": results,  # Use "results" for list operations
                "filters_applied": filters or {},
                "limit_used": limit,
                "total_count": len(results) if isinstance(results, list) else 1
            }
            
        except Exception as e:
            frappe.log_error(f"Error in operation_2: {str(e)}")
            return {"success": False, "error": str(e)}
    

# Helper functions - implement these based on your tool's requirements
def perform_operation_1_logic(doctype: str, name: str, optional_param: Optional[str] = None):
    """
    Implement the actual logic for operation 1
    
    Args:
        doctype (str): DocType name
        name (str): Document name
        optional_param (str, optional): Optional parameter
        
    Returns:
        Any: Result of the operation
    """
    # TODO: Implement actual operation logic
    # Example:
    doc = frappe.get_doc(doctype, name)
    
    # Perform your operation here
    # This could be data analysis, calculations, transformations, etc.
    
    return {
        "processed": True,
        "document_data": doc.as_dict(),
        "additional_info": "Operation completed"
    }

def perform_operation_2_logic(doctype: str, filters: Optional[Dict] = None, limit: int = 20):
    """
    Implement the actual logic for operation 2
    
    Args:
        doctype (str): DocType name
        filters (dict, optional): Filter criteria
        limit (int): Maximum records to return
        
    Returns:
        List: Result of the operation
    """
    # TODO: Implement actual operation logic
    # Example:
    
    # Build query filters
    query_filters = filters or {}
    
    # Get documents using frappe.get_all
    # NOTE: frappe.get_all returns objects with dot notation access (obj.field_name)
    # NOT dictionaries - this is important for testing mock patterns
    documents = frappe.get_all(
        doctype,
        filters=query_filters,
        limit=limit,
        order_by="creation desc"
    )
    
    # Process documents if needed
    processed_results = []
    for doc in documents:
        # NOTE: Use dot notation to access doc fields (doc.name, doc.field)
        # because frappe.get_all returns objects, not dictionaries
        processed_results.append({
            "name": doc.name,  # Use dot notation, NOT doc.get("name")
            "processed_data": doc,
            "processing_timestamp": frappe.utils.now()
        })
    
    return processed_results

# Additional helper functions as needed
def validate_[tool_category]_specific_permission(operation: str) -> bool:
    """
    Validate [tool category] specific permissions
    
    Args:
        operation (str): The operation being performed
        
    Returns:
        bool: True if user has permission, False otherwise
    """
    # TODO: Implement permission logic specific to your tool category
    # Example:
    user_roles = frappe.get_roles()
    
    required_roles = {
        "operation_1": ["System Manager", "[ToolCategory] User"],
        "operation_2": ["System Manager", "[ToolCategory] Manager"]
    }
    
    if operation not in required_roles:
        return False
    
    return any(role in user_roles for role in required_roles[operation])

def get_[tool_category]_settings() -> Dict[str, Any]:
    """
    Get [tool category] specific settings
    
    Returns:
        Dict[str, Any]: Configuration settings for the tool category
    """
    # TODO: Implement settings retrieval
    # This could read from Frappe settings, custom DocTypes, or configuration files
    
    return {
        "enabled": True,
        "max_records": 1000,
        "cache_enabled": True,
        "cache_timeout": 300
    }