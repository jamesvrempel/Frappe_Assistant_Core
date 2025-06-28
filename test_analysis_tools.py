#!/usr/bin/env python3
"""
Test script to check AnalysisTools loading
"""

def test_analysis_tools():
    """Test if AnalysisTools can be imported and get_tools() works"""
    
    print("Testing AnalysisTools loading...")
    
    try:
        # Test 1: Direct import
        print("1. Testing direct import...")
        from frappe_assistant_core.tools.analysis_tools import AnalysisTools
        print("   ✅ Direct import successful")
        
        # Test 2: Call get_tools()
        print("2. Testing get_tools() method...")
        tools = AnalysisTools.get_tools()
        print(f"   ✅ get_tools() returned {len(tools)} tools")
        
        # Test 3: List tool names
        print("3. Tool names:")
        for tool in tools:
            print(f"   - {tool.get('name', 'unnamed')}")
        
        # Test 4: Check for specific expected tools
        expected_tools = [
            'execute_python_code',
            'analyze_frappe_data', 
            'query_and_analyze',
            'create_visualization'
        ]
        
        found_tools = [tool.get('name') for tool in tools]
        
        print("4. Checking expected tools:")
        for expected in expected_tools:
            if expected in found_tools:
                print(f"   ✅ {expected}")
            else:
                print(f"   ❌ {expected} - MISSING")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        print("   Traceback:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = test_analysis_tools()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")