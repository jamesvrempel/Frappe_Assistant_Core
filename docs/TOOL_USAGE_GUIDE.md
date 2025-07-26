# Frappe Assistant Core - Tool Usage Guide for LLMs

This guide provides comprehensive information about the Frappe Assistant Core tools in the plugin architecture to help LLMs make the most effective use of them when assisting users. 

**⚠️ Important**: This guide reflects the latest plugin-based architecture with improved tool organization, discovery, and management.

## Overview

The Frappe Assistant Core provides powerful tools for interacting with Frappe/ERPNext systems through a plugin-based architecture. These tools are organized in discoverable plugins and designed for business data analysis, document management, reporting, and visualization.

## Plugin-Based Tool Categories

### 📦 Core Plugin - Document Management Tools
**Plugin:** `core` (always enabled)  
**Primary Use Cases:** CRUD operations on business documents

#### `list_documents` - 🔍 Primary Discovery Tool ✅ FIXED
- **When to use:** User asks about finding, searching, or listing any records
- **Key patterns:** "show me", "find", "list", "how many", "search for"
- **Recent Fix:** Now correctly returns documents instead of 0 records
- **Best practices:**
  - Always start with this tool for data exploration
  - Use specific fields to get relevant data: `["name", "customer_name", "grand_total"]`
  - Apply filters to narrow results: `{"status": "Paid", "company": "Your Company"}`
  - Set appropriate limits: 5-10 for previews, 50+ for comprehensive analysis
  - Tool now returns both `documents` and `results` keys for compatibility

#### `get_document` - 📋 Detailed Record Retrieval
- **When to use:** User wants details about a specific document they know the ID/name of
- **Key patterns:** "details about SINV-00001", "show me customer CUST-00001"

#### `create_document` - ✨ Record Creation
- **When to use:** User wants to add new records
- **Key patterns:** "create a new", "add a customer", "make an invoice"
- **Best practices:**
  - Always check required fields first using metadata tools
  - Include all mandatory fields in the data object
  - Use proper field names and data types

#### `update_document` - ✏️ Record Modification  
- **When to use:** User wants to modify existing records
- **Key patterns:** "update", "change", "modify", "edit"
- **Best practices:**
  - Fetch the document first to understand current values
  - Only include fields that need to be changed

### 📦 Core Plugin - Report & Analytics Tools
**Plugin:** `core` (always enabled)  
**Primary Use Cases:** Business intelligence and data analysis

#### `report_list` - 📋 Report Discovery
- **When to use:** User asks for reports, analytics, or when you need to find available reports
- **Key patterns:** "reports", "analytics", "financial data", "sales analysis"

#### `generate_report` - 📈 Report Execution ✅ ENHANCED
- **When to use:** User wants to run business reports for insights
- **Key patterns:** "run the", "execute", "show me the [report name]"
- **Recent Enhancements:** Improved error handling and debugging information
- **Best practices:**
  - Always check report_list first if unsure of report names
  - Include common filters like `{"company": "Your Company"}`
  - Use date ranges for time-based reports: `{"from_date": "2024-01-01", "to_date": "2024-12-31"}`
  - Tool now provides detailed debug info when reports return empty results

#### `report_columns` - 🔍 Report Structure Analysis
- **When to use:** You need to understand report fields before execution or visualization
- **Best practices:** Use before creating visualizations from report data

### 📊 Visualization Plugin - Dashboard & Chart Tools  
**Plugin:** `visualization` (optional - enable through settings)  
**Primary Use Cases:** Professional dashboards and chart creation  
**Total Tools:** 3 essential visualization tools

#### `create_dashboard` - 🏗️ Frappe Dashboard Creation
- **When to use:** User wants comprehensive dashboards with multiple charts
- **Key patterns:** "dashboard", "create a dashboard", "multiple charts", "overview"
- **Features:**
  - Creates Frappe Dashboard documents (not Insights dashboards)
  - Combines multiple chart types in one dashboard
  - Professional layouts and styling
  - Chart configuration with proper mappings
  - Time series support with date field detection
- **Best practices:**
  - Provide multiple chart_configs for comprehensive dashboards
  - Use appropriate chart types (bar, line, pie, donut, percentage, heatmap)
  - Include time series configuration for time-based data

#### `create_dashboard_chart` - 📈 Individual Chart Creation
- **When to use:** User asks for specific charts for dashboards
- **Key patterns:** "chart", "graph", "visualize", "plot", "show me a chart for dashboard"
- **Chart Types Available:**
  - **Basic Charts:** bar, line, pie, donut, percentage, heatmap
- **Features:**
  - Creates Dashboard Chart documents (not base64 images)
  - Proper time series configuration for line charts
  - Auto-detection of suitable date fields for time series
  - Field validation using DocType metadata
  - Can add charts to existing dashboards
