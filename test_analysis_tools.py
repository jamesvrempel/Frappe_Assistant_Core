#!/usr/bin/env python3

# Test script to directly check AnalysisTools loading
import sys
import os

# Add the frappe_assistant_core path
sys.path.insert(0, '/Users/clinton/frappe/bench/frappe-bench/apps/frappe_assistant_core')

try:
    print("Testing AnalysisTools import...")
    from frappe_assistant_core.tools.analysis_tools import AnalysisTools
    print("✅ AnalysisTools imported successfully")
    
    print("Testing get_tools() method...")
    tools = AnalysisTools.get_tools()
    print(f"✅ Found {len(tools)} analysis tools:")
    
    for tool in tools:
        print(f"  - {tool.get('name', 'unnamed')}: {tool.get('description', 'no description')[:50]}...")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()