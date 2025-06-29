# Tool Development Templates for Frappe Assistant Core

## Overview

This document provides templates and examples for creating new tools and their corresponding test cases in the Frappe Assistant Core system. These templates ensure consistency and completeness across all tool implementations.

## Tool Class Template

### Basic Tool Structure

```python
"""
[Tool Category] Tools
[Brief description of what this tool category handles]
"""

import frappe
import json
from typing import Dict, Any, List, Optional
from frappe_assistant_core.utils.permissions import check_user_permission
from frappe_assistant_core.utils.response_builder import build_response
from frappe_assistant_core.utils.validation import validate_doctype_access
from frappe_assistant_core.utils.enhanced_error_handling import handle_tool_error

class [ToolName]Tools:
    """[Tool category] operations for Frappe Assistant Core"""
    
    @staticmethod
    def get_tools() -> List[Dict[str, Any]]:
        """Get available [tool category] tools with MCP schema"""
        return [
            {
                "name": "tool_operation_1",
                "description": "Description of what this tool does",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "Description of parameter 1"
                        },
                        "param2": {
                            "type": "string", 
                            "description": "Description of parameter 2",
                            "optional": True
                        }
                    },
                    "required": ["param1"]
                }
            },
            {
                "name": "tool_operation_2", 
                "description": "Description of second tool operation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doctype": {
                            "type": "string",
                            "description": "DocType name"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Filter criteria",
                            "optional": True
                        }
                    },
                    "required": ["doctype"]
                }
            }
        ]
    
    @staticmethod
    @handle_tool_error
    def tool_operation_1(param1: str, param2: Optional[str] = None) -> Dict[str, Any]:
        """
        [Description of operation 1]
        
        Args:
            param1 (str): Description of parameter 1
            param2 (str, optional): Description of parameter 2
            
        Returns:
            Dict[str, Any]: Response with operation results
        """
        try:
            # Permission check
            if not check_user_permission("Operation1"):
                return build_response(
                    success=False,
                    error="Insufficient permissions for operation 1"
                )
            
            # Input validation
            if not param1 or not param1.strip():
                return build_response(
                    success=False,
                    error="param1 is required and cannot be empty"
                )
            
            # Main operation logic
            result = perform_operation_1(param1, param2)
            
            return build_response(
                success=True,
                data={
                    "operation_result": result,
                    "param1_used": param1,
                    "param2_used": param2
                }
            )
            
        except frappe.PermissionError:
            return build_response(
                success=False,
                error="Permission denied for operation 1"
            )
        except frappe.DoesNotExistError:
            return build_response(
                success=False,
                error=f"Resource not found: {param1}"
            )
        except Exception as e:
            frappe.log_error(f"Error in tool_operation_1: {str(e)}")
            return build_response(
                success=False,
                error=f"Operation failed: {str(e)}"
            )
    
    @staticmethod
    @handle_tool_error
    def tool_operation_2(doctype: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        [Description of operation 2]
        
        Args:
            doctype (str): Name of the DocType
            filters (dict, optional): Filter criteria
            
        Returns:
            Dict[str, Any]: Response with operation results
        """
        try:
            # Validate DocType access
            if not validate_doctype_access(doctype):
                return build_response(
                    success=False,
                    error=f"Access denied to DocType: {doctype}"
                )
            
            # Permission check
            if not frappe.has_permission(doctype, "read"):
                return build_response(
                    success=False,
                    error=f"No read permission for {doctype}"
                )
            
            # Main operation logic
            result = perform_operation_2(doctype, filters)
            
            return build_response(
                success=True,
                data={
                    "doctype": doctype,
                    "results": result,
                    "filters_applied": filters or {},
                    "count": len(result) if isinstance(result, list) else 1
                }
            )
            
        except Exception as e:
            frappe.log_error(f"Error in tool_operation_2: {str(e)}")
            return build_response(
                success=False,
                error=f"Operation failed: {str(e)}"
            )
    
    @staticmethod
    def execute_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific tool by name
        
        Args:
            tool_name (str): Name of the tool to execute
            args (dict): Arguments for the tool
            
        Returns:
            Dict[str, Any]: Tool execution result
        """
        tool_methods = {
            "tool_operation_1": [ToolName]Tools.tool_operation_1,
            "tool_operation_2": [ToolName]Tools.tool_operation_2,
        }
        
        if tool_name not in tool_methods:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        method = tool_methods[tool_name]
        return method(**args)

# Helper functions (implement as needed)
def perform_operation_1(param1: str, param2: Optional[str] = None):
    """Helper function for operation 1"""
    # Implementation here
    pass

def perform_operation_2(doctype: str, filters: Optional[Dict] = None):
    """Helper function for operation 2"""
    # Implementation here
    pass
```

