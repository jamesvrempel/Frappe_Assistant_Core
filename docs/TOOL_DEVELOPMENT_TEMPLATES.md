# Tool Development Guide for Frappe Assistant Core

## Overview

This document provides comprehensive templates and examples for creating tools in the Frappe Assistant Core architecture. The system supports both **internal plugins** (within frappe_assistant_core) and **external app tools** (from any Frappe app) using a flexible hooks-based discovery system.

## Architecture Overview

### Two Ways to Create Tools

1. **External App Tools** (Recommended for custom apps)

   - Tools in any Frappe app using hooks
   - Auto-discovered via `assistant_tools` hooks
   - No need to modify frappe_assistant_core

2. **Internal Plugin Tools** (For core functionality)
   - Tools within frappe_assistant_core plugin system
   - Backward compatibility with existing structure

## Method 1: External App Tools (Recommended)

### Step 1: Create Tool in Your App

```python
# your_app/assistant_tools/my_custom_tool.py
"""
My Custom Tool - Example external app tool
Demonstrates how to create tools in external Frappe apps
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class MyCustomTool(BaseTool):
    """
    Custom tool from external app demonstrating the architecture.

    Provides capabilities for:
    - Custom business logic
    - Integration with app-specific DocTypes
    - App-specific configurations
    """

    def __init__(self):
        super().__init__()
        self.name = "my_custom_tool"
        self.description = self._get_description()
        self.category = "Custom Business"
        self.source_app = "your_app_name"  # Set your app name
        self.dependencies = ["pandas"]  # Optional dependencies
        self.requires_permission = None  # Or specific DocType/permission

        # Tool-specific default configuration
        self.default_config = {
            "max_records": 1000,
            "timeout": 30,
            "enable_caching": True
        }

        self.inputSchema = {
            "type": "object",
            "properties": {
                "operation_type": {
                    "type": "string",
                    "enum": ["create", "update", "analyze"],
                    "description": "Type of operation to perform"
                },
                "data": {
                    "type": "object",
                    "description": "Operation data"
                },
                "options": {
                    "type": "object",
                    "properties": {
                        "validate": {"type": "boolean", "default": True},
                        "batch_size": {"type": "integer", "default": 100}
                    },
                    "description": "Operation options"
                }
            },
            "required": ["operation_type"]
        }

    def _get_description(self) -> str:
        """Get tool description with rich formatting"""
        return """Perform custom business operations with advanced features.

🚀 **OPERATIONS:**
• Create - Create new business records
• Update - Modify existing records
• Analyze - Generate business insights

⚙️ **FEATURES:**
• Batch Processing - Handle multiple records efficiently
• Validation - Built-in business rules validation
• Caching - Performance optimization
• Audit Trail - Complete operation logging

🔧 **CONFIGURATION:**
• Configurable batch sizes and timeouts
• App-level and site-level overrides
• Performance monitoring and alerts"""

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the custom tool operation"""
        operation_type = arguments.get("operation_type")
        data = arguments.get("data", {})
        options = arguments.get("options", {})

        # Get effective configuration (site > app > tool defaults)
        config = self.get_config()

        try:
            if operation_type == "create":
                return self._handle_create(data, options, config)
            elif operation_type == "update":
                return self._handle_update(data, options, config)
            elif operation_type == "analyze":
                return self._handle_analyze(data, options, config)
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation type: {operation_type}"
                }

        except Exception as e:
            frappe.log_error(
                title=_("Custom Tool Error"),
                message=f"Error in {self.name}: {str(e)}"
            )

            return {
                "success": False,
                "error": str(e)
            }

    def _handle_create(self, data: Dict, options: Dict, config: Dict) -> Dict[str, Any]:
        """Handle create operation"""
        batch_size = options.get("batch_size", config.get("max_records", 100))

        # Your custom create logic here
        result = {
            "operation": "create",
            "processed": len(data),
            "batch_size": batch_size,
            "config_used": config
        }

        return {
            "success": True,
            "result": result
        }

    def _handle_update(self, data: Dict, options: Dict, config: Dict) -> Dict[str, Any]:
        """Handle update operation"""
        # Your custom update logic here
        return {
            "success": True,
            "result": {"operation": "update", "data": data}
        }

    def _handle_analyze(self, data: Dict, options: Dict, config: Dict) -> Dict[str, Any]:
        """Handle analyze operation"""
        # Your custom analysis logic here
        return {
            "success": True,
            "result": {"operation": "analyze", "insights": "Analysis complete"}
        }


# Export the tool class for discovery
__all__ = ["MyCustomTool"]
```

### Step 2: Register Tool in App Hooks

```python
# your_app/hooks.py

# ... existing hooks ...

# Register tools with Frappe Assistant Core
assistant_tools = [
    "your_app.assistant_tools.my_custom_tool.MyCustomTool",
    "your_app.assistant_tools.another_tool.AnotherTool",
    # Add more tools as needed
]

# Optional: Tool-specific configuration overrides
assistant_tool_configs = {
    "my_custom_tool": {
        "max_records": 5000,  # Override default
        "timeout": 60,
        "enable_caching": False
    },
    "another_tool": {
        "batch_size": 200
    }
}
```

