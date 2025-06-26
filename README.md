# Frappe Assistant Core

🤖 **Professional AI Assistant for ERPNext** - Transform your ERPNext experience with intelligent AI assistance through the Model Context Protocol (MCP).

Built for businesses who want to leverage AI to streamline their ERP operations, automate workflows, and gain intelligent insights from their data.

---

## 🌟 Why Choose Frappe Assistant Core?

- **🔌 Plug & Play AI Integration**: Seamlessly connect Claude and other AI assistants to your ERPNext data
- **🛡️ Enterprise Security**: Built-in permissions, audit logging, and secure authentication
- **📊 Intelligent Analytics**: AI-powered insights and visualization capabilities
- **🚀 Production Ready**: Rate limiting, comprehensive monitoring, and robust error handling
- **🆓 Completely Open Source**: MIT licensed - free for all uses, commercial and personal
- **🤝 Community Driven**: Built by the community, for the community

---

## 🎯 Features Overview

### 🚀 Complete Feature Set (MIT Licensed)
- **Complete MCP Protocol Support**: JSON-RPC 2.0 based Model Context Protocol implementation
- **Document Operations**: Create, read, update, delete, and search Frappe documents with full permission integration
- **Advanced Reporting**: Execute Frappe reports with enhanced debugging and error handling
- **Data Visualization**: Create charts and graphs with inline display support
- **Advanced Analytics**: Statistical analysis and business intelligence tools
- **Global Search**: Search across all accessible documents and data
- **Metadata Access**: Query DocType schemas, permissions, and workflow information
- **Audit Logging**: Comprehensive operation tracking and monitoring
- **Python Code Execution**: Execute custom Python code with full Frappe context
- **Admin Interface**: Web-based management interface for server configuration

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

## 🚀 Quick Start

### Prerequisites
- **Frappe Framework** v15 (v15+ recommended)
- **Python** 3.11+
- **ERPNext** (optional but recommended)
- **Redis** for caching and session management

### 1. Installation

```bash
# Get the app from GitHub
bench get-app frappe_assistant_core https://github.com/clinu/Frappe-Assistant-Core.git

# Install on your site
bench --site your-site.local install-app frappe_assistant_core

# Restart to apply changes
bench restart
```

### 2. Basic Configuration

1. Navigate to **Setup → Frappe Assistant Core Settings**
2. Configure basic server settings:
   ```
   ✓ Server Enabled: Yes
   ✓ Server Port: 8000 (default)
   ✓ Max Connections: 100
   ✓ Rate Limit: 60 requests/minute
   ```

3. **Optional**: Configure advanced settings like rate limiting and monitoring

