"""
Data Science Plugin for Frappe Assistant Core.
Provides Python code execution, data analysis, and visualization tools.
"""

import frappe
from frappe import _
from frappe_assistant_core.plugins.base_plugin import BasePlugin
from typing import Dict, Any, List, Tuple, Optional


class DataSciencePlugin(BasePlugin):
    """
    Plugin for data science and analysis capabilities.
    
    Provides tools for:
    - Python code execution
    - Data analysis with pandas
    - Visualization with matplotlib/seaborn/plotly
    - Statistical analysis
    """
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            'name': 'data_science',
            'display_name': 'Data Science & Analytics',
            'description': 'Python code execution, data analysis, and visualization tools',
            'version': '1.0.0',
            'author': 'Frappe Assistant Core Team',
            'dependencies': [
                'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly', 'scipy'
            ],
            'requires_restart': False
        }
    
    def get_tools(self) -> List[str]:
        """Get list of tools provided by this plugin"""
        return [
            'execute_python_code',
            'analyze_frappe_data',
            'query_and_analyze',
            'create_visualization'
        ]
    
    def validate_environment(self) -> Tuple[bool, Optional[str]]:
        """Validate that required dependencies are available"""
        info = self.get_info()
        dependencies = info['dependencies']
        
        # Check Python dependencies
        can_enable, error = self._check_dependencies(dependencies)
        if not can_enable:
            return can_enable, error
        
        # Check if Python code execution is allowed
        try:
            # Test basic imports
            import pandas as pd
            import numpy as np
            import matplotlib.pyplot as plt
            
            # Basic functionality test
            df = pd.DataFrame({'test': [1, 2, 3]})
            result = df.sum()
            
            self.logger.info("Data science plugin validation passed")
            return True, None
            
        except Exception as e:
            return False, _("Environment validation failed: {0}").format(str(e))
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get plugin capabilities"""
        return {
            "experimental": {
                "data_analysis": True,
                "python_execution": True,
                "visualization": True,
                "statistical_analysis": True
            },
            "data_formats": {
                "pandas": True,
                "numpy": True,
                "json": True,
                "csv": True
            },
            "visualization_types": {
                "matplotlib": True,
                "seaborn": True,
                "plotly": True
            }
        }
    
    def on_enable(self) -> None:
        """Called when plugin is enabled"""
        super().on_enable()
        
        # Initialize any required settings
        self._setup_matplotlib_backend()
        
        # Log successful enable
        self.logger.info("Data science plugin enabled with visualization support")
    
    def on_disable(self) -> None:
        """Called when plugin is disabled"""
        super().on_disable()
        
        # Cleanup any resources
        self._cleanup_matplotlib()
    
    def _setup_matplotlib_backend(self):
        """Setup matplotlib backend for server environment"""
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
            plt.ioff()  # Turn off interactive mode
            
            self.logger.debug("Matplotlib backend configured for server environment")
        except Exception as e:
            self.logger.warning(f"Failed to configure matplotlib: {str(e)}")
    
    def _cleanup_matplotlib(self):
        """Cleanup matplotlib resources"""
        try:
            import matplotlib.pyplot as plt
            plt.close('all')  # Close all figures
            self.logger.debug("Matplotlib cleanup completed")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup matplotlib: {str(e)}")