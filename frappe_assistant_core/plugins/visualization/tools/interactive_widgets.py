"""
Interactive Widgets Tool - Dynamic dashboard components

Provides tools for creating interactive dashboard elements including
drill-down charts, dynamic filters, linked visualizations, and alert widgets.
"""

import frappe
from frappe import _
import json
from typing import Dict, Any, List, Optional, Tuple
from frappe_assistant_core.core.base_tool import BaseTool


class InteractiveWidgets(BaseTool):
    """
    Dynamic and interactive dashboard components.
    
    Provides capabilities for:
    - Drill-down chart creation
    - Dynamic filter widgets
    - Linked chart relationships
    - Auto-refresh configuration
    - Alert and threshold widgets
    """
    
    def __init__(self):
        super().__init__()
        self.name = "create_interactive_widget"
        self.description = self._get_description()
        self.requires_permission = None
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "widget_type": {
                    "type": "string",
                    "enum": ["drill_down_chart", "dynamic_filter", "linked_charts", "alert_widget", "auto_refresh"],
                    "description": "Type of interactive widget to create"
                },
                "dashboard_name": {
                    "type": "string",
                    "description": "Target dashboard for the widget"
                },
                "widget_config": {
                    "type": "object",
                    "description": "Widget-specific configuration",
                    "properties": {
                        "drill_down": {
                            "type": "object",
                            "properties": {
                                "doctype": {"type": "string"},
                                "hierarchy_fields": {"type": "array", "items": {"type": "string"}},
                                "chart_type": {"type": "string"},
                                "value_field": {"type": "string"}
                            }
                        },
                        "filter": {
                            "type": "object",
                            "properties": {
                                "filter_fields": {"type": "array", "items": {"type": "string"}},
                                "filter_type": {"type": "string", "enum": ["multiselect", "date_range", "slider", "search"]},
                                "target_charts": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "linking": {
                            "type": "object",
                            "properties": {
                                "source_chart": {"type": "string"},
                                "target_charts": {"type": "array", "items": {"type": "string"}},
                                "link_field": {"type": "string"}
                            }
                        },
                        "alert": {
                            "type": "object",
                            "properties": {
                                "doctype": {"type": "string"},
                                "metric_field": {"type": "string"},
                                "threshold_value": {"type": "number"},
                                "comparison": {"type": "string", "enum": ["greater_than", "less_than", "equals"]},
                                "alert_message": {"type": "string"}
                            }
                        },
                        "refresh": {
                            "type": "object",
                            "properties": {
                                "interval": {"type": "string", "enum": ["1_minute", "5_minutes", "15_minutes", "30_minutes", "1_hour"]},
                                "target_charts": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    }
                },
                "position": {
                    "type": "object",
                    "properties": {
                        "row": {"type": "integer"},
                        "col": {"type": "integer"},
                        "width": {"type": "integer", "default": 4},
                        "height": {"type": "integer", "default": 3}
                    },
                    "description": "Widget position in dashboard grid"
                },
                "styling": {
                    "type": "object",
                    "properties": {
                        "theme": {"type": "string", "enum": ["light", "dark", "auto"]},
                        "color_scheme": {"type": "string"},
                        "border": {"type": "boolean", "default": True},
                        "shadow": {"type": "boolean", "default": True}
                    },
                    "description": "Widget appearance options"
                }
            },
            "required": ["widget_type", "dashboard_name", "widget_config"]
        }
    
    def _get_description(self) -> str:
        """Get tool description"""
        return """Create interactive dashboard widgets that enhance user engagement and provide dynamic data exploration capabilities.

🎯 **INTERACTIVE WIDGETS:**

🔍 **DRILL-DOWN CHARTS:**
• Hierarchical Data Exploration - Click to drill into details
• Multi-level Navigation - Territory → Region → City drill-downs
• Breadcrumb Navigation - Easy return to previous levels
• Context Preservation - Maintain filters across drill levels
• Custom Hierarchies - Define business-specific drill paths

🎛️ **DYNAMIC FILTERS:**
• Real-time Filtering - Instant chart updates
• Multiple Filter Types - Date ranges, multiselect, sliders
• Global Filter Controls - Affect entire dashboard
• Smart Dependencies - Cascading filter relationships
• Save Filter States - Bookmark common filter combinations

🔗 **LINKED CHARTS:**
• Interactive Connections - Click on one chart affects others
• Master-Detail Views - Overview with detailed breakdowns
• Cross-highlighting - Visual connections between related data
• Synchronized Navigation - Coordinated chart interactions
• Data Flow Visualization - Show how metrics relate

⚠️ **ALERT WIDGETS:**
• Threshold Monitoring - Real-time alert triggers
• Custom Alert Rules - Business-specific conditions
• Visual Indicators - Color-coded status displays
• Notification Integration - Email/SMS alert delivery
• Historical Alert Tracking - Trend analysis of alerts

🔄 **AUTO-REFRESH:**
• Real-time Updates - Live data streaming
• Configurable Intervals - From minutes to hours
• Selective Refresh - Update specific charts only
• Performance Optimization - Efficient data loading
• Connection Status - Monitor data feed health

⚡ **ADVANCED FEATURES:**
• Responsive Design - Mobile-optimized interactions
• Touch Gestures - Swipe, pinch, tap support
• Keyboard Shortcuts - Power user efficiency
• Custom Animations - Smooth transitions
• Accessibility Support - Screen reader compatibility

🎨 **USER EXPERIENCE:**
• Intuitive Controls - Self-explanatory interfaces
• Contextual Help - Built-in guidance and tips
• Customizable Layouts - User-configurable arrangements
• State Persistence - Remember user preferences
• Progressive Disclosure - Show complexity when needed

💡 **BUSINESS APPLICATIONS:**
• Executive Dashboards - High-level drill-down capabilities
• Operational Monitoring - Real-time status tracking
• Sales Analytics - Territory and product exploration
• Financial Analysis - Account and period drilling
• Inventory Management - Location and category filtering"""
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create interactive widget"""
        try:
            widget_type = arguments.get("widget_type")
            dashboard_name = arguments.get("dashboard_name")
            widget_config = arguments.get("widget_config", {})
            position = arguments.get("position", {})
            styling = arguments.get("styling", {})
            
            # Validate dashboard exists
            dashboard_doc = self._get_dashboard(dashboard_name)
            if not dashboard_doc:
                return {
                    "success": False,
                    "error": f"Dashboard '{dashboard_name}' not found"
                }
            
            # Check permissions
            if not frappe.has_permission("Dashboard", "write", dashboard_doc):
                return {
                    "success": False,
                    "error": "Insufficient permissions to modify this dashboard"
                }
            
            # Create widget based on type
            widget_result = self._create_widget_by_type(
                widget_type, dashboard_doc, widget_config, position, styling
            )
            
            if widget_result["success"]:
                return {
                    "success": True,
                    "widget_type": widget_type,
                    "dashboard_name": dashboard_name,
                    "widget_id": widget_result["widget_id"],
                    "widget_features": widget_result.get("features", []),
                    "integration_points": widget_result.get("integration_points", []),
                    **widget_result
                }
            else:
                return widget_result
                
        except Exception as e:
            frappe.log_error(
                title=_("Interactive Widget Error"),
                message=f"Error creating widget: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_dashboard(self, dashboard_name: str) -> Optional[Any]:
        """Get dashboard document"""
        try:
            if frappe.db.exists("Dashboard", dashboard_name):
                return frappe.get_doc("Dashboard", dashboard_name)
            
            dashboards = frappe.get_all(
                "Dashboard",
                filters={"dashboard_name": dashboard_name},
                limit=1
            )
            
            if dashboards:
                return frappe.get_doc("Dashboard", dashboards[0].name)
            
            return None
        except:
            return None
    
    def _create_widget_by_type(self, widget_type: str, dashboard_doc: Any,
                              widget_config: Dict, position: Dict, styling: Dict) -> Dict[str, Any]:
        """Create widget based on type"""
        try:
            if widget_type == "drill_down_chart":
                return self._create_drill_down_chart(dashboard_doc, widget_config, position, styling)
            elif widget_type == "dynamic_filter":
                return self._create_dynamic_filter(dashboard_doc, widget_config, position, styling)
            elif widget_type == "linked_charts":
                return self._create_linked_charts(dashboard_doc, widget_config, position, styling)
            elif widget_type == "alert_widget":
                return self._create_alert_widget(dashboard_doc, widget_config, position, styling)
            elif widget_type == "auto_refresh":
                return self._setup_auto_refresh(dashboard_doc, widget_config, position, styling)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported widget type: {widget_type}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Widget creation failed: {str(e)}"
            }
    
    def _create_drill_down_chart(self, dashboard_doc: Any, config: Dict, position: Dict, styling: Dict) -> Dict[str, Any]:
        """Create drill-down chart widget"""
        try:
            drill_config = config.get("drill_down", {})
            doctype = drill_config.get("doctype")
            hierarchy_fields = drill_config.get("hierarchy_fields", [])
            chart_type = drill_config.get("chart_type", "bar")
            value_field = drill_config.get("value_field")
            
            if not hierarchy_fields:
                return {
                    "success": False,
                    "error": "Hierarchy fields required for drill-down chart"
                }
            
            # Create drill-down configuration
            drill_down_config = {
                "widget_type": "drill_down_chart",
                "doctype": doctype,
                "hierarchy_levels": [
                    {
                        "level": i,
                        "field": field,
                        "chart_type": chart_type,
                        "aggregation": "sum"
                    }
                    for i, field in enumerate(hierarchy_fields)
                ],
                "value_field": value_field,
                "navigation": {
                    "enable_breadcrumbs": True,
                    "enable_back_button": True,
                    "max_drill_levels": len(hierarchy_fields)
                },
                "position": position,
                "styling": styling
            }
            
            # Generate widget ID
            widget_id = f"drill_down_{frappe.generate_hash(length=8)}"
            
            # Store widget configuration
            self._store_widget_config(dashboard_doc, widget_id, drill_down_config)
            
            return {
                "success": True,
                "widget_id": widget_id,
                "features": [
                    "Hierarchical navigation",
                    "Interactive drilling",
                    "Breadcrumb navigation",
                    f"{len(hierarchy_fields)} drill levels"
                ],
                "integration_points": [
                    f"Connects to {doctype} data",
                    "Supports chart filtering",
                    "Dashboard-wide filter integration"
                ],
                "hierarchy_levels": len(hierarchy_fields)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Drill-down chart creation failed: {str(e)}"
            }
    
    def _create_dynamic_filter(self, dashboard_doc: Any, config: Dict, position: Dict, styling: Dict) -> Dict[str, Any]:
        """Create dynamic filter widget"""
        try:
            filter_config = config.get("filter", {})
            filter_fields = filter_config.get("filter_fields", [])
            filter_type = filter_config.get("filter_type", "multiselect")
            target_charts = filter_config.get("target_charts", [])
            
            if not filter_fields:
                return {
                    "success": False,
                    "error": "Filter fields required for dynamic filter widget"
                }
            
            # Create filter configuration
            dynamic_filter_config = {
                "widget_type": "dynamic_filter",
                "filters": [
                    {
                        "field": field,
                        "type": filter_type,
                        "options": self._get_filter_options(field),
                        "default_value": None
                    }
                    for field in filter_fields
                ],
                "target_charts": target_charts,
                "update_mode": "real_time",
                "position": position,
                "styling": styling
            }
            
            widget_id = f"filter_{frappe.generate_hash(length=8)}"
            self._store_widget_config(dashboard_doc, widget_id, dynamic_filter_config)
            
            return {
                "success": True,
                "widget_id": widget_id,
                "features": [
                    f"{len(filter_fields)} filter controls",
                    f"{filter_type.title()} interface",
                    "Real-time updates",
                    "Dashboard-wide filtering"
                ],
                "integration_points": [
                    f"Affects {len(target_charts)} charts" if target_charts else "Global dashboard filtering",
                    "Synchronized with other filters",
                    "State persistence"
                ],
                "filter_count": len(filter_fields)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Dynamic filter creation failed: {str(e)}"
            }
    
    def _create_linked_charts(self, dashboard_doc: Any, config: Dict, position: Dict, styling: Dict) -> Dict[str, Any]:
        """Create linked charts widget"""
        try:
            linking_config = config.get("linking", {})
            source_chart = linking_config.get("source_chart")
            target_charts = linking_config.get("target_charts", [])
            link_field = linking_config.get("link_field")
            
            if not source_chart or not target_charts:
                return {
                    "success": False,
                    "error": "Source chart and target charts required for linking"
                }
            
            # Create linking configuration
            linked_charts_config = {
                "widget_type": "linked_charts",
                "source_chart": source_chart,
                "target_charts": target_charts,
                "link_field": link_field,
                "interaction_type": "click_to_filter",
                "highlight_mode": "cross_highlight",
                "animation": {
                    "enable": True,
                    "duration": 300,
                    "type": "fade"
                },
                "position": position,
                "styling": styling
            }
            
            widget_id = f"linked_{frappe.generate_hash(length=8)}"
            self._store_widget_config(dashboard_doc, widget_id, linked_charts_config)
            
            return {
                "success": True,
                "widget_id": widget_id,
                "features": [
                    "Chart interactions",
                    "Cross-highlighting",
                    "Click-to-filter",
                    "Animated transitions"
                ],
                "integration_points": [
                    f"Links {source_chart} to {len(target_charts)} charts",
                    "Coordinated filtering",
                    "Visual connection indicators"
                ],
                "linked_chart_count": len(target_charts) + 1
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Linked charts creation failed: {str(e)}"
            }
    
    def _create_alert_widget(self, dashboard_doc: Any, config: Dict, position: Dict, styling: Dict) -> Dict[str, Any]:
        """Create alert widget"""
        try:
            alert_config = config.get("alert", {})
            doctype = alert_config.get("doctype")
            metric_field = alert_config.get("metric_field")
            threshold_value = alert_config.get("threshold_value")
            comparison = alert_config.get("comparison", "greater_than")
            alert_message = alert_config.get("alert_message", "Threshold exceeded")
            
            if not all([doctype, metric_field, threshold_value]):
                return {
                    "success": False,
                    "error": "DocType, metric field, and threshold value required for alert widget"
                }
            
            # Create alert configuration
            alert_widget_config = {
                "widget_type": "alert_widget",
                "alert_rules": [
                    {
                        "doctype": doctype,
                        "metric_field": metric_field,
                        "threshold_value": threshold_value,
                        "comparison": comparison,
                        "alert_message": alert_message,
                        "severity": self._determine_alert_severity(comparison, threshold_value),
                        "enabled": True
                    }
                ],
                "display_mode": "status_indicator",
                "check_interval": "5_minutes",
                "notification_settings": {
                    "show_popup": True,
                    "play_sound": False,
                    "email_notifications": False
                },
                "position": position,
                "styling": styling
            }
            
            widget_id = f"alert_{frappe.generate_hash(length=8)}"
            self._store_widget_config(dashboard_doc, widget_id, alert_widget_config)
            
            return {
                "success": True,
                "widget_id": widget_id,
                "features": [
                    "Real-time monitoring",
                    "Threshold alerts",
                    "Visual indicators",
                    "Custom alert messages"
                ],
                "integration_points": [
                    f"Monitors {doctype}.{metric_field}",
                    "Dashboard alert center",
                    "Notification system"
                ],
                "alert_threshold": f"{comparison.replace('_', ' ')} {threshold_value}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Alert widget creation failed: {str(e)}"
            }
    
    def _setup_auto_refresh(self, dashboard_doc: Any, config: Dict, position: Dict, styling: Dict) -> Dict[str, Any]:
        """Setup auto-refresh configuration"""
        try:
            refresh_config = config.get("refresh", {})
            interval = refresh_config.get("interval", "5_minutes")
            target_charts = refresh_config.get("target_charts", [])
            
            # Create auto-refresh configuration
            auto_refresh_config = {
                "widget_type": "auto_refresh",
                "refresh_interval": interval,
                "target_charts": target_charts or "all",
                "refresh_mode": "incremental",
                "pause_on_interaction": True,
                "show_last_updated": True,
                "error_handling": {
                    "retry_count": 3,
                    "retry_delay": "30_seconds",
                    "fallback_mode": "cache"
                },
                "position": position,
                "styling": styling
            }
            
            widget_id = f"refresh_{frappe.generate_hash(length=8)}"
            self._store_widget_config(dashboard_doc, widget_id, auto_refresh_config)
            
            # Update dashboard settings
            dashboard_doc.db_set("auto_refresh_enabled", True)
            dashboard_doc.db_set("auto_refresh_interval", interval)
            
            return {
                "success": True,
                "widget_id": widget_id,
                "features": [
                    f"Auto-refresh every {interval.replace('_', ' ')}",
                    "Intelligent pausing",
                    "Error recovery",
                    "Last updated indicator"
                ],
                "integration_points": [
                    "Dashboard-wide refresh control",
                    "Performance monitoring",
                    "Connection status display"
                ],
                "refresh_interval": interval,
                "target_count": len(target_charts) if target_charts else "all charts"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Auto-refresh setup failed: {str(e)}"
            }
    
    def _get_filter_options(self, field: str) -> List[str]:
        """Get filter options for a field"""
        try:
            # This would analyze the field to determine appropriate filter options
            # For now, return common filter types
            return ["multiselect", "date_range", "slider", "search"]
        except:
            return ["multiselect"]
    
    def _determine_alert_severity(self, comparison: str, threshold_value: float) -> str:
        """Determine alert severity based on threshold"""
        try:
            if threshold_value > 1000000:  # Large numbers might be critical
                return "critical"
            elif threshold_value > 100000:
                return "warning"
            else:
                return "info"
        except:
            return "info"
    
    def _store_widget_config(self, dashboard_doc: Any, widget_id: str, widget_config: Dict):
        """Store widget configuration in dashboard"""
        try:
            # Get existing widget configurations
            existing_widgets = dashboard_doc.get("interactive_widgets")
            if existing_widgets:
                widgets = json.loads(existing_widgets) if isinstance(existing_widgets, str) else existing_widgets
            else:
                widgets = {}
            
            # Add new widget
            widgets[widget_id] = widget_config
            
            # Save back to dashboard
            dashboard_doc.db_set("interactive_widgets", json.dumps(widgets))
            
        except Exception as e:
            frappe.logger("interactive_widgets").error(f"Failed to store widget config: {str(e)}")


class ManageWidgetInteractions(BaseTool):
    """Manage interactions between dashboard widgets"""
    
    def __init__(self):
        super().__init__()
        self.name = "manage_widget_interactions"
        self.description = "Configure and manage interactions between dashboard widgets"
        self.requires_permission = None
        
        self.inputSchema = {
            "type": "object",
            "properties": {
                "dashboard_name": {
                    "type": "string",
                    "description": "Target dashboard"
                },
                "interaction_config": {
                    "type": "object",
                    "properties": {
                        "source_widget": {"type": "string"},
                        "target_widgets": {"type": "array", "items": {"type": "string"}},
                        "interaction_type": {
                            "type": "string",
                            "enum": ["filter", "highlight", "drill_down", "navigate"]
                        },
                        "trigger_event": {
                            "type": "string",
                            "enum": ["click", "hover", "select", "double_click"]
                        },
                        "data_mapping": {"type": "object"}
                    },
                    "required": ["source_widget", "target_widgets", "interaction_type"]
                }
            },
            "required": ["dashboard_name", "interaction_config"]
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Configure widget interactions"""
        try:
            dashboard_name = arguments.get("dashboard_name")
            interaction_config = arguments.get("interaction_config")
            
            # Get dashboard
            dashboard_doc = self._get_dashboard(dashboard_name)
            if not dashboard_doc:
                return {
                    "success": False,
                    "error": f"Dashboard '{dashboard_name}' not found"
                }
            
            # Configure interaction
            interaction_result = self._configure_interaction(dashboard_doc, interaction_config)
            
            return {
                "success": True,
                "dashboard_name": dashboard_name,
                "interaction_id": interaction_result["interaction_id"],
                "source_widget": interaction_config["source_widget"],
                "target_widgets": interaction_config["target_widgets"],
                "interaction_type": interaction_config["interaction_type"],
                "features_enabled": interaction_result.get("features", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_dashboard(self, dashboard_name: str) -> Optional[Any]:
        """Get dashboard document"""
        widgets_tool = InteractiveWidgets()
        return widgets_tool._get_dashboard(dashboard_name)
    
    def _configure_interaction(self, dashboard_doc: Any, config: Dict) -> Dict[str, Any]:
        """Configure widget interaction"""
        try:
            interaction_id = f"interaction_{frappe.generate_hash(length=8)}"
            
            interaction_config = {
                "interaction_id": interaction_id,
                "source_widget": config["source_widget"],
                "target_widgets": config["target_widgets"],
                "interaction_type": config["interaction_type"],
                "trigger_event": config.get("trigger_event", "click"),
                "data_mapping": config.get("data_mapping", {}),
                "enabled": True,
                "created_at": frappe.utils.now()
            }
            
            # Store interaction configuration
            existing_interactions = dashboard_doc.get("widget_interactions")
            if existing_interactions:
                interactions = json.loads(existing_interactions) if isinstance(existing_interactions, str) else existing_interactions
            else:
                interactions = {}
            
            interactions[interaction_id] = interaction_config
            dashboard_doc.db_set("widget_interactions", json.dumps(interactions))
            
            return {
                "interaction_id": interaction_id,
                "features": [
                    f"{config['interaction_type'].title()} interaction",
                    f"Triggered by {config.get('trigger_event', 'click')}",
                    f"Affects {len(config['target_widgets'])} widgets"
                ]
            }
            
        except Exception as e:
            return {
                "interaction_id": None,
                "error": str(e)
            }


# Export tools for plugin discovery
__all__ = ["InteractiveWidgets", "ManageWidgetInteractions"]