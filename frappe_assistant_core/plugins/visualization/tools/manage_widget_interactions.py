"""
Manage Widget Interactions Tool - Configure widget behaviors

Manages interactive behaviors between dashboard widgets
including linking, filtering, and data synchronization.
"""

import frappe
from frappe import _
from typing import Dict, Any
from frappe_assistant_core.core.base_tool import BaseTool


class ManageWidgetInteractions(BaseTool):
    """
    Tool for managing widget interaction behaviors.
    
    Provides capabilities for:
    - Widget linking and communication
    - Filter propagation setup
    - Event-driven interactions
    - Behavior customization
    """
    
    def __init__(self):
        super().__init__()
        self.name = "link_dashboard_widgets"
        self.description = self._get_description()
        self.requires_permission = None  # Permission checked dynamically
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "dashboard_name": {
                    "type": "string",
                    "description": "Dashboard containing widgets to configure"
                },
                "interaction_type": {
                    "type": "string",
                    "enum": [
                        "filter_propagation", "selection_linking", "drill_down_navigation",
                        "data_synchronization", "event_broadcasting", "custom_interaction"
                    ],
                    "description": "Type of interaction to configure"
                },
                "source_widget": {
                    "type": "string",
                    "description": "Widget that triggers the interaction"
                },
                "target_widgets": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Widgets that respond to the interaction"
                },
                "interaction_rules": {
                    "type": "object",
                    "properties": {
                        "trigger_events": {"type": "array"},
                        "filter_mapping": {"type": "object"},
                        "data_transformation": {"type": "object"},
                        "conditional_logic": {"type": "object"}
                    },
                    "description": "Rules governing the interaction behavior"
                },
                "advanced_settings": {
                    "type": "object",
                    "properties": {
                        "debounce_delay": {"type": "integer"},
                        "cascade_behavior": {"type": "string"},
                        "error_handling": {"type": "string"},
                        "performance_optimization": {"type": "boolean"}
                    },
                    "description": "Advanced interaction configuration"
                }
            },
            "required": ["dashboard_name", "interaction_type", "source_widget"]
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Configure sophisticated interactions between dashboard widgets for seamless user experience.

🔗 **INTERACTION TYPES:**
• Filter Propagation - One widget filters others automatically
• Selection Linking - Coordinate selections across widgets
• Drill-Down Navigation - Navigate between detail levels
• Data Synchronization - Keep related widgets in sync
• Event Broadcasting - Custom inter-widget communication

⚙️ **CONFIGURATION OPTIONS:**
• Trigger Events - Click, hover, selection, data change
• Filter Mapping - How filters translate between widgets
• Data Transformation - Modify data before passing
• Conditional Logic - Rules for when interactions occur

🔄 **BEHAVIOR PATTERNS:**
• Master-Detail - One widget controls detail view
• Coordinated Filtering - Multiple widgets filter together
• Hierarchical Navigation - Drill up/down through levels
• Cross-Reference - Jump between related data views

🚀 **PERFORMANCE FEATURES:**
• Debounce Controls - Prevent excessive updates
• Cascade Management - Control interaction chains
• Error Handling - Graceful failure recovery
• Optimization - Efficient data transfer and updates

💡 **SMART DEFAULTS:**
• Auto-Detection - Suggest logical interactions
• Best Practices - Pre-configured interaction patterns
• Validation - Ensure interactions make sense
• Testing Mode - Preview interactions before applying"""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Manage widget interactions"""
        try:
            # Import the actual widget interaction manager
            from ..tools.interactive_widgets import ManageWidgetInteractions as ManageInteractionsImpl
            
            # Map parameters to match expected structure
            interaction_args = {
                "dashboard_name": arguments.get("dashboard_name"),
                "interaction_config": {
                    "source_widget": arguments.get("source_widget"),
                    "target_widgets": arguments.get("target_widgets", []),
                    "interaction_type": arguments.get("interaction_type"),
                    "trigger_event": arguments.get("interaction_rules", {}).get("trigger_events", ["click"])[0] if arguments.get("interaction_rules", {}).get("trigger_events") else "click",
                    "data_mapping": arguments.get("interaction_rules", {}).get("filter_mapping", {})
                }
            }
            
            # Create interaction manager and execute
            interaction_manager = ManageInteractionsImpl()
            return interaction_manager.execute(interaction_args)
            
        except Exception as e:
            frappe.log_error(
                title=_("Widget Interaction Management Error"),
                message=f"Error managing widget interactions: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }


# Make sure class name matches file name for discovery
manage_widget_interactions = ManageWidgetInteractions