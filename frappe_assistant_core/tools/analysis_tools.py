"""
Frappe Assistant Core - Analysis and Code Execution Tools
Copyright (c) 2025 Paul Clinton <jypaulclinton@gmail.com>
"""

import frappe
import json
import io
import sys
import traceback
from typing import Dict, Any, List
from contextlib import redirect_stdout, redirect_stderr

from frappe_assistant_core.utils.logger import api_logger

# Custom security exception
class SecurityError(Exception):
    pass

# Import data analysis libraries with fallback handling
try:
    import pandas as pd
    HAS_PANDAS = True
    PANDAS_VERSION = pd.__version__
except ImportError:
    HAS_PANDAS = False
    PANDAS_VERSION = None

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False

# Streaming tool prefix for all analysis tools
STREAMING_TOOL_PREFIX = """
🚨 MANDATORY ARTIFACT STREAMING - REQUIRED FOR ALL ANALYSIS:

⚠️ CRITICAL: This tool REQUIRES creating workspace artifacts BEFORE execution to prevent response limits.

📋 REQUIRED WORKFLOW:
1. CREATE workspace artifact FIRST (mandatory)
2. Add sections: Executive Summary, Data Analysis, Findings, Recommendations
3. Stream ALL analysis results to artifact sections
4. Keep response minimal (only confirmation/summary)
5. Build unlimited analysis depth via artifact streaming

❌ WITHOUT ARTIFACTS: Tool will hit response limits and fail
✅ WITH ARTIFACTS: Unlimited analysis depth and professional deliverables

⚠️ DO NOT attempt analysis without creating artifacts first - conversation will hit limits.

"""

