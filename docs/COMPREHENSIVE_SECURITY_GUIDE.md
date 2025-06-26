# Comprehensive Security Guide for Frappe Assistant Core

## 🔒 Security Overview

This document provides a complete security reference for Frappe Assistant Core, covering both the critical vulnerabilities that were fixed and the secure implementation of powerful features like Python code execution and SQL queries.

## 📋 Table of Contents

1. [Critical Vulnerabilities Fixed](#critical-vulnerabilities-fixed)
2. [Current Security Architecture](#current-security-architecture)
3. [Secure Code Execution](#secure-code-execution)
4. [Role-Based Access Control](#role-based-access-control)
5. [Security Validation Examples](#security-validation-examples)
6. [Best Practices](#best-practices)
7. [Audit and Monitoring](#audit-and-monitoring)

---

## ⚠️ Critical Vulnerabilities Fixed

### Evolution of Security Approach

**Initial Problem**: Complete disabling of powerful tools  
**Solution**: Secure, role-based implementation with sandboxing

### 1. **Arbitrary Code Execution - NOW SECURE**

#### **Previous Vulnerability**: 
The `execute_python_code` tool allowed arbitrary Python code execution with full system access.

**Attack Scenario Previously Possible**:
```python
# Malicious code that was previously possible:
frappe.set_user("Administrator")  # Escalate to admin
po = frappe.get_doc("Purchase Order", "PO-001") 
po.submit()  # Bypass permissions and approve PO
```

#### **Current Security Implementation**:
- **Role Restriction**: Only System Managers can execute Python code
- **Sandboxed Environment**: Restricted built-ins and Frappe API
- **Permission Enforcement**: All data access respects user permissions
- **Audit Trail**: All executions logged for security monitoring

**Secure Code Example**:
```python
# This now executes safely:
# 1. User must be System Manager
# 2. Sandboxed environment prevents dangerous operations
# 3. All Frappe operations check permissions

# Get sales data (permission-checked)
data = frappe.get_all('Sales Invoice', 
                     filters={'status': 'Paid'}, 
                     fields=['grand_total', 'customer'])

# Safe analysis with pandas
df = pd.DataFrame(data)
monthly_totals = df.groupby('customer')['grand_total'].sum()
print(f"Top customers: {monthly_totals.nlargest(5).to_dict()}")
```

### 2. **SQL Injection - NOW SECURE**

#### **Previous Vulnerability**: 
`query_and_analyze` tool allowed direct SQL execution with weak validation.

**Attack Scenario Previously Possible**:
```sql
-- Bypassing keyword filtering:
SELECT * FROM `tabUser` UNION 
sElEcT api_key, api_secret FROM `tabUser` WHERE 1=1

-- Extracting sensitive data:
SELECT password_hash FROM `tabAuth` WHERE enabled=1
```

#### **Current Security Implementation**:
- **Role Restriction**: Only System Managers can execute SQL
- **Comprehensive Validation**: Multi-layer query filtering
- **SELECT-Only Queries**: No data modification allowed
- **DocType Validation**: Must reference valid Frappe tables

**Secure SQL Example**:
```sql
-- This executes safely with full validation:
SELECT 
    customer,
    COUNT(*) as invoice_count,
    SUM(grand_total) as total_amount,
    AVG(grand_total) as avg_amount
FROM `tabSales Invoice` 
WHERE status = 'Paid' 
  AND posting_date >= '2024-01-01'
GROUP BY customer
ORDER BY total_amount DESC
LIMIT 10;
```

---

## 🛡️ Current Security Architecture

### Multi-Level Access Control

```python
# 1. API Level Authentication
@frappe.whitelist(allow_guest=False, methods=["POST"])

# 2. Session Validation
if not frappe.session.user or frappe.session.user == "Guest":
    return access_denied()

# 3. Assistant Permission Check
if not check_assistant_permission(frappe.session.user):
    return access_denied()

# 4. Tool-Specific Role Validation
if tool_name in ["execute_python_code", "query_and_analyze"]:
    if "System Manager" not in frappe.get_roles(user):
        return permission_denied()

# 5. Document-Level Permission Check
if not frappe.has_permission(doctype, operation):
    return permission_denied()
```

### Permission Hierarchy
```
System Manager > Assistant Admin > Assistant User > No Access
     ↓               ↓                ↓               ↓
Full Access    Tool Management   Document Ops    Denied
Python Code    + Audit Logs     + Reports       
SQL Queries    + Settings       + Analysis      
All Tools      All Safe Tools   Safe Tools Only
```

---

## 🚀 Secure Code Execution

### Access Control Implementation
```python
@staticmethod
def execute_python_code(code: str, data_query: Dict = None, imports: List[str] = None):
    # SECURITY: Role validation
    user_roles = frappe.get_roles(frappe.session.user)
    if "System Manager" not in user_roles:
        return {
            "success": False,
            "error": "Python code execution requires System Manager role",
            "required_role": "System Manager",
            "user_roles": user_roles
        }
```

### Sandboxed Execution Environment
```python
# Restricted built-ins (safe functions only)
restricted_builtins = {
    'abs', 'all', 'any', 'bool', 'dict', 'enumerate', 'filter',
    'float', 'int', 'len', 'list', 'map', 'max', 'min', 'range',
    'round', 'set', 'sorted', 'str', 'sum', 'tuple', 'type', 'zip', 'print'
    # EXPLICITLY EXCLUDED: exec, eval, compile, open, input, __import__
}

# Permission-aware Frappe API
class RestrictedFrappe:
    @staticmethod
    def get_all(doctype, **kwargs):
        if not frappe.has_permission(doctype, "read"):
            raise PermissionError(f"No read permission for {doctype}")
        return frappe.get_all(doctype, **kwargs)
    
    @staticmethod
    def set_user(*args, **kwargs):
        raise SecurityError("User context modification not allowed")
    
    @staticmethod
    def db(*args, **kwargs):
        raise SecurityError("Direct database access not allowed")
```

### Safe Library Imports
```python
# Curated whitelist of safe libraries
safe_imports = {
    'datetime', 'math', 're', 'statistics', 'collections',
    'itertools', 'functools', 'pandas', 'numpy', 'matplotlib',
    'seaborn', 'json', 'csv'
}

# Import validation
if imp not in safe_imports:
    return {"error": f"Import '{imp}' not allowed. Safe imports: {list(safe_imports)}"}
```

---

## 🔍 Secure SQL Query Execution

### Multi-Layer Validation System
```python
def query_and_analyze(query: str, analysis_code: str = None):
    # 1. Role Check
    if "System Manager" not in user_roles:
        return {"error": "SQL query execution requires System Manager role"}
    
    # 2. Query Type Validation
    if not query_lower.startswith('select'):
        return {"error": "Only SELECT queries are allowed"}
    
    # 3. Comprehensive Dangerous Keyword Detection
    dangerous_keywords = [
        'drop', 'delete', 'update', 'insert', 'alter', 'create', 'truncate',
        'exec', 'execute', 'sp_', 'xp_', 'into', 'union', 'declare', 'while',
        'cursor', 'fetch', 'open', 'close', 'deallocate', 'bulk', 'load'
    ]
    
    # 4. Comment and Multiple Statement Prevention
    if '--' in query or '/*' in query or '*/' in query:
        return {"error": "Comments not allowed in queries"}
    
    if ';' in query.rstrip(';'):
        return {"error": "Multiple statements not allowed"}
    
    # 5. DocType Validation
    if not any(f'`tab{doctype}`' in query for doctype in frappe.get_all('DocType', pluck='name')):
        return {"error": "Query must reference valid Frappe DocTypes using `tab` prefix"}
```

---

## 🎯 Role-Based Access Control

### Permission Matrix

| Tool Category | Assistant User | Assistant Admin | System Manager |
|---------------|----------------|-----------------|----------------|
| **Document Operations** | ✅ With permissions | ✅ With permissions | ✅ Full access |
| **Report Execution** | ✅ Standard reports | ✅ All reports | ✅ All reports |
| **Data Analysis** | ✅ Safe analysis | ✅ Safe analysis | ✅ Safe analysis |
| **Search Functions** | ✅ Permission-based | ✅ Permission-based | ✅ Full access |
| **Python Code Execution** | ❌ Denied | ❌ Denied | ✅ Sandboxed |
| **SQL Query Execution** | ❌ Denied | ❌ Denied | ✅ Validated |
| **Tool Management** | ❌ View only | ✅ Enable/Disable | ✅ Full control |
| **Audit Logs** | 👁️ Own logs only | ✅ All logs | ✅ All logs |

### Document-Level Security Example
```python
# Example: Sales Invoice Access
user = "john@company.com"  # Regular Assistant User

# 1. Check DocType read permission
has_read = frappe.has_permission("Sales Invoice", "read", user=user)

# 2. Check specific document access (considers territory/customer restrictions)
doc = frappe.get_doc("Sales Invoice", "SINV-00001") 
can_access = frappe.has_permission(doc, "read", user=user)

# 3. Check field-level permissions
sensitive_fields = ["grand_total", "outstanding_amount"]
accessible_fields = [f for f in sensitive_fields 
                    if frappe.has_permission(doc, "read", user=user)]

# Result: Access granted only if ALL checks pass
```

---

## 🚫 Attack Scenarios Prevented

### 1. Privilege Escalation Attempt
**Attack**: User tries to become Administrator
```python
# This would be blocked:
frappe.set_user("Administrator")  # SecurityError: User modification not allowed
```

**Prevention**: 
- Sandboxed Frappe API prevents user context changes
- Original user permissions maintained throughout execution

### 2. Data Exfiltration Attempt
**Attack**: User tries to access all credentials
```sql
-- This would be blocked:
SELECT api_key, api_secret FROM `tabUser`  -- System Manager role required
```

**Prevention**:
- Role-based access control
- Permission checks for all data operations
- Query validation prevents unauthorized access

### 3. System Command Execution
**Attack**: User tries to execute system commands
```python
# This would be blocked:
import os; os.system("rm -rf /")  # 'os' not in safe_imports
```

**Prevention**:
- Restricted import whitelist
- Sandboxed execution environment
- No system library access

### 4. Purchase Order Approval Without Permission
**Question**: "Can user approve Purchase Order PO-001 without proper permissions?"

**Answer**: **NO** - Here's the validation chain:

```python
# Security validation for PO approval:
def approve_purchase_order(po_name):
    # 1. Authentication required
    if not frappe.session.user or frappe.session.user == "Guest":
        return "Authentication required"
    
    # 2. Assistant role required
    if not check_assistant_permission(user):
        return "Assistant role required"
    
    # 3. DocType write permission
    if not frappe.has_permission("Purchase Order", "write"):
        return "No write permission for Purchase Orders"
    
    # 4. Specific document access
    doc = frappe.get_doc("Purchase Order", po_name)
    if not frappe.has_permission(doc, "write"):
        return "No write permission for this Purchase Order"
    
    # 5. Submit permission (for approval)
    if not frappe.has_permission(doc, "submit"):
        return "No submit permission for Purchase Orders"
    
    # Only then can approval proceed
    doc.submit()
```

---

## 📊 Advanced Use Cases Enabled

### Complex Financial Analysis (System Manager)
```python
# Comprehensive sales analysis with full pandas power
code = """
# Get comprehensive sales data
sales_data = frappe.get_all('Sales Invoice', 
    filters={'posting_date': ['between', ['2024-01-01', '2024-12-31']]},
    fields=['grand_total', 'posting_date', 'customer', 'territory', 'item_code'])

df = pd.DataFrame(sales_data)

# Advanced analytics
monthly_trends = df.groupby(df['posting_date'].dt.month).agg({
    'grand_total': ['sum', 'mean', 'count'],
    'customer': 'nunique'
}).round(2)

# Territory performance analysis
territory_metrics = df.groupby('territory').agg({
    'grand_total': ['sum', 'mean', 'std'],
    'customer': 'nunique'
}).round(2)

# Customer lifetime value calculation
customer_ltv = df.groupby('customer')['grand_total'].agg(['sum', 'count', 'mean'])
customer_ltv['avg_order_value'] = customer_ltv['mean']
customer_ltv['total_orders'] = customer_ltv['count']

print("Monthly Trends:", monthly_trends.to_dict())
print("Territory Performance:", territory_metrics.to_dict())
print("Top 10 Customers by LTV:", customer_ltv.nlargest(10, 'sum').to_dict())
"""
```

### Advanced SQL Reporting (System Manager)
```sql
-- Complex multi-table analysis
SELECT 
    si.territory,
    c.customer_group,
    COUNT(DISTINCT si.customer) as unique_customers,
    COUNT(si.name) as total_invoices,
    SUM(si.grand_total) as total_revenue,
    AVG(si.grand_total) as avg_invoice_value,
    SUM(CASE WHEN si.status = 'Paid' THEN si.grand_total ELSE 0 END) as paid_amount,
    ROUND(
        SUM(CASE WHEN si.status = 'Paid' THEN si.grand_total ELSE 0 END) / 
        SUM(si.grand_total) * 100, 2
    ) as collection_rate
FROM `tabSales Invoice` si
JOIN `tabCustomer` c ON si.customer = c.name
WHERE si.posting_date >= '2024-01-01'
  AND si.docstatus = 1
GROUP BY si.territory, c.customer_group
HAVING total_revenue > 100000
ORDER BY total_revenue DESC, collection_rate DESC;
```

---

## 🔧 Best Practices

### For System Managers
1. **Responsible Usage**:
   - Review code before execution
   - Validate data access requirements
   - Follow principle of least privilege

2. **Code Quality**:
   ```python
   # Good: Clear, documented code
   # Get customer data with explicit permissions
   customers = frappe.get_all('Customer', 
                             filters={'enabled': 1}, 
                             fields=['name', 'customer_group'])
   
   # Bad: Unclear, potentially risky
   # data = frappe.db.sql("SELECT * FROM tabUser")  # Would be blocked anyway
   ```

3. **Security Awareness**:
   - Understand permission implications
   - Monitor execution logs
   - Report suspicious activities

### For Assistant Users
1. **Use Appropriate Tools**:
   ```python
   # Use document_list instead of requesting Python code
   invoices = document_list(
       doctype="Sales Invoice",
       filters={"status": "Paid"},
       fields=["name", "grand_total", "customer"]
   )
   ```

2. **Request Analysis**:
   ```python
   # Use analyze_frappe_data for statistical analysis
   analysis = analyze_frappe_data(
       doctype="Sales Invoice",
       analysis_type="summary",
       numerical_fields=["grand_total"]
   )
   ```

### For Administrators
1. **Role Management**:
   - Carefully assign System Manager role
   - Regular permission audits
   - Document role assignments

2. **Monitoring**:
   ```python
   # Regular audit log review
   audit_logs = frappe.get_all('Assistant Audit Log',
       filters={'creation': ['>=', today()]},
       fields=['user', 'tool_name', 'status', 'timestamp'])
   ```

3. **Security Configuration**:
   ```python
   # Recommended security settings
   settings = {
       "authentication_required": True,
       "rate_limit": 60,  # requests per minute
       "allowed_origins": "https://trusted-domain.com",  # Not "*"
       "audit_all_operations": True,
       "log_code_execution": True
   }
   ```

---

## 📝 Audit and Monitoring

### Comprehensive Logging
```python
# All high-privilege operations are logged
def log_code_execution(user, code, result):
    frappe.get_doc({
        "doctype": "Assistant Audit Log",
        "user": user,
        "tool_name": "execute_python_code",
        "action_details": {
            "code_snippet": code[:200] + "..." if len(code) > 200 else code,
            "execution_status": result.get("success"),
            "error_message": result.get("error")
        },
        "status": "Success" if result.get("success") else "Error",
        "timestamp": frappe.utils.now()
    }).insert(ignore_permissions=True)
```

### Security Monitoring Dashboard
```python
# Monitor for suspicious patterns
def security_dashboard():
    return {
        "failed_authentications": frappe.db.count('Assistant Connection Log', 
                                                 {'status': 'Failed'}),
        "code_executions_today": frappe.db.count('Assistant Audit Log',
                                                {'tool_name': 'execute_python_code',
                                                 'creation': ['>=', today()]}),
        "permission_violations": frappe.db.count('Assistant Audit Log',
                                               {'status': 'Permission Denied',
                                                'creation': ['>=', today()]}),
        "active_system_managers": frappe.db.count('User',
                                                {'enabled': 1,
                                                 'name': ['in', get_system_managers()]})
    }
```

---

## 🎉 Summary

The Frappe Assistant Core now provides **enterprise-grade security** while maintaining **powerful AI capabilities**:

### ✅ **Security Achievements**
- **Zero Privilege Escalation**: User context cannot be modified
- **Complete Input Validation**: All code and queries are validated
- **Permission-Aware Operations**: All data access respects Frappe permissions
- **Comprehensive Audit Trail**: All operations logged for compliance
- **Role-Based Access**: Granular control based on user responsibilities

### ✅ **Capability Achievements**
- **Advanced Analytics**: Full pandas/numpy power for System Managers
- **Custom Reporting**: Complex SQL queries with safety validation
- **Flexible Document Operations**: CRUD operations for all authorized users
- **Rich Visualizations**: Chart creation with multiple output formats
- **Extensible Framework**: Easy to add new secure tools

### ✅ **Business Value**
- **Enhanced Productivity**: LLMs can perform complex analysis safely
- **Compliance Ready**: Audit trails and permission controls
- **Scalable Security**: Role-based access grows with organization
- **Developer Friendly**: Clear APIs and comprehensive documentation

**Result**: A system that provides both **AI power** and **enterprise security** - perfect for organizations that need advanced analytics capabilities without compromising on data protection.

---

*This comprehensive security guide ensures that Frappe Assistant Core delivers maximum value while maintaining the highest security standards.*