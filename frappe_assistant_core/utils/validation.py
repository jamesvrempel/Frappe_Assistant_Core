import frappe
from frappe import _

def validate_document(doctype, data):
    """Validate the document data against the DocType schema."""
    if not doctype or not data:
        raise ValueError(_("Doctype and data must be provided for validation."))

    # Fetch the DocType schema
    schema = frappe.get_meta(doctype)
    
    for field in schema.fields:
        fieldname = field.fieldname
        if fieldname not in data:
            if field.required:
                raise ValueError(_("{fieldname} is required.").format(fieldname=field.label))
            continue
        
        value = data[fieldname]
        if field.fieldtype == "Int" and not isinstance(value, int):
            raise ValueError(_("{fieldname} must be an integer.").format(fieldname=field.label))
        elif field.fieldtype == "Float" and not isinstance(value, (int, float)):
            raise ValueError(_("{fieldname} must be a float.").format(fieldname=field.label))
        elif field.fieldtype == "Data" and not isinstance(value, str):
            raise ValueError(_("{fieldname} must be a string.").format(fieldname=field.label))
        elif field.fieldtype == "Select" and value not in field.options.split("\n"):
            raise ValueError(_("{fieldname} must be one of: {options}.").format(fieldname=field.label, options=field.options))
        # Add more field type validations as necessary

def validate_tool_input(tool_name, input_data):
    """Validate input data for a specific assistant tool."""
    # Implement tool-specific validation logic here
    pass

def validate_rate_limit(request_count, rate_limit):
    """Validate if the request count exceeds the rate limit."""
    if request_count > rate_limit:
        raise ValueError(_("Rate limit exceeded. Maximum allowed: {rate_limit}").format(rate_limit=rate_limit))