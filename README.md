# Frappe Assistant Core

🤖 **Professional AI Assistant for ERPNext** - Transform your ERPNext experience with intelligent AI assistance through the Model Context Protocol (MCP).

Built for businesses who want to leverage AI to streamline their ERP operations, automate workflows, and gain intelligent insights from their data.

## 🚀 Version 1.0.0 - Major Architecture Overhaul (June 2025)

**🎉 What's New:**
- **🏗️ Modular Architecture**: Complete refactoring with clean, maintainable, extensible codebase
- **📝 Professional Logging**: Replaced 905+ print statements with structured logging system
- **🔧 Modern Packaging**: pyproject.toml with proper dependency management
- **🐛 Critical Fixes**: Resolved import errors and missing modules
- **🧹 Code Cleanup**: Removed 26 temporary files, organized module structure
- **📊 Performance**: 87% reduction in main API file size (1580 → 200 lines)

---

## 🌟 Why Choose Frappe Assistant Core?

- **🔌 Plug & Play AI Integration**: Seamlessly connect Claude and other AI assistants to your ERPNext data
- **🛡️ Enterprise Security**: Built-in permissions, audit logging, and secure authentication
- **📊 Intelligent Analytics**: AI-powered insights and visualization capabilities
- **🚀 Production Ready**: Rate limiting, comprehensive monitoring, and robust error handling
- **🏗️ Modern Architecture**: Modular, maintainable, and extensible codebase
- **📝 Professional Logging**: Structured logging system for debugging and monitoring
- **🆓 Completely Open Source**: MIT licensed - free for all uses, commercial and personal
- **🤝 Community Driven**: Built by the community, for the community

---

## 🎯 Features Overview

### 🚀 Complete Feature Set (MIT Licensed)
- **🔄 Modern MCP Protocol**: JSON-RPC 2.0 with modular handler architecture
- **📄 Document Operations**: Create, read, update, delete, and search Frappe documents with full permission integration
- **📈 Advanced Reporting**: Execute Frappe reports with enhanced debugging and error handling
- **📊 Data Visualization**: Create charts and graphs with inline display support
- **🔍 Advanced Analytics**: Statistical analysis and business intelligence tools with hybrid streaming
- **🔎 Global Search**: Search across all accessible documents and data
- **🗂️ Metadata Access**: Query DocType schemas, permissions, and workflow information
- **📋 Audit Logging**: Comprehensive operation tracking and monitoring
- **🐍 Python Code Execution**: Execute custom Python code with full Frappe context and 30+ libraries
- **⚙️ Admin Interface**: Web-based management interface for server configuration
- **🔧 Tool Registry**: Auto-discovery tool system with zero configuration
- **🎨 Prompts Support**: Built-in prompts for artifact streaming workflows

### 🏗️ Modern Architecture Features (New in v1.0.0)
- **📦 Modular Handlers**: Separated API concerns into focused modules
- **🔧 Centralized Constants**: All configuration and strings in dedicated module
- **📝 Professional Logging**: Structured logging with proper levels and formatting
- **📋 Modern Packaging**: pyproject.toml with development and analysis dependency groups
- **🐛 Error Handling**: Robust error management with centralized error codes
- **🔍 Tool Execution Engine**: Dedicated tool validation and execution system

---

## 📦 Installation

### Prerequisites
- Frappe Framework 14+
- Python 3.8+
- MariaDB/MySQL

### Quick Installation
```bash
# Navigate to your Frappe bench
cd frappe-bench

# Get the app
bench get-app https://github.com/paulclinton/frappe-assistant-core

# Install on site
bench --site [site-name] install-app frappe_assistant_core

# Run database migrations
bench --site [site-name] migrate
```

### Modern Package Installation (New in v1.0.0)
```bash
# Development installation with all dependencies
pip install -e .[dev,analysis]

# Production installation
pip install .

# Analysis dependencies only
pip install .[analysis]
```

### Configuration
```bash
# Enable through admin interface
https://your-site.com/desk#/assistant-admin

# Or via CLI
bench --site [site-name] set-config assistant_enabled 1
```

