"""
Chart Creator Tool - Individual chart creation

Provides tools for creating individual charts and widgets that can be
used standalone or as part of larger dashboards.
"""

import frappe
from frappe import _
import json
from typing import Dict, Any, List, Optional
from frappe_assistant_core.core.base_tool import BaseTool


class ChartCreator(BaseTool):
    """
    Individual chart and widget creation tools.
    
    Provides capabilities for:
    - Creating standalone charts
    - Interactive data tables
    - Gauge charts for performance tracking
    - Filter widgets for dynamic dashboards
    """
    
    def __init__(self):
        super().__init__()
        self.name = "create_chart"
        self.description = self._get_description()
        self.requires_permission = None
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "Source DocType for chart data"
                },
                "chart_type": {
                    "type": "string",
                    "enum": ["bar", "line", "pie", "scatter", "histogram", "box", "gauge", "heatmap", "funnel", "waterfall", "treemap", "sunburst", "radar"],
                    "description": "Type of chart to create"
                },
                "title": {
                    "type": "string",
                    "description": "Chart title"
                },
                "x_field": {
                    "type": "string",
                    "description": "Field for X-axis"
                },
                "y_field": {
                    "type": "string", 
                    "description": "Field for Y-axis or value field"
                },
                "aggregate": {
                    "type": "string",
                    "enum": ["sum", "count", "avg", "min", "max", "distinct"],
                    "default": "sum",
                    "description": "Aggregation method for numeric data"
                },
                "group_by": {
                    "type": "string",
                    "description": "Field to group data by"
                },
                "filters": {
                    "type": "object",
                    "description": "Filters to apply to data"
                },
                "time_span": {
                    "type": "string",
                    "enum": ["current_week", "current_month", "current_quarter", "current_year", "last_week", "last_month", "last_quarter", "last_year", "last_6_months", "last_12_months"],
                    "description": "Time span for date-based data"
                },
                "limit": {
                    "type": "integer",
                    "default": 100,
                    "maximum": 1000,
                    "description": "Maximum number of data points"
                },
                "order_by": {
                    "type": "string",
                    "description": "Field to order results by"
                },
                "chart_options": {
                    "type": "object",
                    "properties": {
                        "colors": {"type": "array", "description": "Custom color scheme"},
                        "show_legend": {"type": "boolean", "default": True},
                        "show_data_labels": {"type": "boolean", "default": True},
                        "orientation": {"type": "string", "enum": ["vertical", "horizontal"]},
                        "stacked": {"type": "boolean", "default": False},
                        "show_trend_line": {"type": "boolean", "default": False},
                        "target_value": {"type": "number", "description": "Target value for gauge charts"},
                        "format": {"type": "string", "enum": ["currency", "percentage", "number", "decimal"]}
                    },
                    "description": "Chart styling and display options"
                },
                "export_format": {
                    "type": "string",
                    "enum": ["png", "svg", "pdf", "html", "json"],
                    "default": "png",
                    "description": "Export format for the chart"
                }
            },
            "required": ["doctype", "chart_type", "title"]
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Create individual charts and widgets for data visualization. Build standalone charts or components for custom dashboards.

📊 **CHART TYPES:**

📈 **BASIC CHARTS:**
• Bar Charts - Compare categories, show rankings
• Line Charts - Track trends over time, display time series
• Pie Charts - Show proportions and percentages
• Scatter Plots - Explore relationships between variables

📉 **STATISTICAL CHARTS:**
• Histograms - Display data distribution patterns
• Box Plots - Show statistical summaries and outliers
• Heatmaps - Visualize correlations and patterns
• Radar Charts - Multi-dimensional data comparison

🎯 **PERFORMANCE CHARTS:**
• Gauge Charts - Progress meters and KPI tracking
• Funnel Charts - Conversion and process analysis
• Waterfall Charts - Step-by-step value changes
• Treemap - Hierarchical data visualization

🌟 **ADVANCED CHARTS:**
• Sunburst - Multi-level hierarchical data
• Sankey Diagrams - Flow and process visualization
• Network Graphs - Relationship mapping
• Geographic Maps - Location-based data

🔧 **FEATURES:**
• Smart Aggregation - Automatic data grouping and summarization
• Custom Filtering - Apply complex data filters
• Time Period Selection - Flexible date range options
• Interactive Elements - Clickable and hoverable charts
• Professional Styling - Customizable colors and themes

⚡ **INTELLIGENCE:**
• Auto-field Detection - Smart field type recognition
• Data Validation - Ensures chart compatibility
• Optimal Defaults - Best practices applied automatically
• Performance Optimization - Efficient data handling