### 3. Connect with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "frappe": {
      "command": "python",
      "args": ["-m", "frappe_assistant_core.assistant_core.stdio_server"],
      "env": {
        "FRAPPE_SITE": "your-site.localhost",
        "FRAPPE_API_KEY": "your_api_key",
        "FRAPPE_API_SECRET": "your_api_secret"
      }
    }
  }
}
```

---

## 🛠️ Available AI Tools

### 📄 Document Operations
- **`document_create`**: Create new documents with validation
- **`document_get`**: Retrieve specific documents with permissions
- **`document_update`**: Update existing documents safely
- **`document_delete`**: Delete documents with audit trail
- **`document_list`**: List documents with advanced filtering

### 📊 Reporting & Analytics
- **`report_execute`**: Run standard Frappe reports with enhanced debugging
- **`report_list`**: List available reports by module
- **`report_columns`**: Get detailed column information for reports
- **`analyze_frappe_data`**: Advanced statistical analysis

### 🔍 Search & Discovery  
- **`search_global`**: Search across all accessible data
- **`search_doctype`**: Targeted DocType searching
- **`search_link`**: Search for link field options

### ⚙️ Metadata & Configuration
- **`metadata_doctype`**: Get DocType schemas and field info
- **`metadata_permissions`**: Check user permissions
- **`metadata_workflow`**: Access workflow and document state information

### 🔧 Advanced Tools & Analytics
- **`execute_python_code`**: Execute custom Python code with Frappe context
- **`analyze_frappe_data`**: Statistical analysis and business insights
- **`create_visualization`**: Generate charts and graphs from data
- **`query_and_analyze`**: Custom SQL queries with analysis

---

## 🏆 Proven Capabilities

**✅ 100% Operational - Validated with Business Data**

Our comprehensive testing demonstrates enterprise-ready performance across all capabilities:

### **📊 Live System Validation Results**
- **19 Core Tools**: 100% operational rate across all categories
- **765 DocTypes**: Complete ERP coverage with full metadata access
- **Enterprise Security**: Full role-based access with audit trails
- **Sub-second Performance**: < 200ms for most operations, < 1s for analytics
- **Production Scale**: Business data processing and analysis

### **🎯 Proven Business Value**
- **Customer Intelligence**: AI-powered portfolio analysis across 8 customers and 4 segments
- **Financial Automation**: 49 accounting reports automated with real-time data access
- **Real-time Analytics**: SQL queries + statistical analysis + visualization generation
- **Zero Configuration**: Auto-discovery eliminates setup - 765 DocTypes detected automatically

### **⚡ Performance Benchmarks**
```yaml
Response Times (Production Validated):
  - Metadata Queries: < 100ms
  - Document Operations: < 200ms  
  - Search Operations: < 300ms
  - Analysis Operations: 1-5 seconds
  - Report Generation: Variable (size-dependent)

Business Operations Tested:
  - Customer Relationship Intelligence ✅
  - Financial Reporting Automation ✅
  - System Administration Intelligence ✅
  - Advanced Data Visualization ✅
```

### **🛡️ Enterprise Security Validation**
- **Authentication**: Session-based + API Key/Secret + Role inheritance
- **Authorization**: DocType-level + Field-level + Record-level permissions
- **Audit Trail**: Complete operation logging with input/output tracking
- **Data Integrity**: 100% complete records across all tested operations

[**→ View Complete Technical Validation Report**](docs/CAPABILITIES_REPORT.md)

---

## 💡 Usage Examples

### Creating a Customer with AI

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "document_create",
    "arguments": {
      "doctype": "Customer",
      "data": {
        "customer_name": "TechCorp Solutions",
        "customer_type": "Company",
        "territory": "United States",
        "customer_group": "Enterprise"
      }
    }
  },
  "id": 1
}
```

### AI-Powered Search

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "search_global",
    "arguments": {
      "query": "high-value customers in technology sector",
      "limit": 10
    }
  },
  "id": 2
}
```

### Business Intelligence Report

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "report_execute",
    "arguments": {
      "report_name": "Sales Analytics",
      "filters": {
        "from_date": "2024-01-01",
        "to_date": "2024-12-31",
        "company": "Your Company"
      }
    }
  },
  "id": 3
}
```

---

## 🔐 Security & Compliance

### 🛡️ Authentication Methods
- **API Key/Secret**: Secure programmatic access
- **Session-based**: Web interface authentication  
- **JWT Tokens**: Stateless API authentication
- **Frappe Authentication**: Native Frappe user authentication

### 🔒 Permission Integration
- **Role-based Access**: Respects all Frappe permission rules
- **Field-level Security**: Control access to sensitive data
- **Document-level Permissions**: User-specific document access
- **Audit Trail**: Comprehensive operation logging

### 📊 Rate Limiting & Monitoring
- **Configurable Limits**: Prevent API abuse
- **Real-time Monitoring**: Track usage and performance
- **Comprehensive Logging**: Detailed audit trails and error tracking

---

## 🎛️ Administration

### Web Interface
Access the admin dashboard at **`/app/assistant-admin`**:
- 📊 **Server Status**: Monitor connections and performance
- 📈 **Usage Analytics**: View usage patterns and trends
- 🔍 **Audit Logs**: Track all AI operations
- ⚙️ **Tool Configuration**: Manage available AI tools
- 👥 **User Management**: Control access and permissions

