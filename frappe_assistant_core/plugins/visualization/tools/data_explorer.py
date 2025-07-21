"""
Data Explorer Tool - AI-powered data discovery and visualization suggestions

Analyzes data sources and provides intelligent recommendations for
optimal visualizations and dashboard configurations.
"""

import frappe
from frappe import _
import json
from typing import Dict, Any, List, Optional, Tuple
from frappe_assistant_core.core.base_tool import BaseTool


class DataExplorer(BaseTool):
    """
    AI-powered data discovery and visualization suggestions.
    
    Provides capabilities for:
    - Analyzing data structure and patterns
    - Suggesting optimal visualizations
    - Recommending dashboard templates
    - Detecting data relationships and correlations
    - Identifying trending patterns and anomalies
    """
    
    def __init__(self):
        super().__init__()
        self.name = "suggest_visualizations"
        self.description = self._get_description()
        self.requires_permission = None
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "DocType to analyze for visualization suggestions"
                },
                "user_intent": {
                    "type": "string",
                    "description": "User's stated purpose or goal for the visualization"
                },
                "analysis_depth": {
                    "type": "string",
                    "enum": ["basic", "detailed", "comprehensive"],
                    "default": "detailed",
                    "description": "Level of analysis to perform"
                },
                "include_relationships": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include analysis of linked doctypes"
                },
                "sample_size": {
                    "type": "integer",
                    "default": 1000,
                    "maximum": 5000,
                    "description": "Number of records to analyze"
                },
                "focus_areas": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["trends", "distributions", "correlations", "outliers", "comparisons", "time_series"]
                    },
                    "description": "Specific analysis areas to focus on"
                }
            },
            "required": ["doctype"]
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Analyze data sources and provide AI-powered recommendations for optimal visualizations. Performs field type detection, pattern analysis, and suggests appropriate chart types and dashboard templates based on data characteristics."""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data and suggest visualizations"""
        try:
            doctype = arguments.get("doctype")
            user_intent = arguments.get("user_intent", "")
            analysis_depth = arguments.get("analysis_depth", "detailed")
            include_relationships = arguments.get("include_relationships", True)
            sample_size = arguments.get("sample_size", 1000)
            focus_areas = arguments.get("focus_areas", [])
            
            # Validate doctype access
            if not frappe.has_permission(doctype, "read"):
                return {
                    "success": False,
                    "error": f"Insufficient permissions to access {doctype} data"
                }
            
            # Analyze doctype structure
            doctype_analysis = self._analyze_doctype_structure(doctype, sample_size)
            
            if not doctype_analysis["valid"]:
                return {
                    "success": False,
                    "error": f"Unable to analyze {doctype}: {doctype_analysis['error']}"
                }
            
            # Perform data analysis based on depth
            data_insights = self._analyze_data_patterns(
                doctype, doctype_analysis, analysis_depth, focus_areas, sample_size
            )
            
            # Generate visualization suggestions
            chart_suggestions = self._generate_chart_suggestions(
                doctype_analysis, data_insights, user_intent
            )
            
            # Recommend dashboard templates
            template_recommendations = self._recommend_templates(
                doctype, doctype_analysis, user_intent
            )
            
            # Analyze relationships if requested
            relationship_analysis = {}
            if include_relationships:
                relationship_analysis = self._analyze_relationships(doctype, doctype_analysis)
            
            return {
                "success": True,
                "doctype": doctype,
                "analysis_summary": {
                    "record_count": doctype_analysis["record_count"],
                    "field_count": len(doctype_analysis["fields"]),
                    "data_quality_score": data_insights.get("quality_score", 0),
                    "analysis_depth": analysis_depth
                },
                "doctype_analysis": doctype_analysis,
                "data_insights": data_insights,
                "chart_suggestions": chart_suggestions,
                "template_recommendations": template_recommendations,
                "relationship_analysis": relationship_analysis,
                "recommended_actions": self._generate_recommended_actions(
                    doctype_analysis, data_insights, chart_suggestions, template_recommendations
                )
            }
            
        except Exception as e:
            frappe.log_error(
                title=_("Data Explorer Error"),
                message=f"Error analyzing {doctype}: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_doctype_structure(self, doctype: str, sample_size: int) -> Dict[str, Any]:
        """Analyze doctype metadata and structure"""
        try:
            # Get doctype metadata
            meta = frappe.get_meta(doctype)
            
            # Analyze fields
            fields_analysis = {}
            numeric_fields = []
            categorical_fields = []
            date_fields = []
            text_fields = []
            
            for field in meta.fields:
                field_info = {
                    "fieldtype": field.fieldtype,
                    "label": field.label,
                    "mandatory": field.reqd,
                    "unique": field.unique
                }
                
                # Categorize fields
                if field.fieldtype in ["Int", "Float", "Currency", "Percent"]:
                    numeric_fields.append(field.fieldname)
                    field_info["category"] = "numeric"
                elif field.fieldtype in ["Select", "Link", "Data"]:
                    categorical_fields.append(field.fieldname)
                    field_info["category"] = "categorical"
                elif field.fieldtype in ["Date", "Datetime", "Time"]:
                    date_fields.append(field.fieldname)
                    field_info["category"] = "temporal"
                elif field.fieldtype in ["Text", "Small Text", "Long Text"]:
                    text_fields.append(field.fieldname)
                    field_info["category"] = "text"
                else:
                    field_info["category"] = "other"
                
                fields_analysis[field.fieldname] = field_info
            
            # Get record count
            record_count = frappe.db.count(doctype)
            
            # Analyze sample data for field characteristics
            if record_count > 0:
                sample_data = frappe.get_all(
                    doctype,
                    fields=["*"],
                    limit=min(sample_size, record_count),
                    order_by="creation desc"
                )
                
                # Analyze field characteristics from sample
                field_stats = self._analyze_field_statistics(sample_data, fields_analysis)
            else:
                field_stats = {}
            
            return {
                "valid": True,
                "doctype": doctype,
                "record_count": record_count,
                "fields": fields_analysis,
                "field_categories": {
                    "numeric": numeric_fields,
                    "categorical": categorical_fields,
                    "temporal": date_fields,
                    "text": text_fields
                },
                "field_statistics": field_stats,
                "sample_analyzed": len(sample_data) if record_count > 0 else 0
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def _analyze_field_statistics(self, sample_data: List[Dict], fields_analysis: Dict) -> Dict[str, Any]:
        """Analyze statistical properties of fields from sample data"""
        try:
            import pandas as pd
            import numpy as np
            
            if not sample_data:
                return {}
            
            df = pd.DataFrame(sample_data)
            field_stats = {}
            
            for field_name, field_info in fields_analysis.items():
                if field_name not in df.columns:
                    continue
                
                series = df[field_name]
                stats = {
                    "null_count": series.isnull().sum(),
                    "null_percentage": (series.isnull().sum() / len(series)) * 100,
                    "unique_count": series.nunique(),
                    "unique_percentage": (series.nunique() / len(series)) * 100
                }
                
                # Category-specific statistics
                if field_info["category"] == "numeric":
                    numeric_series = pd.to_numeric(series, errors='coerce')
                    if not numeric_series.isnull().all():
                        stats.update({
                            "min": float(numeric_series.min()),
                            "max": float(numeric_series.max()),
                            "mean": float(numeric_series.mean()),
                            "median": float(numeric_series.median()),
                            "std": float(numeric_series.std()),
                            "outlier_count": self._count_outliers(numeric_series)
                        })
                
                elif field_info["category"] == "categorical":
                    value_counts = series.value_counts()
                    stats.update({
                        "most_common": value_counts.index[0] if not value_counts.empty else None,
                        "most_common_count": int(value_counts.iloc[0]) if not value_counts.empty else 0,
                        "distribution": value_counts.head(10).to_dict()
                    })
                
                elif field_info["category"] == "temporal":
                    date_series = pd.to_datetime(series, errors='coerce')
                    if not date_series.isnull().all():
                        stats.update({
                            "min_date": date_series.min().isoformat() if pd.notna(date_series.min()) else None,
                            "max_date": date_series.max().isoformat() if pd.notna(date_series.max()) else None,
                            "date_range_days": (date_series.max() - date_series.min()).days if pd.notna(date_series.min()) and pd.notna(date_series.max()) else 0
                        })
                
                field_stats[field_name] = stats
            
            return field_stats
            
        except Exception as e:
            frappe.logger("data_explorer").error(f"Field statistics analysis failed: {str(e)}")
            return {}
    
    def _count_outliers(self, series) -> int:
        """Count outliers using IQR method"""
        try:
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = series[(series < lower_bound) | (series > upper_bound)]
            return len(outliers)
        except:
            return 0
    
    def _analyze_data_patterns(self, doctype: str, doctype_analysis: Dict, 
                              analysis_depth: str, focus_areas: List[str], 
                              sample_size: int) -> Dict[str, Any]:
        """Analyze data patterns and generate insights"""
        try:
            insights = {
                "quality_score": 0,
                "patterns": [],
                "trends": [],
                "anomalies": [],
                "recommendations": []
            }
            
            field_stats = doctype_analysis.get("field_statistics", {})
            
            # Calculate data quality score
            quality_factors = []
            for field_name, stats in field_stats.items():
                # Completeness factor (lower null percentage is better)
                completeness = max(0, 100 - stats.get("null_percentage", 100))
                quality_factors.append(completeness)
            
            insights["quality_score"] = sum(quality_factors) / len(quality_factors) if quality_factors else 0
            
            # Identify patterns based on field analysis
            numeric_fields = doctype_analysis["field_categories"]["numeric"]
            categorical_fields = doctype_analysis["field_categories"]["categorical"]
            date_fields = doctype_analysis["field_categories"]["temporal"]
            
            # Pattern detection
            if len(numeric_fields) >= 2:
                insights["patterns"].append({
                    "type": "correlation_opportunity",
                    "description": f"Multiple numeric fields ({len(numeric_fields)}) available for correlation analysis",
                    "fields": numeric_fields[:5],  # Limit to first 5
                    "recommended_charts": ["scatter", "heatmap"]
                })
            
            if len(categorical_fields) >= 1 and len(numeric_fields) >= 1:
                insights["patterns"].append({
                    "type": "comparison_opportunity",
                    "description": "Categorical and numeric fields available for comparison analysis",
                    "categorical_fields": categorical_fields[:3],
                    "numeric_fields": numeric_fields[:3],
                    "recommended_charts": ["bar", "pie", "box"]
                })
            
            if len(date_fields) >= 1 and len(numeric_fields) >= 1:
                insights["patterns"].append({
                    "type": "time_series_opportunity",
                    "description": "Time-based data available for trend analysis",
                    "date_fields": date_fields,
                    "numeric_fields": numeric_fields[:3],
                    "recommended_charts": ["line", "area"]
                })
            
            # Detect high-cardinality fields (good for grouping)
            for field_name, stats in field_stats.items():
                unique_percentage = stats.get("unique_percentage", 0)
                if 5 <= unique_percentage <= 50:  # Good for grouping
                    insights["patterns"].append({
                        "type": "grouping_opportunity",
                        "description": f"Field '{field_name}' has good cardinality for grouping",
                        "field": field_name,
                        "unique_count": stats.get("unique_count", 0),
                        "recommended_use": "group_by or color_coding"
                    })
            
            # Generate specific recommendations based on analysis depth
            if analysis_depth in ["detailed", "comprehensive"]:
                insights["recommendations"] = self._generate_detailed_recommendations(
                    doctype_analysis, insights, focus_areas
                )
            
            return insights
            
        except Exception as e:
            frappe.logger("data_explorer").error(f"Data pattern analysis failed: {str(e)}")
            return {"quality_score": 0, "patterns": [], "trends": [], "anomalies": [], "recommendations": []}
    
    def _generate_detailed_recommendations(self, doctype_analysis: Dict, insights: Dict, focus_areas: List[str]) -> List[Dict]:
        """Generate detailed recommendations based on analysis"""
        recommendations = []
        
        field_stats = doctype_analysis.get("field_statistics", {})
        numeric_fields = doctype_analysis["field_categories"]["numeric"]
        categorical_fields = doctype_analysis["field_categories"]["categorical"]
        date_fields = doctype_analysis["field_categories"]["temporal"]
        
        # Recommend based on focus areas
        if "trends" in focus_areas and date_fields and numeric_fields:
            recommendations.append({
                "type": "trend_analysis",
                "priority": "high",
                "title": "Time Series Trend Analysis",
                "description": "Create line charts to analyze trends over time",
                "suggested_charts": [
                    {
                        "chart_type": "line",
                        "x_field": date_fields[0],
                        "y_field": numeric_fields[0],
                        "rationale": "Track changes over time"
                    }
                ]
            })
        
        if "distributions" in focus_areas and numeric_fields:
            recommendations.append({
                "type": "distribution_analysis",
                "priority": "medium",
                "title": "Data Distribution Analysis",
                "description": "Understand data distribution patterns",
                "suggested_charts": [
                    {
                        "chart_type": "histogram",
                        "y_field": numeric_fields[0],
                        "rationale": "Show distribution pattern"
                    }
                ]
            })
        
        if "comparisons" in focus_areas and categorical_fields and numeric_fields:
            recommendations.append({
                "type": "comparison_analysis",
                "priority": "high", 
                "title": "Category Comparison",
                "description": "Compare values across different categories",
                "suggested_charts": [
                    {
                        "chart_type": "bar",
                        "x_field": categorical_fields[0],
                        "y_field": numeric_fields[0],
                        "rationale": "Compare categories side by side"
                    }
                ]
            })
        
        # Quality-based recommendations
        low_quality_fields = [
            field for field, stats in field_stats.items()
            if stats.get("null_percentage", 0) > 30
        ]
        
        if low_quality_fields:
            recommendations.append({
                "type": "data_quality",
                "priority": "high",
                "title": "Data Quality Improvement",
                "description": f"Fields with high missing values: {', '.join(low_quality_fields[:3])}",
                "action": "Consider data cleaning or filtering these fields"
            })
        
        return recommendations
    
    def _generate_chart_suggestions(self, doctype_analysis: Dict, data_insights: Dict, user_intent: str) -> List[Dict]:
        """Generate specific chart suggestions"""
        suggestions = []
        
        numeric_fields = doctype_analysis["field_categories"]["numeric"]
        categorical_fields = doctype_analysis["field_categories"]["categorical"]
        date_fields = doctype_analysis["field_categories"]["temporal"]
        field_stats = doctype_analysis.get("field_statistics", {})
        
        # High-priority suggestions based on data structure
        
        # 1. Time series analysis
        if date_fields and numeric_fields:
            for date_field in date_fields[:2]:
                for numeric_field in numeric_fields[:3]:
                    suggestions.append({
                        "chart_type": "line",
                        "title": f"{field_stats.get(numeric_field, {}).get('label', numeric_field)} Trend",
                        "x_field": date_field,
                        "y_field": numeric_field,
                        "aggregate": "sum",
                        "priority": "high",
                        "rationale": "Time-based trend analysis reveals patterns and seasonality",
                        "business_value": "Track performance over time, identify trends and seasonal patterns"
                    })
        
        # 2. Category comparisons
        if categorical_fields and numeric_fields:
            for cat_field in categorical_fields[:2]:
                for num_field in numeric_fields[:2]:
                    # Check if categorical field has reasonable cardinality
                    cardinality = field_stats.get(cat_field, {}).get("unique_count", 0)
                    if 2 <= cardinality <= 20:  # Good for bar charts
                        suggestions.append({
                            "chart_type": "bar",
                            "title": f"{field_stats.get(num_field, {}).get('label', num_field)} by {field_stats.get(cat_field, {}).get('label', cat_field)}",
                            "x_field": cat_field,
                            "y_field": num_field,
                            "aggregate": "sum",
                            "priority": "high",
                            "rationale": f"Compare {num_field} across different {cat_field} categories",
                            "business_value": "Identify top performers and compare category performance"
                        })
        
        # 3. Distribution analysis
        for numeric_field in numeric_fields[:3]:
            suggestions.append({
                "chart_type": "histogram",
                "title": f"{field_stats.get(numeric_field, {}).get('label', numeric_field)} Distribution",
                "y_field": numeric_field,
                "priority": "medium",
                "rationale": "Understand data distribution and identify outliers",
                "business_value": "Spot anomalies and understand data patterns"
            })
        
        # 4. Proportional analysis
        for cat_field in categorical_fields[:2]:
            cardinality = field_stats.get(cat_field, {}).get("unique_count", 0)
            if 2 <= cardinality <= 10:  # Good for pie charts
                suggestions.append({
                    "chart_type": "pie",
                    "title": f"Distribution by {field_stats.get(cat_field, {}).get('label', cat_field)}",
                    "x_field": cat_field,
                    "y_field": "name",  # Count
                    "aggregate": "count",
                    "priority": "medium",
                    "rationale": f"Show proportional breakdown by {cat_field}",
                    "business_value": "Understand composition and market share"
                })
        
        # 5. Correlation analysis for multiple numeric fields
        if len(numeric_fields) >= 2:
            suggestions.append({
                "chart_type": "scatter",
                "title": f"{field_stats.get(numeric_fields[0], {}).get('label', numeric_fields[0])} vs {field_stats.get(numeric_fields[1], {}).get('label', numeric_fields[1])}",
                "x_field": numeric_fields[0],
                "y_field": numeric_fields[1],
                "priority": "medium",
                "rationale": "Explore correlation between numeric variables",
                "business_value": "Identify relationships and dependencies between metrics"
            })
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda x: priority_order.get(x["priority"], 2))
        
        return suggestions[:10]  # Return top 10 suggestions
    
    def _recommend_templates(self, doctype: str, doctype_analysis: Dict, user_intent: str) -> List[Dict]:
        """Recommend dashboard templates based on doctype and analysis"""
        recommendations = []
        
        # Map doctypes to likely business functions
        doctype_mapping = {
            "Sales Invoice": ["sales"],
            "Sales Order": ["sales"],
            "Customer": ["sales"],
            "GL Entry": ["financial"],
            "Journal Entry": ["financial"],
            "Payment Entry": ["financial"],
            "Stock Ledger Entry": ["inventory"],
            "Item": ["inventory"],
            "Warehouse": ["inventory"],
            "Employee": ["hr"],
            "Attendance": ["hr"],
            "Leave Application": ["hr"],
            "Company": ["executive"],
            "Lead": ["sales"],
            "Opportunity": ["sales"]
        }
        
        # Get template recommendations based on doctype
        likely_templates = doctype_mapping.get(doctype, [])
        
        # Add context-based recommendations
        numeric_fields = doctype_analysis["field_categories"]["numeric"]
        date_fields = doctype_analysis["field_categories"]["temporal"]
        
        # Executive template for high-level overview
        if len(numeric_fields) >= 3 and date_fields:
            recommendations.append({
                "template_type": "executive",
                "confidence": 0.8,
                "title": "Executive Summary Dashboard",
                "description": "High-level KPIs and performance metrics",
                "rationale": "Multiple numeric fields suggest comprehensive business metrics suitable for executive overview"
            })
        
        # Add specific template recommendations
        for template in likely_templates:
            confidence = 0.9  # High confidence for direct doctype matches
            
            template_info = {
                "sales": {
                    "title": "Sales Performance Dashboard",
                    "description": "Revenue trends, customer analysis, and sales metrics",
                    "rationale": "Sales-related doctype detected"
                },
                "financial": {
                    "title": "Financial Performance Dashboard", 
                    "description": "P&L analysis, cash flow, and financial ratios",
                    "rationale": "Financial data structure detected"
                },
                "inventory": {
                    "title": "Inventory Management Dashboard",
                    "description": "Stock levels, movement trends, and warehouse analytics",
                    "rationale": "Inventory-related doctype detected"
                },
                "hr": {
                    "title": "HR Analytics Dashboard",
                    "description": "Employee metrics, attendance, and performance tracking",
                    "rationale": "HR-related doctype detected"
                }
            }
            
            if template in template_info:
                recommendations.append({
                    "template_type": template,
                    "confidence": confidence,
                    **template_info[template]
                })
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        
        return recommendations
    
    def _analyze_relationships(self, doctype: str, doctype_analysis: Dict) -> Dict[str, Any]:
        """Analyze relationships with other doctypes"""
        try:
            meta = frappe.get_meta(doctype)
            relationships = {
                "linked_doctypes": [],
                "child_tables": [],
                "parent_doctype": None
            }
            
            # Find link fields
            for field in meta.fields:
                if field.fieldtype == "Link" and field.options:
                    relationships["linked_doctypes"].append({
                        "doctype": field.options,
                        "field": field.fieldname,
                        "label": field.label
                    })
                elif field.fieldtype == "Table" and field.options:
                    relationships["child_tables"].append({
                        "doctype": field.options,
                        "field": field.fieldname,
                        "label": field.label
                    })
            
            # Check if this is a child table
            if meta.istable:
                relationships["parent_doctype"] = meta.module
            
            return relationships
            
        except Exception as e:
            frappe.logger("data_explorer").error(f"Relationship analysis failed: {str(e)}")
            return {"linked_doctypes": [], "child_tables": [], "parent_doctype": None}
    
    def _generate_recommended_actions(self, doctype_analysis: Dict, data_insights: Dict,
                                    chart_suggestions: List[Dict], template_recommendations: List[Dict]) -> List[str]:
        """Generate list of recommended actions"""
        actions = []
        
        # Template recommendations
        if template_recommendations:
            top_template = template_recommendations[0]
            actions.append(f"Create {top_template['title']} using the {top_template['template_type']} template")
        
        # Chart recommendations
        high_priority_charts = [chart for chart in chart_suggestions if chart.get("priority") == "high"]
        if high_priority_charts:
            actions.append(f"Start with {len(high_priority_charts)} high-priority charts: {', '.join([c['chart_type'] for c in high_priority_charts[:3]])}")
        
        # Data quality actions
        quality_score = data_insights.get("quality_score", 0)
        if quality_score < 70:
            actions.append("Improve data quality by addressing missing values and cleaning data")
        
        # Pattern-based actions
        patterns = data_insights.get("patterns", [])
        correlation_patterns = [p for p in patterns if p.get("type") == "correlation_opportunity"]
        if correlation_patterns:
            actions.append("Explore correlations between numeric fields using scatter plots and heatmaps")
        
        time_series_patterns = [p for p in patterns if p.get("type") == "time_series_opportunity"]
        if time_series_patterns:
            actions.append("Create time series analysis to track trends and seasonality")
        
        return actions[:5]  # Return top 5 actions


# Export tools for plugin discovery
__all__ = ["DataExplorer"]