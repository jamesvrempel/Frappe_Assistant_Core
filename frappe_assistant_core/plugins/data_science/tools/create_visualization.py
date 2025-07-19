"""
Visualization Creation Tool for Data Science Plugin.
Creates charts and visualizations from Frappe data.
"""

import frappe
from frappe import _
import json
import base64
import io
from typing import Dict, Any, List
from frappe_assistant_core.core.base_tool import BaseTool


class CreateVisualization(BaseTool):
    """
    Tool for creating data visualizations from Frappe data.
    
    Provides capabilities for:
    - Chart generation (bar, line, pie, scatter, etc.)
    - Statistical plots (histograms, box plots)
    - Dashboard-style visualizations
    - Export to various formats
    """
    
    def __init__(self):
        super().__init__()
        self.name = "create_visualization"
        self.description = self._get_dynamic_description()
        self.requires_permission = None  # Permission checked dynamically per DocType
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "data_source": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["doctype", "query", "data"],
                            "description": "Source of data for visualization"
                        },
                        "doctype": {
                            "type": "string",
                            "description": "DocType name (if type is 'doctype')"
                        },
                        "query": {
                            "type": "string",
                            "description": "SQL query (if type is 'query')"
                        },
                        "data": {
                            "type": "array",
                            "description": "Direct data array (if type is 'data')"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Filters for DocType data"
                        },
                        "fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Fields to include"
                        }
                    },
                    "required": ["type"]
                },
                "chart_config": {
                    "type": "object",
                    "properties": {
                        "chart_type": {
                            "type": "string",
                            "enum": ["bar", "line", "pie", "scatter", "histogram", "box", "heatmap"],
                            "description": "Type of chart to create"
                        },
                        "x_field": {
                            "type": "string",
                            "description": "Field for X-axis"
                        },
                        "y_field": {
                            "type": "string",
                            "description": "Field for Y-axis"
                        },
                        "group_by": {
                            "type": "string",
                            "description": "Field to group data by"
                        },
                        "title": {
                            "type": "string",
                            "description": "Chart title"
                        },
                        "x_label": {
                            "type": "string",
                            "description": "X-axis label"
                        },
                        "y_label": {
                            "type": "string",
                            "description": "Y-axis label"
                        }
                    },
                    "required": ["chart_type"]
                },
                "output_format": {
                    "type": "string",
                    "enum": ["base64", "html", "json"],
                    "default": "base64",
                    "description": "Output format for the visualization"
                },
                "limit": {
                    "type": "integer",
                    "default": 1000,
                    "maximum": 5000,
                    "description": "Maximum number of data points"
                }
            },
            "required": ["data_source", "chart_config"]
        }
    
    def _get_dynamic_description(self) -> str:
        """Generate description based on current streaming settings"""
        base_description = """Create professional charts and visualizations from Frappe business data. Generate bar charts, line graphs, pie charts, scatter plots, histograms, box plots, and heatmaps with customizable styling and multiple output formats.

📊 **VISUALIZATION TYPES:**
• Bar Charts - Compare categories, show trends over time
• Line Charts - Track changes, display time series data
• Pie Charts - Show proportions and percentages
• Scatter Plots - Explore relationships between variables
• Histograms - Display data distribution patterns
• Box Plots - Show statistical summaries and outliers
• Heatmaps - Visualize correlations and patterns

🎯 **DATA SOURCES:**
• DocType Records - Query any Frappe document type
• Custom SQL - Execute complex database queries (System Manager)
• Direct Data - Use pre-processed data arrays

🔄 **Progress Streaming Enabled**: This tool provides real-time progress updates during execution."""
        
        try:
            from frappe_assistant_core.utils.streaming_manager import get_streaming_manager
            
            streaming_manager = get_streaming_manager()
            streaming_suffix = streaming_manager.get_tool_description_suffix(self.name)
            
            return base_description + streaming_suffix
            
        except Exception as e:
            # Fallback to basic description if streaming manager fails
            frappe.logger("create_visualization").warning(f"Failed to load streaming configuration: {str(e)}")
            return base_description + "\n\n💡 **ARTIFACT STREAMING**: Consider using artifacts for comprehensive visualization reports."
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create visualization from data"""
        data_source = arguments.get("data_source", {})
        chart_config = arguments.get("chart_config", {})
        output_format = arguments.get("output_format", "base64")
        limit = arguments.get("limit", 1000)
        
        try:
            # Check dependencies
            self._check_dependencies()
            
            # Get data from source
            data = self._get_data_from_source(data_source, limit)
            
            if not data:
                return {
                    "success": False,
                    "error": "No data available for visualization"
                }
            
            # Create visualization
            chart_result = self._create_chart(data, chart_config, output_format)
            
            return {
                "success": True,
                "data_points": len(data),
                "chart_type": chart_config.get("chart_type"),
                "output_format": output_format,
                **chart_result
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Visualization Creation Error"),
                message=f"Error creating visualization: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _check_dependencies(self):
        """Check if required visualization libraries are available"""
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
            import numpy as np
        except ImportError:
            frappe.throw(
                _("Visualization dependencies not available. Please install matplotlib, pandas, and numpy."),
                frappe.ValidationError
            )
    
    def _get_data_from_source(self, data_source: Dict, limit: int) -> List[Dict]:
        """Get data from specified source"""
        source_type = data_source.get("type")
        
        if source_type == "doctype":
            return self._get_doctype_data(data_source, limit)
        elif source_type == "query":
            return self._get_query_data(data_source, limit)
        elif source_type == "data":
            return data_source.get("data", [])[:limit]
        else:
            frappe.throw(_("Invalid data source type: {0}").format(source_type))
    
    def _get_doctype_data(self, data_source: Dict, limit: int) -> List[Dict]:
        """Get data from DocType"""
        doctype = data_source.get("doctype")
        filters = data_source.get("filters", {})
        fields = data_source.get("fields", ["name"])
        
        # Check permission
        if not frappe.has_permission(doctype, "read"):
            frappe.throw(
                _("Insufficient permissions to read {0} data").format(doctype),
                frappe.PermissionError
            )
        
        # Use raw SQL to avoid frappe._dict objects that cause __array_struct__ issues
        try:
            # Build SQL query manually to get clean data
            field_list = ", ".join([f"`{field}`" for field in fields])
            table_name = f"tab{doctype}"
            
            # Build WHERE clause from filters
            where_conditions = []
            values = []
            
            for key, value in filters.items():
                if isinstance(value, (list, tuple)):
                    placeholders = ", ".join(["%s"] * len(value))
                    where_conditions.append(f"`{key}` IN ({placeholders})")
                    values.extend(value)
                elif value is None:
                    where_conditions.append(f"`{key}` IS NULL")
                else:
                    where_conditions.append(f"`{key}` = %s")
                    values.append(value)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            query = f"""
                SELECT {field_list}
                FROM `{table_name}`
                {where_clause}
                ORDER BY creation DESC
                LIMIT {limit}
            """
            
            # Execute raw SQL to get clean data without frappe._dict objects
            result = frappe.db.sql(query, values, as_dict=True)
            
            # Convert to plain Python dicts to avoid array interface issues
            return [dict(row) for row in result]
            
        except Exception as e:
            # Fallback to get_all with conversion if SQL approach fails
            frappe.log_error(f"SQL visualization query failed: {str(e)}")
            
            raw_data = frappe.get_all(
                doctype,
                filters=filters,
                fields=fields,
                limit=limit,
                order_by="creation desc"
            )
            
            # Convert frappe._dict objects to plain dicts
            return [dict(row) for row in raw_data]
    
    def _get_query_data(self, data_source: Dict, limit: int) -> List[Dict]:
        """Get data from SQL query"""
        query = data_source.get("query", "")
        
        # Check permission (requires System Manager for direct SQL)
        if not frappe.has_permission("System Manager"):
            frappe.throw(
                _("Insufficient permissions to execute SQL queries"),
                frappe.PermissionError
            )
        
        # Apply limit to query
        if "LIMIT" not in query.upper():
            query = f"{query.rstrip(';')} LIMIT {limit}"
        
        raw_results = frappe.db.sql(query, as_dict=True)
        
        # Convert to serializable format to avoid array structure issues
        import json
        serializable_results = []
        
        for row in raw_results:
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
                    frappe.log_error(f"Visualization serialization error for key {key}: {str(e)}")
                    serializable_row[key] = str(value) if value is not None else None
            
            serializable_results.append(serializable_row)
        
        return serializable_results
    
    def _create_chart(self, data: List[Dict], chart_config: Dict, output_format: str) -> Dict[str, Any]:
        """Create chart based on configuration"""
        try:
            import matplotlib
            matplotlib.use('Agg')  # Set backend before importing pyplot
            import matplotlib.pyplot as plt
            import pandas as pd
            import numpy as np
        except ImportError as e:
            return {"error": f"Required libraries not available: {str(e)}"}
        
        # Convert data to DataFrame - data should already be clean Python dicts
        df = pd.DataFrame(data)
        
        if df.empty:
            return {"error": "No data to visualize"}
        
        # Smart data type conversion for visualization compatibility
        df = self._optimize_dataframe_for_visualization(df)
        
        chart_type = chart_config.get("chart_type")
        
        # Setup matplotlib for server environment
        plt.switch_backend('Agg')
        plt.ioff()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        try:
            if chart_type == "bar":
                self._create_bar_chart(df, chart_config, ax, plt)
            elif chart_type == "line":
                self._create_line_chart(df, chart_config, ax, plt)
            elif chart_type == "pie":
                self._create_pie_chart(df, chart_config, ax, plt)
            elif chart_type == "scatter":
                self._create_scatter_chart(df, chart_config, ax, plt)
            elif chart_type == "histogram":
                self._create_histogram(df, chart_config, ax, plt)
            elif chart_type == "box":
                self._create_box_plot(df, chart_config, ax, plt)
            elif chart_type == "heatmap":
                self._create_heatmap(df, chart_config, ax, plt)
            else:
                plt.close(fig)
                return {"error": f"Unsupported chart type: {chart_type}"}
            
            # Apply common styling
            self._apply_chart_styling(ax, chart_config, plt)
            
            # Generate output
            result = self._generate_output(fig, output_format, plt)
            
            plt.close(fig)
            return result
            
        except Exception as e:
            plt.close(fig)
            raise e
    
    def _create_bar_chart(self, df, config, ax, plt=None):
        """Create bar chart"""
        x_field = config.get("x_field")
        y_field = config.get("y_field")
        group_by = config.get("group_by")
        
        if not x_field or not y_field:
            # Auto-detect fields
            if len(df.columns) >= 2:
                x_field = df.columns[0]
                y_field = df.columns[1]
            else:
                raise ValueError("Need at least 2 columns for bar chart")
        
        if group_by and group_by in df.columns:
            # Grouped bar chart
            grouped = df.groupby([x_field, group_by])[y_field].sum().unstack(fill_value=0)
            grouped.plot(kind='bar', ax=ax)
        else:
            # Simple bar chart
            if x_field in df.columns and y_field in df.columns:
                df_agg = df.groupby(x_field)[y_field].sum()
                ax.bar(df_agg.index, df_agg.values)
    
    def _create_line_chart(self, df, config, ax, plt=None):
        """Create line chart"""
        x_field = config.get("x_field", df.columns[0])
        y_field = config.get("y_field", df.columns[1] if len(df.columns) > 1 else df.columns[0])
        
        if x_field in df.columns and y_field in df.columns:
            ax.plot(df[x_field], df[y_field], marker='o')
    
    def _create_pie_chart(self, df, config, ax, plt=None):
        """Create pie chart"""
        x_field = config.get("x_field")
        y_field = config.get("y_field")
        
        if not x_field:
            # Use first categorical column
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                x_field = categorical_cols[0]
        
        if x_field in df.columns:
            if y_field and y_field in df.columns:
                # Aggregate by y_field
                pie_data = df.groupby(x_field)[y_field].sum()
            else:
                # Count by x_field
                pie_data = df[x_field].value_counts()
            
            ax.pie(pie_data.values, labels=pie_data.index, autopct='%1.1f%%')
    
    def _create_scatter_chart(self, df, config, ax, plt=None):
        """Create scatter plot"""
        x_field = config.get("x_field")
        y_field = config.get("y_field")
        
        # Auto-detect numeric fields
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if not x_field and len(numeric_cols) > 0:
            x_field = numeric_cols[0]
        if not y_field and len(numeric_cols) > 1:
            y_field = numeric_cols[1]
        
        if x_field in df.columns and y_field in df.columns:
            ax.scatter(df[x_field], df[y_field], alpha=0.6)
    
    def _create_histogram(self, df, config, ax, plt=None):
        """Create histogram"""
        x_field = config.get("x_field")
        
        if not x_field:
            # Use first numeric column
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                x_field = numeric_cols[0]
        
        if x_field in df.columns:
            ax.hist(df[x_field].dropna(), bins=20, alpha=0.7, edgecolor='black')
    
    def _create_box_plot(self, df, config, ax, plt=None):
        """Create box plot"""
        y_field = config.get("y_field")
        group_by = config.get("group_by")
        
        if not y_field:
            # Use first numeric column
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                y_field = numeric_cols[0]
        
        if y_field in df.columns:
            if group_by and group_by in df.columns:
                # Grouped box plot
                groups = [group[y_field].dropna() for name, group in df.groupby(group_by)]
                ax.boxplot(groups, labels=df[group_by].unique())
            else:
                # Single box plot
                ax.boxplot(df[y_field].dropna())
    
    def _create_heatmap(self, df, config, ax, plt=None):
        """Create heatmap"""
        import numpy as np
        
        # Use correlation matrix for numeric data
        numeric_df = df.select_dtypes(include=['number'])
        if len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()
            im = ax.imshow(corr_matrix.values, cmap='coolwarm', aspect='auto')
            
            # Set ticks and labels
            ax.set_xticks(range(len(corr_matrix.columns)))
            ax.set_yticks(range(len(corr_matrix.columns)))
            ax.set_xticklabels(corr_matrix.columns, rotation=45)
            ax.set_yticklabels(corr_matrix.columns)
            
            # Add colorbar
            if plt:
                plt.colorbar(im, ax=ax)
    
    def _apply_chart_styling(self, ax, config, plt=None):
        """Apply styling to chart"""
        title = config.get("title", "Data Visualization")
        x_label = config.get("x_label", "")
        y_label = config.get("y_label", "")
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)
        
        ax.grid(True, alpha=0.3)
        if plt:
            plt.tight_layout()
    
    def _generate_output(self, fig, output_format: str, plt=None) -> Dict[str, Any]:
        """Generate output in specified format"""
        import io
        import base64
        
        if output_format == "base64":
            # Convert to base64 image
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            
            return {
                "visualization": image_base64,
                "format": "base64_png",
                "display_hint": "data:image/png;base64," + image_base64
            }
            
        elif output_format == "html":
            # Convert to HTML (simplified)
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            
            html_content = f'''
            <div class="visualization-container">
                <img src="data:image/png;base64,{image_base64}" 
                     style="max-width: 100%; height: auto;" 
                     alt="Data Visualization" />
            </div>
            '''
            
            return {
                "visualization": html_content,
                "format": "html"
            }
            
        elif output_format == "json":
            # Return chart configuration (for frontend rendering)
            return {
                "visualization": {
                    "message": "JSON format not fully implemented - use base64 or html"
                },
                "format": "json"
            }
        
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _optimize_dataframe_for_visualization(self, df):
        """Optimize DataFrame data types for visualization compatibility"""
        import pandas as pd
        import numpy as np
        
        # Create a copy to avoid modifying original
        df_optimized = df.copy()
        
        for column in df_optimized.columns:
            # Try to convert string representations back to appropriate types
            if df_optimized[column].dtype == 'object':
                # Try numeric conversion first
                try:
                    # Check if it looks like numbers
                    numeric_series = pd.to_numeric(df_optimized[column], errors='coerce')
                    if not numeric_series.isna().all():
                        df_optimized[column] = numeric_series
                        continue
                except:
                    pass
                
                # Try datetime conversion
                try:
                    # Check if it looks like dates
                    if df_optimized[column].astype(str).str.contains(r'\d{4}-\d{2}-\d{2}').any():
                        df_optimized[column] = pd.to_datetime(df_optimized[column], errors='coerce')
                        continue
                except:
                    pass
                
                # Try boolean conversion
                try:
                    if df_optimized[column].isin(['0', '1', 'True', 'False', 'true', 'false']).all():
                        df_optimized[column] = df_optimized[column].map({
                            '0': False, '1': True, 'True': True, 'False': False,
                            'true': True, 'false': False
                        })
                        continue
                except:
                    pass
        
        return df_optimized
    
    


# Make sure class is available for discovery
# The plugin manager will find CreateVisualization automatically