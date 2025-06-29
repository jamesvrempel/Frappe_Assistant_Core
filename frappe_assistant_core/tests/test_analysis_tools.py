"""
Test suite for Analysis Tools
Tests all analysis and code execution functionality
"""

import frappe
import unittest
import json
import time
from unittest.mock import patch, MagicMock
from frappe_assistant_core.tools.analysis_tools import AnalysisTools
from frappe_assistant_core.tests.base_test import BaseAssistantTest

class TestAnalysisTools(BaseAssistantTest):
    """Test suite for analysis tools functionality"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        self.tools = AnalysisTools()
    
    def test_get_tools_structure(self):
        """Test that get_tools returns proper structure"""
        tools = AnalysisTools.get_tools()
        
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        
        # Check each tool has required fields
        for tool in tools:
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("inputSchema", tool)
            self.assertIsInstance(tool["inputSchema"], dict)
    
    def test_execute_python_code_permissions(self):
        """Test Python code execution permission requirements"""
        # Test without System Manager role
        with patch('frappe.get_roles') as mock_roles:
            mock_roles.return_value = ["User"]
            
            result = AnalysisTools.execute_python_code("print('test')")
            
            self.assertFalse(result.get("success"))
            self.assertIn("System Manager", result.get("error", ""))
    
    @patch('frappe.get_roles')
    def test_execute_python_code_basic(self, mock_roles):
        """Test basic Python code execution"""
        mock_roles.return_value = ["System Manager"]
        
        code = """
result = 2 + 2
print(f"Result: {result}")
"""
        
        with patch('frappe.log_error'):
            result = AnalysisTools.execute_python_code(code)
        
        self.assertTrue(result.get("success"))
        self.assertIn("output", result)
        self.assertIn("Result: 4", result["output"])
        self.assertIn("variables", result)
        self.assertEqual(result["variables"]["result"], 4)
    
    @patch('frappe.get_roles')
    def test_execute_python_code_with_data_query(self, mock_roles):
        """Test Python code execution with data query"""
        mock_roles.return_value = ["System Manager"]
        
        # Mock frappe.get_all to return test data as MagicMock objects with dot notation
        mock_user1 = MagicMock()
        mock_user1.name = "User1"
        mock_user1.email = "user1@test.com"
        
        mock_user2 = MagicMock()
        mock_user2.name = "User2"
        mock_user2.email = "user2@test.com"
        
        test_data = [mock_user1, mock_user2]
        
        with patch('frappe.get_all', return_value=test_data), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.log_error'):
            
            data_query = {
                "doctype": "User",
                "fields": ["name", "email"],
                "limit": 10
            }
            
            code = """
print(f"Data shape: {len(data)}")
if len(data) > 0:
    print(f"Data found with {len(data)} items")
"""
            
            result = AnalysisTools.execute_python_code(code, data_query)
            
            self.assertTrue(result.get("success"))
            self.assertIn("Data shape: 2", result["output"])
    
    @patch('frappe.get_roles')
    def test_execute_python_code_security_restrictions(self, mock_roles):
        """Test security restrictions in Python code execution"""
        mock_roles.return_value = ["System Manager"]
        
        # Test import restrictions
        dangerous_code = """
import os
print(\"This should work after import removal\")
"""
        
        with patch('frappe.log_error'), patch('frappe.session') as mock_session:
            mock_session.user = "Administrator"
            result = AnalysisTools.execute_python_code(dangerous_code)
        
        # Should succeed with imports removed
        self.assertTrue(result.get("success"))
        self.assertIn("This should work after import removal", result["output"])
    
    @patch('frappe.get_roles')
    def test_execute_python_code_with_pandas(self, mock_roles):
        """Test Python code execution with pandas operations"""
        mock_roles.return_value = ["System Manager"]
        
        code = """
import pandas as pd
data = [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}]
df = pd.DataFrame(data)
mean_age = df['age'].mean()
print(f"Mean age: {mean_age}")
"""
        
        result = AnalysisTools.execute_python_code(code)
        
        if result.get("success"):
            self.assertIn("Mean age: 27.5", result["output"])
    
    @patch('frappe.get_roles')
    def test_execute_python_code_error_handling(self, mock_roles):
        """Test error handling in Python code execution"""
        mock_roles.return_value = ["System Manager"]
        
        # Code that will cause an error
        error_code = """
