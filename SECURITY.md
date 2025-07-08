# Frappe Assistant Core - Security Implementation

## Overview

Frappe Assistant Core implements a comprehensive, multi-layered security system that follows Frappe Framework standards and provides enterprise-grade access control. The system combines role-based tool filtering, document-level permission validation, sensitive field protection, and comprehensive audit logging.

## Security Architecture

### 🔐 Multi-Layer Security Model

```
┌─────────────────────────────────────────────────────────────┐
│                    User Authentication                       │
│                   (API Key + Secret)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Role-Based Tool Filtering                   │
│              (check_tool_access function)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Document-Level Permissions                     │
│           (frappe.has_permission validation)                │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Sensitive Field Filtering                      │
│              (filter_sensitive_fields)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│            Submitted Document Protection                    │
│           (docstatus=1 write/delete prevention)             │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Audit Trail Logging                        │
│               (audit_log_tool_access)                       │
└─────────────────────────────────────────────────────────────┘
```

## Role-Based Access Control Matrix

### 🎯 **Updated Tool Access Matrix**

| Tool Category | System Manager | Assistant Admin | Assistant User | Default (All Users) |
|---------------|----------------|-----------------|----------------|-------------------|
| **Document Operations** | ✅ ALL | ✅ ALL | ✅ ALL | ✅ ALL |
| - document_create | ✅ | ✅ | ✅ | ✅ |
| - document_get | ✅ | ✅ | ✅ | ✅ |
| - document_update | ✅ | ✅ | ✅ | ✅ |
| - document_list | ✅ | ✅ | ✅ | ✅ |
| **Search & Discovery** | ✅ ALL | ✅ ALL | ✅ ALL | ✅ ALL |
| - search_global | ✅ | ✅ | ✅ | ✅ |
| - search_doctype | ✅ | ✅ | ✅ | ✅ |
| - search_link | ✅ | ✅ | ✅ | ✅ |
| **Reporting** | ✅ ALL | ✅ ALL | ✅ ALL | ✅ ALL |
| - report_execute | ✅ | ✅ | ✅ | ✅ |
| - report_list | ✅ | ✅ | ✅ | ✅ |
| - report_columns | ✅ | ✅ | ✅ | ✅ |
| **Analysis & Visualization** | ✅ ALL | ✅ ALL | ✅ ALL | ✅ ALL |
| - analyze_frappe_data | ✅ | ✅ | ✅ | ✅ |
| - create_visualization | ✅ | ✅ | ✅ | ✅ |
| **Basic Metadata** | ✅ ALL | ✅ ALL | ✅ ALL | ✅ ALL |
| - metadata_doctype | ✅ | ✅ | ✅ | ✅ |
| **Basic Workflow** | ✅ ALL | ✅ ALL | ✅ ALL | ✅ ALL |
| - workflow_status | ✅ | ✅ | ✅ | ✅ |
| - workflow_list | ✅ | ✅ | ✅ | ✅ |
| **🚨 DANGEROUS OPERATIONS** | | | | |
| - execute_python_code | ✅ ONLY | ❌ | ❌ | ❌ |
| - query_and_analyze | ✅ ONLY | ❌ | ❌ | ❌ |
| **🔧 ADMINISTRATIVE TOOLS** | | | | |
| - metadata_permissions | ✅ | ✅ ONLY | ❌ | ❌ |
| - metadata_workflow | ✅ | ✅ ONLY | ❌ | ❌ |
| - tool_registry_list | ✅ | ✅ ONLY | ❌ | ❌ |
| - tool_registry_toggle | ✅ | ✅ ONLY | ❌ | ❌ |
| - audit_log_view | ✅ | ✅ ONLY | ❌ | ❌ |
| - workflow_action | ✅ | ✅ ONLY | ❌ | ❌ |

### 📊 **Access Summary**
- **System Manager**: 23+ tools (ALL tools including dangerous operations)
- **Assistant Admin**: ~20 tools (All basic + administrative, no dangerous)
- **Assistant User**: 14 tools (Basic core tools only)
- **Default (All Users)**: 14 tools (Same as Assistant User - basic core tools)

## Key Security Features

### 🔒 **1. Universal Basic Tool Access**

**NEW**: All users (regardless of role) now have access to basic Core tools, with security enforced through **document-level permissions**.

```python
# Basic tools available to ALL users
BASIC_CORE_TOOLS = [
    "document_create", "document_get", "document_update", "document_list",
    "search_global", "search_doctype", "search_link",
    "report_execute", "report_list", "report_columns",
    "metadata_doctype", "create_visualization",
    "analyze_frappe_data", "workflow_status", "workflow_list"
]
```

**Rationale**: Since document-level permissions are robustly implemented, users can only access documents they have proper permissions for, making basic tools safe for all users.

### 🛡️ **2. Document-Level Permission Validation**

Every document operation goes through comprehensive permission checking:

```python
def validate_document_access(user, doctype, name, perm_type):
    # 1. Check DocType accessibility for user role
    # 2. Validate Frappe DocType-level permissions
    # 3. Validate document-level permissions (if specific document)
    # 4. Check submitted document protection
    # 5. Return validation result with user role
```

**Layers of Protection:**
- **DocType Access**: Restricted DocTypes blocked by role
- **DocType Permissions**: Standard Frappe `has_permission()` checking
- **Document Permissions**: Document-specific access validation
- **Submitted Document Protection**: Cannot edit/delete submitted docs

### 🔐 **3. Sensitive Field Filtering**

Role-based field filtering protects sensitive information:

