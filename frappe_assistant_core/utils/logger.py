"""
Centralized logging configuration for Frappe Assistant Core
Provides consistent logging across all modules
"""

import logging
import frappe
from typing import Optional

class AssistantLogger:
    """Centralized logger for Frappe Assistant Core"""
    
    def __init__(self, name: str = "frappe_assistant_core"):
        self.name = name
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger with appropriate configuration"""
        logger = logging.getLogger(self.name)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
            
        # Set level based on environment
        logger.setLevel(logging.DEBUG if frappe.conf.get('developer_mode') else logging.INFO)
        
        # Create console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(message, *args, **kwargs)
        # Also log to Frappe's error log for visibility
        try:
            frappe.log_error(message, self.name)
        except:
            pass  # Don't fail if Frappe logging fails
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        self.logger.critical(message, *args, **kwargs)
        try:
            frappe.log_error(f"CRITICAL: {message}", self.name)
        except:
            pass

# Global logger instances
logger = AssistantLogger("frappe_assistant_core")
api_logger = AssistantLogger("frappe_assistant_core.api")
tools_logger = AssistantLogger("frappe_assistant_core.tools")
server_logger = AssistantLogger("frappe_assistant_core.server")

def get_logger(name: str) -> AssistantLogger:
    """Get a logger for a specific module"""
    return AssistantLogger(f"frappe_assistant_core.{name}")