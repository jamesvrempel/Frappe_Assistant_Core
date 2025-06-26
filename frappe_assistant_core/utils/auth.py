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