## Test File Template

### Unit Test Template

```python
"""
Test suite for [Tool Category] Tools
Tests all [tool category] functionality
"""

import frappe
import unittest
import json
from unittest.mock import patch, MagicMock
from frappe_assistant_core.tools.[tool_file_name] import [ToolName]Tools
from frappe_assistant_core.tests.base_test import BaseAssistantTest, TestDataBuilder

class Test[ToolName]Tools(BaseAssistantTest):
    """Test suite for [tool category] tools functionality"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        self.tools = [ToolName]Tools()
    
    def test_get_tools_structure(self):
        """Test that get_tools returns proper structure"""
        tools = [ToolName]Tools.get_tools()
        
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        
        # Check each tool has required fields
        for tool in tools:
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("inputSchema", tool)
            self.assertIsInstance(tool["inputSchema"], dict)
    
    def test_tool_operation_1_basic(self):
        """Test basic tool operation 1 functionality"""
        # Mock dependencies
        with patch('[module_path].perform_operation_1') as mock_operation, \
             patch('frappe_assistant_core.utils.permissions.check_user_permission', return_value=True):
            
            mock_operation.return_value = "operation_result"
            
            result = [ToolName]Tools.tool_operation_1("test_param1", "test_param2")
            
            self.assertTrue(result.get("success"))
            self.assertIn("data", result)
            self.assertIn("operation_result", result["data"])
            self.assertEqual(result["data"]["param1_used"], "test_param1")
            self.assertEqual(result["data"]["param2_used"], "test_param2")
    
    def test_tool_operation_1_no_permission(self):
        """Test tool operation 1 without permission"""
        with patch('frappe_assistant_core.utils.permissions.check_user_permission', return_value=False):
            result = [ToolName]Tools.tool_operation_1("test_param")
            
            self.assertFalse(result.get("success"))
            self.assertIn("permission", result.get("error", "").lower())
    
    def test_tool_operation_1_invalid_input(self):
        """Test tool operation 1 with invalid input"""
        with patch('frappe_assistant_core.utils.permissions.check_user_permission', return_value=True):
            # Empty param1
            result = [ToolName]Tools.tool_operation_1("")
            
            self.assertFalse(result.get("success"))
            self.assertIn("required", result.get("error", "").lower())
    
    def test_tool_operation_2_basic(self):
        """Test basic tool operation 2 functionality"""
        mock_results = [
            {"name": "Doc1", "field": "value1"},
            {"name": "Doc2", "field": "value2"}
        ]
        
        with patch('[module_path].perform_operation_2', return_value=mock_results), \
             patch('frappe_assistant_core.utils.validation.validate_doctype_access', return_value=True), \
             patch('frappe.has_permission', return_value=True):
            
            result = [ToolName]Tools.tool_operation_2("Test DocType", {"field": "value"})
            
            self.assertTrue(result.get("success"))
            self.assertIn("data", result)
            self.assertIn("results", result["data"])
            self.assertEqual(len(result["data"]["results"]), 2)
            self.assertEqual(result["data"]["count"], 2)
    
    def test_tool_operation_2_no_doctype_access(self):
        """Test tool operation 2 without DocType access"""
        with patch('frappe_assistant_core.utils.validation.validate_doctype_access', return_value=False):
            result = [ToolName]Tools.tool_operation_2("Restricted DocType")
            
            self.assertFalse(result.get("success"))
            self.assertIn("access denied", result.get("error", "").lower())
    
    def test_tool_operation_2_no_permission(self):
        """Test tool operation 2 without permission"""
        with patch('frappe_assistant_core.utils.validation.validate_doctype_access', return_value=True), \
             patch('frappe.has_permission', return_value=False):
            
            result = [ToolName]Tools.tool_operation_2("Test DocType")
            
            self.assertFalse(result.get("success"))
            self.assertIn("permission", result.get("error", "").lower())
    
    def test_execute_tool_routing(self):
        """Test tool execution routing"""
        valid_tools = [
            "tool_operation_1",
            "tool_operation_2"
        ]
        
        for tool_name in valid_tools:
            try:
                result = [ToolName]Tools.execute_tool(tool_name, {})
                self.assertIsInstance(result, dict)
            except Exception:
                # Expected for some tools due to missing arguments
                pass
    
    def test_execute_tool_invalid_tool(self):
        """Test execution of invalid tool name"""
        with self.assertRaises(ValueError):
            [ToolName]Tools.execute_tool("invalid_tool_name", {})

class Test[ToolName]ToolsIntegration(BaseAssistantTest):
    """Integration tests for [tool category] tools"""
    
    def setUp(self):
        """Set up integration test environment"""
        super().setUp()
    
    def test_complete_workflow(self):
        """Test complete [tool category] workflow"""
        # Mock comprehensive workflow
        with patch('frappe_assistant_core.utils.permissions.check_user_permission', return_value=True), \
             patch('frappe_assistant_core.utils.validation.validate_doctype_access', return_value=True), \
             patch('frappe.has_permission', return_value=True):
            
            # Step 1: Operation 1
            with patch('[module_path].perform_operation_1', return_value="step1_result"):
                result1 = [ToolName]Tools.tool_operation_1("workflow_param")
                self.assertTrue(result1.get("success"))
            
            # Step 2: Operation 2 using result from step 1
            with patch('[module_path].perform_operation_2', return_value=[{"data": "step2_result"}]):
                result2 = [ToolName]Tools.tool_operation_2("Test DocType")
                self.assertTrue(result2.get("success"))
            
            # Verify workflow consistency
            self.assertIsNotNone(result1["data"]["operation_result"])
            self.assertIsNotNone(result2["data"]["results"])
    
    def test_error_handling_scenarios(self):
        """Test various error scenarios"""
        error_scenarios = [
            {
                "operation": "tool_operation_1",
                "args": ["test_param"],
                "side_effect": frappe.DoesNotExistError("Resource not found"),
                "expected_error": "not found"
            },
            {
                "operation": "tool_operation_2", 
                "args": ["Test DocType"],
                "side_effect": frappe.PermissionError("Access denied"),
                "expected_error": "permission"
            }
        ]
        
        for scenario in error_scenarios:
            with patch('[module_path].perform_operation_1', side_effect=scenario["side_effect"]), \
                 patch('[module_path].perform_operation_2', side_effect=scenario["side_effect"]), \
                 patch('frappe_assistant_core.utils.permissions.check_user_permission', return_value=True), \
                 patch('frappe_assistant_core.utils.validation.validate_doctype_access', return_value=True):
                
                method = getattr([ToolName]Tools, scenario["operation"])
                result = method(*scenario["args"])
                
                self.assertFalse(result.get("success"))
                self.assertIn(scenario["expected_error"], result.get("error", "").lower())
    
    def test_performance_with_large_dataset(self):
        """Test performance with large dataset"""
        # Create large mock dataset
        large_dataset = [
            {"name": f"Doc{i}", "field": f"value{i}"}
            for i in range(1000)
        ]
        
        with patch('[module_path].perform_operation_2', return_value=large_dataset), \
             patch('frappe_assistant_core.utils.validation.validate_doctype_access', return_value=True), \
             patch('frappe.has_permission', return_value=True):
            
            result, execution_time = self.measure_execution_time(
                [ToolName]Tools.tool_operation_2, "Test DocType"
            )
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["data"]["count"], 1000)
            self.assertLess(execution_time, 2.0)  # Should complete within 2 seconds

if __name__ == "__main__":
    unittest.main()
```