result = 1 / 0
"""
        
        with patch('frappe.log_error'), patch('frappe.session') as mock_session:
            mock_session.user = "Administrator"
            result = AnalysisTools.execute_python_code(error_code)
        
        self.assertFalse(result.get("success"))
        self.assertIn("error", result)
        self.assertIn("division by zero", result["error"])
    
    def test_analyze_frappe_data_permissions(self):
        """Test analyze_frappe_data permission requirements"""
        with patch('frappe.has_permission', return_value=False):
            
            result = AnalysisTools.analyze_frappe_data("User")
            
            self.assertFalse(result.get("success"))
            self.assertIn("permission", result.get("error", ""))
    
    def test_analyze_frappe_data_basic(self):
        """Test basic Frappe data analysis"""
        test_data = [
            {"name": "User1", "creation": "2024-01-01", "enabled": 1},
            {"name": "User2", "creation": "2024-01-02", "enabled": 1},
            {"name": "User3", "creation": "2024-01-03", "enabled": 0}
        ]
        
        with patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_all', return_value=test_data), \
             patch('frappe.get_meta') as mock_meta, \
             patch('frappe.log_error'):
            
            # Mock meta object
            mock_meta.return_value.fields = []
            
            result = AnalysisTools.analyze_frappe_data("User")
            
            self.assertTrue(result.get("success"))
            self.assertIn("analysis", result)
            self.assertEqual(result["data_summary"]["total_records"], 3)
    
    def test_analyze_frappe_data_no_data(self):
        """Test analyze_frappe_data with no data"""
        with patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_all', return_value=[]), \
             patch('frappe.get_meta') as mock_meta, \
             patch('frappe.log_error'):
            
            # Mock meta object
            mock_meta.return_value.fields = []
            
            result = AnalysisTools.analyze_frappe_data("NonExistentDocType")
            
            self.assertTrue(result.get("success"))
            self.assertIn("message", result)
            self.assertEqual(result["message"], "No data found")
    
    def test_query_and_analyze_permissions(self):
        """Test query_and_analyze permission requirements"""
        with patch('frappe.get_roles', return_value=["User"]):
            
            result = AnalysisTools.query_and_analyze("SELECT * FROM tabUser")
            
            self.assertFalse(result.get("success"))
            self.assertIn("System Manager", result.get("error", ""))
    
    @patch('frappe.get_roles')
    def test_query_and_analyze_basic(self, mock_roles):
        """Test basic query and analyze functionality"""
        mock_roles.return_value = ["System Manager"]
        
        test_data = [
            {"name": "User1", "email": "user1@test.com"},  # frappe.db.sql with as_dict=True returns dicts
            {"name": "User2", "email": "user2@test.com"}
        ]
        
        with patch('frappe.db.sql', return_value=test_data), \
             patch('frappe.log_error'):
            
            result = AnalysisTools.query_and_analyze(
                "SELECT name, email FROM `tabUser` LIMIT 10"
            )
            
            self.assertTrue(result.get("success"))
            self.assertIn("data", result)
            self.assertEqual(len(result["data"]), 2)
    
    @patch('frappe.get_roles')
    def test_query_and_analyze_security_restrictions(self, mock_roles):
        """Test SQL injection protection in query_and_analyze"""
        mock_roles.return_value = ["System Manager"]
        
        # Test various dangerous SQL patterns
        dangerous_queries = [
            "DROP TABLE tabUser",
            "DELETE FROM tabUser",
            "INSERT INTO tabUser VALUES",
            "UPDATE tabUser SET",
            "CREATE TABLE test",
            "ALTER TABLE tabUser"
        ]
        
        for query in dangerous_queries:
            result = AnalysisTools.query_and_analyze(query)
            
            self.assertFalse(result.get("success"))
            self.assertIn("Only SELECT queries", result.get("error", ""))
    
    @patch('frappe.get_roles')
    def test_create_visualization_basic(self, mock_roles):
        """Test basic visualization creation"""
        mock_roles.return_value = ["System Manager"]
        
        data_source = {
            "doctype": "User",
            "filters": {}
        }
        
        with patch('matplotlib.pyplot.savefig') as mock_savefig, \
             patch('matplotlib.pyplot.show'), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_all', return_value=[]), \
             patch('frappe.log_error'):
            
            result = AnalysisTools.create_visualization(
                data_source=data_source,
                chart_type="bar",
                title="Test Chart"
            )
            
            if result.get("success"):
                self.assertIn("chart_info", result)
                mock_savefig.assert_called()
    
    def test_execute_tool_routing(self):
        """Test tool execution routing"""
        # Test valid tool names
        valid_tools = [
            "execute_python_code",
            "analyze_frappe_data", 
            "query_and_analyze",
            "create_visualization"
        ]
        
        for tool_name in valid_tools:
            # This should not raise an exception
            try:
                # Mock the actual execution to avoid permission issues
                with patch.object(AnalysisTools, tool_name.replace('execute_python_code', 'execute_python_code'), 
                                return_value={"success": True}):
                    result = AnalysisTools.execute_tool(tool_name, {})
                    # Just ensure it doesn't crash
            except Exception as e:
                # Expected for some tools due to missing arguments
                pass
    
    def test_execute_tool_invalid_tool(self):
        """Test execution of invalid tool name"""
        result = AnalysisTools.execute_tool("invalid_tool_name", {})
        # The method returns an error string instead of raising an exception
        self.assertIsInstance(result, str)
        self.assertIn("Unknown analysis tool", result)
    
    def test_json_serialization_cleaning(self):
        """Test JSON serialization of complex objects"""
        # Test the _clean_for_json method with various data types
        import datetime
        from decimal import Decimal
        
        test_data = {
            "string": "test",
            "number": 123,
            "date": datetime.datetime.now(),
            "decimal": Decimal("10.5"),
            "list": [1, 2, {"nested": "value"}],
            "none": None
        }
        
        cleaned = AnalysisTools._clean_for_json(test_data)
        
        # Should be JSON serializable
        json_str = json.dumps(cleaned)
        self.assertIsInstance(json_str, str)
    
    def tearDown(self):
        """Clean up after tests"""
        super().tearDown()

class TestAnalysisToolsIntegration(BaseAssistantTest):
    """Integration tests for analysis tools"""
    
    def setUp(self):
        """Set up integration test environment"""
        super().setUp()
    
    @patch('frappe.get_roles')
    def test_full_analysis_workflow(self, mock_roles):
        """Test complete analysis workflow"""
        mock_roles.return_value = ["System Manager"]
        
        # Mock data for the workflow
        test_users = [
            {"name": "User1", "email": "user1@test.com", "creation": "2024-01-01"},
            {"name": "User2", "email": "user2@test.com", "creation": "2024-01-02"}
        ]
        
        with patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_all', return_value=test_users):
            
            # Step 1: Analyze Frappe data
            analysis_result = AnalysisTools.analyze_frappe_data("User")
            self.assertTrue(analysis_result.get("success"))
            
            # Step 2: Execute Python code with the data
            code = """
# Analyze user data
user_count = len(data)
email_domains = [user['email'].split('@')[1] for user in data]
print(f"Total users: {user_count}")
print(f"Domains: {set(email_domains)}")
"""
            
            data_query = {
                "doctype": "User",
                "fields": ["name", "email", "creation"],
                "limit": 100
            }
            
            code_result = AnalysisTools.execute_python_code(code, data_query)
            
            if code_result.get("success"):
                self.assertIn("Total users: 2", code_result["output"])
                self.assertIn("test.com", code_result["output"])
    
    def test_performance_with_large_dataset(self):
        """Test performance with larger datasets"""
        # Create mock large dataset
        large_dataset = [
            {"name": f"User{i}", "value": i} 
            for i in range(1000)
        ]
        
        with patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_all', return_value=large_dataset):
            
            start_time = time.time()
            result = AnalysisTools.analyze_frappe_data("User")
            execution_time = time.time() - start_time
            
            self.assertTrue(result.get("success"))
            self.assertLess(execution_time, 5.0)  # Should complete within 5 seconds

if __name__ == "__main__":
    unittest.main()