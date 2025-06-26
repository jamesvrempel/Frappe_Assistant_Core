import frappe
import json
from frappe import _
from frappe.utils import now

def log_document_change(doc, method):
    """Log document changes for audit trail"""
    if should_log_document(doc.doctype):
        try:
            frappe.get_doc({
                "doctype": "assistant Audit Log",
                "action": "update_document",
                "user": frappe.session.user,
                "status": "Success",
                "timestamp": now(),
                "target_doctype": doc.doctype,
                "target_name": doc.name,
                "ip_address": frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None
            }).insert(ignore_permissions=True)
        except Exception:
            pass  # Ignore audit logging errors

def log_document_submit(doc, method):
    """Log document submissions"""
    if should_log_document(doc.doctype):
        try:
            frappe.get_doc({
                "doctype": "assistant Audit Log",
                "action": "submit_document",
                "user": frappe.session.user,
                "status": "Success",
                "timestamp": now(),
                "target_doctype": doc.doctype,
                "target_name": doc.name,
                "ip_address": frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None
            }).insert(ignore_permissions=True)
        except Exception:
            pass

def log_document_cancel(doc, method):
    """Log document cancellations"""
    if should_log_document(doc.doctype):
        try:
            frappe.get_doc({
                "doctype": "assistant Audit Log",
                "action": "cancel_document",
                "user": frappe.session.user,
                "status": "Success",
                "timestamp": now(),
                "target_doctype": doc.doctype,
                "target_name": doc.name,
                "ip_address": frappe.local.request_ip if hasattr(frappe.local, 'request_ip') else None
            }).insert(ignore_permissions=True)
        except Exception:
            pass

def should_log_document(doctype):
    """Check if document type should be logged"""
    # Don't log assistant internal documents to avoid recursion
    if doctype.startswith("assistant "):
        return False
    
    # try:
    #     # Get audit settings using the correct method
    #     audit_doctypes = frappe.db.get_single_value("assistant Server Settings", "audit_doctypes") or ""
        
    #     if audit_doctypes:
    #         return doctype in audit_doctypes.split(",")
    # except Exception:
    #     # If assistant Server Settings doesn't exist or has issues, don't log
    #     pass
    
    # By default, don't audit everything to avoid performance impact
    return False