## Helper Utility Templates

### Response Builder Usage

```python
from frappe_assistant_core.utils.response_builder import build_response

# Success response
return build_response(
    success=True,
    data={"key": "value"},
    message="Operation completed successfully"
)

# Error response
return build_response(
    success=False,
    error="Operation failed: specific reason",
    error_code="OPERATION_FAILED"
)
```

### Permission Check Template

```python
from frappe_assistant_core.utils.permissions import check_user_permission

# Check specific permission
if not check_user_permission("OperationName"):
    return build_response(
        success=False,
        error="Insufficient permissions for this operation"
    )

# Check DocType permission
if not frappe.has_permission(doctype, "read"):
    return build_response(
        success=False,
        error=f"No read permission for {doctype}"
    )
```

### Validation Template

```python
from frappe_assistant_core.utils.validation import validate_doctype_access

# Validate DocType access
if not validate_doctype_access(doctype):
    return build_response(
        success=False,
        error=f"Access denied to DocType: {doctype}"
    )

# Input validation
if not param or not str(param).strip():
    return build_response(
        success=False,
        error="Parameter is required and cannot be empty"
    )
```

### Error Handling Template

```python
from frappe_assistant_core.utils.enhanced_error_handling import handle_tool_error

@handle_tool_error
def tool_method(self, param1, param2):
    """Tool method with error handling decorator"""
    try:
        # Tool logic here
        result = perform_operation()
        return build_response(success=True, data=result)
        
    except frappe.DoesNotExistError:
        return build_response(
            success=False,
            error="Resource not found"
        )
    except frappe.PermissionError:
        return build_response(
            success=False,
            error="Permission denied"
        )
    except Exception as e:
        frappe.log_error(f"Error in tool_method: {str(e)}")
        return build_response(
            success=False,
            error=f"Operation failed: {str(e)}"
        )
```

