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

### 📊 Visualization & Business Intelligence Plugin - Dashboard & Chart Tools  
**Plugin:** `visualization` (always enabled)  
**Primary Use Cases:** Professional dashboards, charts, KPIs, and business intelligence  
**Total Tools:** 9 comprehensive visualization tools

#### `create_chart` - 📈 Individual Chart Creation ✅ COMPREHENSIVE
- **When to use:** User asks for specific charts, graphs, visual analysis
- **Key patterns:** "chart", "graph", "visualize", "plot", "show me a chart"
- **Chart Types Available:**
  - **Basic Charts:** bar, line, pie, scatter
  - **Statistical Charts:** histogram, box, heatmap, radar  
  - **Performance Charts:** gauge, funnel, waterfall, treemap
  - **Advanced Charts:** sunburst, sankey diagrams, network graphs
- **Features:**
  - Smart aggregation with sum/count/avg/min/max options
  - Time period filtering (current/last week/month/quarter/year)
  - Custom filtering and grouping
  - Multiple export formats (PNG, SVG, PDF, HTML, JSON)
  - Professional styling and color schemes
  - Interactive elements and responsive design

#### `create_kpi_card` - 📊 KPI Metric Cards
- **When to use:** User wants KPI tracking, performance indicators, metric cards
- **Key patterns:** "KPI", "metric card", "track performance", "show key metrics"
- **Features:**
  - Current value with trend indicators
  - Period-over-period comparisons
  - Target vs actual comparisons  
  - Professional color schemes (green/red/amber indicators)
  - Multiple format options (currency, percentage, number, decimal)

#### `create_insights_dashboard` - 🏗️ Multi-Chart Dashboard Creation
- **When to use:** User wants comprehensive dashboards with multiple charts
- **Key patterns:** "dashboard", "create a dashboard", "multiple charts", "overview"
- **Features:**
  - Combines multiple chart types in one dashboard
  - Insights app integration with Frappe Dashboard fallback
  - Auto-refresh capabilities
  - Mobile optimization
  - Team sharing and collaboration
  - Professional layouts and styling

#### `create_dashboard_from_template` - 🎯 Template-Based Dashboards ✅ BUSINESS-READY
- **When to use:** User wants quick professional dashboards for business domains
- **Key patterns:** "sales dashboard", "financial dashboard", "business analytics"
- **Available Templates:**
  - **Sales Template:** Revenue tracking, customer analysis, territory performance
  - **Financial Template:** P&L tracking, cash flow, expense analysis
  - **Inventory Template:** Stock monitoring, movement tracking, valuation
  - **HR Template:** Employee metrics, department analysis, attendance
  - **Executive Template:** High-level KPIs, growth tracking, strategic metrics
- **Customization Options:**
  - Override primary DocType
  - Custom time periods
  - Additional filters and modifications
  - Chart additions/removals

#### `create_bi_dashboard` - 🎯 Professional Business Intelligence ✅ INDUSTRY-STANDARD
- **When to use:** User needs industry-standard BI dashboards with professional KPIs
- **Key patterns:** "business intelligence", "professional dashboard", "industry standard"
- **Business Domains:**
  - **Sales:** Revenue Growth Rate, Sales Velocity, Win Rate, Average Deal Size
  - **Finance:** Gross Margin, Operating Cash Flow, Current Ratio, DSO
  - **Operations:** OEE, Cycle Time, Quality Rate, On-Time Delivery
  - **HR:** Employee Retention, Time to Hire, Training ROI, Engagement Score
  - **Executive:** Revenue Growth, Profit Margin, Market Share, Customer Satisfaction
- **Features:**
  - Modern Frappe Workspace integration
  - Industry benchmarks and targets
  - Executive/Management/Operational detail levels
  - Professional BI layout principles

#### `get_bi_recommendations` - 💡 BI Best Practices
- **When to use:** User needs guidance on professional dashboard creation
- **Key patterns:** "dashboard recommendations", "best practices", "how to create good dashboards"
- **Provides:**
  - Domain-specific KPI recommendations
  - Audience-appropriate design principles
  - Implementation best practices
  - Common mistakes to avoid
  - Next steps and action items

#### `list_user_dashboards` - 📋 Dashboard Management
- **When to use:** User wants to see existing dashboards
- **Key patterns:** "my dashboards", "list dashboards", "show dashboards"
- **Features:**
  - Lists owned and shared dashboards
  - Filters by dashboard type (insights/frappe)
  - Shows access permissions and creation dates

#### `clone_dashboard` - 📄 Dashboard Duplication
- **When to use:** User wants to copy and modify existing dashboards
- **Key patterns:** "copy dashboard", "clone", "duplicate dashboard"
- **Features:**
  - Copies all charts and configurations
  - Optional filter modifications
  - Permission copying options
  - Chart customization during cloning

#### `list_dashboard_templates` - 📚 Template Discovery
- **When to use:** User wants to see available dashboard templates
- **Key patterns:** "available templates", "dashboard templates", "what templates"
- **Features:**
  - Lists all business templates with descriptions
  - Shows required permissions and features
  - Category filtering (business/technical/custom)

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
3. `create_chart` → Create individual charts for visual analysis

### 📊 Business Intelligence Workflow
1. `generate_report` → Get business report data
2. `create_bi_dashboard` → Create professional BI dashboard
3. `get_bi_recommendations` → Get improvement suggestions

### 🎯 Quick Dashboard Creation Workflow
1. `list_dashboard_templates` → See available templates
2. `create_dashboard_from_template` → Create from business template
3. `clone_dashboard` → Customize for specific needs