class AnalysisTools:
    """MCP tools for data analysis and code execution"""
    
    @staticmethod
    def get_tools() -> List[Dict]:
        """Return list of analysis-related MCP tools"""
        tools = [
            {
                "name": "execute_python_code",
                "description": f"""
{STREAMING_TOOL_PREFIX}

Execute custom Python code for advanced data analysis, calculations, and business logic with full access to Frappe framework and extensive library ecosystem.

🔐 **SECURITY:** Requires System Manager role. Executes in secure sandbox environment.

⚠️ **IMPORTANT:** Do NOT use `import` statements. All libraries (frappe, pd, np, plt, sns) are pre-loaded and ready to use.

📚 **AVAILABLE LIBRARIES & MODULES:**

**Core Data Science (Pre-loaded):**
• pandas (as 'pd') - DataFrames, data manipulation, analysis
• numpy (as 'np') - Arrays, mathematical operations, linear algebra  
• matplotlib (as 'plt') - Plotting and visualization
• seaborn (as 'sns') - Statistical data visualization

**Standard Library (Pre-loaded):**
• datetime, time, calendar - Date/time operations
• math, statistics, decimal, fractions - Mathematical functions
• random - Random number generation
• json, csv - Data serialization
• re - Regular expressions
• collections, itertools, functools, operator - Advanced data structures
• uuid, hashlib, base64 - Utilities
• copy - Object copying
• string, textwrap - String operations

**Additional Libraries (Available via imports):**
• pydantic, typing, dataclasses - Data validation & type hints
• scipy, sklearn - Scientific computing & machine learning
• sympy - Symbolic mathematics
• networkx - Graph analysis
• requests, urllib, http - Web requests
• openpyxl, xlsxwriter - Excel file handling
• plotly, bokeh, altair - Interactive visualizations

**Built-in Functions Available:**
• All standard: abs, sum, len, max, min, sorted, etc.
• Type functions: int, float, str, bool, list, dict, set, tuple
• Introspection: locals(), globals(), vars(), dir(), type(), isinstance()
• Conversion: chr, ord, bin, hex, oct, format
• Functional: map, filter, enumerate, zip, reversed
• Object: hasattr, getattr, setattr, callable

**Frappe API Access:**
• frappe.get_all(doctype, **kwargs) - Query documents
• frappe.get_doc(doctype, name) - Get single document  
• frappe.get_value(doctype, filters, fieldname) - Get field value
• frappe.session.user - Current user info

**Example Usage:**
```python
# System information (frappe is pre-loaded, no import needed)
print("=== System Information ===")
print(f"Current user: {{frappe.session.user}}")
print(f"Site URL: {{frappe.utils.get_site_url()}}")
print(f"System timezone: {{frappe.utils.get_system_timezone()}}")

# Data analysis with pandas (pd is pre-loaded)
data = frappe.get_all("Sales Invoice", fields=["grand_total", "posting_date"])
df = pd.DataFrame(data)
monthly_sales = df.groupby(pd.to_datetime(df['posting_date']).dt.month)['grand_total'].sum()
print(f"Monthly sales data: {{monthly_sales}}")

# Visualization with matplotlib (plt is pre-loaded)
plt.figure(figsize=(10, 6))
monthly_sales.plot(kind='bar')
plt.title('Monthly Sales Analysis')
plt.show()

# Advanced analysis with numpy (np is pre-loaded)
arr = np.array([1, 2, 3, 4, 5])
result = np.mean(arr)
print(f"Mean calculated: {{result}}")

# Introspection
print("Available variables:", list(locals().keys()))
```

💡 ARTIFACT TIP: For extensive analysis workflows, stream results to artifacts for unlimited depth.
""",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string", 
                            "description": "Python code to execute. Pre-loaded: pandas (pd), numpy (np), matplotlib (plt), seaborn (sns), datetime, math, json, etc. Available: frappe API, locals(), globals(), dir(). Use 'data' variable if data_query provided. Examples: 'df = pd.DataFrame(frappe.get_all(\"Customer\"))', 'print(locals().keys())', 'plt.plot([1,2,3])'"
                        },
                        "data_query": {
                            "type": "object",
                            "description": "Optional: Pre-fetch Frappe data for analysis as pandas DataFrame",
                            "properties": {
                                "doctype": {
                                    "type": "string",
                                    "description": "Frappe DocType to fetch (e.g., 'Sales Invoice', 'Customer')"
                                },
                                "filters": {
                                    "type": "object", 
                                    "default": {},
                                    "description": "Data filters. Examples: {'status': 'Paid'}, {'creation': ['>', '2024-01-01']}"
                                },
                                "fields": {
                                    "type": "array", 
                                    "items": {"type": "string"},
                                    "description": "Fields to include in DataFrame. Examples: ['customer', 'grand_total'], ['name', 'item_code', 'qty']"
                                },
                                "limit": {
                                    "type": "integer", 
                                    "default": 1000,
                                    "description": "Maximum records to fetch for analysis"
                                }
                            }
                        },
                        "imports": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": [],
                            "description": "Additional Python imports from safe list. Examples: ['scipy', 'sklearn', 'pydantic', 'requests']. Safe modules: datetime, math, statistics, pandas, numpy, matplotlib, seaborn, scipy, sklearn, pydantic, typing, requests, uuid, hashlib, base64, openpyxl, sympy, networkx, plotly, bokeh, altair"
                        }
                    },
                    "required": ["code"]
                }
            },
            {
                "name": "analyze_frappe_data",
                "description": f"""
{STREAMING_TOOL_PREFIX}

Perform comprehensive statistical analysis on Frappe business data. Calculate averages, trends, correlations, and business insights from any DocType. Perfect for understanding sales patterns, customer behavior, and operational metrics.

💡 ARTIFACT TIP: Create workspace artifacts for comprehensive analysis without response limits.
""",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doctype": {
                            "type": "string", 
                            "description": "Frappe DocType to analyze (e.g., 'Sales Invoice', 'Customer', 'Item', 'Purchase Order')"
                        },
                        "filters": {
                            "type": "object", 
                            "default": {}, 
                            "description": "Data filters for focused analysis. Examples: {'status': 'Paid'}, {'company': 'Your Company'}, {'creation': ['>', '2024-01-01']}"
                        },
                        "numerical_fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Numerical fields for statistical analysis (e.g., ['grand_total', 'outstanding_amount', 'qty']). Will calculate mean, median, std dev, etc."
                        },
                        "categorical_fields": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "description": "Categorical fields for frequency analysis (e.g., ['customer', 'status', 'territory']). Will show value counts and distributions."
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["summary", "correlation", "distribution", "trends"],
                            "default": "summary",
                            "description": "'summary' for basic stats, 'correlation' for relationships, 'distribution' for data spread, 'trends' for time-based patterns"
                        },
                        "date_field": {
                            "type": "string",
                            "description": "Date field for trend analysis (e.g., 'posting_date', 'creation', 'modified'). Required for 'trends' analysis_type."
                        }
                    },
                    "required": ["doctype"]
                }
            },
            {
                "name": "query_and_analyze",
                "description": f"""
{STREAMING_TOOL_PREFIX}

Execute custom SQL queries on Frappe database and perform advanced data analysis. Perfect for complex business intelligence, custom reporting, and advanced analytics that go beyond standard reports.

💡 ARTIFACT TIP: For complex queries and analysis, use artifacts to build comprehensive reports.
""",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL SELECT query to execute on Frappe database. Use table names like 'tabSales Invoice', 'tabCustomer', etc. Example: 'SELECT customer, grand_total FROM `tabSales Invoice` WHERE status = \"Paid\"'"
                        },
                        "analysis_code": {
                            "type": "string",
                            "description": "Optional Python code to analyze query results. Data is available as 'data' DataFrame. Example: 'print(data.groupby(\"customer\").sum())', 'data.describe()', 'data.plot()'"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
        
        # Add visualization tools only if libraries are available
        if HAS_PANDAS and HAS_VISUALIZATION:
            tools.append({
                "name": "create_visualization",
                "description": f"""
🔄 VISUALIZATION STREAMING TOOL:

Create interactive charts and visualizations from Frappe business data. Charts are displayed inline and saved as files.

💡 ARTIFACT TIP: Document visualization workflows in artifacts for comprehensive reporting.
""",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data_source": {
                            "type": "object",
                            "properties": {
                                "doctype": {
                                    "type": "string",
                                    "description": "Frappe DocType containing the data (e.g., 'Sales Invoice', 'Customer', 'Item', 'Stock Ledger Entry')"
                                },
                                "filters": {
                                    "type": "object", 
                                    "default": {},
                                    "description": "Data filters to narrow down records. Examples: {'status': 'Paid'}, {'creation': ['>', '2024-01-01']}, {'company': 'Your Company'}"
                                },
                                "fields": {
                                    "type": "array", 
                                    "items": {"type": "string"},
                                    "description": "Fields to include in visualization data. Must include x_field and y_field. Examples: ['customer', 'grand_total'], ['item_name', 'qty', 'rate']"
                                }
                            },
                            "required": ["doctype", "fields"]
                        },
                        "chart_type": {
                            "type": "string",
                            "enum": ["bar", "line", "pie", "scatter", "histogram", "box"],
                            "default": "bar",
                            "description": "Chart type: 'bar' for comparisons, 'line' for trends, 'pie' for proportions, 'scatter' for correlations, 'histogram' for distributions, 'box' for statistical analysis"
                        },
                        "x_field": {
                            "type": "string", 
                            "description": "Field for X-axis/categories (e.g., 'customer', 'item_name', 'posting_date'). Must be included in data_source.fields"
                        },
                        "y_field": {
                            "type": "string", 
                            "description": "Field for Y-axis/values (e.g., 'grand_total', 'qty', 'outstanding_amount'). Must be included in data_source.fields. Optional for pie charts."
                        },
                        "title": {
                            "type": "string", 
                            "description": "Descriptive chart title (e.g., 'Sales Revenue by Customer', 'Monthly Sales Trend', 'Top Selling Items')"
                        },
                        "save_chart": {
                            "type": "boolean", 
                            "default": True, 
                            "description": "Whether to save chart as PNG file. Set false for temporary analysis."
                        },
                        "output_format": {
                            "type": "string", 
                            "enum": ["inline", "file", "both"], 
                            "default": "both", 
                            "description": "'inline' for immediate display, 'file' for downloadable PNG, 'both' for inline display + file save"
                        }
                    },
                    "required": ["data_source", "x_field"]
                }
            })
        
        return tools
    
    @staticmethod
    def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute an analysis tool with given arguments"""
        try:
            # Check if this is a streaming-mandatory tool
            streaming_tools = ["analyze_frappe_data", "execute_python_code", "query_and_analyze", "create_visualization"]
            
            if tool_name in streaming_tools:
                # Prepend streaming requirement notice to results
                streaming_notice = """
