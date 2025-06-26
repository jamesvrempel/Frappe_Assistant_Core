

import frappe
from frappe.model.document import Document
from frappe.utils import now, time_diff_in_seconds
from frappe import _

class AssistantConnectionLog(Document):
    """assistant Connection Log DocType controller"""
    
    def before_insert(self):
        """Set default values before inserting"""
        if not self.connected_at:
            self.connected_at = now()
        if not self.last_activity:
            self.last_activity = now()
    
    def calculate_duration(self):
        """Calculate connection duration"""
        if self.connected_at and self.disconnected_at:
            duration_seconds = time_diff_in_seconds(self.disconnected_at, self.connected_at)
            self.duration = duration_seconds
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.db_set("last_activity", now())
    
    def increment_request_count(self):
        """Increment request count"""
        self.db_set("request_count", self.request_count + 1)
        self.update_activity()
    
    def increment_error_count(self):
        """Increment error count"""
        self.db_set("error_count", self.error_count + 1)
        self.update_activity()
    
    def close_connection(self, error_message=None):
        """Close the connection and calculate duration"""
        self.db_set("disconnected_at", now())
        self.db_set("status", "Error" if error_message else "Disconnected")
        
        if error_message:
            self.db_set("error_message", error_message)
        
        # Calculate and set duration
        if self.connected_at:
            duration_seconds = time_diff_in_seconds(now(), self.connected_at)
            self.db_set("duration", duration_seconds)

@frappe.whitelist()
def get_connection_stats():
    """Get connection statistics for dashboard"""
    active_connections = frappe.db.count("assistant Connection Log", 
                                         filters={"status": "Connected"})
    
    total_connections_today = frappe.db.count("assistant Connection Log", 
                                             filters={"creation": [">=", frappe.utils.today()]})
    
    avg_duration = frappe.db.sql("""
        SELECT AVG(duration) as avg_duration 
        FROM `tabassistant Connection Log` 
        WHERE status = 'Disconnected' 
        AND duration IS NOT NULL
    """)[0][0] or 0
    
    return {
        "active_connections": active_connections,
        "total_connections_today": total_connections_today,
        "average_duration": round(avg_duration, 2) if avg_duration else 0
    }

def get_context(context):
    context.title = _("assistant Connection Log")
    context.docs = get_logs()

def get_logs():
    return frappe.get_all("assistant Connection Log", fields=["*"], order_by="creation desc")