## MCP Schema Templates

### Basic Parameter Schema
```python
{
    "type": "object",
    "properties": {
        "doctype": {
            "type": "string",
            "description": "Name of the DocType to operate on"
        },
        "name": {
            "type": "string", 
            "description": "Document name/ID"
        },
        "filters": {
            "type": "object",
            "description": "Filter criteria for the operation",
            "optional": True
        }
    },
    "required": ["doctype", "name"]
}
```

### List Operation Schema
```python
{
    "type": "object",
    "properties": {
        "doctype": {
            "type": "string",
            "description": "DocType to list"
        },
        "limit": {
            "type": "number",
            "description": "Maximum number of records to return",
            "optional": True,
            "default": 20
        },
        "offset": {
            "type": "number", 
            "description": "Number of records to skip",
            "optional": True,
            "default": 0
        },
        "order_by": {
            "type": "string",
            "description": "Field to order by",
            "optional": True
        }
    },
    "required": ["doctype"]
}
```

### Search Operation Schema
```python
{
    "type": "object",
    "properties": {
        "search_term": {
            "type": "string",
            "description": "Text to search for"
        },
        "doctype": {
            "type": "string",
            "description": "DocType to search in",
            "optional": True
        },
        "fields": {
            "type": "array",
            "description": "Fields to search in",
            "items": {"type": "string"},
            "optional": True
        }
    },
    "required": ["search_term"]
}
```

## File Naming Conventions

### Tool Files
- Location: `frappe_assistant_core/tools/`
- Naming: `[category]_tools.py` (e.g., `document_tools.py`)
- Class name: `[Category]Tools` (e.g., `DocumentTools`)

### Test Files  
- Location: `frappe_assistant_core/tests/`
- Naming: `test_[category]_tools.py` (e.g., `test_document_tools.py`)
- Unit test class: `Test[Category]Tools` (e.g., `TestDocumentTools`)
- Integration test class: `Test[Category]ToolsIntegration`

### Import Structure
```python
# Tool file imports
import frappe
from typing import Dict, Any, List, Optional
from frappe_assistant_core.utils.permissions import check_user_permission
from frappe_assistant_core.utils.response_builder import build_response
from frappe_assistant_core.utils.validation import validate_doctype_access

# Test file imports
import frappe
import unittest
from unittest.mock import patch, MagicMock
from frappe_assistant_core.tools.[tool_file] import [ToolClass]
from frappe_assistant_core.tests.base_test import BaseAssistantTest
```

## Quick Start Checklist

When creating a new tool:

1. ✅ Create tool file using tool class template
2. ✅ Implement get_tools() method with proper MCP schema
3. ✅ Implement individual tool methods with error handling
4. ✅ Add execute_tool() routing method
5. ✅ Create test file using test template
6. ✅ Implement unit tests for each tool method
7. ✅ Implement integration tests
8. ✅ Add performance tests if applicable
9. ✅ Update tool registry if needed
10. ✅ Add to test_all.py if creating new category

## Documentation Requirements

Each new tool should include:
- Clear docstrings for all methods
- Parameter descriptions in MCP schema
- Usage examples in comments
- Error handling documentation
- Integration points with Frappe framework

Remember to follow Frappe coding standards and maintain consistency with existing tool implementations.