### Command Line Management
```bash
# Start the MCP server
bench execute frappe_assistant_core.assistant_core.server.start_server

# Monitor server status  
bench execute frappe_assistant_core.assistant_core.server.get_server_status

# View connection logs
bench execute frappe_assistant_core.assistant_core.server.get_connection_logs
```

---

## 🆘 Support & Resources

### 🆓 Open Source Community
- 📖 **Documentation**: [Technical Docs](docs/) | [Tool Usage Guide](docs/TOOL_USAGE_GUIDE.md)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/clinu/frappe-assistant-core/issues)
- 💬 **Community Discussion**: [GitHub Discussions](https://github.com/clinu/frappe-assistant-core/discussions)
- 🗣️ **Frappe Forum**: [Community Support](https://discuss.frappe.io)

### 💼 Professional Services
Need help with implementation, customization, or support?
- 📧 **Contact**: [jypaulclinton@gmail.com](mailto:jypaulclinton@gmail.com)
- 🛠️ **Services Available**: Custom development, training, and consulting
- 🎯 **Enterprise Support**: Implementation assistance and professional services

---

## 🧑‍💻 Development & Contributing

### 🔧 Adding Custom Tools

Create custom AI tools for your specific business needs:

```python
class CustomBusinessTools:
    @staticmethod
    def get_tools():
        return [{
            "name": "sales_forecast",
            "description": "Generate AI-powered sales forecasts",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "period": {"type": "string"},
                    "territory": {"type": "string"}
                }
            }
        }]
    
    @staticmethod
    def execute_tool(tool_name, arguments):
        if tool_name == "sales_forecast":
            # Your custom logic here
            return {"forecast": "AI-generated forecast data"}
```

### 🤝 Contributing
We welcome contributions from the community! 

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request
5. Follow our [Contributing Guidelines](CONTRIBUTING.md)

For detailed documentation, see our [Documentation Hub](docs/)

---

## 🐛 Troubleshooting

### Common Issues & Solutions

**🔴 Connection Refused**
```bash
# Check server status
bench execute frappe_assistant_core.assistant_core.server.get_server_status

# Verify port and firewall settings
netstat -tlnp | grep 8001
```

**🔴 Permission Denied**
- Verify user has MCP access roles
- Check API key permissions
- Review tool-specific permission requirements

**🔴 Tool Not Found**
- Ensure tool is enabled in Assistant Tool Registry
- Check user permissions for tool category
- Verify tool name is spelled correctly

### 📊 Monitoring & Logs
- **Error Logs**: `sites/your-site/logs/error.log`
- **MCP Logs**: View in MCP Connection Log DocType
- **Audit Trail**: MCP Audit Log DocType
- **Performance**: Built-in monitoring dashboard

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### What this means:
- ✅ **Free for everyone**: Personal and commercial use
- ✅ **Modify freely**: Change the code as needed
- ✅ **Distribute openly**: Share with others
- ✅ **No restrictions**: Use in proprietary software
- ✅ **Commercial friendly**: Build businesses around it

---

## 🚀 About the Author

**Paul Clinton**  
*AI & ERP Integration Specialist*

📧 **Email**: [jypaulclinton@gmail.com](mailto:jypaulclinton@gmail.com)  
🔗 **LinkedIn**: [linkedin.com/in/paulclinton](https://linkedin.com/in/paul--clinton)  
💻 **GitHub**: [github.com/paulclinton](https://github.com/clinu)

*Passionate about making AI accessible to businesses through intelligent ERP integration.*

---

⭐ **Star this repository** if you find it valuable!  
🔄 **Share** with your network to help others discover AI-powered ERP  
📧 **Contact us** for enterprise demonstrations and custom solutions

**Ready to transform your ERPNext with AI?** [Get started today! →](#-quick-start)