### Step 3: Tool Configuration Hierarchy

Tools support a three-level configuration hierarchy:

```python
# 1. Tool-level defaults (in tool code)
self.default_config = {
    "max_records": 1000,
    "timeout": 30
}

# 2. App-level overrides (in hooks.py)
assistant_tool_configs = {
    "my_custom_tool": {
        "max_records": 5000  # Override default
    }
}

# 3. Site-level overrides (in site_config.json)
{
    "assistant_tools": {
        "my_custom_tool": {
            "timeout": 120  # Site-specific override
        }
    }
}
```

### Step 4: Testing External Tools

```python
# your_app/tests/test_assistant_tools.py
"""
Test suite for your app's assistant tools
"""

import frappe
import unittest
from frappe_assistant_core.core.tool_registry import get_tool_registry


class TestMyCustomTool(unittest.TestCase):
    """Test custom tool functionality"""

    def setUp(self):
        """Set up test environment"""
        self.registry = get_tool_registry()

    def test_tool_discovery(self):
        """Test tool is discovered correctly"""
        tools = self.registry.get_all_tools()
        self.assertIn("my_custom_tool", tools)

        tool = tools["my_custom_tool"]
        self.assertEqual(tool.source_app, "your_app_name")
        self.assertEqual(tool.category, "Custom Business")

    def test_tool_execution(self):
        """Test tool execution"""
        tool = self.registry.get_tool("my_custom_tool")

        result = tool._safe_execute({
            "operation_type": "create",
            "data": {"test": "data"}
        })

        self.assertTrue(result.get("success"))
        self.assertIn("result", result)

    def test_configuration_hierarchy(self):
        """Test configuration hierarchy"""
        tool = self.registry.get_tool("my_custom_tool")
        config = tool.get_config()

        # Should include defaults and any overrides
        self.assertIn("max_records", config)
        self.assertIn("timeout", config)


if __name__ == "__main__":
    unittest.main()
```

## Method 2: Internal Plugin Tools

### Plugin Structure

```
frappe_assistant_core/plugins/my_plugin/
├── __init__.py                 # Plugin package
├── plugin.py                   # Plugin definition
└── tools/                      # Individual tool files
    ├── __init__.py
    ├── tool_one.py             # Tool implementation
    └── tool_two.py             # Tool implementation
```

### Plugin Definition

```python
# frappe_assistant_core/plugins/my_plugin/plugin.py
"""
My Plugin - Internal plugin example
"""

import frappe
from frappe import _
from typing import Dict, Any, List, Tuple
from frappe_assistant_core.plugins.base_plugin import BasePlugin


class MyPlugin(BasePlugin):
    """
    Plugin for specialized functionality within frappe_assistant_core
    """

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            "name": "my_plugin",
            "display_name": "My Plugin",
            "description": "Specialized functionality plugin",
            "version": "1.0.0",
            "author": "Your Name",
            "category": "Business Tools",
            "dependencies": ["pandas", "numpy"],
            "requires_restart": False
        }

    def get_tools(self) -> List[str]:
        """Return list of tool names provided by this plugin"""
        return [
            "tool_one",
            "tool_two"
        ]

    def validate_environment(self) -> Tuple[bool, str]:
        """Validate plugin can run in current environment"""
        try:
            # Check dependencies
            import pandas
            import numpy

            return True, None

        except ImportError as e:
            return False, f"Missing dependency: {str(e)}"

    def get_capabilities(self) -> Dict[str, Any]:
        """Get plugin capabilities"""
        return {
            "data_processing": {
                "batch_operations": True,
                "streaming": False,
                "formats": ["json", "csv"]
            },
            "integrations": {
                "external_apis": True,
                "webhooks": False
            }
        }

    def on_enable(self):
        """Called when plugin is enabled"""
        frappe.logger("my_plugin").info("My Plugin enabled")

    def on_disable(self):
        """Called when plugin is disabled"""
        frappe.logger("my_plugin").info("My Plugin disabled")
```

### Individual Tool File

```python
# frappe_assistant_core/plugins/my_plugin/tools/tool_one.py
"""
Tool One - Example internal plugin tool
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class ToolOne(BaseTool):
    """
    Example tool within an internal plugin
    """

    def __init__(self):
        super().__init__()
        self.name = "tool_one"
        self.description = "Example tool within internal plugin"
        self.category = "My Plugin"
        self.source_app = "frappe_assistant_core"

        self.inputSchema = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["process", "validate", "export"],
                    "description": "Action to perform"
                },
                "data": {
                    "type": "object",
                    "description": "Input data"
                }
            },
            "required": ["action"]
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool"""
        action = arguments.get("action")
        data = arguments.get("data", {})

        if action == "process":
            return {"success": True, "result": f"Processed {len(data)} items"}
        elif action == "validate":
            return {"success": True, "result": "Validation complete"}
        elif action == "export":
            return {"success": True, "result": "Export complete"}
        else:
            return {"success": False, "error": f"Unknown action: {action}"}


# Export for plugin discovery
tool_one = ToolOne
```

