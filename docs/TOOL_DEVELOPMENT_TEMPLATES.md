# Plugin & Tool Development Guide for Frappe Assistant Core

## Overview

This document provides templates and examples for creating new plugins and tools in the Frappe Assistant Core plugin-based system. These templates ensure consistency and proper integration with the auto-discovery system.

## Plugin Development

### Plugin Structure

```
your_plugin/
├── plugin.py                   # Plugin definition (required)
├── __init__.py                 # Python package marker
└── tools/                      # Tools directory (optional)
    ├── __init__.py
    ├── tool_one.py             # Individual tool implementations
    └── tool_two.py
```

### Plugin Definition Template

```python
"""
Plugin: [Plugin Name]
Description: [Brief description of plugin functionality]
"""

import frappe
from typing import Dict, Any, List

class [PluginName]:
    """
    Plugin for [specific functionality area]
    """
    
    def __init__(self):
        self.name = "[plugin_name]"
        self.display_name = "[Plugin Display Name]"
        self.description = "[Detailed description of plugin capabilities]"
        self.version = "1.0.0"
        self.dependencies = []  # List of required dependencies
        self.tools = []  # Will be populated by auto-discovery
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate plugin requirements and dependencies
        
        Returns:
            Dict with 'can_enable' boolean and 'validation_error' string
        """
        try:
            # Check dependencies
            for dep in self.dependencies:
                try:
                    __import__(dep)
                except ImportError:
                    return {
                        'can_enable': False,
                        'validation_error': f'Missing dependency: {dep}'
                    }
            
            # Additional validation logic here
            
            return {'can_enable': True, 'validation_error': ''}
            
        except Exception as e:
            return {
                'can_enable': False, 
                'validation_error': f'Validation error: {str(e)}'
            }
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Return plugin metadata"""
        return {
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'version': self.version,
            'dependencies': self.dependencies,
            'tools': self.tools
        }

# Plugin instance for auto-discovery
plugin = [PluginName]()
```

## Tool Development

### Tool Class Template

```python
"""
[Tool Name] for [Plugin Name] Plugin
[Brief description of what this tool does]
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool

class [ToolName](BaseTool):
    """
    Tool for [specific functionality]
    
    Provides capabilities for:
    - [Feature 1]
    - [Feature 2]
    - [Feature 3]
    """
    
    def __init__(self):
        super().__init__()
        self.name = "[tool_name]"
        self.description = "[Tool description for UI/documentation]"
        self.requires_permission = None  # Or specific DocType/role
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description of parameter 1"
                },
                "param2": {
                    "type": "object",
                    "description": "Optional parameter object",
                    "properties": {
                        "sub_param": {
                            "type": "string",
                            "description": "Sub-parameter description"
                        }
                    }
                }
            },
            "required": ["param1"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with given arguments
        
        Args:
            arguments: Tool arguments matching input_schema
            
        Returns:
            Tool execution result with success/error status
        """
        param1 = arguments.get("param1")
        param2 = arguments.get("param2", {})
        
        # Input validation
        if not param1:
            return {
                "success": False,
                "error": "param1 is required"
            }
        
        try:
            # Main tool logic here
            result = self._perform_operation(param1, param2)
            
            return {
                "success": True,
                "result": result,
                "param1": param1
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("[Tool Name] Error"),
                message=f"Error in [tool_name]: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _perform_operation(self, param1: str, param2: Dict) -> Dict[str, Any]:
        """
        Internal method to perform the main operation
        
        Args:
            param1: Primary parameter
            param2: Secondary parameters
            
        Returns:
            Operation result
        """
        # Implementation details
        return {
            "message": f"Operation completed for {param1}",
            "details": param2
        }

# Tool instance for auto-discovery (this line is required)
[tool_name] = [ToolName]()
```

## Plugin Registration

### Auto-Discovery
Plugins are automatically discovered by the plugin manager when:

1. **Plugin Directory**: Located in `frappe_assistant_core/plugins/`
2. **Plugin File**: Contains `plugin.py` with plugin class
3. **Plugin Instance**: Module-level instance named `plugin`

### Manual Registration
If needed, plugins can be manually registered:

```python
# In frappe_assistant_core/utils/plugin_manager.py
from frappe_assistant_core.plugins.your_plugin.plugin import plugin

plugin_manager.register_plugin(plugin)
```

## Testing Templates

### Plugin Test Template

```python
"""
Test suite for [Plugin Name] plugin
"""

import frappe
import unittest
from frappe_assistant_core.core.tool_registry import get_tool_registry
from frappe_assistant_core.tests.base_test import BaseAssistantTest

class Test[PluginName](BaseAssistantTest):
    """Test [plugin name] plugin functionality"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        self.registry = get_tool_registry()
    
    def test_plugin_discovery(self):
        """Test plugin is discovered correctly"""
        available_tools = self.registry.get_available_tools()
        plugin_tools = [t for t in available_tools if t['name'].startswith('[tool_prefix]')]
        
        self.assertGreater(len(plugin_tools), 0)
        self.assertIn('[tool_name]', [t['name'] for t in plugin_tools])
    
    def test_[tool_name]_basic(self):
        """Test basic [tool_name] functionality"""
        result = self.execute_tool_and_get_result(
            self.registry, "[tool_name]", {
                "param1": "test_value"
            }
        )
        
        self.assertTrue(result.get("success"))
        self.assertIn("result", result)
    
    def test_[tool_name]_validation(self):
        """Test [tool_name] input validation"""
        result = self.execute_tool_expect_failure(
            self.registry, "[tool_name]", {}
        )
        
        self.assertFalse(result.get("success"))
        self.assertIn("param1 is required", result.get("error", ""))

if __name__ == "__main__":
    unittest.main()
```

## Development Workflow

### 1. Create Plugin Structure
```bash
mkdir frappe_assistant_core/plugins/my_plugin
touch frappe_assistant_core/plugins/my_plugin/__init__.py
touch frappe_assistant_core/plugins/my_plugin/plugin.py
mkdir frappe_assistant_core/plugins/my_plugin/tools
touch frappe_assistant_core/plugins/my_plugin/tools/__init__.py
```

### 2. Implement Plugin Class
- Use plugin template above
- Define plugin metadata
- Implement validation logic

### 3. Create Tools
- Use tool template above  
- Inherit from `BaseTool`
- Implement `execute` method
- Add module-level instance

### 4. Test Integration
- Use test templates
- Test plugin discovery
- Test tool functionality
- Test error handling

### 5. Enable Plugin
- Through web interface: Assistant Core Settings → Refresh Plugins → Enable
- Or programmatically via plugin manager

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