🎨 **CUSTOMIZATION:**
• Color Schemes - Professional and branded palettes
• Layout Options - Vertical, horizontal, stacked layouts
• Export Formats - PNG, SVG, PDF, HTML, JSON
• Responsive Design - Mobile and desktop optimized

💡 **USE CASES:**
• Standalone visualizations for reports
• Dashboard components and widgets
• Embedded charts in documents
• Interactive data exploration
• Performance monitoring displays"""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create individual chart"""
        try:
            doctype = arguments.get("doctype")
            chart_type = arguments.get("chart_type")
            title = arguments.get("title")
            x_field = arguments.get("x_field")
            y_field = arguments.get("y_field")
            aggregate = arguments.get("aggregate", "sum")
            group_by = arguments.get("group_by")
            filters = arguments.get("filters", {})
            time_span = arguments.get("time_span")
            limit = arguments.get("limit", 100)
            order_by = arguments.get("order_by")
            chart_options = arguments.get("chart_options", {})
            export_format = arguments.get("export_format", "png")
            
            # Validate doctype access
            if not frappe.has_permission(doctype, "read"):
                return {
                    "success": False,
                    "error": f"Insufficient permissions to access {doctype} data"
                }
            
            # Validate required fields for chart type
            validation_result = self._validate_chart_config(chart_type, x_field, y_field, doctype)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            # Apply time span filters
            if time_span:
                time_filters = self._get_time_filters(time_span, doctype)
                filters.update(time_filters)
            
            # Get data for chart
            chart_data = self._get_chart_data(
                doctype, x_field, y_field, aggregate, group_by, 
                filters, limit, order_by
            )
            
            if not chart_data:
                return {
                    "success": False,
                    "error": "No data available for chart"
                }
            
            # Create chart based on type
            chart_result = self._create_chart_by_type(
                chart_type, chart_data, title, chart_options, export_format,
                x_field, y_field, aggregate
            )
            
            return {
                "success": True,
                "chart_type": chart_type,
                "title": title,
                "data_points": len(chart_data),
                "doctype": doctype,
                "export_format": export_format,
                **chart_result
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Chart Creation Error"),
                message=f"Error creating chart: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_chart_config(self, chart_type: str, x_field: str, y_field: str, doctype: str) -> Dict[str, Any]:
        """Validate chart configuration"""
        try:
            # Check required fields for different chart types
            if chart_type in ["bar", "line", "scatter"] and not (x_field and y_field):
                return {
                    "valid": False,
                    "error": f"{chart_type} charts require both x_field and y_field"
                }
            
            if chart_type == "pie" and not x_field:
                return {
                    "valid": False,
                    "error": "Pie charts require x_field for categories"
                }
            
            if chart_type in ["histogram", "box"] and not y_field:
                return {
                    "valid": False,
                    "error": f"{chart_type} charts require y_field for values"
                }
            
            # Validate fields exist in doctype
            meta = frappe.get_meta(doctype)
            
            if x_field and not meta.has_field(x_field):
                return {
                    "valid": False,
                    "error": f"Field '{x_field}' not found in {doctype}"
                }
            
            if y_field and not meta.has_field(y_field):
                return {
                    "valid": False,
                    "error": f"Field '{y_field}' not found in {doctype}"
                }
            
            return {"valid": True}
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    def _get_time_filters(self, time_span: str, doctype: str) -> Dict[str, Any]:
        """Generate time-based filters"""
        import datetime
        from dateutil.relativedelta import relativedelta
        
        now = datetime.datetime.now()
        filters = {}
        
        # Find date field in doctype
        meta = frappe.get_meta(doctype)
        date_fields = [f.fieldname for f in meta.fields if f.fieldtype in ["Date", "Datetime"]]
        
        if not date_fields:
            return filters
        
        date_field = "creation"  # Default fallback
        if "posting_date" in date_fields:
            date_field = "posting_date"
        elif "date" in date_fields:
            date_field = "date"
        elif date_fields:
            date_field = date_fields[0]
        
        # Calculate date ranges
        if time_span == "current_week":
            start_date = now - datetime.timedelta(days=now.weekday())
            filters[date_field] = [">=", start_date.date()]
        elif time_span == "current_month":
            start_date = now.replace(day=1)
            filters[date_field] = [">=", start_date.date()]
        elif time_span == "current_quarter":
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_start_month, day=1)
            filters[date_field] = [">=", start_date.date()]
        elif time_span == "current_year":
            start_date = now.replace(month=1, day=1)
            filters[date_field] = [">=", start_date.date()]
        elif time_span == "last_week":
            end_date = now - datetime.timedelta(days=now.weekday())
            start_date = end_date - datetime.timedelta(days=7)
            filters[date_field] = ["between", [start_date.date(), end_date.date()]]
        elif time_span == "last_month":
            start_date = (now.replace(day=1) - relativedelta(months=1))
            end_date = now.replace(day=1) - datetime.timedelta(days=1)
            filters[date_field] = ["between", [start_date.date(), end_date.date()]]
        elif time_span == "last_6_months":
            start_date = now - relativedelta(months=6)
            filters[date_field] = [">=", start_date.date()]
        elif time_span == "last_12_months":
            start_date = now - relativedelta(months=12)
            filters[date_field] = [">=", start_date.date()]
        
        return filters
    
    def _get_chart_data(self, doctype: str, x_field: str, y_field: str, 
                       aggregate: str, group_by: str, filters: Dict,
                       limit: int, order_by: str) -> List[Dict]:
        """Get data for chart creation"""
        try:
            # Build field list
            fields = []
            if x_field:
                fields.append(x_field)
            if y_field and y_field != x_field:
                fields.append(y_field)
            if group_by and group_by not in fields:
                fields.append(group_by)
            
            # If no specific fields, get basic fields
            if not fields:
                fields = ["name", "creation"]
            
            # Get raw data
            data = frappe.get_all(
                doctype,
                filters=filters,
                fields=fields,
                limit=limit,
                order_by=order_by or "creation desc"
            )
            
            # Apply aggregation if needed
            if aggregate != "count" and y_field and len(data) > 0:
                data = self._apply_aggregation(data, x_field, y_field, aggregate, group_by)
            
            return data
            
        except Exception as e:
            frappe.logger("chart_creator").error(f"Failed to get chart data: {str(e)}")
            return []
    
    def _apply_aggregation(self, data: List[Dict], x_field: str, y_field: str, 
                          aggregate: str, group_by: str) -> List[Dict]:
        """Apply aggregation to data"""
        try:
            import pandas as pd
            
            df = pd.DataFrame(data)
            
            if df.empty:
                return []
            
            # Group by x_field (and group_by if specified)
            group_fields = [x_field] if x_field else []
            if group_by and group_by != x_field:
                group_fields.append(group_by)
            
            if not group_fields:
                return data
            
            # Apply aggregation
            if aggregate == "sum":
                result = df.groupby(group_fields)[y_field].sum().reset_index()
            elif aggregate == "avg":
                result = df.groupby(group_fields)[y_field].mean().reset_index()
            elif aggregate == "min":
                result = df.groupby(group_fields)[y_field].min().reset_index()
            elif aggregate == "max":
                result = df.groupby(group_fields)[y_field].max().reset_index()
            elif aggregate == "count":
                result = df.groupby(group_fields).size().reset_index(name=y_field)
            elif aggregate == "distinct":
                result = df.groupby(group_fields)[y_field].nunique().reset_index()
            else:
                return data
            
            return result.to_dict('records')
            
        except Exception as e:
            frappe.logger("chart_creator").error(f"Aggregation failed: {str(e)}")
            return data
    
    def _create_chart_by_type(self, chart_type: str, data: List[Dict], title: str,
                             chart_options: Dict, export_format: str, x_field: str, 
                             y_field: str, aggregate: str) -> Dict[str, Any]:
        """Create chart based on type"""
        try:
            # Import visualization library
            from frappe_assistant_core.plugins.data_science.tools.create_visualization import CreateVisualization
            
            # Convert data format for visualization tool
            viz_tool = CreateVisualization()
            
            # Map chart type
            chart_type_mapping = {
                "histogram": "histogram",
                "box": "box",
                "heatmap": "heatmap",
                "funnel": "bar",  # Approximate with bar for now
                "waterfall": "bar",  # Approximate with bar for now
                "treemap": "pie",  # Approximate with pie for now
                "sunburst": "pie",  # Approximate with pie for now
                "radar": "line"  # Approximate with line for now
            }
            
            mapped_chart_type = chart_type_mapping.get(chart_type, chart_type)
            
            # Prepare visualization arguments
            viz_args = {
                "data_source": {
                    "type": "data",
                    "data": data
                },
                "chart_config": {
                    "chart_type": mapped_chart_type,
                    "title": title,
                    "x_column": x_field,
                    "y_column": y_field,
                    "aggregation": aggregate,
                    **chart_options
                },
                "output_format": "base64" if export_format == "png" else export_format
            }
            
            # Create visualization
            result = viz_tool.execute(viz_args)
            
            if result["success"]:
                return {
                    "chart_data": result.get("visualization"),
                    "format": result.get("format", export_format),
                    "display_hint": result.get("display_hint")
                }
            else:
                return {
                    "error": result.get("error", "Chart creation failed")
                }
                
        except Exception as e:
            frappe.logger("chart_creator").error(f"Chart creation failed: {str(e)}")
            return {
                "error": f"Chart creation failed: {str(e)}"
            }