"""
Migrate Visualization Tool - Legacy system migration

Migrates from old create_visualization tool to new
comprehensive dashboard system with backward compatibility.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class MigrateVisualization(BaseTool):
    """
    Tool for migrating from legacy visualization system.
    
    Provides capabilities for:
    - Legacy tool analysis and migration
    - Backward compatibility maintenance
    - Feature upgrade recommendations
    - Smooth transition planning
    """
    
    def __init__(self):
        super().__init__()
        self.name = "migrate_old_charts"
        self.description = self._get_description()
        self.requires_permission = None  # Permission checked dynamically
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "migration_type": {
                    "type": "string",
                    "enum": ["analyze", "preview", "execute", "rollback"],
                    "default": "analyze",
                    "description": "Type of migration operation"
                },
                "source_charts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific charts to migrate (optional)"
                },
                "target_dashboard_name": {
                    "type": "string",
                    "description": "Name for migrated dashboard"
                },
                "preserve_legacy": {
                    "type": "boolean",
                    "default": True,
                    "description": "Keep old visualization tool available"
                },
                "upgrade_features": {
                    "type": "boolean",
                    "default": True,
                    "description": "Apply new features during migration"
                },
                "migration_options": {
                    "type": "object",
                    "properties": {
                        "batch_size": {"type": "integer"},
                        "test_mode": {"type": "boolean"},
                        "backup_data": {"type": "boolean"},
                        "notification_list": {"type": "array"}
                    },
                    "description": "Migration execution options"
                }
            }
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Seamlessly migrate from legacy visualization tools to modern dashboard system with feature upgrades.

🔄 **MIGRATION OPERATIONS:**
• Analysis Mode - Assess current visualization usage
• Preview Mode - Show what migration would create
• Execute Mode - Perform actual migration
• Rollback Mode - Revert migration if needed

📊 **LEGACY COMPATIBILITY:**
• Chart Mapping - Convert old charts to new format
• Data Preservation - Maintain all existing data
• Permission Migration - Transfer access controls
• URL Redirection - Preserve existing links

⬆️ **FEATURE UPGRADES:**
• Enhanced Styling - Modern chart appearances
• Interactive Features - Add drill-down and filtering
• Dashboard Layouts - Professional arrangements
• Sharing Capabilities - Team collaboration features
• Mobile Optimization - Responsive design upgrades

🔒 **SAFE MIGRATION:**
• Backup Creation - Full system backup before migration
• Test Mode - Preview changes without applying
• Rollback Support - Undo migration if issues arise
• Validation Checks - Ensure data integrity

📅 **MIGRATION PLANNING:**
• Usage Analysis - Understand current chart usage
• Impact Assessment - Identify affected users
• Timeline Planning - Schedule migration phases
• Training Requirements - User education needs"""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute migration operation"""
        try:
            # Check if user has admin privileges for migration operations
            if not frappe.has_permission("System Settings", "write"):
                return {
                    "success": False,
                    "error": "Migration operations require administrator privileges"
                }
            
            # Import the actual migration tool
            from ..tools.migration_tool import MigrationTool
            
            # Create migration tool and execute
            migration_tool = MigrationTool()
            return migration_tool.execute(arguments)
            
        except Exception as e:
            frappe.log_error(
                title=_("Visualization Migration Error"),
                message=f"Error during migration: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
migrate_visualization = MigrateVisualization