- **Best practices:**
  - Use time_series configuration for time-based charts
  - Validate that fields exist in the target DocType
  - Use appropriate aggregation functions (Sum, Count, Average)

#### `list_user_dashboards` - 📋 Dashboard Management
- **When to use:** User wants to see existing dashboards
- **Key patterns:** "my dashboards", "list dashboards", "show dashboards"
- **Features:**
  - Lists user's accessible Frappe dashboards
  - Shows dashboard names and basic information
  - Helps users discover existing dashboard resources

### 🧪 Data Science Plugin - Advanced Analysis Tools  
**Plugin:** `data_science` (optional - enable through settings)  
**Primary Use Cases:** Statistical analysis and custom code execution

#### `analyze_business_data` - 📈 Statistical Analysis
- **When to use:** User asks for insights, trends, statistical summaries
- **Key patterns:** "analyze", "trends", "average", "correlation", "insights"
- **Analysis types:**
  - `"profile"`: Complete data profiling with statistics
  - `"statistics"`: Basic statistics (mean, median, count)
  - `"correlations"`: Relationships between fields
  - `"trends"`: Time-based patterns (requires date_field)
  - `"quality"`: Data quality assessment

#### `run_python_code` - 🐍 Custom Analysis ✅ ENHANCED
- **When to use:** Complex calculations, custom business logic, advanced analysis
- **Available libraries:** frappe, pandas, numpy, matplotlib, seaborn, datetime
- **Features:**
  - Data query integration for pre-loading DataFrames
  - Artifact streaming for large results
  - Execution timeout and error handling
  - Variable return capabilities
- **Best practices:**
  - Use data_query to pre-fetch data as DataFrame
  - Stream detailed work to artifacts
  - Keep responses minimal with artifact references

#### `run_database_query` - 💾 Advanced SQL Analysis ✅ SECURE
- **When to use:** Complex queries beyond standard tools, custom reporting
- **Key patterns:** "complex analysis", "custom query", "join data", "advanced reporting"
- **Features:**
  - SELECT-only queries for security
  - Query validation and optimization
  - Statistical analysis of results
  - Schema information inclusion
- **Table naming:** Use Frappe convention: `tabSales Invoice`, `tabCustomer`, etc.

## Common Usage Patterns

### 🔍 Data Exploration Workflow
1. `list_documents` → Discover available data
2. `analyze_business_data` → Get statistical insights  
3. `create_dashboard_chart` → Create individual charts for visual analysis

### 📊 Dashboard Creation Workflow
1. `generate_report` → Get business report data
2. `create_dashboard` → Create comprehensive dashboard with multiple charts
3. `list_user_dashboards` → View and manage created dashboards

### 🎯 Chart-First Dashboard Workflow
1. `create_dashboard_chart` → Create individual charts
2. `create_dashboard` → Combine charts into dashboard
3. `list_user_dashboards` → Manage dashboard collection

### 🏗️ Document Management Workflow
1. `list_documents` → Find existing records
2. `get_document` → Get detailed information
3. `update_document` / `create_document` → Modify or create records

### 📈 Performance Tracking Workflow
1. `list_documents` → Get performance data
2. `create_dashboard_chart` → Create metric charts with trends
3. `create_dashboard` → Combine into comprehensive dashboard

## Field Name Guidelines

### Common DocType Examples
- **Sales Invoice:** `customer`, `grand_total`, `outstanding_amount`, `posting_date`, `status`
- **Customer:** `customer_name`, `customer_type`, `territory`, `customer_group`
- **Item:** `item_name`, `item_code`, `item_group`, `standard_rate`, `stock_uom`
- **Purchase Order:** `supplier`, `grand_total`, `transaction_date`, `status`

### Filter Examples
```python
# Date filters
{"creation": [">", "2024-01-01"]}
{"posting_date": ["between", ["2024-01-01", "2024-12-31"]]}

# Status filters
{"status": "Paid"}
{"docstatus": 1}  # Submitted documents

# Numeric filters
{"grand_total": [">", 1000]}
{"outstanding_amount": [">", 0]}

# Text filters
{"customer": ["like", "%Corp%"]}
{"item_group": "Products"}
```

## Visualization Best Practices

### Chart Creation Guidelines (`create_dashboard_chart`)
- **Chart Types:** bar, line, pie, donut, percentage, heatmap
- **Chart Type Selection:**
  - **Revenue analysis:** Bar charts (customer vs grand_total)
  - **Time trends:** Line charts with time series (posting_date vs values)
  - **Market share:** Pie or donut charts (territory distribution)  
  - **Performance metrics:** Percentage charts for ratios
  - **Correlation data:** Heatmap charts for multi-dimensional data
- **Time Series Configuration:** Include `time_series_based_on` field for time-based charts
- **Field Validation:** Ensure fields exist in target DocType before chart creation

