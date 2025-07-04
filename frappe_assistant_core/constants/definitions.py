"""
Constants and string definitions for Frappe Assistant Core
Centralizes all string literals, messages, and configuration constants
"""

# MCP Protocol Constants
MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "Frappe Assistant Core MCP Server"
SERVER_VERSION = "1.2.0"

# API Error Codes
class ErrorCodes:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    AUTHENTICATION_REQUIRED = -32000

# Tool Categories
class ToolCategories:
    DOCUMENT = "document"
    ANALYSIS = "analysis"
    REPORT = "report"
    SEARCH = "search"
    METADATA = "metadata"
    VISUALIZATION = "visualization"

# Analysis Tool Thresholds
class AnalysisThresholds:
    SMALL_OUTPUT_LINES = 20
    LARGE_VARIABLE_COUNT = 15
    LARGE_DATA_ROWS = 100
    MEDIUM_OUTPUT_LINES = 10
    MEDIUM_VARIABLE_COUNT = 8

# Streaming Messages
class StreamingMessages:
    TOOL_PREFIX = """📊 ANALYSIS TOOL - Artifact Streaming Recommended:

💡 SUGGESTION: For complex multi-step analysis, consider creating workspace artifacts to:
• Prevent response limits during extensive analysis
• Build comprehensive reports with unlimited depth  
• Create professional deliverables for stakeholders
• Preserve analysis history across sessions

This tool works perfectly in responses AND artifacts - use artifacts for unlimited analysis scope."""

    SYSTEM_INSTRUCTIONS = """🔄 FRAPPE ARTIFACT STREAMING PROTOCOL - MANDATORY FOR ANALYSIS

⚠️ CRITICAL REQUIREMENT: All substantial analysis using Frappe analysis tools (execute_python_code, analyze_frappe_data, query_and_analyze, create_visualization) MUST be performed in workspace artifacts.

🚫 RESPONSE LIMIT PREVENTION:
Analysis tools will enforce artifact streaming automatically when substantial results are detected to prevent response truncation.

📋 MANDATORY WORKFLOW FOR ANALYSIS:
• Simple data queries → Direct response (small results)
• ANY substantial analysis → REQUIRED artifact workspace
• Multi-step analysis → MUST use artifacts exclusively  
• Data visualization → REQUIRED in artifacts
• Business intelligence → REQUIRED in artifacts

⚡ AUTOMATIC ENFORCEMENT:
The server detects substantial analysis results and enforces artifact streaming by:
- Providing summary and redirection when large results detected
- Requiring re-execution in artifact workspace for complete results
- Ensuring unlimited analysis depth through artifact streaming

🎯 ARTIFACT STREAMING TRIGGERS:
- Output > 500 characters
- Variables > 10 created
- Data rows > 50 processed
- Any visualization creation
- Multi-step analytical workflows

✅ BENEFITS OF MANDATORY APPROACH:
- Eliminates response limit errors completely
- Professional deliverable creation guaranteed
- Unlimited analytical depth ensured
- Stakeholder-ready outputs automatic

This protocol ensures reliable, unlimited analysis capabilities through intelligent artifact streaming."""

    ARTIFACT_CREATION_PROMPT = """I'll create a comprehensive analysis artifact to present these substantial results without response limits.

{summary}

The analysis contains extensive output that benefits from artifact presentation for professional formatting and unlimited depth. Let me create a dedicated workspace for these results:

{content}"""

    SMALL_ANALYSIS_TIP = """

---

💡 **ARTIFACT TIP:** For larger analyses (>20 lines output), results will auto-stream to artifacts for unlimited depth."""

# Error Messages
class ErrorMessages:
    AUTHENTICATION_REQUIRED = "Authentication required: No valid user session"
    ACCESS_DENIED = "Access denied: User does not have assistant permissions"
    INVALID_REQUEST_FORMAT = "Invalid Request - Not JSON-RPC 2.0 format"
    METHOD_NOT_FOUND = "Method '{}' not found"
    MISSING_TOOL_NAME = "Missing tool name"
    MISSING_PROMPT_NAME = "Missing prompt name"
    UNKNOWN_PROMPT = "Unknown prompt: {}"
    UNKNOWN_TOOL = "Unknown tool: {}"
    TOOL_EXECUTION_ERROR = "Error executing tool"
    CONNECTION_FAILED = "Cannot connect to assistant server. Make sure it's running on {}"
    PARSE_ERROR = "Invalid JSON received"
    INTERNAL_ERROR = "Internal error"

# Log Messages
class LogMessages:
    API_AUTHENTICATED = "Assistant API authenticated user: {}"
    API_RECEIVED_DATA = "Assistant API received data: {}"
    METHOD_PARAMS = "Assistant Method: {}, Params: {}"
    TOOLS_LIST_REQUEST = "Handling tools/list request with streaming protocol"
    PROMPTS_LIST_REQUEST = "Handling prompts/list request"
    PROMPTS_GET_REQUEST = "Handling prompts/get request with params: {}"
    TOOL_CALL_REQUEST = "Handling tools/call request with params: {}"
    TOOL_EXECUTION = "Executing tool: {} with args: {}"
    FORCE_LOADING = "FORCING manual tool loading..."
    FORCE_IMPORT_SUCCESS = "FORCE: AnalysisTools imported successfully"
    FORCE_LOADING_COMPLETE = "FORCE: Manual loading complete. Total manual tools: {}"
    
