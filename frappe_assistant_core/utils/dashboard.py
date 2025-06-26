import frappe
from frappe import _
from frappe.utils import today

# Constants
DEFAULT_PORT = 8000  # Frappe's default port fallback

def get_frappe_port():
    """Get Frappe's actual running port from configuration"""
    import os
    import json
    
    try:
        # Method 1: Try to get from Frappe configuration
        if hasattr(frappe, 'conf') and hasattr(frappe.conf, 'webserver_port'):
            return int(frappe.conf.webserver_port)
        
        # Method 2: Try to find common_site_config.json by traversing up
        current_dir = os.getcwd()
        search_dir = current_dir
        
        # Walk up the directory tree to find the bench root (contains sites folder)
        for _ in range(10):  # Limit iterations
            sites_path = os.path.join(search_dir, 'sites')
            config_file = os.path.join(sites_path, 'common_site_config.json')
            
            if os.path.exists(sites_path) and os.path.isdir(sites_path):
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        common_config = json.load(f)
                        if 'webserver_port' in common_config:
                            return int(common_config['webserver_port'])
                break  # Found sites directory, stop searching
            
            parent_dir = os.path.dirname(search_dir)
            if parent_dir == search_dir:  # Reached root
                break
            search_dir = parent_dir
        
        # Method 3: Try to get from environment
        if 'FRAPPE_SITE_PORT' in os.environ:
            return int(os.environ['FRAPPE_SITE_PORT'])
        
        # Fallback to default
        return DEFAULT_PORT
        
    except Exception:
        return DEFAULT_PORT

