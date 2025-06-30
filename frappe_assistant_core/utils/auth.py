import frappe
from frappe import _

def get_user_roles(user):
    """Fetch the roles assigned to a user."""
    return frappe.get_roles(user)

def has_permission(doctype, permission_type, user=None):
    """Check if the user has the specified permission for the given DocType."""
    if user is None:
        user = frappe.session.user
    return frappe.has_permission(doctype, permission_type, user=user)

def validate_api_key(api_key):
    """Validate the provided API key."""
    if not api_key or not frappe.db.exists("API Key", api_key):
        raise frappe.PermissionError(_("Invalid API Key"))

def validate_api_secret(api_secret):
    """Validate the provided API secret."""
    if not api_secret or not frappe.db.exists("API Secret", api_secret):
        raise frappe.PermissionError(_("Invalid API Secret"))

def check_authentication(api_key, api_secret):
    """Check if the provided API key and secret are valid."""
    validate_api_key(api_key)
    validate_api_secret(api_secret)

def is_authenticated(user):
    """Check if the user is authenticated."""
    return user != "Guest" and frappe.session.user != "Guest"

def validate_api_credentials(api_key, api_secret):
    """
    Validate API credentials and return the authenticated user
    Returns user name if valid, None if invalid
    """
    try:
        # Custom validation using database lookup and password verification
        user_data = frappe.db.get_value("User", 
            {"api_key": api_key, "enabled": 1}, 
            ["name", "api_secret"]
        )
        
        if user_data:
            user, stored_secret = user_data
            # Compare the provided secret with stored secret
            from frappe.utils.password import get_decrypted_password
            decrypted_secret = get_decrypted_password("User", user, "api_secret")
            
            if api_secret == decrypted_secret:
                return user
                
        return None
    except Exception:
        return None