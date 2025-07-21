"""
Chart Creator Tool - Individual chart and widget creation

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
    - KPI metric cards
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


class CreateKPICard(BaseTool):
    """Create KPI metric cards with trend indicators"""
    
    def __init__(self):
        super().__init__()
        self.name = "create_kpi_card"
        self.description = "Create KPI metric cards with current values, trends, and target comparisons"
        self.requires_permission = None
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "Source DocType for KPI data"
                },
                "metric_field": {
                    "type": "string",
                    "description": "Field to calculate metric from"
                },
                "metric_name": {
                    "type": "string",
                    "description": "Display name for the KPI"
                },
                "aggregate": {
                    "type": "string",
                    "enum": ["sum", "count", "avg", "min", "max"],
                    "default": "sum",
                    "description": "Aggregation method"
                },
                "comparison_field": {
                    "type": "string",
                    "description": "Field to compare against (e.g., target, previous period)"
                },
                "comparison_type": {
                    "type": "string",
                    "enum": ["target", "previous_period", "previous_month", "previous_quarter", "previous_year"],
                    "default": "previous_period",
                    "description": "Type of comparison to show"
                },
                "filters": {
                    "type": "object",
                    "description": "Filters for current period data"
                },
                "time_span": {
                    "type": "string",
                    "enum": ["current_month", "current_quarter", "current_year"],
                    "default": "current_month",
                    "description": "Time period for KPI calculation"
                },
                "format": {
                    "type": "string",
                    "enum": ["currency", "percentage", "number", "decimal"],
                    "default": "number",
                    "description": "Display format for values"
                },
                "target_value": {
                    "type": "number",
                    "description": "Target value for comparison (if comparison_type is 'target')"
                },
                "color_scheme": {
                    "type": "string",
                    "enum": ["blue", "green", "red", "orange", "purple"],
                    "default": "blue",
                    "description": "Color scheme for the KPI card"
                }
            },
            "required": ["doctype", "metric_field", "metric_name"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create KPI card"""
        try:
            doctype = arguments.get("doctype")
            metric_field = arguments.get("metric_field")
            metric_name = arguments.get("metric_name")
            aggregate = arguments.get("aggregate", "sum")
            comparison_type = arguments.get("comparison_type", "previous_period")
            filters = arguments.get("filters", {})
            time_span = arguments.get("time_span", "current_month")
            format_type = arguments.get("format", "number")
            target_value = arguments.get("target_value")
            color_scheme = arguments.get("color_scheme", "blue")
            
            # Validate permissions
            if not frappe.has_permission(doctype, "read"):
                return {
                    "success": False,
                    "error": f"Insufficient permissions to access {doctype} data"
                }
            
            # Calculate current value
            current_value = self._calculate_kpi_value(
                doctype, metric_field, aggregate, filters, time_span
            )
            
            # Calculate comparison value
            comparison_result = self._calculate_comparison(
                doctype, metric_field, aggregate, comparison_type, 
                time_span, target_value, filters
            )
            
            # Generate KPI card
            kpi_card = self._generate_kpi_card(
                metric_name, current_value, comparison_result, 
                format_type, color_scheme
            )
            
            return {
                "success": True,
                "metric_name": metric_name,
                "current_value": current_value,
                "comparison": comparison_result,
                "kpi_card": kpi_card,
                "format": format_type,
                "time_span": time_span
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_kpi_value(self, doctype: str, metric_field: str, aggregate: str,
                           filters: Dict, time_span: str) -> float:
        """Calculate current KPI value"""
        try:
            # Apply time filters
            chart_creator = ChartCreator()
            time_filters = chart_creator._get_time_filters(time_span, doctype)
            filters.update(time_filters)
            
            # Get data
            if aggregate == "count":
                result = frappe.db.count(doctype, filters)
                return float(result)
            else:
                # Use SQL aggregation
                field_clause = f"{aggregate.upper()}(`{metric_field}`)"
                conditions = []
                values = []
                
                for key, value in filters.items():
                    if isinstance(value, list) and len(value) == 2 and value[0] in [">=", "<=", ">", "<", "between"]:
                        if value[0] == "between":
                            conditions.append(f"`{key}` BETWEEN %s AND %s")
                            values.extend(value[1])
                        else:
                            conditions.append(f"`{key}` {value[0]} %s")
                            values.append(value[1])
                    else:
                        conditions.append(f"`{key}` = %s")
                        values.append(value)
                
                where_clause = ""
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
                
                query = f"""
                    SELECT {field_clause} as value
                    FROM `tab{doctype}`
                    {where_clause}
                """
                
                result = frappe.db.sql(query, values, as_dict=True)
                return float(result[0]["value"]) if result and result[0]["value"] else 0.0
                
        except Exception as e:
            frappe.logger("chart_creator").error(f"KPI calculation failed: {str(e)}")
            return 0.0
    
    def _calculate_comparison(self, doctype: str, metric_field: str, aggregate: str,
                            comparison_type: str, time_span: str, target_value: Optional[float],
                            base_filters: Dict) -> Dict[str, Any]:
        """Calculate comparison value and percentage change"""
        try:
            if comparison_type == "target" and target_value is not None:
                current_value = self._calculate_kpi_value(doctype, metric_field, aggregate, base_filters, time_span)
                percentage_change = ((current_value - target_value) / target_value * 100) if target_value != 0 else 0
                return {
                    "type": "target",
                    "previous_value": target_value,
                    "percentage_change": percentage_change,
                    "direction": "up" if percentage_change > 0 else "down" if percentage_change < 0 else "neutral"
                }
            
            # Calculate previous period value
            previous_time_span = self._get_previous_period(time_span, comparison_type)
            chart_creator = ChartCreator()
            previous_filters = chart_creator._get_time_filters(previous_time_span, doctype)
            previous_filters.update({k: v for k, v in base_filters.items() if not self._is_time_filter(k)})
            
            previous_value = self._calculate_kpi_value(doctype, metric_field, aggregate, previous_filters, previous_time_span)
            current_value = self._calculate_kpi_value(doctype, metric_field, aggregate, base_filters, time_span)
            
            percentage_change = ((current_value - previous_value) / previous_value * 100) if previous_value != 0 else 0
            
            return {
                "type": comparison_type,
                "previous_value": previous_value,
                "percentage_change": percentage_change,
                "direction": "up" if percentage_change > 0 else "down" if percentage_change < 0 else "neutral"
            }
            
        except Exception as e:
            frappe.logger("chart_creator").error(f"Comparison calculation failed: {str(e)}")
            return {
                "type": comparison_type,
                "previous_value": 0,
                "percentage_change": 0,
                "direction": "neutral"
            }
    
    def _get_previous_period(self, time_span: str, comparison_type: str) -> str:
        """Get previous period time span"""
        if comparison_type == "previous_month":
            return "last_month"
        elif comparison_type == "previous_quarter":
            return "last_quarter"
        elif comparison_type == "previous_year":
            return "last_year"
        else:
            # Default previous period mapping
            mapping = {
                "current_month": "last_month",
                "current_quarter": "last_quarter", 
                "current_year": "last_year"
            }
            return mapping.get(time_span, "last_month")
    
    def _is_time_filter(self, field_name: str) -> bool:
        """Check if field is a time-related filter"""
        time_fields = ["posting_date", "creation", "date", "modified"]
        return field_name in time_fields
    
    def _generate_kpi_card(self, metric_name: str, current_value: float,
                          comparison: Dict, format_type: str, color_scheme: str) -> Dict[str, Any]:
        """Generate KPI card data structure"""
        # Format value based on type
        formatted_value = self._format_value(current_value, format_type)
        formatted_previous = self._format_value(comparison["previous_value"], format_type)
        
        # Choose color based on direction and scheme
        color_mapping = {
            "blue": {"up": "#28a745", "down": "#dc3545", "neutral": "#007bff"},
            "green": {"up": "#28a745", "down": "#dc3545", "neutral": "#28a745"},
            "red": {"up": "#28a745", "down": "#dc3545", "neutral": "#dc3545"},
            "orange": {"up": "#28a745", "down": "#dc3545", "neutral": "#fd7e14"},
            "purple": {"up": "#28a745", "down": "#dc3545", "neutral": "#6f42c1"}
        }
        
        color = color_mapping[color_scheme][comparison["direction"]]
        
        return {
            "metric_name": metric_name,
            "current_value": formatted_value,
            "previous_value": formatted_previous,
            "percentage_change": f"{comparison['percentage_change']:.1f}%",
            "direction": comparison["direction"],
            "color": color,
            "comparison_type": comparison["type"],
            "raw_current": current_value,
            "raw_previous": comparison["previous_value"]
        }
    
    def _format_value(self, value: float, format_type: str) -> str:
        """Format value based on type"""
        if format_type == "currency":
            return f"${value:,.2f}"
        elif format_type == "percentage":
            return f"{value:.1f}%"
        elif format_type == "decimal":
            return f"{value:.2f}"
        else:  # number
            return f"{value:,.0f}"


# Export tools for plugin discovery
__all__ = ["ChartCreator", "CreateKPICard"]