---

## 🛠️ Architecture Overview

### Plugin-Based Architecture (v1.0.0)
```
frappe_assistant_core/
├── core/
│   ├── tool_registry.py         # Auto-discovery tool registry
│   └── base_tool.py             # Base tool class
├── plugins/                     # Plugin system
│   ├── core/                    # Core tools plugin
│   │   ├── plugin.py            # Plugin definition
│   │   └── tools/               # Core tool implementations
│   │       ├── document_*.py    # Document operations
│   │       ├── search_*.py      # Search tools
│   │       ├── metadata_*.py    # Metadata tools
│   │       ├── report_*.py      # Report tools
│   │       └── workflow_*.py    # Workflow tools
│   ├── data_science/            # Data science plugin
│   │   ├── plugin.py            # Plugin definition
│   │   └── tools/               # Analysis tool implementations
│   │       ├── execute_python_code.py
│   │       ├── analyze_frappe_data.py
│   │       ├── query_and_analyze.py
│   │       └── create_visualization.py
│   ├── websocket/               # WebSocket plugin
│   └── batch_processing/        # Batch processing plugin
├── utils/
│   ├── plugin_manager.py        # Plugin discovery & loading
│   └── logger.py                # Professional logging
├── assistant_core/
│   └── doctype/                 # Frappe DocTypes
│       ├── assistant_core_settings/
│       ├── assistant_plugin_repository/
│       └── assistant_tool_registry/
└── pyproject.toml               # Modern packaging
```

### Plugin Architecture Benefits
- **🔌 Modular Plugins**: Tools organized in discoverable plugins
- **🚀 Auto-Discovery**: Automatic tool registration from enabled plugins
- **⚙️ Plugin Management**: Web interface for enabling/disabling plugins
- **🔧 Extensible**: Easy to add new plugins and tools
- **🎯 Focused**: Each plugin handles specific functionality

---

## 🔧 Tools Available (Plugin-Based)

### 📦 Core Plugin
**Document Operations**
- `document_create` - Create new documents
- `document_get` - Fetch document data  
- `document_update` - Update existing documents
- `document_delete` - Delete documents
- `document_list` - List documents with filters

**Search & Discovery**
- `search_global` - Search across all accessible documents
- `search_doctype` - Search within specific DocTypes
- `search_link` - Search for link field values

**Metadata & Schema**
- `metadata_doctype` - Get DocType information
- `metadata_list_doctypes` - List available DocTypes
- `metadata_doctype_fields` - Get DocType field definitions
- `metadata_permissions` - Check DocType permissions
- `metadata_workflow` - Get workflow information

**Reports & Analysis**
- `report_execute` - Execute Frappe reports
- `report_list` - List available reports
- `report_details` - Get report configuration

**Workflow Operations**
- `workflow_action` - Execute workflow actions
- `workflow_list` - List available workflows
- `workflow_status` - Get workflow status

### 🧪 Data Science Plugin
**Python Execution & Analysis**
- `execute_python_code` - Secure Python execution with data science libraries
- `analyze_frappe_data` - Statistical analysis of Frappe data
- `query_and_analyze` - SQL query execution with analysis
- `create_visualization` - Chart and graph generation

### 🌐 WebSocket Plugin
**Real-time Communication**
- WebSocket server integration for real-time features

### ⚡ Batch Processing Plugin  
**Bulk Operations**
- Background task processing and bulk operations

---

## 🚀 Getting Started

### 1. Claude Desktop Integration
```json
{
  "mcpServers": {
    "frappe-assistant": {
      "command": "python",
      "args": ["/path/to/frappe_assistant_stdio_bridge.py"],
      "env": {
        "FRAPPE_SITE": "your-site.localhost",
        "FRAPPE_API_KEY": "your-api-key",
        "FRAPPE_API_SECRET": "your-api-secret"
      }
    }
  }
}
```

### 2. Basic Usage Examples

