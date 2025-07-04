"""
Query and Analyze Tool for Data Science Plugin.
Executes custom SQL queries and performs analysis on the results.
"""

import frappe
from frappe import _
import json
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class QueryAndAnalyze(BaseTool):
    """
    Tool for executing SQL queries and performing analysis on the results.
    
    Provides capabilities for:
    - Custom SQL query execution
    - Result set analysis
    - Data aggregation and summarization
    - Cross-DocType analysis
    """
    
    def __init__(self):
        super().__init__()
        self.name = "query_and_analyze"
        self.description = """
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


Execute custom SQL queries on Frappe database and perform advanced data analysis. Perfect for complex business intelligence, custom reporting, and advanced analytics that go beyond standard reports.

💡 ARTIFACT TIP: For complex queries and analysis, use artifacts to build comprehensive reports.


🔄 **Progress Streaming Enabled**: This tool provides real-time progress updates during execution."""
        self.requires_permission = None  # Permission checked manually in execute method
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query to execute (SELECT statements only)"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["basic", "statistical", "aggregation", "distribution"],
                    "default": "basic",
                    "description": "Type of analysis to perform on query results"
                },
                "parameters": {
                    "type": "object",
                    "description": "Query parameters for parameterized queries"
                },
                "limit": {
                    "type": "integer",
                    "default": 1000,
                    "maximum": 10000,
                    "description": "Maximum number of rows to return"
                },
                "timeout": {
                    "type": "integer",
                    "default": 30,
                    "maximum": 300,
                    "description": "Query timeout in seconds"
                }
            },
            "required": ["query"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query and analyze results"""
        query = arguments.get("query", "").strip()
        analysis_type = arguments.get("analysis_type", "basic")
        parameters = arguments.get("parameters", {})
        limit = arguments.get("limit", 1000)
        timeout = arguments.get("timeout", 30)
        
        # Check permissions - requires System Manager role
        user_roles = frappe.get_roles()
        if "System Manager" not in user_roles:
            return {
                "success": False,
                "error": "Insufficient permissions. System Manager role required for SQL queries"
            }
        
        # Validate query
        if not query:
            return {
                "success": False,
                "error": "Query cannot be empty"
            }
        
        # Security check - only allow SELECT statements
        if not self._is_safe_query(query):
            return {
                "success": False,
                "error": "Only SELECT statements are allowed"
            }
        
        try:
            # Check dependencies
            self._check_dependencies()
            
            # Apply limit to query if not already present
            modified_query = self._apply_limit_to_query(query, limit)
            
            # Execute query
            results = self._execute_query(modified_query, parameters, timeout)
            
            if not results:
                return {
                    "success": True,
                    "query": query,
                    "row_count": 0,
                    "analysis": {"message": "Query returned no results"}
                }
            
            # Perform analysis on results
            analysis = self._perform_analysis(results, analysis_type)
            
            return {
                "success": True,
                "query": query,
                "row_count": len(results),
                "analysis_type": analysis_type,
                "results": results[:100],  # Return first 100 rows for preview
                "data": results,  # Also include as 'data' for backward compatibility
                "analysis": analysis
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Query Execution Error"),
                message=f"Error executing query: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "query": query
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
    
    def _is_safe_query(self, query: str) -> bool:
        """Check if query is safe to execute (SELECT only)"""
        # Remove comments and normalize whitespace
        clean_query = " ".join(query.split())
        clean_query = clean_query.strip().upper()
        
        # Check for dangerous statements
        dangerous_keywords = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
            'TRUNCATE', 'REPLACE', 'MERGE', 'CALL', 'EXEC', 'EXECUTE'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in clean_query:
                return False
        
        # Must start with SELECT
        if not clean_query.startswith('SELECT'):
            return False
        
        return True
    
    def _apply_limit_to_query(self, query: str, limit: int) -> str:
        """Apply LIMIT clause to query if not already present"""
        upper_query = query.upper()
        
        # If LIMIT already exists, don't modify
        if 'LIMIT' in upper_query:
            return query
        
        # Add LIMIT clause
        return f"{query.rstrip(';')} LIMIT {limit}"
    
    def _execute_query(self, query: str, parameters: Dict, timeout: int) -> List[Dict]:
        """Execute SQL query safely"""
        try:
            # Execute query with parameters
            if parameters:
                results = frappe.db.sql(query, parameters, as_dict=True)
            else:
                results = frappe.db.sql(query, as_dict=True)
            
            # Convert to serializable format to avoid array structure issues
            import json
            serializable_results = []
            
            for row in results:
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
                        frappe.log_error(f"Serialization error for key {key}: {str(e)}")
                        serializable_row[key] = str(value) if value is not None else None
                
                serializable_results.append(serializable_row)
            
            return serializable_results
            
        except Exception as e:
            raise e
    
    def _perform_analysis(self, results: List[Dict], analysis_type: str) -> Dict[str, Any]:
        """Perform analysis on query results"""
        import pandas as pd
        import numpy as np
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        if analysis_type == "basic":
            return self._basic_analysis(df)
        elif analysis_type == "statistical":
            return self._statistical_analysis(df)
        elif analysis_type == "aggregation":
            return self._aggregation_analysis(df)
        elif analysis_type == "distribution":
            return self._distribution_analysis(df)
        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}
    
    def _basic_analysis(self, df) -> Dict[str, Any]:
        """Perform basic analysis on results"""
        analysis = {
            "summary": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "column_names": list(df.columns),
                "memory_usage": df.memory_usage(deep=True).sum()
            },
            "data_types": {},
            "null_counts": {},
            "unique_counts": {}
        }
        
        # Analyze each column
        for column in df.columns:
            analysis["data_types"][column] = str(df[column].dtype)
            analysis["null_counts"][column] = int(df[column].isna().sum())
            analysis["unique_counts"][column] = int(df[column].nunique())
        
        return analysis
    
    def _statistical_analysis(self, df) -> Dict[str, Any]:
        """Perform statistical analysis on numeric columns"""
        import numpy as np
        
        # Get numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_columns:
            return {"message": "No numeric columns found for statistical analysis"}
        
        analysis = {
            "numeric_columns": numeric_columns,
            "statistics": {}
        }
        
        for column in numeric_columns:
            stats = {
                "count": int(df[column].count()),
                "mean": float(df[column].mean()) if not df[column].isna().all() else None,
                "std": float(df[column].std()) if not df[column].isna().all() else None,
                "min": float(df[column].min()) if not df[column].isna().all() else None,
                "max": float(df[column].max()) if not df[column].isna().all() else None,
                "median": float(df[column].median()) if not df[column].isna().all() else None,
                "q25": float(df[column].quantile(0.25)) if not df[column].isna().all() else None,
                "q75": float(df[column].quantile(0.75)) if not df[column].isna().all() else None
            }
            
            # Remove None values
            stats = {k: v for k, v in stats.items() if v is not None}
            analysis["statistics"][column] = stats
        
        return analysis
    
    def _aggregation_analysis(self, df) -> Dict[str, Any]:
        """Perform aggregation analysis"""
        import numpy as np
        
        analysis = {
            "row_count": len(df),
            "aggregations": {}
        }
        
        # Get numeric columns for aggregation
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        for column in numeric_columns:
            if not df[column].isna().all():
                analysis["aggregations"][column] = {
                    "sum": float(df[column].sum()),
                    "average": float(df[column].mean()),
                    "count": int(df[column].count()),
                    "min": float(df[column].min()),
                    "max": float(df[column].max())
                }
        
        # Group by analysis for categorical columns
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        if categorical_columns:
            analysis["groupby_analysis"] = {}
            
            for column in categorical_columns[:3]:  # Limit to first 3 categorical columns
                if df[column].nunique() <= 20:  # Only for columns with reasonable number of unique values
                    value_counts = df[column].value_counts().head(10)
                    analysis["groupby_analysis"][column] = {
                        "top_values": {str(k): int(v) for k, v in value_counts.items()}
                    }
        
        return analysis
    
    def _distribution_analysis(self, df) -> Dict[str, Any]:
        """Perform distribution analysis"""
        import numpy as np
        
        analysis = {
            "distributions": {}
        }
        
        # Analyze numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        for column in numeric_columns:
            if not df[column].isna().all():
                # Calculate histogram-like distribution
                try:
                    hist, bin_edges = np.histogram(df[column].dropna(), bins=10)
                    
                    analysis["distributions"][column] = {
                        "type": "numeric",
                        "histogram": {
                            "counts": hist.tolist(),
                            "bin_edges": bin_edges.tolist()
                        },
                        "skewness": float(df[column].skew()) if len(df[column].dropna()) > 1 else None,
                        "kurtosis": float(df[column].kurtosis()) if len(df[column].dropna()) > 1 else None
                    }
                except Exception:
                    # Skip if histogram calculation fails
                    continue
        
        # Analyze categorical columns
        categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        for column in categorical_columns:
            if df[column].nunique() <= 20:  # Only for manageable number of categories
                value_counts = df[column].value_counts()
                
                analysis["distributions"][column] = {
                    "type": "categorical",
                    "value_counts": {str(k): int(v) for k, v in value_counts.items()},
                    "unique_count": int(df[column].nunique()),
                    "most_common": str(value_counts.index[0]) if len(value_counts) > 0 else None
                }
        
        return analysis


# Make sure class is available for discovery
# The plugin manager will find QueryAndAnalyze automatically