```python
# Sensitive fields hidden from non-admins
SENSITIVE_FIELDS = {
    "all_doctypes": ["password", "api_key", "api_secret", ...],
    "User": ["password", "reset_password_key", "login_attempts", ...],
    "System Settings": [...],
    # ... more DocType-specific fields
}

# Admin-only fields hidden from Assistant Users
ADMIN_ONLY_FIELDS = {
    "all_doctypes": ["owner", "creation", "modified", ...],
    "User": ["enabled", "user_type", "roles", ...],
    # ... more administrative fields
}
```

### 🚫 **4. Submitted Document Protection**

Immutable submitted documents (docstatus = 1):

```python
# Protection in document_update tool
if hasattr(doc, 'docstatus') and doc.docstatus == 1:
    return {
        "success": False,
        "error": "Cannot modify submitted document. Submitted documents are read-only."
    }
```

### 🎯 **5. Restricted DocType Access**

DocTypes completely hidden from Assistant Users and Default users:

```python
RESTRICTED_DOCTYPES = {
    "Assistant User": [
        # System administration
        "System Settings", "Print Settings", "LDAP Settings",
        
        # Security and permissions  
        "Role", "User Permission", "Role Permission",
        
        # System logs and audit
        "Error Log", "Activity Log", "Access Log",
        
        # System customization
        "Server Script", "Custom Script", "DocType",
        
        # Development tools
        "Package", "Data Import", "Bulk Update",
        
        # Workflows (admin level)
        "Workflow", "Workflow Action", "Workflow State",
        
        # Email system internals
        "Email Queue", "Email Alert", "Auto Email Report"
    ]
}
```

### 📊 **6. Comprehensive Audit Trail**

All tool executions are logged:

```python
def audit_log_tool_access(user, tool_name, arguments, result):
    audit_log = frappe.get_doc({
        "doctype": "Assistant Audit Log",
        "user": user,
        "action": "tool_execution", 
        "tool_name": tool_name,
        "arguments": frappe.as_json(arguments),
        "success": result.get("success", False),
        "error": result.get("error", ""),
        "timestamp": frappe.utils.now()
    })
    audit_log.insert(ignore_permissions=True)
```

## Implementation Files

### Core Security Module
- **`/core/security_config.py`**: Main security configuration and functions
  - Role-based tool access matrix
  - Sensitive field definitions
  - Permission validation functions
  - Audit logging functions

### Tool Integration
- **`/core/tool_registry.py`**: Tool filtering and discovery
  - Role-based tool filtering in `get_available_tools()`
  - Integration with security_config functions

### Document Tools with Security
- **`/plugins/core/tools/document_get.py`**: Secure document retrieval
- **`/plugins/core/tools/document_update.py`**: Protected document updates
- **`/plugins/core/tools/document_create.py`**: Secure document creation
- **`/plugins/core/tools/document_list.py`**: Permission-filtered listings

## Security Testing

### Test Results

```bash
# Tool Access Testing
Assistant User: 14 tools available ✅
Default User: 14 tools available ✅  
System Manager: 23 tools available ✅

# Dangerous Tool Restriction
execute_python_code: System Manager ONLY ✅
query_and_analyze: System Manager ONLY ✅

# Document Permission Testing
User access to restricted DocType: BLOCKED ✅
Document-level permission checking: ENFORCED ✅
Submitted document modification: BLOCKED ✅
```

## Security Best Practices

### ✅ **Implemented**
1. **Defense in Depth**: Multiple layers of security validation
2. **Principle of Least Privilege**: Minimal necessary access granted
3. **Role-Based Access Control**: Granular permission matrix
4. **Audit Trail**: Comprehensive logging of all operations
5. **Input Validation**: Proper sanitization and validation
6. **Sensitive Data Protection**: Field-level filtering
7. **Submitted Document Immutability**: Workflow state protection

### 🔧 **For Production**
1. **Rate Limiting**: Implement API request rate limits
2. **Session Management**: Configure appropriate session timeouts
3. **SSL/TLS**: Enforce HTTPS for all communications
4. **Monitoring**: Set up alerts for suspicious activity patterns
5. **Regular Audits**: Periodic security reviews and penetration testing

## Migration Impact

### ✅ **What Changed**
- **Basic tools now available to ALL users** (not just assistant roles)
- **Document permissions remain the primary security control**
- **Dangerous tools still restricted to System Manager only**
- **Enhanced audit logging for all operations**

### ✅ **What Stayed the Same**
- **Document-level permission checking** (unchanged)
- **Sensitive field filtering** (unchanged)  
- **Submitted document protection** (unchanged)
- **Administrative tool restrictions** (unchanged)

### 🎯 **Benefits**
1. **Better User Experience**: Users can access tools they need
2. **Simplified Administration**: Less role management required
3. **Maintained Security**: Document permissions provide robust protection
4. **Scalability**: Works for organizations of any size

## Monitoring and Alerting

### 📊 **Key Metrics to Monitor**
1. **Failed Permission Attempts**: Users trying to access restricted resources
2. **Dangerous Tool Usage**: Python/SQL execution by System Managers
3. **Bulk Operations**: Large-scale document modifications
4. **Administrative Actions**: Tool management and permission changes
5. **Authentication Failures**: Invalid API key/secret attempts

### 🚨 **Alert Conditions**
- Multiple failed permission attempts from same user
- Dangerous tool execution outside business hours
- Attempts to modify system-critical DocTypes
- Unusual patterns in document access
- Failed authentication attempts

## Conclusion

The Frappe Assistant Core security implementation provides **enterprise-grade protection** while maintaining **user accessibility**. The multi-layered approach ensures that:

- **All users** can access basic productivity tools
- **Document permissions** provide granular access control
- **Sensitive operations** remain properly restricted
- **Comprehensive auditing** enables security monitoring
- **Frappe standards** are followed throughout

This implementation strikes the optimal balance between **security** and **usability**, making it suitable for production environments while providing the flexibility needed for diverse organizational structures.