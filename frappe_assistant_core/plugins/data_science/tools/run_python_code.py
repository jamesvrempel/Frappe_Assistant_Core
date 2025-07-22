# -*- coding: utf-8 -*-
# Frappe Assistant Core - AI Assistant integration for Frappe Framework
# Copyright (C) 2025 Paul Clinton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Python Code Execution Tool for Data Science Plugin.
Executes Python code safely in a restricted environment.
"""

import frappe
from frappe import _
import sys
import io
import traceback
from typing import Dict, Any
from contextlib import redirect_stdout, redirect_stderr
from frappe_assistant_core.core.base_tool import BaseTool


class ExecutePythonCode(BaseTool):
    """
    Tool for executing Python code with data science libraries.
    
    Provides safe execution of Python code with access to:
    - pandas, numpy, matplotlib, seaborn, plotly
    - Frappe data access
    - Result capture and display
    """
    
    def __init__(self):
        super().__init__()
        self.name = "run_python_code"
        self.description = self._get_dynamic_description()
        self.requires_permission = None  # Available to all users
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                },
                "data_query": {
                    "type": "object",
                    "description": "Query to fetch data and make it available as 'data' variable",
                    "properties": {
                        "doctype": {"type": "string"},
                        "fields": {"type": "array", "items": {"type": "string"}},
                        "filters": {"type": "object"},
                        "limit": {"type": "integer", "default": 100}
                    }
                },
                "timeout": {
                    "type": "integer",
                    "description": "Execution timeout in seconds (default: 30)",
                    "default": 30,
                    "minimum": 1,
                    "maximum": 300
                },
                "capture_output": {
                    "type": "boolean",
                    "description": "Whether to capture print output (default: true)",
                    "default": True
                },
                "return_variables": {
                    "type": "array",
                    "description": "Variable names to return values for",
                    "items": {"type": "string"}
                }
            },
            "required": ["code"]
        }
    
    def _get_dynamic_description(self) -> str:
        """Generate description based on current streaming settings"""
        base_description = """Execute Python code safely with data science libraries (pandas, numpy, matplotlib, seaborn) and Frappe API access. Pre-loaded libraries ready to use without imports. Requires System Manager role."""
        
        try:
            from frappe_assistant_core.utils.streaming_manager import get_streaming_manager
            streaming_manager = get_streaming_manager()
            streaming_suffix = streaming_manager.get_tool_description_suffix(self.name)
            return base_description + streaming_suffix
            
        except Exception as e:
            frappe.logger("execute_python_code").warning(f"Failed to load streaming configuration: {str(e)}")
            return base_description
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Python code safely"""
        code = arguments.get("code", "")
        data_query = arguments.get("data_query")
        timeout = arguments.get("timeout", 30)
        capture_output = arguments.get("capture_output", True)
        return_variables = arguments.get("return_variables", [])
        
        # Check permissions - requires System Manager role
        user_roles = frappe.get_roles()
        if "System Manager" not in user_roles:
            return {
                "success": False,
                "error": "Insufficient permissions. System Manager role required for code execution",
                "output": "",
                "variables": {}
            }
        
        if not code.strip():
            return {
                "success": False,
                "error": "No code provided",
                "output": "",
                "variables": {}
            }
        
        # Setup execution environment
        execution_globals = self._setup_execution_environment()
        
        # Handle data query if provided
        if data_query:
            try:
                data = self._fetch_data_from_query(data_query)
                execution_globals['data'] = data
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error fetching data: {str(e)}",
                    "output": "",
                    "variables": {}
                }
        
        # Remove dangerous imports for security
        code = self._remove_dangerous_imports(code)
        
        # Capture output
        output = ""
        error = ""
        variables = {}
        
        try:
            if capture_output:
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    # Execute code
                    exec(code, execution_globals)
                
                output = stdout_capture.getvalue()
                error = stderr_capture.getvalue()
            else:
                # Execute without capturing output
                exec(code, execution_globals)
            
            # Extract all user-defined variables (not built-ins)
            for var_name, var_value in execution_globals.items():
                if not var_name.startswith('_') and var_name not in ['frappe', 'pd', 'np', 'plt', 'sns', 'data']:
                    try:
                        # Try to serialize the variable
                        variables[var_name] = self._serialize_variable(var_value)
                    except Exception as e:
                        variables[var_name] = f"<Could not serialize: {str(e)}>"
            
            # Also extract specifically requested variables
            if return_variables:
                for var_name in return_variables:
                    if var_name in execution_globals and var_name not in variables:
                        try:
                            var_value = execution_globals[var_name]
                            variables[var_name] = self._serialize_variable(var_value)
                        except Exception as e:
                            variables[var_name] = f"<Could not serialize: {str(e)}>"
            
            return {
                "success": True,
                "output": output,
                "error": error,
                "variables": variables,
                "execution_info": {
                    "lines_executed": len(code.split('\n')),
                    "variables_returned": len(variables)
                }
            }
            
        except Exception as e:
            error_msg = str(e)
            error_traceback = traceback.format_exc()
            
            self.logger.error(f"Python execution error: {error_msg}")
            
            return {
                "success": False,
                "error": error_msg,
                "traceback": error_traceback,
                "output": output,
                "variables": {}
            }
    
    def _remove_dangerous_imports(self, code: str) -> str:
        """Remove dangerous import statements for security, but allow safe ones"""
        import re
        
        # Define safe modules that are allowed
        safe_modules = {
            'math', 'statistics', 'decimal', 'fractions', 'datetime', 'json', 're', 'random',
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'scipy',
            'pd', 'np', 'plt', 'sns', 'go', 'px', 'stats'
        }
        
        # Define dangerous modules to block
        dangerous_modules = {
            'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests', 'http',
            'ftplib', 'smtplib', 'imaplib', 'poplib', 'telnetlib', 'socketserver',
            'threading', 'multiprocessing', 'asyncio', 'concurrent',
            'ctypes', 'imp', 'importlib', '__import__', 'exec', 'eval',
            'file', 'open', 'input', 'raw_input'
        }
        
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped_line = line.strip()
            
            # Check for import statements
            if stripped_line.startswith('import ') or stripped_line.startswith('from '):
                # Extract module name
                if stripped_line.startswith('import '):
                    module = stripped_line[7:].split()[0].split('.')[0]
                elif stripped_line.startswith('from '):
                    module = stripped_line[5:].split()[0].split('.')[0]
                else:
                    module = ""
                
                # Allow safe modules, block dangerous ones
                if module in safe_modules:
                    cleaned_lines.append(line)  # Keep safe imports
                elif module in dangerous_modules:
                    continue  # Remove dangerous imports
                else:
                    # For unknown modules, be conservative and remove them
                    continue
            else:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _fetch_data_from_query(self, data_query: Dict[str, Any]) -> list:
        """Fetch data from Frappe based on query parameters"""
        doctype = data_query.get('doctype')
        fields = data_query.get('fields', ['name'])
        filters = data_query.get('filters', {})
        limit = data_query.get('limit', 100)
        
        if not doctype:
            raise ValueError("DocType is required for data query")
        
        # Check permission
        if not frappe.has_permission(doctype, "read"):
            raise frappe.PermissionError(f"No permission to read {doctype}")
        
        # Use raw SQL to avoid frappe._dict objects that cause __array_struct__ issues
        try:
            # Build SQL query manually to get clean data
            field_list = ", ".join([f"`{field}`" for field in fields])
            table_name = f"tab{doctype}"
            
            # Build WHERE clause from filters
            where_conditions = []
            values = []
            
            for key, value in filters.items():
                if isinstance(value, (list, tuple)):
                    placeholders = ", ".join(["%s"] * len(value))
                    where_conditions.append(f"`{key}` IN ({placeholders})")
                    values.extend(value)
                elif value is None:
                    where_conditions.append(f"`{key}` IS NULL")
                else:
                    where_conditions.append(f"`{key}` = %s")
                    values.append(value)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            query = f"""
                SELECT {field_list}
                FROM `{table_name}`
                {where_clause}
                ORDER BY creation DESC
                LIMIT {limit}
            """
            
            # Execute raw SQL to get clean data without frappe._dict objects
            result = frappe.db.sql(query, values, as_dict=True)
            
            # Convert to plain Python dicts to avoid array interface issues
            return [dict(row) for row in result]
            
        except Exception as e:
            # Fallback to get_all with conversion if SQL approach fails
            frappe.log_error(f"SQL data query failed: {str(e)}")
            
            raw_data = frappe.get_all(
                doctype,
                fields=fields,
                filters=filters,
                limit=limit
            )
            
            # Convert frappe._dict objects to plain dicts
            return [dict(row) for row in raw_data]
    
    def _setup_execution_environment(self) -> Dict[str, Any]:
        """Setup safe execution environment with data science libraries"""
        # Base environment
        env = {
            '__builtins__': {
                # Safe built-ins
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'sorted': sorted,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'print': print,
                'type': type,
                'isinstance': isinstance,
                'hasattr': hasattr,
                'getattr': getattr,
                'setattr': setattr,
                'Exception': Exception,
                'ValueError': ValueError,
                'TypeError': TypeError,
                'KeyError': KeyError,
                'IndexError': IndexError,
                'AttributeError': AttributeError,
                'NameError': NameError,
                'ZeroDivisionError': ZeroDivisionError,
            }
        }
        
        # Add standard libraries first
        import math
        import statistics
        import decimal
        import fractions
        import datetime
        import json
        import re
        import random
        
        env.update({
            'math': math,
            'statistics': statistics,
            'decimal': decimal,
            'fractions': fractions,
            'datetime': datetime,
            'json': json,
            're': re,
            'random': random
        })
        
        # Add data science libraries
        try:
            import pandas as pd
            import numpy as np
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            env.update({
                'pd': pd,
                'pandas': pd,
                'np': np,
                'numpy': np,
                'plt': plt,
                'matplotlib': plt,
                'sns': sns,
                'seaborn': sns
            })
            
            # Try to add plotly if available
            try:
                import plotly.graph_objects as go
                import plotly.express as px
                env.update({
                    'go': go,
                    'px': px,
                    'plotly': {'graph_objects': go, 'express': px}
                })
            except ImportError:
                pass
            
            # Add scipy if available
            try:
                import scipy
                import scipy.stats as stats
                env.update({
                    'scipy': scipy,
                    'stats': stats
                })
            except ImportError:
                pass
                
        except ImportError as e:
            self.logger.warning(f"Some data science libraries not available: {str(e)}")
        
        # Add Frappe utilities
        env.update({
            'frappe': frappe,
            'get_doc': frappe.get_doc,
            'get_list': frappe.get_list,
            'get_all': frappe.get_all,
            'db': frappe.db,
            'get_single': frappe.get_single,
        })
        
        return env
    
    def _serialize_variable(self, value: Any) -> Any:
        """Serialize a variable for JSON return"""
        try:
            # Handle pandas objects
            if hasattr(value, 'to_dict'):
                return value.to_dict()
            elif hasattr(value, 'to_list'):
                return value.to_list()
            elif hasattr(value, 'tolist'):
                return value.tolist()
            
            # Handle numpy arrays
            import numpy as np
            if isinstance(value, np.ndarray):
                return value.tolist()
            
            # Handle basic types
            if isinstance(value, (str, int, float, bool, list, dict, tuple)):
                return value
            
            # Try to convert to string
            return str(value)
            
        except Exception:
            return f"<{type(value).__name__} object>"
    


# Make sure class is available for discovery
# The plugin manager will find ExecutePythonCode automatically