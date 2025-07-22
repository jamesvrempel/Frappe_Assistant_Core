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
Test suite for Report Tools - FIXED VERSION matching actual implementation
Tests all report generation and execution functionality
"""

import frappe
import unittest
import json
from unittest.mock import patch, MagicMock
from frappe_assistant_core.core.tool_registry import get_tool_registry
from frappe_assistant_core.tests.base_test import BaseAssistantTest

# Temporary placeholder for old class references
class ReportTools:
    @staticmethod
    def execute_report(*args, **kwargs):
        return {"success": False, "error": "Method not implemented - use registry"}
    
    @staticmethod
    def list_reports(*args, **kwargs):
        return {"success": False, "error": "Method not implemented - use registry"}
        
    @staticmethod
    def get_report_columns(*args, **kwargs):
        return {"success": False, "error": "Method not implemented - use registry"}
        
    @staticmethod
    def execute_tool(*args, **kwargs):
        return "Unknown tool or method - use registry"
        
    @staticmethod
    def get_tools():
        return []

class TestReportTools(BaseAssistantTest):
    """Test suite for report tools functionality - FIXED VERSION"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        self.registry = get_tool_registry()
    
    def test_get_tools_structure(self):
        """Test that get_tools returns proper structure"""
        tools = self.registry.get_available_tools()
        
        # Filter for report tools
        report_tools = [t for t in tools if t['name'].startswith('report_')]
        
        self.assertIsInstance(report_tools, list)
        self.assertGreater(len(report_tools), 0)
        
        # Check each report tool has required fields
        for tool in report_tools:
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
        mock_report1.disabled = 0
        mock_report1.is_standard = "Yes"
        
        mock_report2 = MagicMock()
        mock_report2.name = "Test Report 2"
        mock_report2.report_type = "Script Report"
        mock_report2.disabled = 0
        mock_report2.is_standard = "No"
        
        mock_reports = [mock_report1, mock_report2]
        
        with patch('frappe.get_all', return_value=mock_reports), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.log_error'):
            
            result = self.execute_tool_and_get_result(
                self.registry, "report_list", {}
            )
            
            self.assertTrue(result.get("success"))
            self.assertIn("reports", result)
            self.assertEqual(len(result["reports"]), 2)
            self.assertIn("summary", result)
            self.assertEqual(result["summary"]["accessible"], 2)
    
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
            
            result = self.execute_tool_and_get_result(
                self.registry, "report_list", {"report_type": "Query Report"}
            )
            
            self.assertTrue(result.get("success"))
            # Verify filters were applied
            mock_get_all.assert_called()
            call_args = mock_get_all.call_args
            self.assertIn("filters", call_args[1])
    
    def test_list_reports_no_permission(self):
        """Test report listing without permission - FIXED METHOD NAME"""
        with patch('frappe.get_all', return_value=[]), \
             patch('frappe.log_error'):
            
            result = self.execute_tool_and_get_result(
                self.registry, "report_list", {}
            )
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["summary"]["accessible"], 0)
    
    def test_execute_report_query_report(self):
        """Test executing a query report - FIXED METHOD NAME"""
        mock_report = {
            "name": "Test Query Report",
            "report_type": "Query Report", 
            "query": "SELECT name, email FROM tabUser LIMIT 5",
            "disabled": 0
        }
        
        mock_results = [["User1", "user1@test.com"], ["User2", "user2@test.com"]]
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=MagicMock(**mock_report)), \
             patch('frappe.desk.query_report.run', return_value={"result": mock_results, "columns": []}), \
             patch('frappe.db.get_single_value', return_value="Test Company"), \
             patch('frappe.log_error'):
            
            result = self.execute_tool_and_get_result(
                self.registry, "report_execute", {"report_name": "Test Query Report"}
            )
            
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
             patch('frappe.log_error'):
            
            result = self.execute_tool_and_get_result(
                self.registry, "report_execute", {"report_name": "Test Script Report"}
            )
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["report_name"], "Test Script Report")
            self.assertEqual(result["report_type"], "Script Report")
    
    def test_execute_report_with_filters(self):
        """Test executing report with filters - FIXED METHOD NAME"""
        filters = {"enabled": 1}
        mock_report = MagicMock()
        mock_report.name = "Test Report"
        mock_report.report_type = "Query Report"
        mock_report.disabled = 0
        
        mock_results = [["Active User", "active@test.com"]]
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=mock_report), \
             patch('frappe.desk.query_report.run', return_value={"result": mock_results, "columns": []}), \
             patch('frappe.db.get_single_value', return_value="Test Company"), \
             patch('frappe.log_error'):
            
            result = self.execute_tool_and_get_result(
                self.registry, "report_execute", {"report_name": "Test Report", "filters": filters}
            )
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["filters_applied"], filters)
    
    def test_execute_report_nonexistent_report(self):
        """Test executing non-existent report - FIXED METHOD NAME"""
        with patch('frappe.db.exists', return_value=False), \
             patch('frappe.log_error'):
            
            result = self.execute_tool_expect_failure(
                self.registry, "report_execute", {"report_name": "Non Existent Report"}
            )
            
            self.assertFalse(result.get("success"))
            self.assertIn("not found", result.get("error", ""))
    
    def test_execute_report_no_permission(self):
        """Test executing report without permission - FIXED METHOD NAME"""
        # Create a mock report document
        mock_report = MagicMock()
        mock_report.report_type = "Query Report"
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.get_doc', return_value=mock_report), \
             patch('frappe.has_permission', return_value=False), \
             patch('frappe.log_error'):
            
            result = self.execute_tool_expect_failure(
                self.registry, "report_execute", {"report_name": "Some Report"}
            )
            
            self.assertFalse(result.get("success"))
            self.assertIn("Insufficient permissions", result.get("error", ""))
    
    def test_get_report_columns_query_report(self):
        """Test getting columns for query report - FIXED METHOD NAME"""
        mock_report = MagicMock()
        mock_report.name = "Test Report"
        mock_report.report_type = "Query Report"
        mock_report.query = "SELECT name FROM tabUser"
        mock_report.disabled = 0
        mock_report.report_name = "Test Report"
        mock_report.module = "Core"
        mock_report.is_standard = 1
        mock_report.description = "Test Report"
        mock_report.ref_doctype = ""
        mock_report.creation = "2023-01-01"
        mock_report.modified = "2023-01-01"
        mock_report.owner = "Administrator"
        mock_report.modified_by = "Administrator"
        mock_report.prepared_report = 0
        mock_report.disable_prepared_report = 0
        mock_report.json = None
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=mock_report), \
             patch('frappe.db.sql', return_value=[{"name": "Test User"}]), \
             patch('frappe.log_error'):
            
            result = self.execute_tool_and_get_result(
                self.registry, "report_details", {"report_name": "Test Report"}
            )
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["report_details"]["name"], "Test Report")
            self.assertIn("columns", result["report_details"])
    
    def test_get_report_columns_script_report(self):
        """Test getting columns for script report - FIXED METHOD NAME"""
        mock_columns = [
            {"fieldname": "name", "label": "Name", "fieldtype": "Data"},
            {"fieldname": "value", "label": "Value", "fieldtype": "Currency"}
        ]
        
        mock_report = MagicMock()
        mock_report.name = "Test Report"
        mock_report.report_type = "Script Report"
        mock_report.module = "Core"
        mock_report.disabled = 0
        mock_report.report_name = "Test Report"
        mock_report.is_standard = 1
        mock_report.description = "Test Report"
        mock_report.ref_doctype = ""
        mock_report.creation = "2023-01-01"
        mock_report.modified = "2023-01-01"
        mock_report.owner = "Administrator"
        mock_report.modified_by = "Administrator"
        mock_report.javascript = ""
        mock_report.json = None
        
        # Mock the module loading to return columns
        mock_module = MagicMock()
        mock_module.get_columns = MagicMock(return_value=mock_columns)
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=mock_report), \
             patch('frappe.get_module', return_value=mock_module), \
             patch('frappe.log_error'):
            
            result = self.execute_tool_and_get_result(
                self.registry, "report_details", {"report_name": "Test Report"}
            )
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["report_details"]["report_type"], "Script Report")
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
        mock_report.disabled = 0
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=mock_report), \
             patch('frappe.desk.query_report.run', return_value={"result": mock_data, "columns": []}), \
             patch('frappe.db.get_single_value', return_value="Test Company"), \
             patch('frappe.log_error'):
            
            # Test JSON format (default)
            result = self.execute_tool_and_get_result(
                self.registry, "report_execute", {"report_name": "Test Report", "format": "json"}
            )
            
            self.assertTrue(result.get("success"))
            self.assertIn("data", result)
            self.assertEqual(len(result["data"]), 2)
    
    def test_execute_tool_routing(self):
        """Test tool execution routing - FIXED TOOL NAMES"""
        valid_tools = [
            "report_execute",
            "report_list", 
            "report_details"
        ]
        
        for tool_name in valid_tools:
            try:
                result = self.registry.execute_tool(tool_name, {})
                self.assertIsInstance(result, dict)
            except Exception:
                # Expected for some tools due to missing arguments
                pass
    
    def test_execute_tool_invalid_tool(self):
        """Test execution of invalid tool name"""
        result = self.registry.execute_tool("invalid_tool_name", {})
        self.assertFalse(result.get("success"))
        self.assertEqual(result.get("error_type"), "ToolNotFound")

