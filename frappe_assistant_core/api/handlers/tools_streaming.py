"""
Artifact streaming helper functions for tools
"""

import frappe
from typing import Dict, Any


def should_stream_to_artifact(result: str, tool_name: str, line_threshold: int = 5, char_threshold: int = 1000) -> bool:
    """Determine if result should be streamed to artifact"""
    
    # Always stream for analysis tools (these generate complex data)
    analysis_tools = ["analyze_frappe_data", "execute_python_code", "query_and_analyze", "create_visualization"]
    if tool_name in analysis_tools:
        return True
    
    # Stream if result has more than threshold lines
    line_count = len(result.split('\n'))
    if line_count > line_threshold:
        return True
    
    # Stream if result is very long (> character threshold)
    if len(result) > char_threshold:
        return True
    
    # Stream if result contains JSON with many records (indicates large dataset)
    if result.strip().startswith('{') and '"data"' in result and result.count('"name"') > 3:
        return True
    
    # Stream if result contains extensive tabular data
    if result.count('|') > 20:  # Likely a large table
        return True
        
    # Stream if result has many list items
    if result.count('\n- ') > 10 or result.count('\n• ') > 10:
        return True
    
    return False


def format_for_artifact_streaming(result: str, tool_name: str, arguments: Dict[str, Any]) -> str:
    """Format result for artifact streaming with instructions"""
    
    # Extract key information for preview
    lines = result.split('\n')
    line_count = len(lines)
    char_count = len(result)
    
    # Create preview (first few lines)
    preview_lines = lines[:3] if len(lines) > 3 else lines
    preview = '\n'.join(preview_lines)
    if len(lines) > 3:
        preview += f"\n... ({line_count - 3} more lines)"
    
    # Determine tool category for artifact suggestions
    if tool_name in ["analyze_frappe_data", "execute_python_code", "query_and_analyze"]:
        artifact_type = "Data Analysis Report"
        sections = ["Executive Summary", "Key Findings", "Detailed Analysis", "Recommendations"]
    elif tool_name.startswith("report_"):
        artifact_type = "Business Report"
        sections = ["Report Summary", "Key Metrics", "Detailed Data", "Action Items"]
    elif tool_name.startswith("search_") or tool_name.startswith("metadata_"):
        artifact_type = "Technical Documentation"
        sections = ["Overview", "Search Results", "Technical Details", "Usage Notes"]
    else:
        artifact_type = "Comprehensive Results"
        sections = ["Summary", "Main Results", "Detailed Output", "Next Steps"]

    # For extremely large results (>10,000 chars), don't include full result to prevent overwhelming
    include_full_result = char_count <= 10000
    
    if include_full_result:
        streaming_instructions = f"""
🚨 ARTIFACT STREAMING REQUIRED - LARGE RESULT DETECTED

📊 **Result Statistics:**
• Lines: {line_count} (threshold: 5+)
• Characters: {char_count:,} (threshold: 1,000+)
• Tool: {tool_name}

📋 **REQUIRED WORKFLOW:**
1. **CREATE ARTIFACT** - Type: {artifact_type}
2. **ADD SECTIONS:** {', '.join(sections)}
3. **STREAM FULL RESULTS** to artifact sections
4. **KEEP RESPONSE MINIMAL** (only summary/confirmation)

⚠️ **CRITICAL:** The full result below MUST be moved to an artifact to prevent response limits and provide professional deliverables.

═══════════════════════════════════════════════════════════

📄 **PREVIEW:**
```
{preview}
```

🔧 **Tool Execution Details:**
• Tool: {tool_name}
• Arguments: {arguments}
• Timestamp: {frappe.utils.now()}

════════════════════════════════════════════════════════════════

🔄 **FULL RESULT FOR ARTIFACT STREAMING:**

{result}

════════════════════════════════════════════════════════════════

⚠️ **NEXT STEPS:**
1. Create workspace artifact with suggested sections above
2. Stream the complete result to appropriate artifact sections
3. Provide executive summary in your response
4. Build unlimited depth analysis via artifact streaming
"""
    else:
        # For extremely large results, provide instructions without full content
        streaming_instructions = f"""
🚨 ARTIFACT STREAMING REQUIRED - EXTREMELY LARGE RESULT

📊 **Result Statistics:**
• Lines: {line_count} (threshold: 5+)
• Characters: {char_count:,} (threshold: 1,000+)
• Tool: {tool_name}
• Status: Result too large for direct display ({char_count:,} characters)

📋 **MANDATORY WORKFLOW:**
1. **CREATE ARTIFACT** - Type: {artifact_type}
2. **ADD SECTIONS:** {', '.join(sections)}
3. **Re-execute tool and stream to artifact**
4. **Keep response minimal**

⚠️ **CRITICAL:** This result is too large to display directly. You MUST re-execute the tool and stream results to an artifact.

═══════════════════════════════════════════════════════════

📄 **PREVIEW (First 3 lines only):**
```
{preview}
```

🔧 **Tool Execution Details:**
• Tool: {tool_name}
• Arguments: {arguments}
• Timestamp: {frappe.utils.now()}

⚠️ **REQUIRED ACTION:**
1. Create workspace artifact with the suggested sections
2. Re-run this exact tool with same arguments
3. Stream all results directly to artifact sections
4. Provide only executive summary in response

**Result is {char_count:,} characters - too large for conversation display.**
"""

    return streaming_instructions