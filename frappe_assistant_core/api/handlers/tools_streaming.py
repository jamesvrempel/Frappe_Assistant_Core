"""
Artifact streaming helper functions for tools.
Updated to use settings-driven configuration instead of hardcoded values.
"""

import frappe
from typing import Dict, Any


def should_stream_to_artifact(result: str, tool_name: str, line_threshold: int = None, char_threshold: int = None) -> bool:
    """
    Determine if result should be streamed to artifact using settings.
    
    Args:
        result: Tool execution result
        tool_name: Name of the tool
        line_threshold: Legacy parameter (ignored, uses settings)
        char_threshold: Legacy parameter (ignored, uses settings)
        
    Returns:
        bool: True if result should be streamed
    """
    try:
        from frappe_assistant_core.utils.streaming_manager import get_streaming_manager
        
        streaming_manager = get_streaming_manager()
        return streaming_manager.should_stream_tool_result(result, tool_name)
        
    except Exception as e:
        frappe.logger("tools_streaming").error(f"Error determining streaming requirement: {str(e)}")
        # Fallback to basic logic for safety
        return _fallback_streaming_logic(result, tool_name)


def _fallback_streaming_logic(result: str, tool_name: str) -> bool:
    """Fallback streaming logic if settings cannot be loaded"""
    # Basic fallback using hardcoded values
    analysis_tools = ["analyze_frappe_data", "execute_python_code", "query_and_analyze", "create_visualization"]
    if tool_name in analysis_tools:
        return True
    
    line_count = len(result.split('\n'))
    if line_count > 5 or len(result) > 1000:
        return True
    
    return False


def format_for_artifact_streaming(result: str, tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    Format result for artifact streaming using settings-driven configuration.
    
    Args:
        result: Tool execution result
        tool_name: Name of the tool
        arguments: Tool arguments
        
    Returns:
        str: Formatted streaming instructions
    """
    try:
        from frappe_assistant_core.utils.streaming_manager import get_streaming_manager
        
        streaming_manager = get_streaming_manager()
        return streaming_manager.get_streaming_instructions(tool_name, result, arguments)
        
    except Exception as e:
        frappe.logger("tools_streaming").error(f"Error formatting streaming instructions: {str(e)}")
        # Fallback to basic formatting
        return _fallback_streaming_format(result, tool_name, arguments)


def _fallback_streaming_format(result: str, tool_name: str, arguments: Dict[str, Any]) -> str:
    """Fallback streaming format if settings cannot be loaded"""
    lines = len(result.split('\n'))
    chars = len(result)
    
    return f"""
⚠️ STREAMING CONFIGURATION ERROR

📊 **Result Statistics:**
• Lines: {lines}
• Characters: {chars:,}
• Tool: {tool_name}

⚠️ **FALLBACK MODE**: Streaming configuration could not be loaded.
Please check Assistant Core Settings for streaming configuration.

🔧 **Tool Details:**
• Tool: {tool_name}
• Arguments: {arguments}
• Timestamp: {frappe.utils.now()}

**RESULT:**
{result}

**Note:** This is a fallback display. Configure streaming settings in Assistant Core Settings.
"""