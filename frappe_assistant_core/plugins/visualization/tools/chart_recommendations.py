"""
Suggest Visualizations Tool - AI-powered chart recommendations

Analyzes data patterns and suggests optimal visualization approaches
with intelligent reasoning and statistical analysis.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class SuggestVisualizations(BaseTool):
    """
    AI-powered visualization suggestion tool.
    
    Provides capabilities for:
    - Data pattern analysis
    - Chart type recommendations
    - Statistical insights
    - User intent interpretation
    """
    
    def __init__(self):
        super().__init__()
        self.name = "recommend_charts"
        self.description = self._get_description()
        self.requires_permission = None  # Permission checked dynamically
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "doctype": {
                    "type": "string",
                    "description": "DocType to analyze for suggestions"
                },
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific fields to analyze (optional)"
                },
                "user_intent": {
                    "type": "string",
                    "description": "User's goal or intent (e.g., 'show trends', 'compare categories')"
                },
                "analysis_depth": {
                    "type": "string",
                    "enum": ["quick", "standard", "comprehensive"],
                    "default": "standard",
                    "description": "Depth of data analysis"
                },
                "max_suggestions": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum number of suggestions to return"
                },
                "include_reasoning": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include explanation for each suggestion"
                },
                "data_sample_size": {
                    "type": "integer",
                    "default": 100,
                    "description": "Sample size for data analysis"
                }
            },
            "required": ["doctype"]
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Generate AI-powered visualization recommendations by analyzing data patterns and user intent. Suggests optimal chart types with reasoning based on field types, data characteristics, and visualization best practices."""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generate visualization suggestions"""
        try:
            # Import the actual data explorer
            from ..tools.data_explorer import DataExplorer
            
            # Create data explorer and execute
            data_explorer = DataExplorer()
            return data_explorer.execute(arguments)
            
        except Exception as e:
            frappe.log_error(
                title=_("Visualization Suggestion Error"),
                message=f"Error generating suggestions: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
suggest_visualizations = SuggestVisualizations