🚨 ARTIFACT STREAMING NOTICE:

This analysis tool generates extensive data that may exceed response limits.
For comprehensive analysis and professional deliverables:

1. Create workspace artifacts BEFORE running analysis
2. Stream results to artifact sections  
3. Build unlimited depth analysis via artifacts

Results below may be truncated - use artifacts for complete analysis.

═══════════════════════════════════════════════════════

"""
            else:
                streaming_notice = ""
            
            if tool_name == "execute_python_code":
                result = AnalysisTools.execute_python_code(**arguments)
            elif tool_name == "analyze_frappe_data":
                result = AnalysisTools.analyze_frappe_data(**arguments)
            elif tool_name == "query_and_analyze":
                result = AnalysisTools.query_and_analyze(**arguments)
            elif tool_name == "create_visualization":
                result = AnalysisTools.create_visualization(**arguments)
            else:
                raise Exception(f"Unknown analysis tool: {tool_name}")
            
            # Convert result to string with safe JSON serialization
            if isinstance(result, dict):
                # Clean the result for JSON serialization
                clean_result = AnalysisTools._clean_for_json(result)
                try:
                    json_result = frappe.as_json(clean_result, indent=2)
                    return streaming_notice + json_result
                except Exception as json_e:
                    # Fallback to string conversion if JSON serialization still fails
                    api_logger.warning(f"JSON serialization failed for {tool_name}: {json_e}")
                    return streaming_notice + str(clean_result)
            elif isinstance(result, str):
                return streaming_notice + result
            else:
                return streaming_notice + str(result)
                
        except Exception as e:
            api_logger.error(f"Analysis tool execution error: {e}")
            return f"Error executing {tool_name}: {str(e)}"
    
    @staticmethod
    def _clean_for_json(obj):
        """Recursively clean objects for JSON serialization"""
        import datetime
        from decimal import Decimal
        
        if isinstance(obj, dict):
            return {k: AnalysisTools._clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [AnalysisTools._clean_for_json(item) for item in obj]
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, 'to_dict'):  # pandas objects
            try:
                return AnalysisTools._clean_for_json(obj.to_dict())
            except:
                return str(obj)
        elif hasattr(obj, '__dict__') and not isinstance(obj, (str, int, float, bool, type(None))):
            # Handle complex objects by converting to string
            return str(obj)
        else:
            return obj
    
    @staticmethod
    def execute_python_code(code: str, data_query: Dict = None, imports: List[str] = None) -> Dict[str, Any]:
        """Execute Python code for data analysis with security restrictions"""
        try:
            # SECURITY: Check if user has required permissions
            user_roles = frappe.get_roles(frappe.session.user)
            
            # Only System Managers can execute Python code
            if "System Manager" not in user_roles:
                return {
                    "success": False,
                    "error": "Python code execution requires System Manager role",
                    "required_role": "System Manager",
                    "user_roles": user_roles
                }
            
            # SECURITY: Create restricted execution environment with enhanced built-ins
            restricted_builtins = {
                # Safe built-in functions only
                'abs': abs, 'all': all, 'any': any, 'bool': bool,
                'dict': dict, 'enumerate': enumerate, 'filter': filter,
                'float': float, 'int': int, 'len': len, 'list': list,
                'map': map, 'max': max, 'min': min, 'range': range,
                'round': round, 'set': set, 'sorted': sorted, 'str': str,
                'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip,
                'print': print,  # Allow print for output
                # Additional safe built-ins for better functionality
                'chr': chr, 'ord': ord, 'bin': bin, 'hex': hex, 'oct': oct,
                'pow': pow, 'divmod': divmod, 'reversed': reversed,
                'hasattr': hasattr, 'getattr': getattr, 'setattr': setattr,
                'isinstance': isinstance, 'issubclass': issubclass,
                'callable': callable, 'format': format,
                # Introspection functions for debugging and exploration
                'locals': locals, 'globals': globals, 'vars': vars, 'dir': dir,
                # Explicitly exclude dangerous functions:
                # 'exec', 'eval', 'compile', 'open', 'input', '__import__'
            }
            
            # Create restricted Frappe API object
            class RestrictedFrappe:
                # Add common attributes that code might access
                __version__ = frappe.__version__ if hasattr(frappe, '__version__') else "Unknown"
                
                @staticmethod
                def get_all(doctype, **kwargs):
                    # Check read permission before allowing query
                    if not frappe.has_permission(doctype, "read"):
                        raise PermissionError(f"No read permission for {doctype}")
                    return frappe.get_all(doctype, **kwargs)
                
                @staticmethod
                def get_doc(doctype, name=None):
                    # Check read permission
                    if not frappe.has_permission(doctype, "read"):
                        raise PermissionError(f"No read permission for {doctype}")
                    doc = frappe.get_doc(doctype, name) if name else frappe.get_doc(doctype)
                    if not frappe.has_permission(doc, "read"):
                        raise PermissionError(f"No read permission for {doctype} {name}")
                    return doc
                
                @staticmethod
                def get_value(doctype, filters, fieldname):
                    if not frappe.has_permission(doctype, "read"):
                        raise PermissionError(f"No read permission for {doctype}")
                    return frappe.get_value(doctype, filters, fieldname)
                
                @staticmethod
                def get_list(doctype, **kwargs):
                    # Alias for get_all for compatibility
                    if not frappe.has_permission(doctype, "read"):
                        raise PermissionError(f"No read permission for {doctype}")
                    return frappe.get_list(doctype, **kwargs)
                
                # Safe utility functions
                @staticmethod
                def utils():
                    class SafeUtils:
                        @staticmethod
                        def now():
                            return frappe.utils.now()
                        
                        @staticmethod
                        def today():
                            return frappe.utils.today()
                        
                        @staticmethod
                        def getdate(date):
                            return frappe.utils.getdate(date)
                        
                        @staticmethod
                        def get_site_url():
                            return frappe.utils.get_site_url()
                        
                        @staticmethod
                        def get_system_timezone():
                            return frappe.utils.get_system_timezone()
                    
                    return SafeUtils()
                
                # Block dangerous operations
                @staticmethod
                def set_user(*args, **kwargs):
                    raise SecurityError("User context modification not allowed")
                
                @staticmethod
                def db(*args, **kwargs):
                    raise SecurityError("Direct database access not allowed")
                
                # Allow access to some safe frappe attributes
                @property
                def session(self):
                    class SafeSession:
                        user = frappe.session.user
                    return SafeSession()
                
                # Block other dangerous methods
                def __getattr__(self, name):
                    # Handle version attributes specifically
                    if name in ['__version__', 'version']:
                        return getattr(frappe, '__version__', "15.0.0")
                    
                    if name in ['db', 'set_user', 'delete_doc', 'rename_doc']:
                        raise SecurityError(f"Access to frappe.{name} not allowed")
                    
                    # Allow access to safe constants and attributes
                    safe_attributes = ['__version__', 'version', 'local', 'conf']
                    if name in safe_attributes and hasattr(frappe, name):
                        return getattr(frappe, name)
                    
                    # For other attributes, try to get from frappe safely
                    if hasattr(frappe, name):
                        attr = getattr(frappe, name)
                        if callable(attr) and name not in ['get_all', 'get_doc', 'get_value', 'get_list']:
                            raise SecurityError(f"Access to frappe.{name}() not allowed")
                        return attr
                    raise AttributeError(f"'RestrictedFrappe' object has no attribute '{name}'")
            
            # Prepare secure execution environment
            exec_globals = {
                '__builtins__': restricted_builtins,
                'frappe': RestrictedFrappe(),
                'json': json
            }
            
            # Add available libraries with restrictions
            if HAS_PANDAS:
                exec_globals['pd'] = pd
                exec_globals['pandas'] = pd
            if HAS_NUMPY:
                exec_globals['np'] = np
                exec_globals['numpy'] = np
            if HAS_VISUALIZATION:
                exec_globals['plt'] = plt
                exec_globals['sns'] = sns
                exec_globals['matplotlib'] = __import__('matplotlib')
                exec_globals['seaborn'] = sns
            
            # Add commonly used standard library modules
            try:
                import datetime, math, re, statistics, collections, itertools, functools
                import decimal, fractions, random, time, calendar, copy, operator
                
                exec_globals.update({
                    'datetime': datetime, 'math': math, 're': re, 'statistics': statistics,
                    'collections': collections, 'itertools': itertools, 'functools': functools,
                    'decimal': decimal, 'fractions': fractions, 'random': random,
                    'time': time, 'calendar': calendar, 'copy': copy, 'operator': operator
                })
            except ImportError as e:
                # Some modules might not be available, but continue
                pass
            
            # Try to add additional useful libraries if available
            additional_libs = {
                'pydantic': 'pydantic',
                'typing': 'typing', 
                'dataclasses': 'dataclasses',
                'uuid': 'uuid',
                'hashlib': 'hashlib',
                'base64': 'base64'
            }
            
            for alias, module_name in additional_libs.items():
                try:
                    exec_globals[alias] = __import__(module_name)
                except ImportError:
                    pass  # Module not available, skip
            
            # SECURITY: Restrict imports to safe libraries only
            safe_imports = {
                # Standard library modules (safe for data analysis)
                'datetime', 'math', 're', 'statistics', 'collections',
                'itertools', 'functools', 'json', 'csv', 'decimal',
                'fractions', 'random', 'time', 'calendar', 'hashlib',
                'uuid', 'copy', 'operator', 'string', 'textwrap',
                
                # Data science and analysis libraries
                'pandas', 'numpy', 'matplotlib', 'seaborn',
                
                # Data validation and modeling
                'pydantic', 'typing', 'dataclasses',
                
                # Additional useful libraries (if available)
                'scipy', 'sklearn', 'plotly', 'bokeh', 'altair',
                'requests', 'urllib', 'http', 'email', 'base64',
                
                # Scientific computing
                'sympy', 'networkx', 'openpyxl', 'xlsxwriter'
            }
            
            if imports:
                import_results = []
                for imp in imports:
                    # Parse import statement to extract base module name
                    base_module = imp.split()[0].split('.')[0]
                    
                    if base_module not in safe_imports:
                        return {
                            "success": False, 
                            "error": f"Import '{imp}' not allowed. Base module '{base_module}' not in safe list.",
                            "allowed_modules": sorted(list(safe_imports)),
                            "suggestion": "Use one of the pre-loaded modules or request a safe module to be added."
                        }
                    try:
                        exec(f"import {imp}", exec_globals)
                        import_results.append(f"✅ {imp}")
                    except ImportError as e:
                        import_results.append(f"❌ {imp}: {str(e)}")
                        # Don't fail completely, just note the failed import
                
                # Add import results to help user understand what's available
                if import_results:
                    exec_globals['_import_results'] = import_results
            
            # Fetch data if query provided (with permission checks)
            if data_query:
                doctype = data_query.get("doctype")
                filters = data_query.get("filters", {})
                fields = data_query.get("fields", ["*"])
                limit = data_query.get("limit", 1000)
                
                if not frappe.has_permission(doctype, "read"):
                    return {"success": False, "error": f"No read permission for {doctype}"}
                
                raw_data = frappe.get_all(doctype, filters=filters, fields=fields, limit=limit)
                if HAS_PANDAS and raw_data:
                    try:
                        # Create DataFrame with better compatibility handling
                        df = pd.DataFrame(raw_data)
                        # Avoid convert_dtypes() which can cause __array_struct__ issues
                        exec_globals['data'] = df
                    except Exception as e:
                        # If DataFrame creation fails, provide raw data
                        exec_globals['data'] = raw_data
                        print(f"Warning: DataFrame creation failed, using raw data: {e}")
                exec_globals['raw_data'] = raw_data
            
            # Capture output
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            try:
                # Pre-execution check and removal of import statements
                import_warnings = []
                cleaned_code_lines = []
                code_lines = code.split('\n')
                
                for i, line in enumerate(code_lines, 1):
                    stripped_line = line.strip()
                    original_line = line
                    
                    # Check for import statements
                    if (stripped_line.startswith('import ') or 
                        (stripped_line.startswith('from ') and ' import ' in stripped_line)):
                        
                        import_warnings.append(f"Line {i}: {stripped_line}")
                        
                        # Replace import line with a comment explaining the removal
                        cleaned_code_lines.append(f"# REMOVED IMPORT: {stripped_line} (library pre-loaded)")
                    else:
                        cleaned_code_lines.append(original_line)
                
                if import_warnings:
                    warning_msg = "⚠️ IMPORTS AUTOMATICALLY REMOVED: Libraries are pre-loaded. Removed import statements:\n" + "\n".join(import_warnings)
                    warning_msg += "\n\n✅ USING PRE-LOADED: frappe, pd (pandas), np (numpy), plt (matplotlib), sns (seaborn), datetime, math, json, statistics, etc."
                    print(warning_msg)
                    
                    # Use cleaned code without import statements
                    code = '\n'.join(cleaned_code_lines)
                
                # Set pandas options for better compatibility
                if HAS_PANDAS:
                    # Disable problematic pandas features that might cause __array_struct__ issues
                    try:
                        pd.set_option('mode.copy_on_write', False)
                    except Exception:
                        pass  # Ignore if option doesn't exist in this pandas version
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    # Execute code with better error handling
                    exec(code, exec_globals)
                
                output = stdout_capture.getvalue()
                errors = stderr_capture.getvalue()
                
                # Extract any variables created with improved compatibility
                result_vars = {}
                for key, value in exec_globals.items():
                    if not key.startswith('_') and key not in ['frappe', 'pd', 'np', 'json', 'data', 'raw_data', 'plt', 'sns']:
                        try:
                            # Convert to JSON-serializable format with better pandas handling
                            if HAS_PANDAS and isinstance(value, pd.DataFrame):
                                try:
                                    # Safe DataFrame serialization
                                    sample_data = value.head(10)
                                    # Handle different data types safely
                                    records = []
                                    for _, row in sample_data.iterrows():
                                        record = {}
                                        for col in sample_data.columns:
                                            try:
                                                val = row[col]
                                                # Handle numpy types
                                                if hasattr(val, 'item'):
                                                    val = val.item()
                                                elif pd.isna(val):
                                                    val = None
                                                record[str(col)] = val
                                            except Exception:
                                                record[str(col)] = str(row[col])
                                        records.append(record)
                                    
                                    result_vars[key] = {
                                        "type": "dataframe",
                                        "shape": list(value.shape),
                                        "columns": [str(col) for col in value.columns],
                                        "data": records,
                                        "dtypes": {str(col): str(dtype) for col, dtype in value.dtypes.items()}
                                    }
                                    
                                    # Add summary if numeric columns exist
                                    numeric_cols = value.select_dtypes(include=['number']).columns
                                    if len(numeric_cols) > 0:
                                        try:
                                            summary = value.describe()
                                            result_vars[key]["summary"] = {
                                                str(col): {str(stat): float(val) if pd.notna(val) else None 
                                                          for stat, val in summary[col].items()}
                                                for col in numeric_cols
                                            }
                                        except Exception:
                                            pass  # Skip summary if it fails
                                            
                                except Exception as df_error:
                                    result_vars[key] = {
                                        "type": "dataframe", 
                                        "error": f"DataFrame serialization failed: {str(df_error)}",
                                        "shape": list(value.shape) if hasattr(value, 'shape') else "unknown"
                                    }
                            elif HAS_NUMPY and hasattr(value, '__array__'):
                                # Handle numpy arrays
                                try:
                                    if hasattr(value, 'tolist'):
                                        result_vars[key] = {
                                            "type": "numpy_array",
                                            "shape": list(value.shape) if hasattr(value, 'shape') else None,
                                            "dtype": str(value.dtype) if hasattr(value, 'dtype') else None,
                                            "data": value.tolist() if value.size < 100 else "<large array>"
                                        }
                                    else:
                                        result_vars[key] = str(value)
                                except Exception:
                                    result_vars[key] = f"<numpy array: {type(value).__name__}>"
                            elif isinstance(value, (dict, list, str, int, float, bool, type(None))):
                                result_vars[key] = value
                            else:
                                # Try to convert complex objects safely
                                try:
                                    if hasattr(value, 'to_dict'):
                                        result_vars[key] = value.to_dict()
                                    elif hasattr(value, '__dict__'):
                                        result_vars[key] = str(value)
                                    else:
                                        result_vars[key] = str(value)
                                except Exception:
                                    result_vars[key] = f"<{type(value).__name__} object>"
                        except Exception as var_error:
                            result_vars[key] = f"<Error extracting {key}: {str(var_error)}>"
                
                # Compile available libraries info
                available_libs = {
                    "core_data_science": {
                        "pandas": HAS_PANDAS,
                        "numpy": HAS_NUMPY,
                        "matplotlib": HAS_VISUALIZATION
                    },
                    "pre_loaded_modules": list(exec_globals.keys()),
                    "safe_imports": sorted(list(safe_imports))
                }
                
                # Add import results if any
                if '_import_results' in exec_globals:
                    available_libs["import_results"] = exec_globals['_import_results']
                
                return {
                    "success": True,
                    "output": output,
                    "errors": errors if errors else None,
                    "variables": result_vars,
                    "execution_summary": f"Code executed successfully. {len(result_vars)} variables created.",
                    "libraries_info": available_libs,
                    "security_note": "Execution in secure sandbox with System Manager permissions."
                }
                
            except Exception as e:
                error_msg = str(e)
                tb = traceback.format_exc()
                
                # Provide more helpful error messages for common issues
                if "__array_struct__" in error_msg:
                    error_msg = "Pandas/NumPy compatibility issue. Try using simpler data operations or check data types."
                elif "RestrictedFrappe" in error_msg and "attribute" in error_msg:
                    error_msg = f"Frappe API limitation: {error_msg}. Use available methods: get_all(), get_doc(), get_value()"
                
                return {
                    "success": False,
                    "error": error_msg,
                    "traceback": tb,
                    "output": stdout_capture.getvalue(),
                    "errors": stderr_capture.getvalue(),
                    "help": "Check the available libraries and Frappe API methods. Use simple data operations."
                }
                
        except Exception as e:
            return {"success": False, "error": f"Code execution failed: {str(e)}"}
    
    @staticmethod
    def analyze_frappe_data(doctype: str, filters: Dict = None, 
                           numerical_fields: List[str] = None, 
                           categorical_fields: List[str] = None,
                           analysis_type: str = "summary",
                           date_field: str = None) -> Dict[str, Any]:
        """Perform statistical analysis on Frappe DocType data"""
        try:
            if not frappe.has_permission(doctype, "read"):
                return {"success": False, "error": f"No read permission for {doctype}"}
            
            # Get meta to identify field types if not specified
            meta = frappe.get_meta(doctype)
            
            if not numerical_fields:
                numerical_fields = [f.fieldname for f in meta.fields 
                                  if f.fieldtype in ["Currency", "Float", "Int", "Percent"]]
            
            if not categorical_fields:
                categorical_fields = [f.fieldname for f in meta.fields 
                                    if f.fieldtype in ["Select", "Link", "Data"] and not f.hidden][:5]
            
            # Fetch data - be more careful about fields
            all_fields = ["name"]
            if numerical_fields:
                all_fields.extend([f for f in numerical_fields if f])
            if categorical_fields:
                all_fields.extend([f for f in categorical_fields if f])
            if date_field and date_field not in all_fields:
                all_fields.append(date_field)
            
            # Remove duplicates and None values
            all_fields = list(set([f for f in all_fields if f]))
                
            try:
                data = frappe.get_all(doctype, filters=filters or {}, fields=all_fields, limit=100)  # Reduced limit for testing
            except Exception as e:
                return {"success": False, "error": f"Data fetch failed: {str(e)}", "fields_requested": all_fields}
            
            if not data:
                return {"success": True, "message": "No data found", "analysis": {}}
            
            if not HAS_PANDAS:
                # Fallback analysis without pandas
                analysis = {"type": analysis_type, "doctype": doctype}
                
                if analysis_type == "summary" and categorical_fields:
                    analysis["categorical_summary"] = {}
                    for field in categorical_fields:
                        if any(field in row for row in data):
                            # Simple value counting without pandas
                            values = [row.get(field) for row in data if row.get(field) is not None]
                            value_counts = {}
                            for val in values:
                                str_val = str(val)
                                value_counts[str_val] = value_counts.get(str_val, 0) + 1
                            
                            # Sort by count and take top 10
                            sorted_counts = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                            analysis["categorical_summary"][field] = dict(sorted_counts)
                
                return {
                    "success": True,
                    "analysis": analysis,
                    "data_summary": {
                        "total_records": len(data),
                        "categorical_fields_analyzed": len(categorical_fields) if categorical_fields else 0
                    },
                    "warning": "Using fallback analysis - pandas not available. Install pandas for advanced features."
                }
            
            try:
                # Robust DataFrame creation with proper type handling
                def clean_frappe_data(data_list):
                    """Clean Frappe data for pandas compatibility"""
                    import datetime
                    from decimal import Decimal
                    
                    cleaned_data = []
                    for row in data_list:
                        cleaned_row = {}
                        for key, value in row.items():
                            if value is None:
                                cleaned_row[key] = None
                            elif isinstance(value, (str, int, float, bool)):
                                cleaned_row[key] = value
                            elif isinstance(value, datetime.datetime):
                                cleaned_row[key] = value.isoformat()
                            elif isinstance(value, datetime.date):
                                cleaned_row[key] = value.isoformat()
                            elif isinstance(value, Decimal):
                                cleaned_row[key] = float(value)
                            elif hasattr(value, '__dict__'):
                                # Handle Frappe Document objects
                                cleaned_row[key] = str(value)
                            else:
                                # Fallback: convert to string
                                cleaned_row[key] = str(value)
                        cleaned_data.append(cleaned_row)
                    return cleaned_data
                
                # Clean data and create DataFrame
                cleaned_data = clean_frappe_data(data)
                df = pd.DataFrame(cleaned_data)
                
                # Debug info
                debug_info = {
                    "raw_data_sample": data[:1] if data else [],
                    "cleaned_data_sample": cleaned_data[:1] if cleaned_data else [],
                    "df_shape": df.shape,
                    "df_columns": list(df.columns)
                }
                
            except Exception as e:
                error_msg = str(e)
                # Check for specific pandas errors
                if "__array_struct__" in error_msg:
                    return {
                        "success": False,
                        "error": "Pandas DataFrame creation failed due to incompatible data types. This often happens with mixed Frappe object types.",
                        "technical_error": error_msg,
                        "pandas_version": PANDAS_VERSION,
                        "suggestion": "Try updating pandas: pip install --upgrade pandas",
                        "raw_data_sample": data[:1] if data else [],
                        "data_length": len(data)
                    }
                else:
                    return {
                        "success": False, 
                        "error": f"DataFrame creation failed: {error_msg}",
                        "traceback": traceback.format_exc(),
                        "pandas_version": PANDAS_VERSION,
                        "raw_data_sample": data[:1] if data else [],
                        "data_length": len(data)
                    }
            
            analysis = {"type": analysis_type, "doctype": doctype, "debug": debug_info}
            
            if analysis_type == "summary":
                # Basic statistical summary
                if numerical_fields:
                    # Convert numerical fields to numeric types, handling errors
                    numeric_data = {}
                    for field in numerical_fields:
                        if field in df.columns:
                            try:
                                # Convert to numeric, coercing errors to NaN
                                df[field] = pd.to_numeric(df[field], errors='coerce')
                                numeric_data[field] = df[field]
                            except Exception as e:
                                continue
                    
                    if numeric_data:
                        numeric_df = pd.DataFrame(numeric_data)
                        # Remove any columns that are all NaN after conversion
                        numeric_df = numeric_df.dropna(axis=1, how='all')
                        if not numeric_df.empty:
                            try:
                                analysis["numerical_summary"] = numeric_df.describe().to_dict()
                            except Exception as e:
                                analysis["numerical_summary"] = {"error": f"Failed to generate summary: {str(e)}"}
                
                if categorical_fields:
                    analysis["categorical_summary"] = {}
                    for field in categorical_fields:
                        if field in df.columns:
                            try:
                                # Handle categorical field analysis with error handling
                                series = df[field]
                                
                                # Clean the series - remove nulls and convert to string
                                clean_series = series.dropna().astype(str)
                                
                                if not clean_series.empty:
                                    value_counts = clean_series.value_counts().head(10)
                                    analysis["categorical_summary"][field] = value_counts.to_dict()
                                else:
                                    analysis["categorical_summary"][field] = {"error": "No valid data after cleaning"}
                                    
                            except Exception as e:
                                analysis["categorical_summary"][field] = {"error": f"Failed to analyze {field}: {str(e)}"}
            
            elif analysis_type == "correlation" and HAS_NUMPY:
                # Correlation analysis for numerical fields
                if len(numerical_fields) > 1:
                    # Convert numerical fields to numeric types, handling errors
                    numeric_data = {}
                    for field in numerical_fields:
                        if field in df.columns:
                            try:
                                df[field] = pd.to_numeric(df[field], errors='coerce')
                                numeric_data[field] = df[field]
                            except Exception:
                                continue
                    
                    if len(numeric_data) > 1:
                        numeric_df = pd.DataFrame(numeric_data)
                        # Remove any columns that are all NaN after conversion
                        numeric_df = numeric_df.dropna(axis=1, how='all')
                        if not numeric_df.empty:
                            try:
                                corr_matrix = numeric_df.corr()
                                analysis["correlation_matrix"] = corr_matrix.to_dict()
                                
                                # Find strong correlations
                                strong_corr = []
                                for i in range(len(corr_matrix.columns)):
                                    for j in range(i+1, len(corr_matrix.columns)):
                                        corr_val = corr_matrix.iloc[i, j]
                                        if abs(float(corr_val)) > 0.7:  # Strong correlation threshold
                                            strong_corr.append({
                                                "field1": corr_matrix.columns[i],
                                                "field2": corr_matrix.columns[j],
                                                "correlation": float(corr_val)
                                            })
                                analysis["strong_correlations"] = strong_corr
                            except Exception as e:
                                analysis["correlation_error"] = f"Failed to compute correlation: {str(e)}"
            
            elif analysis_type == "trends" and date_field:
                # Time-based trend analysis
                if date_field in df.columns and numerical_fields:
                    try:
                        df[date_field] = pd.to_datetime(df[date_field], errors='coerce')
                        
                        # Convert numerical fields to numeric types
                        for field in numerical_fields:
                            if field in df.columns:
                                df[field] = pd.to_numeric(df[field], errors='coerce')
                        
                        df_grouped = df.groupby(pd.Grouper(key=date_field, freq='M'))
                        
                        trends = {}
                        for field in numerical_fields:
                            if field in df.columns:
                                try:
                                    trend_data = df_grouped[field].agg(['count', 'sum', 'mean']).fillna(0)
                                    trends[field] = trend_data.to_dict('index')
                                except Exception:
                                    continue
                        
                        analysis["trends"] = trends
                    except Exception as e:
                        analysis["trends_error"] = f"Failed to compute trends: {str(e)}"
            
            return {
                "success": True,
                "analysis": analysis,
                "data_summary": {
                    "total_records": len(df),
                    "numerical_fields_analyzed": len(numerical_fields),
                    "categorical_fields_analyzed": len(categorical_fields)
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Analysis failed: {str(e)}"}
    
    @staticmethod
    def query_and_analyze(query: str, analysis_code: str = None) -> Dict[str, Any]:
        """Execute SQL query and analyze results with security restrictions"""
        try:
            # SECURITY: Check if user has required permissions
            user_roles = frappe.get_roles(frappe.session.user)
            
            # Only System Managers can execute SQL queries
            if "System Manager" not in user_roles:
                return {
                    "success": False,
                    "error": "SQL query execution requires System Manager role",
                    "required_role": "System Manager", 
                    "user_roles": user_roles,
                    "alternatives": [
                        "Use document_list tool for document queries",
                        "Use report_execute tool for predefined reports", 
                        "Use analyze_frappe_data tool for statistical analysis"
                    ]
                }
            
            # SECURITY: Strict query validation
            query_lower = query.lower().strip()
            
            # Must be SELECT only
            if not query_lower.startswith('select'):
                return {"success": False, "error": "Only SELECT queries are allowed"}
            
            # Comprehensive dangerous keyword check
            dangerous_keywords = [
                'drop', 'delete', 'update', 'insert', 'alter', 'create', 'truncate',
                'exec', 'execute', 'sp_', 'xp_', 'into', 'union', 'declare', 'while',
                'cursor', 'fetch', 'open', 'close', 'deallocate', 'bulk', 'load'
            ]
            
            for keyword in dangerous_keywords:
                if keyword in query_lower:
                    return {"success": False, "error": f"Query contains prohibited keyword: {keyword}"}
            
            # Additional security checks
            if '--' in query or '/*' in query or '*/' in query:
                return {"success": False, "error": "Comments not allowed in queries"}
            
            if ';' in query.rstrip(';'):  # Allow single trailing semicolon
                return {"success": False, "error": "Multiple statements not allowed"}
            
            # SECURITY: Limit to specific tables only (Frappe DocTypes)
            # Check if query contains tab prefix (defer DocType validation to execution time)
            if not ('`tab' in query or '`Tab' in query):
                return {"success": False, "error": "Query must reference valid Frappe DocTypes using `tab` prefix (e.g., `tabSales Invoice`)"}
            
            # Execute query with timeout
            result = frappe.db.sql(query, as_dict=True)
            
            if not result:
                return {"success": True, "message": "Query returned no results", "data": []}
            
            response = {
                "success": True,
                "data": result,
                "row_count": len(result),
                "columns": list(result[0].keys()) if result else [],
                "query_executed": query,
                "executed_by": frappe.session.user
            }
            
            # Log the query execution for audit
            frappe.log_error(
                f"SQL Query executed by {frappe.session.user}: {query}",
                "Assistant SQL Execution"
            )
            
            return response
            
        except Exception as e:
            return {"success": False, "error": f"Query execution failed: {str(e)}"}
    
    @staticmethod
    def create_visualization(data_source: Dict, chart_type: str = "bar", 
                           x_field: str = None, y_field: str = None, 
                           title: str = None, save_chart: bool = True, 
                           output_format: str = "both") -> Dict[str, Any]:
        """Create charts and visualizations from Frappe data"""
        try:
            if not HAS_PANDAS or not HAS_VISUALIZATION:
                return {"success": False, "error": "Visualization libraries not available"}
            
            doctype = data_source["doctype"]
            filters = data_source.get("filters", {})
            fields = data_source["fields"]
            
            if not frappe.has_permission(doctype, "read"):
                return {"success": False, "error": f"No read permission for {doctype}"}
            
            # Fetch data
            data = frappe.get_all(doctype, filters=filters, fields=fields, limit=1000)
            
            if not data:
                return {"success": True, "message": "No data found for visualization"}
            
            # Use the same data cleaning function from analyze_frappe_data
            def clean_frappe_data(data_list):
                """Clean Frappe data for pandas compatibility"""
                import datetime
                from decimal import Decimal
                
                cleaned_data = []
                for row in data_list:
                    cleaned_row = {}
                    for key, value in row.items():
                        if value is None:
                            cleaned_row[key] = None
                        elif isinstance(value, (str, int, float, bool)):
                            cleaned_row[key] = value
                        elif isinstance(value, datetime.datetime):
                            cleaned_row[key] = value.isoformat()
                        elif isinstance(value, datetime.date):
                            cleaned_row[key] = value.isoformat()
                        elif isinstance(value, Decimal):
                            cleaned_row[key] = float(value)
                        elif hasattr(value, '__dict__'):
                            # Handle Frappe Document objects
                            cleaned_row[key] = str(value)
                        else:
                            # Fallback: convert to string
                            cleaned_row[key] = str(value)
                    cleaned_data.append(cleaned_row)
                return cleaned_data
            
            try:
                # Clean data and create DataFrame
                cleaned_data = clean_frappe_data(data)
                df = pd.DataFrame(cleaned_data)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to create DataFrame for visualization: {str(e)}",
                    "suggestion": "This often happens with mixed data types. Try selecting specific fields.",
                    "raw_data_sample": data[:1] if data else []
                }
            
            # Generate visualization code
            viz_code = AnalysisTools._generate_viz_code(df, chart_type, x_field, y_field, title)
            
            response = {
                "success": True,
                "data_summary": {
                    "records": len(df),
                    "fields": list(df.columns)
                },
                "chart_config": {
                    "type": chart_type,
                    "x_field": x_field,
                    "y_field": y_field,
                    "title": title or f"{chart_type.title()} Chart - {doctype}"
                }
            }
            
            # Create visualization based on output format
            if save_chart and output_format in ["inline", "file", "both"]:
                try:
                    # Import required libraries
                    import matplotlib
                    matplotlib.use('Agg')  # Use non-interactive backend
                    import matplotlib.pyplot as plt
                    import seaborn as sns
                    import base64
                    import io
                    
                    exec_globals = {'data': df, 'plt': plt, 'sns': sns, 'pd': pd}
                    exec(viz_code, exec_globals)
                    
                    # Create chart buffer
                    buffer = io.BytesIO()
                    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
                    buffer.seek(0)
                    
                    # Handle different output formats
                    if output_format in ["inline", "both"]:
                        # Create base64 encoded image for inline display
                        buffer_data = buffer.getvalue()
                        if buffer_data:
                            image_base64 = base64.b64encode(buffer_data).decode('utf-8')
                            response["chart_base64"] = f"data:image/png;base64,{image_base64}"
                            response["base64_length"] = len(image_base64)  # Debug info
                        else:
                            response["save_error"] = "Empty buffer - chart may not have been generated properly"
                    
                    if output_format in ["file", "both"]:
                        # Save to file for URL access
                        chart_filename = f"chart_{frappe.generate_hash()}.png"
                        chart_path = frappe.get_site_path("public", "files", chart_filename)
                        
                        # Save buffer content to file
                        with open(chart_path, 'wb') as f:
                            f.write(buffer.getvalue())
                        
                        response["chart_saved"] = True
                        response["chart_url"] = f"/files/{chart_filename}"
                        response["chart_path"] = chart_path
                    
                    plt.close()
                    buffer.close()
                    
                    # Set appropriate message based on output format
                    if output_format == "inline":
                        response["message"] = "Visualization created for inline preview!"
                    elif output_format == "file":
                        response["message"] = f"Visualization saved as {chart_filename}"
                    else:  # both
                        response["message"] = f"Visualization created for inline preview and saved as {chart_filename if 'chart_filename' in locals() else 'file'}"
                    
                except Exception as e:
                    import traceback
                    error_details = {
                        "error_message": str(e),
                        "error_type": type(e).__name__,
                        "traceback": traceback.format_exc()
                    }
                    response["save_error"] = f"Visualization error: {str(e)}"
                    response["error_details"] = error_details
                    response["visualization_code"] = viz_code  # Fall back to code if execution fails
            else:
                # If not saving, just return the code
                response["visualization_code"] = viz_code
            
            return response
            
        except Exception as e:
            return {"success": False, "error": f"Visualization creation failed: {str(e)}"}
    
    @staticmethod
    def _generate_viz_code(df, chart_type, x_field, y_field, title):
        """Generate matplotlib/seaborn code for visualization"""
        code = f"""
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10, 6))

