"""
WebSocket Plugin for Frappe Assistant Core.
Provides real-time bidirectional communication capabilities.
"""

import frappe
from frappe import _
from frappe_assistant_core.plugins.base_plugin import BasePlugin
from typing import Dict, Any, List, Tuple, Optional


class WebSocketPlugin(BasePlugin):
    """
    Plugin for WebSocket-based real-time communication.
    
    Provides capabilities for:
    - Real-time notifications
    - Bidirectional communication
    - Live updates
    - Streaming responses
    """
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            'name': 'websocket',
            'display_name': 'WebSocket Communication',
            'description': 'Real-time bidirectional communication via WebSocket',
            'version': '1.0.0',
            'author': 'Frappe Assistant Core Team',
            'dependencies': ['websockets'],
            'requires_restart': True  # WebSocket server needs restart
        }
    
    def get_tools(self) -> List[str]:
        """Get list of tools provided by this plugin"""
        return []  # No direct tools, provides infrastructure
    
    def validate_environment(self) -> Tuple[bool, Optional[str]]:
        """Validate that WebSocket dependencies are available"""
        info = self.get_info()
        dependencies = info['dependencies']
        
        # Check WebSocket dependencies
        can_enable, error = self._check_dependencies(dependencies)
        if not can_enable:
            return can_enable, error
        
        # Test WebSocket functionality
        try:
            import websockets
            self.logger.info("WebSocket plugin validation passed")
            return True, None
            
        except Exception as e:
            return False, _("WebSocket validation failed: {0}").format(str(e))
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get plugin capabilities"""
        return {
            "experimental": {
                "websocket": True,
                "real_time": True,
                "streaming": True
            },
            "transports": {
                "websocket": True
            }
        }
    
    def on_enable(self) -> None:
        """Called when plugin is enabled"""
        super().on_enable()
        self.logger.info("WebSocket plugin enabled - server restart may be required")
    
    def on_disable(self) -> None:
        """Called when plugin is disabled"""
        super().on_disable()
        self.logger.info("WebSocket plugin disabled")