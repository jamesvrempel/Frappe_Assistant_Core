# Changelog

All notable changes to Claude for Frappe ERP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-07-04

### 🏗️ Project Restructuring

#### Changed
- **Package Location** - Moved from `claude-for-frappe/` to `client_packages/claude-desktop/`
- **Architecture** - Organized under new client packages structure for future AI platform integrations
- **Documentation** - Updated all paths and references to reflect new structure

#### Added
- **Client Packages Overview** - New `client_packages/README.md` explaining architecture
- **Future Roadmap** - Prepared structure for ChatGPT plugins, GitHub Copilot extensions, and API SDKs

#### Technical Details
- No breaking changes for end users
- Extension functionality remains identical
- Installation process unchanged
- Same DXT package format

## [1.0.0] - 2025-01-04

### 🎉 Initial Release

#### Added
- **Core MCP Server** - Complete Model Context Protocol implementation for Claude Desktop
- **Frappe Bridge** - Secure connection to any Frappe/ERPNext instance via stdio
- **21 Essential Tools** for comprehensive ERP interaction

#### 📊 Data Analysis & Visualization Tools
- `execute_python_code` - Custom Python execution with Frappe framework access
- `analyze_frappe_data` - Statistical analysis with trends and correlations
- `query_and_analyze` - Custom SQL queries with advanced analytics
- `create_visualization` - Interactive charts (bar, line, pie, scatter, heatmap)

#### 📋 Document Management Tools
- `document_create` - Create new documents (Customer, Invoice, Item, etc.)
- `document_get` - Retrieve detailed document information
- `document_update` - Modify existing documents
- `document_list` - Search and filter documents with advanced criteria

#### 🔍 Search & Discovery Tools
- `search_global` - Global search across all accessible documents
- `search_doctype` - DocType-specific search with filters
- `search_link` - Find link field options and references

#### 📈 Reporting Tools
- `report_execute` - Run financial, sales, and custom reports
- `report_list` - Discover available reports across modules
- `report_columns` - Get report structure and column information

#### 🔧 Metadata & System Tools
- `metadata_doctype` - Explore DocType structures and fields
- `metadata_list_doctypes` - List all available DocTypes
- `metadata_permissions` - Check user permissions and access rights
- `metadata_workflow` - Get workflow information and states

#### 🔄 Workflow Management Tools
- `start_workflow` - Initiate document approval processes
- `get_workflow_state` - Check current workflow status
- `get_workflow_actions` - Get available workflow actions

#### 🔒 Security Features
- Secure API key authentication
- Permission-based access control
- HTTPS-only communication
- No external data transmission

#### 🛠️ Configuration
- User-friendly configuration interface
- Environment variable support
- Debug mode for troubleshooting
- Cross-platform compatibility (Windows, macOS, Linux)

#### 📱 Platform Support
- **Windows** - Full support with Python fallback
- **macOS** - Native support with Python 3
- **Linux** - Complete compatibility

### Technical Details
- Python 3.8+ compatibility
- MCP protocol v0.1 compliance
- Async stdio communication
- Comprehensive error handling
- Detailed logging and debugging

### Known Issues
- Large dataset visualizations may take time to render
- Complex SQL queries require appropriate database permissions
- Some advanced Frappe features may need additional configuration

---

## Versioning Strategy

- **Major.Minor.Patch** (e.g., 1.0.0)
- **Major**: Breaking changes, new architecture
- **Minor**: New features, tools, significant enhancements
- **Patch**: Bug fixes, minor improvements, security updates

## Release Notes

Each release includes:
- 📦 **DXT Package** - Ready-to-install Claude Desktop extension
- 📋 **Release Notes** - Detailed changelog and upgrade instructions
- 🔧 **Migration Guide** - For breaking changes (when applicable)
- 🐛 **Bug Fixes** - List of resolved issues

## Future Roadmap

Planned for upcoming releases:
- Enhanced visualization types
- Real-time data streaming
- Advanced AI-powered insights
- Multi-server support
- Plugin system for custom tools
- Mobile companion features