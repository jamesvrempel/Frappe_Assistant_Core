# Frappe Assistant Core Architecture

## Overview

Frappe Assistant Core is built on a modular plugin architecture that separates core functionality from optional features. This design enables clean separation of concerns, extensibility, and maintainability while following Frappe framework standards.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frappe Assistant Core                   │
├─────────────────────────────────────────────────────────────┤
│                    MCP Protocol Layer                       │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │ Initialize    │  │ Tools/List    │  │ Tools/Call    │   │
│  │ Handler       │  │ Handler       │  │ Handler       │   │
│  └───────────────┘  └───────────────┘  └───────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Tool Registry                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                Tool Discovery Engine                    │ │
│  │  ┌─────────────┐              ┌─────────────────────┐   │ │
│  │  │ Core Tools  │              │  Plugin Tools       │   │ │
│  │  │ Discovery   │              │  Discovery          │   │ │
│  │  └─────────────┘              └─────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Core System                              │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │ Document      │  │ Search        │  │ Metadata      │   │
│  │ Tools         │  │ Tools         │  │ Tools         │   │
│  └───────────────┘  └───────────────┘  └───────────────┘   │
│  ┌───────────────┐  ┌───────────────┐                      │
│  │ Report        │  │ Workflow      │                      │
│  │ Tools         │  │ Tools         │                      │
│  └───────────────┘  └───────────────┘                      │
├─────────────────────────────────────────────────────────────┤
│                   Plugin System                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                Plugin Manager                           │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │ │
│  │  │ Discovery   │  │ Validation  │  │ Lifecycle       │ │ │
│  │  │ Engine      │  │ Engine      │  │ Management      │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │ Data Science  │  │ WebSocket     │  │ Batch         │   │
│  │ Plugin        │  │ Plugin        │  │ Processing    │   │
│  └───────────────┘  └───────────────┘  └───────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Frappe Framework                          │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │ Database      │  │ Permissions   │  │ Caching       │   │
│  │ ORM           │  │ System        │  │ System        │   │
│  └───────────────┘  └───────────────┘  └───────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. MCP Protocol Layer

The Model Context Protocol (MCP) layer handles communication between AI assistants and the Frappe system.

**Key Components:**
- **Protocol Handlers**: Process MCP requests and responses
- **Request Validation**: Ensure proper protocol compliance
- **Response Formatting**: Convert internal responses to MCP format
- **Error Handling**: Standardized error responses

**Implementation:**
- Located in `api/` directory
- Uses Frappe's `@frappe.whitelist()` decorators
- Implements JSON-RPC 2.0 specification
- Supports all MCP protocol methods

### 2. Tool Registry

The tool registry manages discovery, registration, and execution of all available tools through a plugin-based architecture.

**Architecture:**
```python
ToolRegistry
├── Plugin Discovery
│   ├── Scans plugins/*/plugin.py
│   ├── Discovers enabled plugins
│   └── Validates plugin requirements
├── Tool Loading
│   ├── Loads tools from enabled plugins
│   ├── Instantiates tool classes
│   └── Registers with plugin metadata
└── Permission Filtering
    ├── Checks user permissions
    ├── Filters available tools
    └── Returns accessible tools only
```

**Features:**
- **Plugin-Based Discovery**: Tools discovered from enabled plugins
- **Runtime Management**: Enable/disable plugins through web interface
- **Permission Integration**: Only accessible tools are exposed
- **Metadata Management**: Tool information cached for performance

### 3. Base Tool Architecture

All tools inherit from a common base class that provides standardized functionality.

```python
BaseTool (Abstract)
├── Metadata Management
│   ├── name: str
│   ├── description: str
│   ├── input_schema: Dict
│   └── requires_permission: Optional[str]
├── Validation System
│   ├── validate_arguments()
│   ├── check_permission()
│   └── _validate_type()
├── Execution Framework
│   ├── execute() [Abstract]
│   ├── _safe_execute()
│   └── Error handling
└── MCP Integration
    ├── to_mcp_format()
    ├── get_metadata()
    └── Protocol compliance
```

**Benefits:**
- **Consistent Interface**: All tools follow same patterns
- **Built-in Validation**: Automatic argument and permission checking
- **Error Handling**: Standardized error capture and reporting
- **MCP Compliance**: Automatic protocol formatting

### 4. Plugin System

The plugin system enables modular functionality that can be enabled/disabled as needed.

**Plugin Architecture:**
```python
BasePlugin (Abstract)
├── Plugin Information
│   ├── get_info() [Abstract]
│   ├── get_capabilities()
│   └── Plugin metadata
├── Tool Management
│   ├── get_tools() [Abstract]
│   ├── Tool registration
│   └── Tool lifecycle
├── Environment Validation
│   ├── validate_environment() [Abstract]
│   ├── Dependency checking
│   └── Permission validation
└── Lifecycle Hooks
    ├── on_enable()
    ├── on_disable()
    ├── on_server_start()
    └── on_server_stop()
```

**Plugin Manager:**
- **Discovery**: Automatically finds plugin directories
- **Validation**: Checks dependencies and environment
- **Loading**: Manages plugin lifecycle and tool registration
- **Configuration**: Integration with Frappe settings

### 5. Core Plugin Tools

Core plugin provides essential functionality that's always available.

**Tool Categories:**

1. **Document Tools** (`plugins/core/tools/document_*.py`)
   - Create, read, update, delete operations
   - List and bulk operations
   - Transaction support

2. **Search Tools** (`plugins/core/tools/search_*.py`)
   - Global search across all DocTypes
   - DocType-specific search
   - Link field search and filtering

