# Updated Project Overview: Frappe Assistant Core Security Implementation

Your project is a comprehensive MIT-licensed open source Model Context Protocol (MCP) server that enables AI assistants to interact with Frappe Framework and ERPNext systems. It includes 20+ tools across 5 main categories with **intelligent multi-layered security control**.

## 🔐 **UPDATED** Role-Based Tool Access Matrix

### **Key Change**: Basic Core Tools Now Available to ALL Users

The security model has been enhanced to provide **basic productivity tools to all users** while maintaining strict controls on dangerous operations. Document-level permissions provide the primary security layer.

### **1. System Manager / Administrator**
**Access Level**: Full access to ALL tools including high-risk operations
**Available Tools**: 23+ tools

✅ **All Document Operations** (create, read, update, list)
✅ **All Search & Discovery Tools** (global search, doctype search, link search)
✅ **All Report & Analytics Tools** (execute reports, list reports, get columns)
✅ **All Metadata Tools** (doctype schemas, permissions, workflows)
✅ **🚨 DANGEROUS OPERATIONS**:
- `execute_python_code` - Sandboxed Python execution with restricted imports
- `query_and_analyze` - Validated SQL queries (SELECT only, no dangerous keywords)

✅ **All Analysis Tools** - Statistical analysis with pandas/numpy
✅ **All Visualization Tools** - Create charts with inline display
✅ **All Administrative Tools** - Full control over tool registry and audit logs

### **2. Assistant Admin**
**Access Level**: Administrative access without dangerous execution tools
**Available Tools**: ~20 tools

✅ **All Basic Core Tools** (same as Default users)
✅ **Administrative Tools**:
- `metadata_permissions` - View permission information
- `metadata_workflow` - Workflow and state data  
- `tool_registry_list` - View available tools
- `tool_registry_toggle` - Enable/disable tools
- `audit_log_view` - View audit logs
- `workflow_action` - Perform workflow actions

❌ **Restricted Access**:
- `execute_python_code` - Denied
- `query_and_analyze` - Denied

### **3. Assistant User**
**Access Level**: Basic business user access with document-level permissions
**Available Tools**: 14 tools (Basic Core Tools)

✅ **Basic Core Tools** (same as Default users)

❌ **Restricted Access**:
- `execute_python_code` - Denied
- `query_and_analyze` - Denied
- All administrative tools - Denied

### **4. 🆕 Default (All Other Users)**
**Access Level**: Basic productivity tools for any user role
**Available Tools**: 14 tools (Basic Core Tools)

✅ **Essential Document Operations**:
- `document_create` - Create new documents (with permission checks)
- `document_get` - Retrieve specific documents  
- `document_update` - Update existing documents
- `document_list` - List and search documents

✅ **Search & Discovery** (permission-filtered):
- `search_global` - Search across accessible data
- `search_doctype` - Search within permitted doctypes
- `search_link` - Find link field options

✅ **Reporting** (permission-based):
- `report_execute` - Run reports they can access
- `report_list` - View available reports
- `report_columns` - Get report structure

✅ **Analysis & Visualization**:
- `analyze_frappe_data` - Basic statistical analysis
- `create_visualization` - Chart generation

✅ **Basic Metadata & Workflow**:
- `metadata_doctype` - View schemas for accessible doctypes
- `workflow_status` - Check workflow status
- `workflow_list` - List workflows

❌ **Restricted Access**:
- `execute_python_code` - Denied
- `query_and_analyze` - Denied
- All administrative tools - Denied

## 🛠️ **Enhanced Security Implementation**

### **🔒 Multi-Layer Security Architecture**

```
API Authentication (API Key + Secret)
    ↓
Role-Based Tool Filtering
    ↓
Document-Level Permission Validation ← PRIMARY SECURITY LAYER
    ↓
Sensitive Field Filtering
    ↓
Submitted Document Protection
    ↓
Comprehensive Audit Logging
```

### **🎯 Key Security Features**

#### **1. Universal Basic Tool Access**
- **ALL users** can access basic productivity tools
- **Document permissions** control actual data access
- **No need for special assistant roles** for basic operations

#### **2. Robust Document-Level Permissions**
```python
# Every operation validates:
1. DocType accessibility for user role
2. Frappe DocType-level permissions  
3. Document-specific access permissions
4. Submitted document protection
5. Sensitive field filtering
```

