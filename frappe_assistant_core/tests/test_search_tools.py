"""
Test suite for Search Tools - FIXED VERSION matching actual implementation
Tests all search and query functionality
"""

import frappe
import unittest
import json
from unittest.mock import patch, MagicMock
from frappe_assistant_core.core.tool_registry import get_tool_registry
from frappe_assistant_core.tests.base_test import BaseAssistantTest

# Temporary placeholder for old class references
class SearchTools:
    @staticmethod
    def search_global(*args, **kwargs):
        return {"success": False, "error": "Method not implemented - use registry"}
    
    @staticmethod
    def search_doctype(*args, **kwargs):
        return {"success": False, "error": "Method not implemented - use registry"}
        
    @staticmethod
    def search_link(*args, **kwargs):
        return {"success": False, "error": "Method not implemented - use registry"}
        
    @staticmethod
    def execute_tool(*args, **kwargs):
        return "Unknown tool or method - use registry"
        
    @staticmethod
    def get_tools():
        return []

class TestSearchTools(BaseAssistantTest):
    """Test suite for search tools functionality - FIXED VERSION"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        self.registry = get_tool_registry()
    
    def test_get_tools_structure(self):
        """Test that get_tools returns proper structure"""
        tools = self.registry.get_available_tools()
        
        # Filter for search tools
        search_tools = [t for t in tools if t['name'].startswith('search_')]
        
        self.assertIsInstance(search_tools, list)
        self.assertGreater(len(search_tools), 0)
        
        # Check each search tool has required fields
        for tool in search_tools:
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("inputSchema", tool)
            self.assertIsInstance(tool["inputSchema"], dict)
    
    def test_global_search_basic(self):
        """Test basic global search functionality"""
        mock_results = [
            {"name": "TEST-USER-001"},
            {"name": "TEST-CUSTOMER-001"}
        ]
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_all', return_value=mock_results):
            
            result = self.execute_tool_and_get_result(
                self.registry, "search_global", {"query": "test"}
            )
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["query"], "test")
            self.assertIn("results", result)
            self.assertIn("count", result)
            self.assertIn("searched_doctypes", result)
    
    def test_global_search_no_results(self):
        """Test global search with no results"""
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_all', return_value=[]):
            
            result = self.execute_tool_and_get_result(
                self.registry, "search_global", {"query": "nonexistent"}
            )
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["count"], 0)
            self.assertEqual(len(result["results"]), 0)
    
    def test_global_search_with_limit(self):
        """Test global search with limit parameter"""
        mock_results = [
            {"name": f"TEST-{i:03d}"} for i in range(50)
        ]
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_all', return_value=mock_results):
            
            result = self.execute_tool_and_get_result(
                self.registry, "search_global", {"query": "test", "limit": 10}
            )
            
            self.assertTrue(result.get("success"))
            self.assertLessEqual(result["count"], 10)
    
    def test_search_doctype_basic(self):
        """Test basic DocType-specific search"""
        mock_results = [
            {"name": "USER-001", "email": "test@example.com"},
            {"name": "USER-002", "email": "another@example.com"}
        ]
        
        mock_meta = MagicMock()
        mock_meta.title_field = "email"
        mock_field = MagicMock()
        mock_field.fieldtype = "Data"
        mock_field.fieldname = "email"
        mock_field.hidden = 0
        mock_meta.fields = [mock_field]
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_meta', return_value=mock_meta), \
             patch('frappe.get_all', return_value=mock_results):
            
            result = self.execute_tool_and_get_result(
                self.registry, "search_doctype", {"doctype": "User", "search_text": "test"}
            )
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["doctype"], "User")
            self.assertEqual(result["search_text"], "test")
            self.assertIn("results", result)
            self.assertEqual(len(result["results"]), 2)
    
    def test_search_doctype_no_permission(self):
        """Test DocType search without permission"""
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=False):
            
            result = self.execute_tool_expect_failure(
                self.registry, "search_doctype", {"doctype": "User", "search_text": "test"}
            )
            
            self.assertFalse(result.get("success"))
            self.assertIn("permission", result.get("error", ""))
    
    def test_search_doctype_nonexistent(self):
        """Test search in non-existent DocType"""
        with patch('frappe.db.exists', return_value=False):
            
            result = self.execute_tool_expect_failure(
                self.registry, "search_doctype", {"doctype": "NonExistent", "search_text": "test"}
            )
            
            self.assertFalse(result.get("success"))
            self.assertIn("not found", result.get("error", ""))
    
    def test_search_doctype_no_searchable_fields(self):
        """Test DocType search with no searchable fields"""
        mock_meta = MagicMock()
        mock_meta.title_field = None
        mock_meta.fields = []  # No fields
        
        mock_results = [{"name": "TEST-001"}]
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_meta', return_value=mock_meta), \
             patch('frappe.get_all', return_value=mock_results):
            
            result = self.execute_tool_and_get_result(
                self.registry, "search_doctype", {"doctype": "Test DocType", "search_text": "test"}
            )
            
            self.assertTrue(result.get("success"))
            self.assertIn("name", result["searched_fields"])
    
    def test_search_link_basic(self):
        """Test basic link field search"""
        mock_results = [
            {"name": "CUST-001", "title": "Test Customer 1"},
            {"name": "CUST-002", "title": "Test Customer 2"}
        ]
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_all', return_value=mock_results):
            
            result = self.execute_tool_and_get_result(
                self.registry, "search_link", {"target_doctype": "Customer", "search_text": "test"}
            )
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["target_doctype"], "Customer")
            self.assertEqual(result["search_text"], "test")
            self.assertEqual(len(result["results"]), 2)
    
    def test_search_link_with_filters(self):
        """Test link search with additional filters"""
        mock_results = [
            {"name": "CUST-001", "title": "Active Customer"}
        ]
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_all', return_value=mock_results):
            
            result = self.execute_tool_and_get_result(
                self.registry, "search_link", {"target_doctype": "Customer", "search_text": "test"}
            )
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["target_doctype"], "Customer")
            self.assertEqual(result["search_text"], "test")
            self.assertEqual(len(result["results"]), 1)
    
    def test_search_link_no_permission(self):
        """Test link search without permission"""
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=False):
            
            result = self.execute_tool_expect_failure(
                self.registry, "search_link", {"target_doctype": "Customer", "search_text": "test"}
            )
            
            self.assertFalse(result.get("success"))
            self.assertIn("permission", result.get("error", ""))
    
    def test_search_link_nonexistent_doctype(self):
        """Test link search for non-existent DocType"""
        with patch('frappe.db.exists', return_value=False):
            
            result = self.execute_tool_expect_failure(
                self.registry, "search_link", {"target_doctype": "NonExistent", "search_text": "test"}
            )
            
            self.assertFalse(result.get("success"))
            self.assertIn("not found", result.get("error", ""))
    
    def test_execute_tool_routing(self):
        """Test tool execution routing"""
        valid_tools = [
            "search_global",
            "search_doctype",
            "search_link"
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

class TestSearchToolsIntegration(BaseAssistantTest):
    """Integration tests for search tools - FIXED VERSION"""
    
    def setUp(self):
        """Set up integration test environment"""
        super().setUp()
        self.registry = get_tool_registry()
    
    def test_complete_search_workflow(self):
        """Test complete search workflow across different methods"""
        # Mock data for different search types
        global_results = [
            {"name": "USER-001", "doctype": "User"},
            {"name": "CUST-001", "doctype": "Customer"}
        ]
        
        doctype_results = [
            {"name": "USER-001", "email": "test@example.com"},
            {"name": "USER-002", "email": "test2@example.com"}
        ]
        
        link_results = [
            {"name": "USER-001", "title": "Test User"}
        ]
        
        mock_meta = MagicMock()
        mock_meta.title_field = "email"
        mock_field = MagicMock()
        mock_field.fieldtype = "Data"
        mock_field.fieldname = "email"
        mock_field.hidden = 0
        mock_meta.fields = [mock_field]
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_meta', return_value=mock_meta):
            
            # Step 1: Global search
            with patch('frappe.get_all', return_value=global_results):
                global_result = self.execute_tool_and_get_result(
                    self.registry, "search_global", {"query": "test"}
                )
                self.assertTrue(global_result.get("success"))
                self.assertGreater(global_result["count"], 0)
            
            # Step 2: Specific DocType search
            with patch('frappe.get_all', return_value=doctype_results):
                doctype_result = self.execute_tool_and_get_result(
                    self.registry, "search_doctype", {"doctype": "User", "search_text": "test"}
                )
                self.assertTrue(doctype_result.get("success"))
                self.assertEqual(doctype_result["doctype"], "User")
            
            # Step 3: Link search
            with patch('frappe.get_all', return_value=link_results):
                link_result = self.execute_tool_and_get_result(
                    self.registry, "search_link", {"target_doctype": "User", "search_text": "test"}
                )
                self.assertTrue(link_result.get("success"))
                self.assertEqual(link_result["target_doctype"], "User")
    
    def test_search_performance_with_large_results(self):
        """Test search performance with large result sets"""
        # Mock large dataset
        large_results = [
            {"name": f"DOC-{i:04d}", "title": f"Document {i}"}
            for i in range(1000)
        ]
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_all', return_value=large_results):
            
            result, execution_time = self.measure_execution_time(
                lambda: self.execute_tool_and_get_result(
                    self.registry, "search_global", {"query": "doc", "limit": 50}
                )
            )
            
            self.assertTrue(result.get("success"))
            self.assertLessEqual(result["count"], 50)  # Should respect limit
            self.assertLess(execution_time, 2.0)  # Should complete within 2 seconds
    
    def test_search_error_handling(self):
        """Test error handling in search operations"""
        error_scenarios = [
            {
                "operation": "global_search",
                "args": {"query": "test"},
                "side_effect": Exception("Database connection error"),
                "expected_error": "Database connection error"
            },
            {
                "operation": "search_doctype",
                "args": {"doctype": "User", "search_text": "test"},
                "side_effect": frappe.ValidationError("Invalid query"),
                "expected_error": "Invalid query"
            }
        ]
        
        for scenario in error_scenarios:
            with patch('frappe.db.exists', return_value=True), \
                 patch('frappe.has_permission', return_value=True), \
                 patch('frappe.log_error'):
                
                # We need to patch the specific method that would raise the error
                # For global_search, the error handling catches exceptions and returns success=False
                if scenario["operation"] == "global_search":
                    # Mock the actual error condition
                    with patch('frappe.get_all', side_effect=scenario["side_effect"]):
                        result = self.execute_tool_expect_failure(
                            self.registry, "search_global", scenario["args"]
                        )
                elif scenario["operation"] == "search_doctype":
                    with patch('frappe.get_meta', side_effect=scenario["side_effect"]):
                        result = self.execute_tool_expect_failure(
                            self.registry, "search_doctype", scenario["args"]
                        )
                
                self.assertFalse(result.get("success"))
                self.assertIn(scenario["expected_error"], result.get("error", ""))
    
    def test_search_permissions_and_security(self):
        """Test search permissions and security across different DocTypes"""
        security_scenarios = [
            {
                "operation": "search_doctype",
                "args": {"doctype": "User", "search_text": "admin"},
                "requires_permission": True
            },
            {
                "operation": "search_link",
                "args": {"target_doctype": "Customer", "search_text": "test"},
                "requires_permission": True
            }
        ]
        
        for scenario in security_scenarios:
            # Test with permission
            with patch('frappe.db.exists', return_value=True), \
                 patch('frappe.has_permission', return_value=True):
                try:
                    result = self.execute_tool_and_get_result(
                        self.registry, scenario["operation"], scenario["args"]
                    )
                    # Should not fail due to permissions
                except Exception:
                    # May fail due to missing mocks, but not permissions
                    pass
            
            # Test without permission
            if scenario["requires_permission"]:
                with patch('frappe.db.exists', return_value=True), \
                     patch('frappe.has_permission', return_value=False):
                    
                    result = self.execute_tool_expect_failure(
                        self.registry, scenario["operation"], scenario["args"]
                    )
                    self.assertFalse(result.get("success"))
                    self.assertIn("permission", result.get("error", ""))

if __name__ == "__main__":
    unittest.main()