3. **Metadata Tools** (`plugins/core/tools/metadata_*.py`)
   - DocType structure exploration
   - Field information and validation
   - System metadata access

4. **Report Tools** (`plugins/core/tools/report_*.py`)
   - Report execution and management
   - Parameter handling
   - Result formatting

5. **Workflow Tools** (`plugins/core/tools/workflow_*.py`)
   - Workflow action execution
   - Status checking and querying
   - Approval queue management

## Data Flow

### 1. Request Processing

```
Client Request
↓
MCP Protocol Handler
↓
Request Validation
↓
Tool Registry Lookup
↓
Permission Check
↓
Tool Execution
↓
Response Formatting
↓
Client Response
```

### 2. Tool Discovery

```
Server Start
↓
Tool Registry Initialization
↓
Plugin Manager Query
↓
Plugin Discovery (plugins/*/plugin.py)
↓
Plugin Tool Loading
↓
Registry Population
↓
Permission Filtering
```

### 3. Plugin Lifecycle

```
Plugin Discovery
↓
Environment Validation
↓
Dependency Check
↓
Configuration Load
↓
Tool Registration
↓
Lifecycle Hook Execution
```

## Security Architecture

### 1. Permission System

- **Frappe Integration**: Uses native Frappe permission system
- **Tool-Level Permissions**: Each tool can specify required permissions
- **Dynamic Checking**: Permissions checked at execution time
- **User Context**: All operations respect current user context

### 2. Input Validation

- **JSON Schema**: All tool inputs validated against schemas
- **Type Checking**: Automatic type validation and conversion
- **Sanitization**: Input sanitization for security
- **Error Handling**: Secure error messages without data leakage

### 3. SQL Security

- **Query Restrictions**: Only SELECT statements allowed in query tools
- **Parameterization**: All queries use parameterized statements
- **Permission Checks**: Database access requires appropriate permissions
- **Timeout Protection**: Query timeouts prevent resource exhaustion

## Performance Considerations

### 1. Caching Strategy

- **Tool Registry**: Cached between requests
- **Permission Results**: Cached with TTL
- **Plugin State**: Cached plugin configurations
- **Metadata**: DocType metadata cached

### 2. Lazy Loading

- **Plugin Loading**: Plugins loaded only when enabled
- **Tool Instantiation**: Tools created on first use
- **Dependency Import**: Heavy libraries imported on demand

### 3. Resource Management

- **Connection Pooling**: Database connections managed by Frappe
- **Memory Management**: Proper cleanup in tool execution
- **Error Isolation**: Plugin errors don't affect core system

## Extensibility Patterns

### 1. Adding Core Tools

```python
# 1. Create tool class inheriting from BaseTool
class MyTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "my_tool"
        # ... configuration

    def execute(self, arguments):
        # ... implementation

# 2. Place in appropriate plugins/core/tools/ file
# 3. Tool automatically discovered on server start
```

### 2. Creating Plugins

```python
# 1. Create plugin directory structure
plugins/my_plugin/
├── __init__.py
├── plugin.py        # Plugin definition
├── requirements.txt # Dependencies
└── tools/          # Plugin tools
    └── my_tool.py

# 2. Implement BasePlugin
class MyPlugin(BasePlugin):
    def get_info(self): # ... implementation
    def get_tools(self): # ... implementation
    def validate_environment(self): # ... implementation

# 3. Plugin automatically discovered
```

### 3. Customizing Behavior

- **Hook System**: Plugins can register hooks for events
- **Configuration**: Settings stored in DocTypes
- **Overrides**: Core behavior can be extended via plugins
- **Custom Validators**: Add custom validation logic

## Testing Architecture

### 1. Test Structure

```
tests/
├── test_plugin_system.py    # Plugin system tests
├── test_core_tools.py       # Core tool tests
├── test_api_endpoints.py    # API endpoint tests
└── plugin-specific tests    # Individual plugin tests
```

### 2. Test Patterns

- **Unit Tests**: Individual tool and component testing
- **Integration Tests**: End-to-end MCP protocol testing
- **Plugin Tests**: Plugin loading and tool execution
- **Permission Tests**: Security and access control testing

## Deployment Considerations

### 1. Installation

- **App Installation**: Standard Frappe app installation
- **Dependency Management**: Optional dependencies for plugins
- **Configuration**: DocType-based configuration
- **Migration**: Automatic schema updates

### 2. Scaling

- **Horizontal Scaling**: Stateless design supports multiple instances
- **Database Scaling**: Leverages Frappe's database layer
- **Caching**: Redis integration through Frappe
- **Load Balancing**: No special requirements

### 3. Monitoring

- **Logging**: Comprehensive logging through Frappe
- **Error Tracking**: Integration with Frappe error system
- **Performance**: Tool execution timing and metrics
- **Health Checks**: Plugin validation and status

## Future Architecture Considerations

### 1. Enhanced Plugin System

- **Plugin Dependencies**: Inter-plugin dependency management
- **Plugin API Versioning**: Backward compatibility management
- **Plugin Marketplace**: Central plugin repository
- **Hot Reloading**: Runtime plugin updates

### 2. Advanced Features

- **Streaming Responses**: Large result set streaming
- **Async Operations**: Long-running operation support
- **Batch Processing**: Enhanced bulk operation support
- **Real-time Features**: WebSocket-based real-time updates

### 3. Integration Enhancements

- **External APIs**: Third-party service integration
- **Webhook Support**: Event-driven integrations
- **Advanced Security**: OAuth, JWT, and advanced auth
- **Multi-tenancy**: Enhanced multi-site support

This architecture provides a solid foundation for extensible, maintainable, and scalable AI assistant integration with Frappe systems.