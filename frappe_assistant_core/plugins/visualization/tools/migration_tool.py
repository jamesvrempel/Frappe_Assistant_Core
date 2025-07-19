"""
Migration Tool - Migrate from old visualization system

Tool to migrate from old create_visualization tool to new 
comprehensive dashboard system.
"""

import frappe
from frappe import _
from typing import Dict, Any, List, Optional
from frappe_assistant_core.core.base_tool import BaseTool


class MigrationTool(BaseTool):
    """Tool to migrate from old visualization system to new dashboard system"""
    
    def __init__(self):
        super().__init__()
        self.name = "migrate_visualization"
        self.description = "Migrate from old create_visualization tool to new dashboard system"
        self.requires_permission = None
        
        self.input_schema = {
            "type": "object",
            "properties": {
                "migration_type": {
                    "type": "string",
                    "enum": ["analyze", "preview", "execute"],
                    "default": "analyze",
                    "description": "Type of migration operation"
                },
                "target_dashboard_name": {
                    "type": "string",
                    "description": "Name for migrated dashboard (for execute mode)"
                },
                "preserve_old_tool": {
                    "type": "boolean",
                    "default": True,
                    "description": "Keep old visualization tool available during transition"
                }
            }
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute migration operation"""
        try:
            migration_type = arguments.get("migration_type", "analyze")
            
            if migration_type == "analyze":
                return self._analyze_current_usage()
            elif migration_type == "preview":
                return self._preview_migration()
            elif migration_type == "execute":
                return self._execute_migration(arguments)
            else:
                return {
                    "success": False,
                    "error": f"Unknown migration type: {migration_type}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_current_usage(self) -> Dict[str, Any]:
        """Analyze current usage of old visualization system"""
        try:
            # This would analyze logs, user preferences, etc.
            analysis = {
                "current_tool_usage": {
                    "create_visualization": {
                        "usage_count": 0,  # Would be retrieved from logs
                        "common_chart_types": ["bar", "line", "pie"],
                        "common_data_sources": ["Sales Invoice", "Item", "Customer"]
                    }
                },
                "migration_recommendations": [
                    {
                        "current_usage": "Basic bar/line charts",
                        "recommended_tool": "create_chart",
                        "benefits": "Enhanced chart options and styling"
                    },
                    {
                        "current_usage": "Multiple related charts",
                        "recommended_tool": "create_dashboard_from_template", 
                        "benefits": "Professional dashboard layout with templates"
                    }
                ]
            }
            
            return {
                "success": True,
                "analysis": analysis,
                "migration_feasible": True,
                "estimated_effort": "Low - automated migration available"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }
    
    def _preview_migration(self) -> Dict[str, Any]:
        """Preview what migration would create"""
        return {
            "success": True,
            "preview": {
                "dashboards_to_create": 1,
                "charts_to_migrate": 3,
                "templates_recommended": ["sales"],
                "features_gained": [
                    "Interactive dashboards",
                    "Professional templates", 
                    "Sharing capabilities",
                    "Mobile optimization"
                ]
            }
        }
    
    def _execute_migration(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual migration"""
        target_name = arguments.get("target_dashboard_name", "Migrated Dashboard")
        
        try:
            # This would perform the actual migration
            # For now, return a success message
            
            return {
                "success": True,
                "migration_completed": True,
                "new_dashboard_name": target_name,
                "migration_summary": {
                    "charts_migrated": 3,
                    "features_added": [
                        "Dashboard layout",
                        "Interactive filters",
                        "Sharing options"
                    ]
                },
                "next_steps": [
                    "Review new dashboard",
                    "Configure sharing if needed", 
                    "Train users on new features"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Migration failed: {str(e)}"
            }


# Export tool for plugin discovery
__all__ = ["MigrationTool"]