### 🏗️ Document Management Workflow
1. `list_documents` → Find existing records
2. `get_document` → Get detailed information
3. `update_document` / `create_document` → Modify or create records

### 📈 Performance Tracking Workflow
1. `list_documents` → Get KPI data
2. `create_kpi_card` → Create metric cards with trends
3. `create_insights_dashboard` → Combine into comprehensive dashboard

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

### Chart Creation Guidelines (`create_chart`)
- **X-axis:** Categories (customer, item, territory, month)  
- **Y-axis:** Numeric values (grand_total, qty, outstanding_amount)
- **Chart Type Selection:**
  - **Revenue analysis:** Bar charts (customer vs grand_total)
  - **Time trends:** Line charts (posting_date vs values)
  - **Market share:** Pie charts (territory distribution)  
  - **Correlations:** Scatter plots (outstanding vs grand_total)
  - **Performance distribution:** Histograms (invoice amounts)
- **Export Formats:** PNG, SVG, PDF, HTML, JSON
- **Time Filtering:** Use time_span for automatic date filtering

### Dashboard Creation Guidelines
- **Template-based:** Use `create_dashboard_from_template` for quick business dashboards
- **Custom dashboards:** Use `create_insights_dashboard` for multi-chart layouts  
- **Professional BI:** Use `create_bi_dashboard` for industry-standard metrics
- **KPI tracking:** Use `create_kpi_card` for performance indicators with trends

### Business Intelligence Best Practices
- **Executive dashboards:** 5-7 key metrics maximum (use `create_bi_dashboard` with executive level)
- **Management dashboards:** 8-12 metrics with detailed comparisons  
- **Operational dashboards:** Real-time data with drill-down capabilities
- **Color schemes:** Use consistent Red/Amber/Green indicators
- **Mobile optimization:** Always enable for responsive design

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
2. `create_chart` (bar chart of sales by customer)
3. `create_kpi_card` (revenue trend card)

### "Create a professional sales dashboard"
1. `create_dashboard_from_template` (template: "sales")
2. `get_bi_recommendations` (for improvement suggestions)
3. `clone_dashboard` (create customized version)

### "I need business intelligence for executives"
1. `create_bi_dashboard` (domain: "executive", audience: "executive")  
2. `list_user_dashboards` (view created dashboard)
3. `get_bi_recommendations` (get executive dashboard best practices)

### "Find unpaid invoices and visualize them"
1. `list_documents` ("Sales Invoice", filters: {"outstanding_amount": [">", 0]})
2. `create_chart` (bar chart of outstanding by customer)
3. `create_kpi_card` (total outstanding amount with trends)

### "Set up performance tracking"
1. `create_kpi_card` (key performance metrics)
2. `create_insights_dashboard` (combine multiple KPI cards)  
3. `clone_dashboard` (create variations for different teams)

## 🔧 Recent Fixes & Improvements

### Document List Tool (Fixed - December 2024)
**Issue**: Was returning 0 records despite data existing  
**Status**: ✅ FIXED - Now correctly returns document data  
**Impact**: All document discovery and listing operations now work as expected

### Visualization System Architecture (Restructured - January 2025) ✅ MAJOR UPDATE
**Issues**: Tools architecture didn't follow one-tool-per-file pattern, missing tools from API  
**Status**: ✅ COMPLETELY RESTRUCTURED - All visualization tools now follow proper architecture  
**Changes**:
- **Split combined files:** Separated 4 combined files into 10 individual tool files
- **Fixed tool registration:** All 9 visualization tools now properly returned by API
- **Improved organization:** Clear naming conventions and proper imports
- **Enhanced functionality:** Maintained all features while fixing architecture

**New Tool Files:**
- `create_chart.py` - Individual chart creation
- `create_kpi_card.py` - KPI metric cards
- `create_insights_dashboard.py` - Multi-chart dashboards  
- `create_dashboard_from_template.py` - Business templates
- `create_bi_dashboard.py` - Professional BI dashboards
- `get_bi_recommendations.py` - BI best practices
- `list_user_dashboards.py` - Dashboard management
- `list_dashboard_templates.py` - Template discovery
- `clone_dashboard.py` - Dashboard duplication

### Business Intelligence Tools (Added - January 2025) ✅ NEW FEATURES
**Status**: ✅ ADDED - Professional BI capabilities with industry-standard KPIs  
**Features**:
- **Industry-standard KPIs:** Sales, Finance, Operations, HR, Executive domains
- **Professional layouts:** Modern Frappe Workspace integration
- **Audience-appropriate detail:** Executive, Management, Operational levels
- **Best practices guidance:** Comprehensive BI recommendations

### Report Execution (Enhanced - December 2024)
**Improvements**: Better debugging, automatic filter handling, comprehensive error reporting  
**Status**: ✅ ENHANCED - Reports now provide detailed feedback when issues occur

### Tool Descriptions (Updated - December 2024)
**Improvements**: All tool descriptions now include comprehensive usage guidance, examples, and best practices  
**Status**: ✅ UPDATED - LLMs now have much better context for tool usage

---

## 📊 Current Tool Summary (January 2025)

**Total Available Tools**: 23 tools across 3 categories
- **Core Operations**: 11 tools (document management, reports, workflows)
- **Visualization & BI**: 9 tools (dashboards, charts, KPIs, templates) ✅ COMPLETE
- **Data Science**: 3 tools (analysis, Python code, SQL queries)

This guide reflects the latest tool architecture and capabilities. All visualization tools are now fully functional with proper one-tool-per-file architecture and comprehensive business intelligence features.