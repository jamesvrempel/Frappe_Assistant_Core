"""
KPI Card Creator Tool - Create KPI metric cards with trend indicators

Create KPI metric cards with current values, trends, and target comparisons.
"""

import frappe
from frappe import _
from typing import Dict, Any, List, Optional
from frappe_assistant_core.core.base_tool import BaseTool


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
            time_filters = self._get_time_filters(time_span, doctype)
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
        if time_span == "current_month":
            start_date = now.replace(day=1)
            filters[date_field] = [">=", start_date.date()]
        elif time_span == "current_quarter":
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_start_month, day=1)
            filters[date_field] = [">=", start_date.date()]
        elif time_span == "current_year":
            start_date = now.replace(month=1, day=1)
            filters[date_field] = [">=", start_date.date()]
        
        return filters
    
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
            previous_filters = self._get_time_filters(previous_time_span, doctype)
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