from typing import Dict, Any

def build_response(success: bool, message: str = "", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Build a standardized response format for assistant API."""
    response = {
        "success": success,
        "message": message,
        "data": data or {}
    }
    return response

def handle_error(error_message: str, error_code: int = 400) -> Dict[str, Any]:
    """Build an error response format for assistant API."""
    return {
        "success": False,
        "error": {
            "message": error_message,
            "code": error_code
        }
    }