@frappe.whitelist()
def get_assistant_dashboard_data():
    """Get comprehensive assistant dashboard data"""
    try:
        # Server status
        settings = frappe.get_single("assistant Server Settings")
        
        # Connection statistics
        active_connections = frappe.db.count("assistant Connection Log", 
                                             filters={"status": "Connected"})
        
        total_connections_today = frappe.db.count("assistant Connection Log", 
                                                 filters={"creation": [">=", today()]})
        
        # Tool statistics
        enabled_tools = frappe.db.count("assistant Tool Registry", 
                                       filters={"enabled": 1})
        
        total_tools = frappe.db.count("assistant Tool Registry")
        
        # Audit statistics
        total_actions_today = frappe.db.count("assistant Audit Log", 
                                             filters={"creation": [">=", today()]})
        
        successful_actions_today = frappe.db.count("assistant Audit Log", 
                                                  filters={
                                                      "creation": [">=", today()],
                                                      "status": "Success"
                                                  })
        
        success_rate = (successful_actions_today / total_actions_today * 100) if total_actions_today > 0 else 0
        
        # Most used tools today
        most_used_tools = frappe.db.sql("""
            SELECT tool_name, COUNT(*) as count
            FROM `tabassistant Audit Log`
            WHERE DATE(creation) = %s AND tool_name IS NOT NULL
            GROUP BY tool_name
            ORDER BY count DESC
            LIMIT 5
        """, (today(),), as_dict=True)
        
        # Recent errors
        recent_errors = frappe.get_all(
            "assistant Audit Log",
            filters={
                "status": ["in", ["Error", "Timeout", "Permission Denied"]],
                "creation": [">=", today()]
            },
            fields=["tool_name", "user", "error_message", "timestamp"],
            order_by="timestamp desc",
            limit=5
        )
        
        # Average execution times by tool category
        category_performance = frappe.db.sql("""
            SELECT tr.category, AVG(al.execution_time) as avg_time, COUNT(*) as count
            FROM `tabassistant Audit Log` al
            JOIN `tabassistant Tool Registry` tr ON al.tool_name = tr.name
            WHERE DATE(al.creation) = %s AND al.execution_time IS NOT NULL
            GROUP BY tr.category
            ORDER BY avg_time DESC
        """, (today(),), as_dict=True)
        
        return {
            "server_info": {
                "enabled": settings.server_enabled,
                "port": get_frappe_port(),
                "max_connections": settings.max_connections,
                "rate_limit": settings.rate_limit
            },
            "connections": {
                "active": active_connections,
                "today_total": total_connections_today
            },
            "tools": {
                "enabled": enabled_tools,
                "total": total_tools,
                "most_used": most_used_tools
            },
            "performance": {
                "actions_today": total_actions_today,
                "success_rate": round(success_rate, 2),
                "category_performance": category_performance
            },
            "issues": {
                "recent_errors": recent_errors
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Dashboard data error: {str(e)}", "assistant Dashboard")
        return {"error": str(e)}

@frappe.whitelist()
def get_system_health_check():
    """Perform comprehensive system health check"""
    health_status = {
        "overall_status": "healthy",
        "checks": [],
        "warnings": [],
        "errors": []
    }
    
    try:
        # Check 1: DocTypes exist and are properly configured
        required_doctypes = [
            "assistant Server Settings",
            "assistant Tool Registry", 
            "assistant Connection Log",
            "assistant Audit Log"
        ]
        
        for doctype in required_doctypes:
            if not frappe.db.table_exists(f"tab{doctype}"):
                health_status["errors"].append(f"DocType '{doctype}' table does not exist")
                health_status["overall_status"] = "critical"
            else:
                health_status["checks"].append(f"DocType '{doctype}' exists")
        
        # Check 2: Server settings are configured
        try:
            settings = frappe.get_single("assistant Server Settings")
            if not settings:
                health_status["warnings"].append("assistant Server Settings not found")
            else:
                health_status["checks"].append("assistant Server Settings configured")
                
                # Port configuration no longer needed (uses Frappe's default port)
                health_status["checks"].append("Using Frappe's default port (8000)")
                    
        except Exception as e:
            health_status["errors"].append(f"Cannot access assistant Server Settings: {str(e)}")
            health_status["overall_status"] = "critical"
        
        # Check 3: Tools are registered
        tool_count = frappe.db.count("assistant Tool Registry")
        if tool_count == 0:
            health_status["warnings"].append("No tools registered in assistant Tool Registry")
        else:
            enabled_tools = frappe.db.count("assistant Tool Registry", filters={"enabled": 1})
            health_status["checks"].append(f"{enabled_tools} of {tool_count} tools enabled")
        
        # Check 4: Recent connection issues
        recent_errors = frappe.db.count("assistant Connection Log", 
                                       filters={
                                           "status": "Error",
                                           "creation": [">=", today()]
                                       })
        
        if recent_errors > 10:
            health_status["warnings"].append(f"High number of connection errors today: {recent_errors}")
        elif recent_errors > 0:
            health_status["checks"].append(f"Minor connection issues: {recent_errors} errors today")
        else:
            health_status["checks"].append("No connection errors today")
        
        # Check 5: Tool execution health
        failed_executions = frappe.db.count("assistant Audit Log",
                                           filters={
                                               "status": ["in", ["Error", "Timeout"]],
                                               "creation": [">=", today()]
                                           })
        
        total_executions = frappe.db.count("assistant Audit Log",
                                          filters={"creation": [">=", today()]})
        
        if total_executions > 0:
            failure_rate = (failed_executions / total_executions) * 100
            if failure_rate > 20:
                health_status["warnings"].append(f"High tool failure rate: {failure_rate:.1f}%")
                health_status["overall_status"] = "warning" if health_status["overall_status"] == "healthy" else health_status["overall_status"]
            else:
                health_status["checks"].append(f"Tool execution health good: {failure_rate:.1f}% failure rate")
        
        # Set overall status based on findings
        if health_status["errors"]:
            health_status["overall_status"] = "critical"
        elif health_status["warnings"] and health_status["overall_status"] == "healthy":
            health_status["overall_status"] = "warning"
            
        return health_status
        
    except Exception as e:
        return {
            "overall_status": "critical",
            "error": f"Health check failed: {str(e)}",
            "checks": [],
            "warnings": [],
            "errors": [f"System health check error: {str(e)}"]
        }

@frappe.whitelist()
def cleanup_old_data():
    """Clean up old logs and data based on settings"""
    try:
        settings = frappe.get_single("assistant Server Settings")
        cleanup_days = settings.cleanup_logs_after_days or 30
        
        # Clean connection logs
        old_connection_logs = frappe.db.sql("""
            DELETE FROM `tabassistant Connection Log`
            WHERE creation < DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (cleanup_days,))
        
        # Clean audit logs (keep longer for compliance)
        audit_cleanup_days = cleanup_days * 2
        old_audit_logs = frappe.db.sql("""
            DELETE FROM `tabassistant Audit Log`
            WHERE creation < DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (audit_cleanup_days,))
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": f"Cleaned up logs older than {cleanup_days} days",
            "connection_logs_deleted": old_connection_logs,
            "audit_logs_deleted": old_audit_logs
        }
        
    except Exception as e:
        frappe.log_error(f"Cleanup error: {str(e)}", "assistant Cleanup")
        return {
            "success": False,
            "error": str(e)
        }