#### Document Operations
```python
# Create a customer
result = document_create({
    "doctype": "Customer",
    "customer_name": "Acme Corp",
    "customer_group": "All Customer Groups"
})

# Read customer data
customer = document_read({
    "doctype": "Customer", 
    "name": "CUST-2024-001"
})
```

#### Data Analysis
```python
# Analyze sales data
code = """
import pandas as pd
sales_data = frappe.get_all("Sales Invoice", 
    fields=["grand_total", "posting_date", "customer"])
df = pd.DataFrame(sales_data)
monthly_sales = df.groupby(df['posting_date'].dt.month)['grand_total'].sum()
print("Monthly Sales Analysis:")
print(monthly_sales)
"""

result = execute_python_code({"code": code})
```

### 3. Advanced Features

#### Hybrid Streaming (Smart Artifact Creation)
- **Small Results**: Displayed directly in chat
- **Large Results**: Automatically streamed to artifacts for unlimited depth
- **Threshold**: 20 lines output triggers artifact streaming

#### Prompts Support
- `enforce_artifact_streaming_analysis`
- `create_business_intelligence_report`  
- `stream_python_analysis_to_artifact`

---

## 📊 Performance & Monitoring

### Performance Improvements (v1.0.0)
- **Memory Usage**: Reduced through modular loading
- **Code Maintainability**: Clean separation of concerns
- **Debugging**: Structured logging for better troubleshooting
- **Extensibility**: Easy to add new handlers and tools

### Monitoring & Logging
```python
# Enable debug logging
from frappe_assistant_core.utils.logger import api_logger
api_logger.setLevel('DEBUG')

# Check system health
from frappe_assistant_core.tools.registry import get_assistant_tools
tools = get_assistant_tools()
print(f"Available tools: {len(tools)}")
```

### Audit Trail
- All operations logged with user, timestamp, and result
- Connection tracking and monitoring
- Error tracking with detailed context
- Performance metrics and timing

---

## 🔒 Security Features

- **Role-Based Access Control**: Tools filtered by user permissions
- **Secure Python Execution**: Sandboxed environment with restricted imports
- **Authentication Required**: API key and session validation
- **Audit Logging**: Complete operation tracking
- **Permission Integration**: Respects Frappe's built-in permission system

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Commercial Use
This software is free for both personal and commercial use. You can:
- ✅ Use in commercial projects
- ✅ Modify and distribute
- ✅ Include in proprietary software
- ✅ Sell services around it

### Enterprise Support
Looking for enterprise features, support, or custom development? 
Contact us at jypaulclinton@gmail.com

---

## 📚 Documentation

- **[Technical Documentation](docs/TECHNICAL_DOCUMENTATION.md)** - Complete technical details and architecture
- **[API Reference](docs/API_REFERENCE.md)** - Detailed API documentation
- **[Installation Guide](docs/INSTALLATION.md)** - Step-by-step installation instructions
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

---

## 🤝 Contributing

This is an open-source MIT licensed project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Follow the modular architecture patterns
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

### Architecture Guidelines
- **Use Modular Handlers**: Add new functionality in separate handler modules
- **Leverage Constants**: All strings and configuration in `constants/definitions.py`
- **Professional Logging**: Use `api_logger` instead of print statements
- **Follow Patterns**: Maintain consistency with existing code structure

---

## 🌟 Support & Community

- **GitHub Repository**: [frappe-assistant-core](https://github.com/paulclinton/frappe-assistant-core)
- **Issues**: GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for questions and community support
- **Email**: jypaulclinton@gmail.com for direct support

---

## 🚀 Roadmap

### Planned Features
1. **Enhanced Analytics**: Advanced statistical analysis tools
2. **Real-time Collaboration**: Multi-user sessions
3. **Plugin System**: Third-party tool extensions
4. **API Rate Limiting**: Advanced throttling mechanisms
5. **Webhook Integration**: External service notifications

---

**Built with ❤️ by the community, for the community**

*Last Updated: June 2025 - Version 1.0.0*
*Architecture: Modular, Modern, Maintainable*