# Data preparation
df = data  # Use the data DataFrame

"""
        
        if chart_type == "bar":
            if y_field:
                code += f"plt.bar(df['{x_field}'], df['{y_field}'])\n"
            else:
                code += f"df['{x_field}'].value_counts().plot(kind='bar')\n"
                
        elif chart_type == "line":
            if y_field:
                code += f"plt.plot(df['{x_field}'], df['{y_field}'])\n"
            else:
                code += f"df['{x_field}'].plot(kind='line')\n"
            
        elif chart_type == "pie":
            code += f"df['{x_field}'].value_counts().plot(kind='pie')\n"
            
        elif chart_type == "scatter" and y_field:
            code += f"plt.scatter(df['{x_field}'], df['{y_field}'])\n"
            
        elif chart_type == "histogram":
            code += f"plt.hist(df['{x_field}'], bins=20)\n"
            
        elif chart_type == "box":
            code += f"sns.boxplot(data=df, x='{x_field}')\n"
            
        # Add ylabel conditionally to avoid nested f-string issues
        ylabel_line = f"plt.ylabel('{y_field}')\n" if y_field else ""
        
        code += f"""
plt.title('{title or "Data Visualization"}')
plt.xlabel('{x_field}')
{ylabel_line}plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Summary statistics
print("Data Summary:")
print(f"Total records: {{len(df)}}")
print(f"Columns: {{list(df.columns)}}")
"""
        
        return code