# Success Messages
class SuccessMessages:
    ANALYSIS_COMPLETED = "Analysis completed successfully"
    TOOLS_LOADED = "Loaded {} {} tools"
    ARTIFACT_CREATED = "Analysis results formatted for artifact creation"
    SERVER_STARTED = "Assistant Server started successfully"
    
# Tool Descriptions
class ToolDescriptions:
    EXECUTE_PYTHON_CODE = """Execute custom Python code for advanced data analysis, calculations, and business logic with full access to Frappe framework and extensive library ecosystem.

🔐 **SECURITY:** Requires System Manager role. Executes in secure sandbox environment.

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
# Data analysis with pandas
import pandas as pd
data = frappe.get_all("Sales Invoice", fields=["grand_total", "posting_date"])
df = pd.DataFrame(data)
monthly_sales = df.groupby(pd.to_datetime(df['posting_date']).dt.month)['grand_total'].sum()
print(monthly_sales)

# Visualization with matplotlib
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
monthly_sales.plot(kind='bar')
plt.title('Monthly Sales Analysis')
plt.show()

# Advanced analysis with numpy
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
result = np.mean(arr)
print(f"Mean: {{result}}")

# Introspection
print("Available variables:", list(locals().keys()))
```

💡 ARTIFACT TIP: For extensive analysis workflows, stream results to artifacts for unlimited depth."""

    ANALYZE_FRAPPE_DATA = """Perform comprehensive statistical analysis on Frappe business data. Calculate averages, trends, correlations, and business insights from any DocType. Perfect for understanding sales patterns, customer behavior, and operational metrics.

💡 ARTIFACT TIP: Create workspace artifacts for comprehensive analysis without response limits."""

    QUERY_AND_ANALYZE = """Execute custom SQL queries on Frappe database and perform advanced data analysis. Perfect for complex business intelligence, custom reporting, and advanced analytics that go beyond standard reports.

💡 ARTIFACT TIP: For complex queries and analysis, use artifacts to build comprehensive reports."""

    CREATE_VISUALIZATION = """Create interactive charts and visualizations from Frappe business data. Charts are displayed inline and saved as files.

💡 ARTIFACT TIP: Document visualization workflows in artifacts for comprehensive reporting."""

# Prompt Templates
class PromptTemplates:
    ENFORCE_STREAMING = """I need to perform a {analysis_type} analysis on {data_source} using Frappe's analysis tools.

🔄 **ARTIFACT STREAMING REQUIREMENT:**
This analysis must be performed in a workspace artifact to:
• Prevent response limits during extensive analysis
• Create professional deliverables with unlimited depth
• Preserve analysis for future reference and sharing
• Enable comprehensive multi-step analytical workflows

Please create a workspace artifact and use Frappe's analysis tools (execute_python_code, analyze_frappe_data, query_and_analyze) to perform this analysis within the artifact environment.

The analysis should include:
- Data extraction and processing
- Statistical analysis and insights
- Visualizations if applicable
- Professional formatting for stakeholder presentation
- Complete documentation of methodology and findings

Begin by creating an artifact workspace for this analysis."""

    BI_REPORT = """Create a comprehensive business intelligence report focusing on {report_focus} for the {time_period} period.

📊 **ARTIFACT-BASED BI REPORT:**
This report must be created in a workspace artifact to ensure:
• Unlimited analysis depth without response truncation
• Professional deliverable formatting
• Stakeholder-ready presentation
• Comprehensive data exploration and insights

The report should include:

1. **Executive Summary**
   - Key findings and insights
   - Performance highlights
   - Critical recommendations

2. **Data Analysis**
   - Relevant Frappe data extraction
   - Statistical analysis and trends
   - Comparative analysis where applicable

3. **Visualizations**
   - Charts and graphs using analysis tools
   - Data visualization for key metrics
   - Professional formatting for presentations

4. **Insights & Recommendations**
   - Business implications
   - Actionable recommendations
   - Future considerations

5. **Methodology**
   - Data sources and extraction methods
   - Analysis techniques used
   - Assumptions and limitations

Please create an artifact workspace and build this comprehensive BI report using Frappe's analysis tools."""

    PYTHON_ANALYSIS = """I need to perform {complexity_level} Python analysis to achieve: {analysis_goal}

🔄 **ARTIFACT STREAMING APPROACH:**
This analysis must be executed in a workspace artifact to:
• Ensure unlimited analysis depth
• Prevent response limit interruptions
• Create professional deliverable documentation
• Enable complex multi-step analytical workflows

**Analysis Requirements:**
- Use Frappe's execute_python_code tool within the artifact
- Include comprehensive data processing and analysis
- Generate visualizations where appropriate
- Document methodology and findings professionally
- Create stakeholder-ready insights and recommendations

**Expected Workflow:**
1. Create dedicated artifact workspace
2. Define analysis scope and methodology
3. Execute comprehensive Python analysis using available libraries
4. Generate insights and visualizations
5. Document findings with professional formatting
6. Provide actionable recommendations

Please create an artifact workspace and perform this analysis using the execute_python_code tool with the full ecosystem of available libraries (pandas, numpy, matplotlib, seaborn, etc.)."""

# Configuration
class Config:
    DEFAULT_PORT = 8000
    DEFAULT_TIMEOUT = 30
    DEFAULT_LIMIT = 20
    MAX_RETRIES = 3
    CLEANUP_DAYS = 30
    
    # Analysis tool defaults
    DEFAULT_DATA_LIMIT = 1000
    PREVIEW_LINES = 8
    PREVIEW_VARIABLES = 5
    PREVIEW_RECORDS = 3