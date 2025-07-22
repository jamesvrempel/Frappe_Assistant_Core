# -*- coding: utf-8 -*-
# Frappe Assistant Core - AI Assistant integration for Frappe Framework
# Copyright (C) 2025 Paul Clinton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Batch Processing Plugin for Frappe Assistant Core.
Provides efficient bulk operations and data processing.
"""

import frappe
from frappe import _
from frappe_assistant_core.plugins.base_plugin import BasePlugin
from typing import Dict, Any, List, Tuple, Optional


class BatchProcessingPlugin(BasePlugin):
    """
    Plugin for batch processing and bulk operations.
    
    Provides capabilities for:
    - Bulk document operations
    - Data import/export
    - Background processing
    - Progress tracking
    """
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            'name': 'batch_processing',
            'display_name': 'Batch Processing',
            'description': 'Efficient bulk operations and data processing',
            'version': '1.0.0',
            'author': 'Frappe Assistant Core Team',
            'dependencies': [],  # No additional dependencies
            'requires_restart': False
        }
    
    def get_tools(self) -> List[str]:
        """Get list of tools provided by this plugin"""
        return []  # Tools would be implemented later
    
    def validate_environment(self) -> Tuple[bool, Optional[str]]:
        """Validate environment - always valid since no dependencies"""
        return True, None
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get plugin capabilities"""
        return {
            "experimental": {
                "batch_processing": True,
                "bulk_operations": True
            }
        }
    
    def on_enable(self) -> None:
        """Called when plugin is enabled"""
        super().on_enable()
        self.logger.info("Batch processing plugin enabled")
    
    def on_disable(self) -> None:
        """Called when plugin is disabled"""
        super().on_disable()
        self.logger.info("Batch processing plugin disabled")