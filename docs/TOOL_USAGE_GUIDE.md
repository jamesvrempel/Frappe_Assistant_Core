# Frappe Assistant Core - Tool Usage Guide for LLMs

This guide provides comprehensive information about the Frappe Assistant Core tools in the plugin architecture to help LLMs make the most effective use of them when assisting users. 

**⚠️ Important**: This guide reflects the latest plugin-based architecture with improved tool organization, discovery, and management.

## Overview

The Frappe Assistant Core provides powerful tools for interacting with Frappe/ERPNext systems through a plugin-based architecture. These tools are organized in discoverable plugins and designed for business data analysis, document management, reporting, and visualization.

## Plugin-Based Tool Categories

### 📦 Core Plugin - Document Management Tools
**Plugin:** `core` (always enabled)  
**Primary Use Cases:** CRUD operations on business documents

#### `document_list` - 🔍 Primary Discovery Tool ✅ FIXED
- **When to use:** User asks about finding, searching, or listing any records
- **Key patterns:** "show me", "find", "list", "how many", "search for"
- **Recent Fix:** Now correctly returns documents instead of 0 records
- **Best practices:**
  - Always start with this tool for data exploration
  - Use specific fields to get relevant data: `["name", "customer_name", "grand_total"]`
  - Apply filters to narrow results: `{"status": "Paid", "company": "Your Company"}`
  - Set appropriate limits: 5-10 for previews, 50+ for comprehensive analysis
  - Tool now returns both `documents` and `results` keys for compatibility

#### `document_get` - 📋 Detailed Record Retrieval
- **When to use:** User wants details about a specific document they know the ID/name of
- **Key patterns:** "details about SINV-00001", "show me customer CUST-00001"

#### `document_create` - ✨ Record Creation
- **When to use:** User wants to add new records
- **Key patterns:** "create a new", "add a customer", "make an invoice"
- **Best practices:**
  - Always check required fields first using metadata tools
  - Include all mandatory fields in the data object
  - Use proper field names and data types

#### `document_update` - ✏️ Record Modification  
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

#### `report_execute` - 📈 Report Execution ✅ ENHANCED
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

### 🧪 Data Science Plugin - Analysis & Visualization Tools
**Plugin:** `data_science` (optional - enable through settings)  
**Primary Use Cases:** Statistical analysis and chart creation

#### `analyze_frappe_data` - 📈 Statistical Analysis
- **When to use:** User asks for insights, trends, statistical summaries
- **Key patterns:** "analyze", "trends", "average", "correlation", "insights"
- **Analysis types:**
  - `"summary"`: Basic statistics (mean, median, count)
  - `"correlation"`: Relationships between fields
  - `"distribution"`: Data spread and frequency
  - `"trends"`: Time-based patterns (requires date_field)

#### `create_visualization` - 📊 Chart Creation ✅ FIXED & ENHANCED
- **When to use:** User asks for charts, graphs, visual analysis
- **Key patterns:** "chart", "graph", "visualize", "plot", "show me visually"
- **Recent Fixes:** Charts now display inline in conversations using base64 encoding
- **New Features:** 
  - Inline display with `output_format: "inline"`
  - File saving with `output_format: "file"`
  - Both options with `output_format: "both"` (default)
- **Chart type guidance:**
  - `"bar"`: Comparisons (sales by customer, items by quantity)
  - `"line"`: Trends over time (monthly revenue, quarterly growth)
  - `"pie"`: Proportions (market share, category distribution)
  - `"scatter"`: Correlations (price vs quantity, revenue vs outstanding)
  - `"histogram"`: Distributions (invoice amounts, customer counts)
  - `"box"`: Statistical analysis (outliers, quartiles)

#### `execute_python_code` - 🐍 Custom Analysis
- **When to use:** Complex calculations, custom business logic, advanced analysis
- **Available libraries:** frappe, pandas, numpy, datetime
- **Best practices:**
  - Use data_query to pre-fetch data as DataFrame
  - Import additional libraries as needed
  - Write clear, well-commented code

#### `query_and_analyze` - 💾 Advanced SQL Analysis
- **When to use:** Complex queries beyond standard tools, custom reporting
- **Key patterns:** "complex analysis", "custom query", "join data", "advanced reporting"
- **Table naming:** Use Frappe convention: `tabSales Invoice`, `tabCustomer`, etc.

## Common Usage Patterns

### 🔍 Data Exploration Workflow
1. `document_list` → Discover available data
2. `analyze_frappe_data` → Get statistical insights
3. `create_visualization` → Create charts for visual analysis

### 📊 Business Intelligence Workflow
1. `report_list` → Find relevant reports
2. `report_execute` → Get report data
3. `create_visualization` → Visualize report results

### 🏗️ Document Management Workflow
1. `document_list` → Find existing records
2. `document_get` → Get detailed information
3. `document_update` / `document_create` → Modify or create records

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

### Field Selection
- **X-axis:** Categories (customer, item, territory, month)
- **Y-axis:** Numeric values (grand_total, qty, outstanding_amount)
- **Include both in data_source.fields**

### Chart Type Selection Guide
- **Revenue analysis:** Bar charts (customer vs grand_total)
- **Time trends:** Line charts (date vs values)
- **Market share:** Pie charts (territory distribution)
- **Correlations:** Scatter plots (outstanding vs grand_total)
- **Performance distribution:** Histograms (invoice amounts)

### Output Formats
- `"inline"`: For immediate viewing in conversation
- `"file"`: For downloadable charts
- `"both"`: Default - shows inline + saves file

## Error Handling & Debugging

### When document_list returns 0 records:
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
1. `report_list` (filter by "Sales")
2. `report_execute` ("Sales Analytics")
3. `create_visualization` (bar chart of sales by customer)

### "Find unpaid invoices"
1. `document_list` ("Sales Invoice", filters: {"outstanding_amount": [">", 0]})
2. `analyze_frappe_data` (summary of outstanding amounts)

### "Create a customer dashboard"
1. `document_list` (Customer data)
2. `execute_python_code` (calculate customer metrics)
3. `create_visualization` (multiple charts for different metrics)

## 🔧 Recent Fixes & Improvements

### Document List Tool (Fixed - December 2024)
**Issue**: Was returning 0 records despite data existing  
**Status**: ✅ FIXED - Now correctly returns document data  
**Impact**: All document discovery and listing operations now work as expected

### Visualization System (Enhanced - December 2024) 
**Issues**: Charts couldn't be displayed inline, "Unsupported image type" errors  
**Status**: ✅ FIXED - Charts now display directly in AI conversations  
**New Features**: Multiple output formats, base64 inline display, better error handling

### Report Execution (Enhanced - December 2024)
**Improvements**: Better debugging, automatic filter handling, comprehensive error reporting  
**Status**: ✅ ENHANCED - Reports now provide detailed feedback when issues occur

### Tool Descriptions (Updated - December 2024)
**Improvements**: All tool descriptions now include comprehensive usage guidance, examples, and best practices  
**Status**: ✅ UPDATED - LLMs now have much better context for tool usage

---

This guide helps LLMs provide more effective assistance by understanding tool capabilities, usage patterns, and best practices for Frappe business data analysis. All tools are now fully functional with recent fixes and improvements.