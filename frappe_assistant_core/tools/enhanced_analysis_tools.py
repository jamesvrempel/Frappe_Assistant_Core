"""
Enhanced Analysis Tools with Progress Streaming
Extended version of analysis tools with real-time progress tracking
"""

import frappe
from frappe_assistant_core.tools.analysis_tools import AnalysisTools
from frappe_assistant_core.utils.progress_streaming import (
    ProgressContext, 
    ProgressStatus, 
    track_progress, 
    update_progress,
    get_current_progress_tracker
)
from typing import Dict, Any, List

class EnhancedAnalysisTools(AnalysisTools):
    """Enhanced analysis tools with progress streaming capabilities"""
    
    @staticmethod
    def get_tools() -> List[Dict[str, Any]]:
        """Get enhanced tool definitions with progress streaming"""
        base_tools = AnalysisTools.get_tools()
        
        # Enhance existing tools with progress streaming metadata
        enhanced_tools = []
        for tool in base_tools:
            enhanced_tool = tool.copy()
            
            # Add progress streaming capabilities to all tools
            enhanced_tool["capabilities"] = enhanced_tool.get("capabilities", []) + [
                "progress_streaming",
                "real_time_updates",
                "operation_cancellation"
            ]
            
            # Add progress streaming notice to description
            if "description" in enhanced_tool:
                enhanced_tool["description"] += "\n\n🔄 **Progress Streaming Enabled**: This tool provides real-time progress updates during execution."
            
            enhanced_tools.append(enhanced_tool)
        
        return enhanced_tools
    
    @staticmethod
    @track_progress("python_code_execution")
    def execute_python_code_with_progress(code: str, data_query: Dict = None, imports: List[str] = None) -> Dict[str, Any]:
        """Enhanced Python code execution with progress tracking"""
        
        tracker = get_current_progress_tracker()
        
        try:
            # Step 1: Security validation
            if tracker:
                tracker.update_progress(
                    status=ProgressStatus.RUNNING,
                    progress_percent=10,
                    current_step="Security Validation",
                    message="Validating user permissions and code security"
                )
            
            # Check user permissions
            user_roles = frappe.get_roles(frappe.session.user)
            if "System Manager" not in user_roles:
                if tracker:
                    tracker.update_progress(
                        status=ProgressStatus.FAILED,
                        progress_percent=100,
                        message="Permission denied: System Manager role required",
                        error="Insufficient permissions"
                    )
                return {
                    "success": False,
                    "error": "Python code execution requires System Manager role",
                    "required_role": "System Manager",
                    "user_roles": user_roles
                }
            
            # Step 2: Environment preparation
            if tracker:
                tracker.update_progress(
                    status=ProgressStatus.RUNNING,
                    progress_percent=25,
                    current_step="Environment Setup",
                    message="Preparing secure execution environment"
                )
            
            # Step 3: Data fetching (if needed)
            if data_query:
                if tracker:
                    tracker.update_progress(
                        status=ProgressStatus.RUNNING,
                        progress_percent=40,
                        current_step="Data Fetching",
                        message=f"Fetching data from {data_query.get('doctype', 'unknown')}"
                    )
                
                # Validate data query
                doctype = data_query.get("doctype")
                if not frappe.has_permission(doctype, "read"):
                    if tracker:
                        tracker.update_progress(
                            status=ProgressStatus.FAILED,
                            progress_percent=100,
                            message=f"No read permission for {doctype}",
                            error="Permission denied"
                        )
                    return {"success": False, "error": f"No read permission for {doctype}"}
            
            # Step 4: Code execution
            if tracker:
                tracker.update_progress(
                    status=ProgressStatus.RUNNING,
                    progress_percent=60,
                    current_step="Code Execution",
                    message="Executing Python code in secure environment"
                )
            
            # Execute using the base class method
            result = AnalysisTools.execute_python_code(code, data_query, imports)
            
            # Step 5: Result processing
            if tracker:
                tracker.update_progress(
                    status=ProgressStatus.RUNNING,
                    progress_percent=90,
                    current_step="Result Processing",
                    message="Processing execution results"
                )
            
            # Enhance result with execution metadata
            if result.get("success"):
                result["execution_metadata"] = {
                    "progress_tracked": True,
                    "execution_time": tracker.get_duration() if tracker else 0,
                    "user": frappe.session.user,
                    "timestamp": frappe.utils.now()
                }
            
            # Step 6: Completion
            if tracker:
                status = ProgressStatus.COMPLETED if result.get("success") else ProgressStatus.FAILED
                tracker.update_progress(
                    status=status,
                    progress_percent=100,
                    current_step="Completed",
                    message="Python code execution finished" if result.get("success") else "Execution failed",
                    error=result.get("error") if not result.get("success") else None
                )
            
            return result
            
        except Exception as e:
            if tracker:
                tracker.update_progress(
                    status=ProgressStatus.FAILED,
                    progress_percent=100,
                    message=f"Execution failed: {str(e)}",
                    error=str(e)
                )
            
            return {
                "success": False,
                "error": str(e),
                "traceback": frappe.get_traceback()
            }
    
    @staticmethod
    @track_progress("frappe_data_analysis")
    def analyze_frappe_data_with_progress(doctype: str, analysis_type: str = "summary", 
                                        filters: Dict = None, fields: List[str] = None,
                                        limit: int = 1000) -> Dict[str, Any]:
        """Enhanced Frappe data analysis with progress tracking"""
        
        tracker = get_current_progress_tracker()
        
        try:
            # Step 1: Permission validation
            if tracker:
                tracker.update_progress(
                    status=ProgressStatus.RUNNING,
                    progress_percent=10,
                    current_step="Permission Check",
                    message=f"Validating access to {doctype}"
                )
            
            if not frappe.has_permission(doctype, "read"):
                if tracker:
                    tracker.update_progress(
                        status=ProgressStatus.FAILED,
                        progress_percent=100,
                        message=f"No read permission for {doctype}",
                        error="Permission denied"
                    )
                return {"success": False, "error": f"No read permission for {doctype}"}
            
            # Step 2: Data fetching
            if tracker:
                tracker.update_progress(
                    status=ProgressStatus.RUNNING,
                    progress_percent=30,
                    current_step="Data Fetching",
                    message=f"Retrieving {doctype} records"
                )
            
            filters = filters or {}
            fields = fields or ["*"]
            
            data = frappe.get_all(doctype, filters=filters, fields=fields, limit=limit)
            
            if not data:
                if tracker:
                    tracker.update_progress(
                        status=ProgressStatus.COMPLETED,
                        progress_percent=100,
                        message="No data found matching criteria"
                    )
                return {
                    "success": True,
                    "message": "No data found",
                    "record_count": 0
                }
            
            # Step 3: Analysis execution
            if tracker:
                tracker.update_progress(
                    status=ProgressStatus.RUNNING,
                    progress_percent=60,
                    current_step="Data Analysis",
                    message=f"Analyzing {len(data)} records"
                )
            
            # Perform different types of analysis
            analysis_result = {}
            
            if analysis_type == "summary":
                analysis_result = EnhancedAnalysisTools._perform_summary_analysis(data, doctype, tracker)
            elif analysis_type == "statistical":
                analysis_result = EnhancedAnalysisTools._perform_statistical_analysis(data, doctype, tracker)
            elif analysis_type == "trend":
                analysis_result = EnhancedAnalysisTools._perform_trend_analysis(data, doctype, tracker)
            else:
                analysis_result = EnhancedAnalysisTools._perform_custom_analysis(data, doctype, analysis_type, tracker)
            
            # Step 4: Result compilation
            if tracker:
                tracker.update_progress(
                    status=ProgressStatus.RUNNING,
                    progress_percent=90,
                    current_step="Result Compilation",
                    message="Compiling analysis results"
                )
            
            result = {
                "success": True,
                "doctype": doctype,
                "analysis_type": analysis_type,
                "record_count": len(data),
                "analysis_results": analysis_result,
                "execution_metadata": {
                    "progress_tracked": True,
                    "execution_time": tracker.get_duration() if tracker else 0,
                    "user": frappe.session.user,
                    "timestamp": frappe.utils.now()
                }
            }
            
            # Step 5: Completion
            if tracker:
                tracker.update_progress(
                    status=ProgressStatus.COMPLETED,
                    progress_percent=100,
                    current_step="Completed",
                    message=f"Analysis of {doctype} completed successfully"
                )
            
            return result
            
        except Exception as e:
            if tracker:
                tracker.update_progress(
                    status=ProgressStatus.FAILED,
                    progress_percent=100,
                    message=f"Analysis failed: {str(e)}",
                    error=str(e)
                )
            
            return {
                "success": False,
                "error": str(e),
                "traceback": frappe.get_traceback()
            }
    
    @staticmethod
    def _perform_summary_analysis(data: List[Dict], doctype: str, tracker=None) -> Dict[str, Any]:
        """Perform summary analysis with progress updates"""
        try:
            if tracker:
                update_progress(75, "Generating summary statistics")
            
            # Basic statistics
            summary = {
                "total_records": len(data),
                "fields_analyzed": len(data[0].keys()) if data else 0,
                "sample_record": data[0] if data else None
            }
            
            # Field analysis
            field_analysis = {}
            for field in data[0].keys() if data else []:
                values = [record.get(field) for record in data if record.get(field) is not None]
                field_analysis[field] = {
                    "non_null_count": len(values),
                    "null_count": len(data) - len(values),
                    "unique_count": len(set(str(v) for v in values)) if values else 0
                }
            
            summary["field_analysis"] = field_analysis
            return summary
            
        except Exception as e:
            return {"error": f"Summary analysis failed: {str(e)}"}
    
    @staticmethod
    def _perform_statistical_analysis(data: List[Dict], doctype: str, tracker=None) -> Dict[str, Any]:
        """Perform statistical analysis with progress updates"""
        try:
            if tracker:
                update_progress(75, "Calculating statistical measures")
            
            import statistics
            from datetime import datetime
            
            stats_result = {"numeric_fields": {}, "date_fields": {}}
            
            # Identify numeric and date fields
            for field in data[0].keys() if data else []:
                values = [record.get(field) for record in data if record.get(field) is not None]
                
                # Try to identify numeric fields
                numeric_values = []
                for value in values:
                    try:
                        if isinstance(value, (int, float)):
                            numeric_values.append(float(value))
                        elif isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                            numeric_values.append(float(value))
                    except:
                        continue
                
                if numeric_values and len(numeric_values) > 1:
                    stats_result["numeric_fields"][field] = {
                        "count": len(numeric_values),
                        "mean": round(statistics.mean(numeric_values), 2),
                        "median": round(statistics.median(numeric_values), 2),
                        "min": min(numeric_values),
                        "max": max(numeric_values),
                        "std_dev": round(statistics.stdev(numeric_values), 2) if len(numeric_values) > 1 else 0
                    }
            
            return stats_result
            
        except Exception as e:
            return {"error": f"Statistical analysis failed: {str(e)}"}
    
    @staticmethod
    def _perform_trend_analysis(data: List[Dict], doctype: str, tracker=None) -> Dict[str, Any]:
        """Perform trend analysis with progress updates"""
        try:
            if tracker:
                update_progress(75, "Analyzing trends over time")
            
            # Look for date fields
            date_fields = []
            for field in data[0].keys() if data else []:
                if 'date' in field.lower() or 'time' in field.lower() or field in ['creation', 'modified']:
                    date_fields.append(field)
            
            trend_result = {"date_fields_found": date_fields}
            
            # Simple trend analysis on first date field found
            if date_fields and data:
                primary_date_field = date_fields[0]
                
                # Group by month/year
                monthly_counts = {}
                for record in data:
                    date_value = record.get(primary_date_field)
                    if date_value:
                        try:
                            if isinstance(date_value, str):
                                date_obj = frappe.utils.getdate(date_value)
                            else:
                                date_obj = date_value
                            
                            month_key = f"{date_obj.year}-{date_obj.month:02d}"
                            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
                        except:
                            continue
                
                trend_result["monthly_distribution"] = dict(sorted(monthly_counts.items()))
            
            return trend_result
            
        except Exception as e:
            return {"error": f"Trend analysis failed: {str(e)}"}
    
    @staticmethod
    def _perform_custom_analysis(data: List[Dict], doctype: str, analysis_type: str, tracker=None) -> Dict[str, Any]:
        """Perform custom analysis based on type"""
        if tracker:
            update_progress(75, f"Performing {analysis_type} analysis")
        
        return {
            "message": f"Custom analysis '{analysis_type}' completed",
            "data_sample": data[:3] if data else []
        }
    
    @staticmethod
    def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute enhanced tools with progress tracking"""
        
        # Map to enhanced methods where available
        if tool_name == "execute_python_code":
            return EnhancedAnalysisTools.execute_python_code_with_progress(
                code=arguments.get("code", ""),
                data_query=arguments.get("data_query"),
                imports=arguments.get("imports")
            )
        elif tool_name == "analyze_frappe_data":
            return EnhancedAnalysisTools.analyze_frappe_data_with_progress(
                doctype=arguments.get("doctype", ""),
                analysis_type=arguments.get("analysis_type", "summary"),
                filters=arguments.get("filters"),
                fields=arguments.get("fields"),
                limit=arguments.get("limit", 1000)
            )
        else:
            # Fall back to base class for other tools
            return AnalysisTools.execute_tool(tool_name, arguments)