## Advanced Features

### 1. Tool Configuration

```python
class AdvancedTool(BaseTool):
    def __init__(self):
        super().__init__()
        # ... other initialization ...

        self.default_config = {
            "api_endpoint": "https://api.example.com",
            "timeout": 30,
            "retry_attempts": 3,
            "enable_cache": True,
            "batch_size": 100
        }

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Get effective configuration
        config = self.get_config()

        # Use configuration
        api_endpoint = config.get("api_endpoint")
        timeout = config.get("timeout", 30)

        # Tool logic using configuration...
```

### 2. Dependency Management

```python
class DependentTool(BaseTool):
    def __init__(self):
        super().__init__()
        # ... other initialization ...

        self.dependencies = [
            "pandas",
            "requests",
            "your_custom_module"
        ]

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Dependencies are automatically validated before execution
        import pandas as pd
        import requests

        # Tool logic...
```

### 3. Audit Logging

```python
class AuditedTool(BaseTool):
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Automatic audit logging is handled by BaseTool._safe_execute()
        # This includes:
        # - Tool execution timing
        # - Success/failure status
        # - Sanitized arguments (sensitive data removed)
        # - Source app tracking
        # - User identification

        # Your tool logic here
        result = self.perform_operation(arguments)

        return {
            "success": True,
            "result": result
        }
```

### 4. Performance Monitoring

All tools automatically include performance monitoring:

```python
# Execution timing is automatic
# Configuration caching
# Dependency validation caching
```

## Migration from Old System

### For Existing Tools

If you have existing tools in the old system:

1. **Keep Current Structure**: Tools in existing plugins continue to work
2. **No Changes Required**: Existing tools work without modification

### For New Development

1. **Use External App Method**: Create tools in your custom Frappe apps
2. **Use BaseTool**: Inherit from the BaseTool
3. **Leverage Configuration**: Use the configuration hierarchy
4. **Add Dependencies**: Declare dependencies for validation

## Testing Framework

### Unit Testing

```python
# Test external app tools
from frappe_assistant_core.core.tool_registry import get_tool_registry

class TestExternalTool(unittest.TestCase):
    def test_tool_discovery(self):
        registry = get_tool_registry()
        tools = registry.get_tools_by_app("your_app_name")
        self.assertIn("my_custom_tool", tools)

    def test_configuration(self):
        tool = registry.get_tool("my_custom_tool")
        config = tool.get_config()
        self.assertIn("max_records", config)
```

## Best Practices

### 1. Tool Naming

- Use descriptive, action-oriented names
- Follow snake_case convention
- Avoid conflicts with existing tools

### 2. Error Handling

- Use the BaseTool error handling
- Provide meaningful error messages
- Log errors appropriately

### 3. Configuration

- Provide sensible defaults
- Document configuration options
- Use the configuration hierarchy

### 4. Dependencies

- Declare all dependencies
- Handle missing dependencies gracefully
- Consider optional dependencies

### 5. Security

- Implement proper permission checking
- Sanitize sensitive data in logs
- Validate all inputs

## Documentation Template

```python
class WellDocumentedTool(BaseTool):
    """
    Brief description of what the tool does.

    Longer description explaining:
    - Main use cases
    - Key features
    - Integration points

    Configuration Options:
        api_key: API key for external service
        timeout: Request timeout in seconds
        batch_size: Number of items to process at once

    Dependencies:
        - requests: For API calls
        - pandas: For data processing

    Examples:
        Basic usage:
        {
            "action": "process",
            "data": {"items": [1, 2, 3]}
        }

        With options:
        {
            "action": "process",
            "data": {"items": [1, 2, 3]},
            "options": {"batch_size": 50}
        }
    """
```

## Quick Start Checklist

### For External App Tools:

1. ✅ Create tool file in `your_app/assistant_tools/`
2. ✅ Inherit from BaseTool
3. ✅ Add to `assistant_tools` in hooks.py
4. ✅ Add configuration if needed
5. ✅ Test tool discovery and execution
6. ✅ Run `bench migrate` to refresh cache

### For Internal Plugin Tools:

1. ✅ Create plugin directory structure
2. ✅ Implement plugin.py with BasePlugin
3. ✅ Create individual tool files
4. ✅ Add tool names to plugin.get_tools()
5. ✅ Test plugin and tool discovery

### For All Tools:

1. ✅ Add comprehensive documentation
2. ✅ Implement proper error handling
3. ✅ Add unit and integration tests
4. ✅ Declare dependencies
5. ✅ Follow security best practices

## Support and Resources

- **BaseTool**: `/core/base_tool.py`
- **Tool Registry**: `/core/tool_registry.py`
- **Plugin Manager**: `/utils/plugin_manager.py`

The architecture provides powerful capabilities while maintaining backward compatibility. Choose the external app method for maximum flexibility and the internal plugin method for core functionality integration.
