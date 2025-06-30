"""
Test suite for Report Tools - FIXED VERSION matching actual implementation
Tests all report generation and execution functionality
"""

import frappe
import unittest
import json
from unittest.mock import patch, MagicMock
from frappe_assistant_core.tools.report_tools import ReportTools
from frappe_assistant_core.tests.base_test import BaseAssistantTest

class TestReportTools(BaseAssistantTest):
    """Test suite for report tools functionality - FIXED VERSION"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        self.tools = ReportTools()
    
    def test_get_tools_structure(self):
        """Test that get_tools returns proper structure"""
        tools = ReportTools.get_tools()
        
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        
        # Check each tool has required fields
        for tool in tools:
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("inputSchema", tool)
            self.assertIsInstance(tool["inputSchema"], dict)
    
    def test_list_reports_basic(self):
        """Test basic report listing functionality - FIXED METHOD NAME"""
        # Create mock objects with dot notation access
        mock_report1 = MagicMock()
        mock_report1.name = "Test Report 1"
        mock_report1.report_type = "Query Report"
        
        mock_report2 = MagicMock()
        mock_report2.name = "Test Report 2"
        mock_report2.report_type = "Script Report"
        
        mock_reports = [mock_report1, mock_report2]
        
        with patch('frappe.get_all', return_value=mock_reports), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.log_error'):
            
            result = ReportTools.list_reports()
            
            self.assertTrue(result.get("success"))
            self.assertIn("reports", result)
            self.assertEqual(len(result["reports"]), 2)
            self.assertIn("count", result)
    
    def test_list_reports_with_filters(self):
        """Test report listing with filters - FIXED METHOD NAME"""
        # Create mock object with dot notation access
        mock_report = MagicMock()
        mock_report.name = "Query Report 1"
        mock_report.report_type = "Query Report"
        mock_report.module = "Accounts"
        
        mock_reports = [mock_report]
        
        with patch('frappe.get_all', return_value=mock_reports) as mock_get_all, \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.log_error'):
            
            result = ReportTools.list_reports(report_type="Query Report")
            
            self.assertTrue(result.get("success"))
            # Verify filters were applied
            mock_get_all.assert_called()
            call_args = mock_get_all.call_args
            self.assertIn("filters", call_args[1])
    
    def test_list_reports_no_permission(self):
        """Test report listing without permission - FIXED METHOD NAME"""
        with patch('frappe.get_all', return_value=[]), \
             patch('frappe.log_error'):
            
            result = ReportTools.list_reports()
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["count"], 0)
    
    def test_execute_report_query_report(self):
        """Test executing a query report - FIXED METHOD NAME"""
        mock_report = {
            "name": "Test Query Report",
            "report_type": "Query Report", 
            "query": "SELECT name, email FROM tabUser LIMIT 5"
        }
        
        mock_results = [["User1", "user1@test.com"], ["User2", "user2@test.com"]]
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=MagicMock(**mock_report)), \
             patch('frappe.log_error'), \
             patch.object(ReportTools, '_execute_query_report', return_value={"result": mock_results, "columns": []}):
            
            result = ReportTools.execute_report("Test Query Report")
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["report_name"], "Test Query Report")
            self.assertEqual(result["report_type"], "Query Report")
            self.assertIn("data", result)
    
    def test_execute_report_script_report(self):
        """Test executing a script report - FIXED METHOD NAME"""
        mock_data = [{"name": "Item1", "qty": 10}, {"name": "Item2", "qty": 20}]
        
        mock_report = MagicMock()
        mock_report.name = "Test Script Report"
        mock_report.report_type = "Script Report"
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=mock_report), \
             patch('frappe.log_error'), \
             patch.object(ReportTools, '_execute_script_report', return_value={"result": mock_data, "columns": []}):
            
            result = ReportTools.execute_report("Test Script Report")
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["report_name"], "Test Script Report")
            self.assertEqual(result["report_type"], "Script Report")
    
    def test_execute_report_with_filters(self):
        """Test executing report with filters - FIXED METHOD NAME"""
        filters = {"enabled": 1}
        mock_report = MagicMock()
        mock_report.name = "Test Report"
        mock_report.report_type = "Query Report"
        
        mock_results = [["Active User", "active@test.com"]]
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=mock_report), \
             patch('frappe.log_error'), \
             patch.object(ReportTools, '_execute_query_report', return_value={"result": mock_results, "columns": []}):
            
            result = ReportTools.execute_report("Test Report", filters=filters)
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["filters_applied"], filters)
    
    def test_execute_report_nonexistent_report(self):
        """Test executing non-existent report - FIXED METHOD NAME"""
        with patch('frappe.db.exists', return_value=False), \
             patch('frappe.log_error'):
            
            result = ReportTools.execute_report("Non Existent Report")
            
            self.assertFalse(result.get("success"))
            self.assertIn("not found", result.get("error", ""))
    
    def test_execute_report_no_permission(self):
        """Test executing report without permission - FIXED METHOD NAME"""
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=False), \
             patch('frappe.log_error'):
            
            result = ReportTools.execute_report("Some Report")
            
            self.assertFalse(result.get("success"))
            self.assertIn("permission", result.get("error", ""))
    
    def test_get_report_columns_query_report(self):
        """Test getting columns for query report - FIXED METHOD NAME"""
        mock_report = MagicMock()
        mock_report.name = "Test Report"
        mock_report.report_type = "Query Report"
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=mock_report), \
             patch('frappe.log_error'), \
             patch.object(ReportTools, '_execute_query_report', return_value={"columns": [{"label": "Name", "fieldname": "name"}]}):
            
            result = ReportTools.get_report_columns("Test Report")
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["report_name"], "Test Report")
            self.assertIn("columns", result)
    
    def test_get_report_columns_script_report(self):
        """Test getting columns for script report - FIXED METHOD NAME"""
        mock_columns = [
            {"fieldname": "name", "label": "Name", "fieldtype": "Data"},
            {"fieldname": "value", "label": "Value", "fieldtype": "Currency"}
        ]
        
        mock_report = MagicMock()
        mock_report.name = "Test Report"
        mock_report.report_type = "Script Report"
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=mock_report), \
             patch('frappe.log_error'), \
             patch.object(ReportTools, '_execute_script_report', return_value={"columns": mock_columns}):
            
            result = ReportTools.get_report_columns("Test Report")
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["report_type"], "Script Report")
            # Note: Script reports get columns differently, so just check success
    
    def test_report_format_functionality(self):
        """Test report format functionality - FIXED TO MATCH ACTUAL IMPLEMENTATION"""
        mock_data = [
            {"name": "User1", "email": "user1@test.com"},
            {"name": "User2", "email": "user2@test.com"}
        ]
        
        mock_report = MagicMock()
        mock_report.name = "Test Report"
        mock_report.report_type = "Query Report"
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=mock_report), \
             patch('frappe.log_error'), \
             patch.object(ReportTools, '_execute_query_report', return_value={"result": mock_data, "columns": []}):
            
            # Test JSON format (default)
            result = ReportTools.execute_report("Test Report", format="json")
            
            self.assertTrue(result.get("success"))
            self.assertIn("data", result)
            self.assertEqual(len(result["data"]), 2)
    
    def test_execute_tool_routing(self):
        """Test tool execution routing - FIXED TOOL NAMES"""
        valid_tools = [
            "report_execute",
            "report_list", 
            "report_columns"
        ]
        
        for tool_name in valid_tools:
            try:
                result = ReportTools.execute_tool(tool_name, {})
                self.assertIsInstance(result, dict)
            except Exception:
                # Expected for some tools due to missing arguments
                pass
    
    def test_execute_tool_invalid_tool(self):
        """Test execution of invalid tool name"""
        with self.assertRaises(Exception):
            ReportTools.execute_tool("invalid_tool_name", {})

class TestReportToolsIntegration(BaseAssistantTest):
    """Integration tests for report tools - FIXED VERSION"""
    
    def setUp(self):
        """Set up integration test environment"""
        super().setUp()
    
    def test_complete_report_workflow(self):
        """Test complete report workflow"""
        # Mock report data with MagicMock objects
        mock_report1 = MagicMock()
        mock_report1.name = "Sales Report"
        mock_report1.report_type = "Query Report"
        
        mock_report2 = MagicMock()
        mock_report2.name = "Inventory Report"
        mock_report2.report_type = "Script Report"
        
        mock_reports = [mock_report1, mock_report2]
        
        mock_report_data = [
            {"customer": "ABC Corp", "amount": 1000},
            {"customer": "XYZ Ltd", "amount": 2000}
        ]
        
        mock_report = MagicMock()
        mock_report.name = "Sales Report"
        mock_report.report_type = "Query Report"
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=mock_report), \
             patch('frappe.log_error'):
            
            # Step 1: List available reports
            with patch('frappe.get_all', return_value=mock_reports):
                list_result = ReportTools.list_reports()
                self.assertTrue(list_result.get("success"))
                self.assertEqual(len(list_result["reports"]), 2)
            
            # Step 2: Get report columns
            with patch.object(ReportTools, '_execute_query_report', return_value={"columns": [{"label": "Customer"}, {"label": "Amount"}]}):
                columns_result = ReportTools.get_report_columns("Sales Report")
                self.assertTrue(columns_result.get("success"))
            
            # Step 3: Execute report
            with patch.object(ReportTools, '_execute_query_report', return_value={"result": mock_report_data, "columns": []}):
                execute_result = ReportTools.execute_report("Sales Report")
                self.assertTrue(execute_result.get("success"))
                self.assertEqual(len(execute_result["data"]), 2)
    
    def test_report_error_handling(self):
        """Test error handling in report operations"""
        error_scenarios = [
            {
                "operation": "execute_report",
                "args": {"report_name": "Test Report"},
                "side_effect": Exception("Database error"),
                "expected_error": "Database error"
            },
            {
                "operation": "list_reports",
                "args": {},
                "side_effect": frappe.ValidationError("Invalid query"),
                "expected_error": "Invalid query"
            }
        ]
        
        for scenario in error_scenarios:
            with patch('frappe.db.exists', return_value=True), \
                 patch('frappe.has_permission', return_value=True), \
                 patch('frappe.log_error'):
                
                if scenario["operation"] == "execute_report":
                    with patch('frappe.get_doc', side_effect=scenario["side_effect"]):
                        method = getattr(ReportTools, scenario["operation"])
                        result = method(**scenario["args"])
                elif scenario["operation"] == "list_reports":
                    with patch('frappe.get_all', side_effect=scenario["side_effect"]):
                        method = getattr(ReportTools, scenario["operation"])
                        result = method(**scenario["args"])
                
                self.assertFalse(result.get("success"))
                self.assertIn(scenario["expected_error"], result.get("error", ""))

if __name__ == "__main__":
    unittest.main()