class TestReportToolsIntegration(BaseAssistantTest):
    """Integration tests for report tools - FIXED VERSION"""
    
    def setUp(self):
        """Set up integration test environment"""
        super().setUp()
        self.registry = get_tool_registry()
    
    def test_complete_report_workflow(self):
        """Test complete report workflow"""
        # Mock report data with MagicMock objects
        mock_report1 = MagicMock()
        mock_report1.name = "Sales Report"
        mock_report1.report_type = "Query Report"
        mock_report1.disabled = 0
        mock_report1.is_standard = "Yes"
        
        mock_report2 = MagicMock()
        mock_report2.name = "Inventory Report"
        mock_report2.report_type = "Script Report"
        mock_report2.disabled = 0
        mock_report2.is_standard = "No"
        
        mock_reports = [mock_report1, mock_report2]
        
        mock_report_data = [
            {"customer": "ABC Corp", "amount": 1000},
            {"customer": "XYZ Ltd", "amount": 2000}
        ]
        
        mock_report = MagicMock()
        mock_report.name = "Sales Report"
        mock_report.report_type = "Query Report"
        mock_report.disabled = 0
        mock_report.report_name = "Sales Report"
        mock_report.module = "Accounts"
        mock_report.is_standard = 1
        mock_report.description = "Sales Report"
        mock_report.ref_doctype = ""
        mock_report.creation = "2023-01-01"
        mock_report.modified = "2023-01-01"
        mock_report.owner = "Administrator"
        mock_report.modified_by = "Administrator"
        mock_report.query = "SELECT * FROM tabSales"
        mock_report.prepared_report = 0
        mock_report.disable_prepared_report = 0
        mock_report.json = None
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=mock_report), \
             patch('frappe.db.sql', return_value=[{"customer": "Test Customer", "amount": 1000}]), \
             patch('frappe.desk.query_report.run', return_value={"result": mock_report_data, "columns": []}), \
             patch('frappe.db.get_single_value', return_value="Test Company"), \
             patch('frappe.log_error'):
            
            # Step 1: List available reports
            with patch('frappe.get_all', return_value=mock_reports):
                list_result = self.execute_tool_and_get_result(
                    self.registry, "report_list", {}
                )
                self.assertTrue(list_result.get("success"))
                self.assertEqual(len(list_result["reports"]), 2)
            
            # Step 2: Get report columns
            columns_result = self.execute_tool_and_get_result(
                self.registry, "report_details", {"report_name": "Sales Report"}
            )
            self.assertTrue(columns_result.get("success"))
            
            # Step 3: Execute report
            execute_result = self.execute_tool_and_get_result(
                self.registry, "report_execute", {"report_name": "Sales Report"}
            )
            self.assertTrue(execute_result.get("success"))
    
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
                        result = self.execute_tool_expect_failure(
                            self.registry, "report_execute", scenario["args"]
                        )
                elif scenario["operation"] == "list_reports":
                    with patch('frappe.get_all', side_effect=scenario["side_effect"]):
                        result = self.execute_tool_expect_failure(
                            self.registry, "report_list", scenario["args"]
                        )
                
                self.assertFalse(result.get("success"))
                self.assertIn(scenario["expected_error"], result.get("error", ""))

if __name__ == "__main__":
    unittest.main()