### Dashboard Creation Guidelines (`create_dashboard`)
- **Multi-chart approach:** Use `create_dashboard` for comprehensive dashboards with multiple charts
- **Chart combination:** Mix different chart types (bar, line, pie) for diverse insights
- **Time series support:** Include proper date field configuration for temporal data
- **Field mapping:** Use correct chart type mappings (Bar→Bar, Line→Line, etc.)

### Dashboard Best Practices
- **Executive dashboards:** 5-7 key charts maximum for clarity
- **Management dashboards:** 8-12 charts with detailed comparisons  
- **Operational dashboards:** Real-time data with appropriate refresh settings
- **Chart organization:** Group related metrics together in dashboard layout

## Error Handling & Debugging

### When list_documents returns 0 records:
- Enable debug mode: `"debug": true`
- Check filters for typos
- Verify DocType name exists
- Try without filters first

### When reports fail:
- Check exact report name with report_list
- Include required filters (often company, date ranges)
- Verify user permissions

### When visualizations fail:
- Ensure fields exist in the data
- Check data types (numeric for Y-axis)
- Verify sufficient data records

## Advanced Tips

### Performance Optimization
- Use specific fields instead of fetching all
- Apply filters to reduce data volume
- Set appropriate limits for large datasets

### Data Quality
- Check for null values in numeric fields
- Validate date ranges
- Handle text encoding issues

### Business Context
- Always include company filters for multi-company setups
- Consider fiscal year for financial reports
- Account for different user permissions

## Example User Scenarios

### "Show me sales analysis"
1. `generate_report` ("Sales Analytics")
2. `create_dashboard_chart` (bar chart of sales by customer)
3. `create_dashboard` (combine multiple sales charts)

### "Create a comprehensive sales dashboard"
1. `list_documents` ("Sales Invoice") to understand data structure
2. `create_dashboard` (multi-chart dashboard with revenue, customer, and trend analysis)
3. `list_user_dashboards` (view and manage created dashboard)

### "I need charts for my business presentation"
1. `create_dashboard_chart` (revenue trend line chart with time series)
2. `create_dashboard_chart` (customer distribution pie chart)
3. `create_dashboard` (combine charts into presentation dashboard)

### "Find unpaid invoices and visualize them"
1. `list_documents` ("Sales Invoice", filters: {"outstanding_amount": [">", 0]})
2. `create_dashboard_chart` (bar chart of outstanding by customer)
3. `create_dashboard` (dashboard with outstanding analysis charts)

### "Set up performance tracking dashboard"
1. `create_dashboard_chart` (key performance metrics charts)
2. `create_dashboard` (combine multiple performance charts)  
3. `list_user_dashboards` (manage dashboard collection)

## 🔧 Recent Fixes & Improvements

### Document List Tool (Fixed - December 2024)
**Issue**: Was returning 0 records despite data existing  
**Status**: ✅ FIXED - Now correctly returns document data  
**Impact**: All document discovery and listing operations now work as expected

### Visualization System Cleanup (Restructured - January 2025) ✅ MAJOR CLEANUP
**Issues**: Too many redundant tools, misleading names, chart creation problems  
**Status**: ✅ COMPLETELY CLEANED UP - Streamlined to 3 essential visualization tools  
**Changes**:
- **Tool consolidation:** Removed 8 redundant tools, kept 3 essential ones
- **Fixed chart creation:** Proper time series support and field validation
- **Clarified naming:** Tools now accurately reflect what they create
- **Enhanced functionality:** Better error handling and field mapping

**Final Tool Set:**
- `create_dashboard.py` - Create Frappe dashboards with multiple charts
- `create_dashboard_chart.py` - Create individual Dashboard Chart documents  
- `list_user_dashboards.py` - List user's accessible dashboards

**Removed Tools:** create_bi_dashboard, create_dashboard_from_template, clone_dashboard, create_chart, create_kpi_card, get_bi_recommendations, list_dashboard_templates, chart_recommendations

### Report Execution (Enhanced - December 2024)
**Improvements**: Better debugging, automatic filter handling, comprehensive error reporting  
**Status**: ✅ ENHANCED - Reports now provide detailed feedback when issues occur

### Tool Descriptions (Updated - December 2024)
**Improvements**: All tool descriptions now include comprehensive usage guidance, examples, and best practices  
**Status**: ✅ UPDATED - LLMs now have much better context for tool usage

---

## 📊 Current Tool Summary (January 2025)

**Total Available Tools**: 17 tools across 3 categories
- **Core Operations**: 11 tools (document management, reports, workflows)
- **Visualization**: 3 tools (dashboards, charts, dashboard management) ✅ STREAMLINED
- **Data Science**: 3 tools (analysis, Python code, SQL queries)

This guide reflects the latest streamlined tool architecture. The visualization plugin has been cleaned up to focus on essential functionality with proper chart creation and dashboard management capabilities.