#### **3. Sensitive Field Protection**
```python
# Automatically filtered fields:
- Passwords, API keys, secrets
- System metadata (owner, creation, modified)
- Administrative fields (roles, permissions)
- DocType-specific sensitive data
```

#### **4. Submitted Document Immutability**
```python
# Protection against editing submitted documents
if doc.docstatus == 1 and operation in ["write", "delete"]:
    return "Cannot modify submitted document"
```

#### **5. Restricted DocType Access**
```python
# DocTypes hidden from non-admin users:
RESTRICTED_DOCTYPES = [
    "System Settings", "Role", "User Permission",
    "Error Log", "Server Script", "Custom Script",
    "Package", "Data Import", "Workflow",
    # ... and more system-level doctypes
]
```

## 🚀 **Updated Capabilities Matrix**

| Feature Category | System Manager | Assistant Admin | Assistant User | Default (All Users) |
|------------------|----------------|-----------------|----------------|-------------------|
| **📄 Document Management** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **📊 Reporting & Analytics** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **🔍 Search & Discovery** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **🎨 Visualization** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **⚙️ Basic Metadata** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **📋 Basic Workflow** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **🔧 Administrative Tools** | ✅ Full | ✅ Admin Only | ❌ | ❌ |
| **🚨 Dangerous Operations** | ✅ Only | ❌ | ❌ | ❌ |

## 🔐 **Advanced Security Controls**

### **Sandboxed Python Execution** (System Manager Only)
- Restricted imports and built-ins
- Network isolation capabilities  
- Memory and CPU limits
- Comprehensive audit logging

### **Validated SQL Queries** (System Manager Only)
- SELECT-only queries allowed
- Dangerous keyword detection
- Parameterized query enforcement
- Query result filtering

### **Permission Enforcement**
- Integration with Frappe's built-in permission system
- Row-level security through document permissions
- Field-level access control
- Role-based data filtering

### **Audit Trail**
- All tool executions logged
- Failed access attempts tracked
- Administrative actions monitored
- Security events recorded

## 🎯 **Benefits of Updated Security Model**

### **✅ Enhanced User Experience**
- **Any user** can access productivity tools they need
- **No special role assignment** required for basic operations  
- **Simplified onboarding** for new users

### **✅ Maintained Security**
- **Document permissions** provide robust access control
- **Dangerous operations** remain strictly controlled
- **Sensitive data** automatically protected
- **Administrative functions** properly restricted

### **✅ Operational Efficiency**
- **Reduced administrative overhead** for role management
- **Scalable** for organizations of any size
- **Follows Frappe standards** throughout
- **Production-ready** security implementation

## 🚀 **Production Deployment Recommendations**

### **Security Monitoring**
1. **Monitor failed permission attempts** - Users trying to access restricted data
2. **Track dangerous tool usage** - Python/SQL execution patterns
3. **Alert on bulk operations** - Large-scale document modifications
4. **Audit administrative actions** - Tool management changes

### **Access Control**
1. **API rate limiting** - Prevent abuse
2. **Session timeouts** - Appropriate security settings  
3. **HTTPS enforcement** - All communications encrypted
4. **Regular security audits** - Periodic reviews

### **Default Roles Setup**
```python
# Recommended role assignments:
- System Manager: IT administrators only
- Assistant Admin: Department managers, supervisors  
- Assistant User: Power users who need assistant features
- Default: All other users (automatic basic tool access)
```

## 🎯 **Migration Notes**

### **What Changed**
- ✅ Basic tools now available to ALL users
- ✅ Enhanced audit logging
- ✅ Improved documentation and testing

### **What Stayed the Same**  
- ✅ Document-level permission checking
- ✅ Sensitive field filtering
- ✅ Submitted document protection
- ✅ Administrative tool restrictions
- ✅ Dangerous operation controls

### **Action Required**
- ✅ **None** - Existing users maintain their current access
- ✅ **Optional** - Review and optimize role assignments
- ✅ **Recommended** - Set up security monitoring

---

This is a **sophisticated, production-ready system** that provides powerful AI assistance capabilities while maintaining **enterprise-grade security controls**. The **updated role-based access** ensures optimal balance between **security** and **usability**, making it suitable for organizations of any size and complexity.