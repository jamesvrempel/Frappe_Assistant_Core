"""
Frappe Data Analysis Tool for Data Science Plugin.
Performs advanced data analysis on Frappe data structures.
"""

import frappe
from frappe import _
import json
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class AnalyzeFrappeData(BaseTool):
    """
    Tool for analyzing Frappe data with statistical and analytical functions.
    
    Provides capabilities for:
    - Statistical analysis of DocType data
    - Data profiling and summarization
    - Trend analysis
    - Data quality assessment
    """
    
    def __init__(self):
        super().__init__()
        self.name = "analyze_business_data"
        self.description = self._get_dynamic_description()
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "The DocType to analyze"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["profile", "statistics", "trends", "quality", "correlations"],
                    "description": "Type of analysis to perform"
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to analyze (optional)"
                },
                "filters": {
                    "type": "object",
                    "description": "Filters to apply to the data"
                },
                "date_field": {
                    "type": "string",
                    "description": "Date field for trend analysis (optional)"
                },
                "limit": {
                    "type": "integer",
                    "default": 1000,
                    "maximum": 10000,
                    "description": "Maximum number of records to analyze"
                }
            },
            "required": ["doctype", "analysis_type"]
        }
    
    def _get_dynamic_description(self) -> str:
        """Generate description based on current streaming settings"""
        base_description = """Perform statistical analysis on Frappe business data. Calculate averages, trends, correlations, and insights from any DocType."""
        
        try:
            from frappe_assistant_core.utils.streaming_manager import get_streaming_manager
            streaming_manager = get_streaming_manager()
            streaming_suffix = streaming_manager.get_tool_description_suffix(self.name)
            return base_description + streaming_suffix
            
        except Exception as e:
            frappe.logger("analyze_frappe_data").warning(f"Failed to load streaming configuration: {str(e)}")
            return base_description
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Perform data analysis on Frappe data"""
        doctype = arguments.get("doctype")
        analysis_type = arguments.get("analysis_type")
        fields = arguments.get("fields", [])
        filters = arguments.get("filters", {})
        date_field = arguments.get("date_field")
        limit = arguments.get("limit", 1000)
        
        # Check permission for DocType
        if not frappe.has_permission(doctype, "read"):
            frappe.throw(
                _("Insufficient permissions to analyze {0} data").format(doctype),
                frappe.PermissionError
            )
        
        try:
            # Validate that required dependencies are available
            self._check_dependencies()
            
            # Get data for analysis
            data = self._get_data_for_analysis(doctype, fields, filters, limit)
            
            if not data:
                return {
                    "success": False,
                    "error": f"No data found for analysis in {doctype}"
                }
            
            # Perform requested analysis
            if analysis_type == "profile":
                result = self._profile_data(data, doctype)
            elif analysis_type == "statistics":
                result = self._statistical_analysis(data, doctype)
            elif analysis_type == "trends":
                result = self._trend_analysis(data, doctype, date_field)
            elif analysis_type == "quality":
                result = self._data_quality_analysis(data, doctype)
            elif analysis_type == "correlations":
                result = self._correlation_analysis(data, doctype)
            else:
                return {
                    "success": False,
                    "error": f"Unknown analysis type: {analysis_type}"
                }
            
            return {
                "success": True,
                "doctype": doctype,
                "analysis_type": analysis_type,
                "record_count": len(data),
                "analysis_result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "doctype": doctype,
                "analysis_type": analysis_type
            }
    
    def _check_dependencies(self):
        """Check if required data science libraries are available"""
        try:
            import pandas as pd
            import numpy as np
        except ImportError:
            frappe.throw(
                _("Data science dependencies not available. Please install pandas and numpy."),
                frappe.ValidationError
            )
    
    def _get_data_for_analysis(self, doctype: str, fields: List[str], filters: Dict, limit: int) -> List[Dict]:
        """Get data from Frappe for analysis"""
        # Get DocType meta to determine available fields
        meta = frappe.get_meta(doctype)
        
        # If no specific fields provided, get all data fields
        if not fields:
            fields = ["name", "creation", "modified"]
            for field in meta.fields:
                if field.fieldtype in [
                    'Data', 'Int', 'Float', 'Currency', 'Percent', 
                    'Date', 'Datetime', 'Time', 'Check', 'Select'
                ]:
                    fields.append(field.fieldname)
        
        # Get data
        raw_data = frappe.get_all(
            doctype,
            filters=filters,
            fields=fields,
            limit=limit,
            order_by="creation desc"
        )
        
        # Convert to serializable format to avoid array structure issues
        import json
        serializable_data = []
        
        for row in raw_data:
            serializable_row = {}
            for key, value in row.items():
                try:
                    # Handle various data types that might cause serialization issues
                    if value is None:
                        serializable_row[key] = None
                    elif hasattr(value, '__array_struct__'):
                        # Convert numpy arrays or similar structures
                        try:
                            serializable_row[key] = value.tolist() if hasattr(value, 'tolist') else str(value)
                        except:
                            serializable_row[key] = str(value)
                    elif hasattr(value, 'isoformat'):
                        # Convert datetime objects to strings
                        serializable_row[key] = value.isoformat()
                    elif isinstance(value, (bytes, bytearray)):
                        # Convert binary data to string
                        serializable_row[key] = value.decode('utf-8', errors='ignore')
                    elif hasattr(value, '__dict__'):
                        # Handle complex objects
                        serializable_row[key] = str(value)
                    else:
                        # Test if value is JSON serializable
                        try:
                            json.dumps(value)
                            serializable_row[key] = value
                        except (TypeError, ValueError):
                            # If not serializable, convert to string
                            serializable_row[key] = str(value)
                except Exception as e:
                    # Fallback: convert problematic values to string
                    frappe.log_error(f"Analysis serialization error for key {key}: {str(e)}")
                    serializable_row[key] = str(value) if value is not None else None
            
            serializable_data.append(serializable_row)
        
        return serializable_data
    
    def _profile_data(self, data: List[Dict], doctype: str) -> Dict[str, Any]:
        """Generate data profile with basic statistics"""
        import pandas as pd
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        profile = {
            "record_count": len(df),
            "field_count": len(df.columns),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "fields": {}
        }
        
        # Analyze each field
        for column in df.columns:
            field_profile = {
                "type": str(df[column].dtype),
                "non_null_count": df[column].notna().sum(),
                "null_count": df[column].isna().sum(),
                "null_percentage": (df[column].isna().sum() / len(df)) * 100,
                "unique_count": df[column].nunique()
            }
            
            # Numeric field analysis
            if df[column].dtype in ['int64', 'float64']:
                field_profile.update({
                    "min": df[column].min(),
                    "max": df[column].max(),
                    "mean": df[column].mean(),
                    "median": df[column].median(),
                    "std": df[column].std()
                })
            
            # String field analysis
            elif df[column].dtype == 'object':
                non_null_values = df[column].dropna()
                if len(non_null_values) > 0:
                    field_profile.update({
                        "avg_length": non_null_values.astype(str).str.len().mean(),
                        "max_length": non_null_values.astype(str).str.len().max(),
                        "min_length": non_null_values.astype(str).str.len().min()
                    })
            
            profile["fields"][column] = field_profile
        
        return profile
    
    def _statistical_analysis(self, data: List[Dict], doctype: str) -> Dict[str, Any]:
        """Perform statistical analysis on numeric fields"""
        import pandas as pd
        import numpy as np
        
        df = pd.DataFrame(data)
        
        # Get numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_columns:
            return {"message": "No numeric fields found for statistical analysis"}
        
        statistics = {}
        
        for column in numeric_columns:
            stats = {
                "count": df[column].count(),
                "mean": df[column].mean(),
                "std": df[column].std(),
                "min": df[column].min(),
                "25%": df[column].quantile(0.25),
                "50%": df[column].quantile(0.50),
                "75%": df[column].quantile(0.75),
                "max": df[column].max(),
                "variance": df[column].var(),
                "skewness": df[column].skew(),
                "kurtosis": df[column].kurtosis()
            }
            
            statistics[column] = stats
        
        return {
            "numeric_fields_analyzed": len(numeric_columns),
            "statistics": statistics
        }
    
    def _trend_analysis(self, data: List[Dict], doctype: str, date_field: str) -> Dict[str, Any]:
        """Perform trend analysis on time-series data"""
        import pandas as pd
        
        df = pd.DataFrame(data)
        
        # Use creation date if no date field specified
        if not date_field:
            date_field = "creation"
        
        if date_field not in df.columns:
            return {"error": f"Date field '{date_field}' not found in data"}
        
        # Convert date field to datetime
        df[date_field] = pd.to_datetime(df[date_field])
        df = df.sort_values(date_field)
        
        # Group by date periods
        daily_counts = df.groupby(df[date_field].dt.date).size()
        monthly_counts = df.groupby(df[date_field].dt.to_period('M')).size()
        
        # Calculate trends
        trends = {
            "daily_trend": {
                "data_points": len(daily_counts),
                "average_per_day": daily_counts.mean(),
                "max_day": daily_counts.max(),
                "min_day": daily_counts.min(),
                "trend_direction": "increasing" if daily_counts.iloc[-1] > daily_counts.iloc[0] else "decreasing"
            },
            "monthly_trend": {
                "data_points": len(monthly_counts),
                "average_per_month": monthly_counts.mean(),
                "max_month": monthly_counts.max(),
                "min_month": monthly_counts.min()
            },
            "date_range": {
                "start_date": df[date_field].min().strftime('%Y-%m-%d'),
                "end_date": df[date_field].max().strftime('%Y-%m-%d'),
                "total_days": (df[date_field].max() - df[date_field].min()).days
            }
        }
        
        return trends
    
    def _data_quality_analysis(self, data: List[Dict], doctype: str) -> Dict[str, Any]:
        """Analyze data quality issues"""
        import pandas as pd
        
        df = pd.DataFrame(data)
        
        quality_report = {
            "total_records": len(df),
            "issues": {},
            "overall_score": 0
        }
        
        issues_found = 0
        total_checks = 0
        
        for column in df.columns:
            column_issues = []
            
            # Check for null values
            null_count = df[column].isna().sum()
            null_percentage = (null_count / len(df)) * 100
            
            if null_percentage > 10:  # More than 10% null values
                column_issues.append(f"High null percentage: {null_percentage:.1f}%")
                issues_found += 1
            total_checks += 1
            
            # Check for duplicates in name fields
            if 'name' in column.lower():
                duplicate_count = df[column].duplicated().sum()
                if duplicate_count > 0:
                    column_issues.append(f"Duplicate values: {duplicate_count}")
                    issues_found += 1
                total_checks += 1
            
            # Check data consistency for numeric fields
            if df[column].dtype in ['int64', 'float64']:
                if df[column].min() < 0 and 'amount' in column.lower():
                    column_issues.append("Negative values in amount field")
                    issues_found += 1
                total_checks += 1
            
            if column_issues:
                quality_report["issues"][column] = column_issues
        
        # Calculate overall quality score
        if total_checks > 0:
            quality_report["overall_score"] = ((total_checks - issues_found) / total_checks) * 100
        
        quality_report["summary"] = {
            "total_issues": issues_found,
            "fields_with_issues": len(quality_report["issues"]),
            "quality_score": quality_report["overall_score"]
        }
        
        return quality_report
    
    def _correlation_analysis(self, data: List[Dict], doctype: str) -> Dict[str, Any]:
        """Analyze correlations between numeric fields"""
        import pandas as pd
        import numpy as np
        
        df = pd.DataFrame(data)
        
        # Get numeric columns only
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return {"message": "Need at least 2 numeric fields for correlation analysis"}
        
        # Calculate correlation matrix
        correlation_matrix = numeric_df.corr()
        
        # Find strong correlations (> 0.7 or < -0.7)
        strong_correlations = []
        
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        "field1": correlation_matrix.columns[i],
                        "field2": correlation_matrix.columns[j],
                        "correlation": corr_value,
                        "strength": "strong positive" if corr_value > 0.7 else "strong negative"
                    })
        
        return {
            "numeric_fields": list(numeric_df.columns),
            "correlation_matrix": correlation_matrix.to_dict(),
            "strong_correlations": strong_correlations,
            "analysis_summary": {
                "total_correlations_analyzed": len(strong_correlations),
                "strongest_correlation": max([abs(c["correlation"]) for c in strong_correlations]) if strong_correlations else 0
            }
        }


# Make sure class is available for discovery
# The plugin manager will find AnalyzeFrappeData automatically