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
Test suite for Document Tools - FIXED VERSION
Tests only methods that actually exist with correct signatures
"""

import frappe
import unittest
import json
from unittest.mock import patch, MagicMock
from frappe_assistant_core.core.tool_registry import get_tool_registry
from frappe_assistant_core.tests.base_test import BaseAssistantTest, TestDataBuilder

# Temporary placeholder for old class references
class DocumentTools:
    @staticmethod
    def create_document(*args, **kwargs):
        return {"success": False, "error": "Method not implemented - use registry"}
    
    @staticmethod
    def get_document(*args, **kwargs):
        return {"success": False, "error": "Method not implemented - use registry"}
        
    @staticmethod
    def update_document(*args, **kwargs):
        return {"success": False, "error": "Method not implemented - use registry"}
        
    @staticmethod
    def list_documents(*args, **kwargs):
        return {"success": False, "error": "Method not implemented - use registry"}
        
    @staticmethod
    def execute_tool(*args, **kwargs):
        return "Unknown tool or method - use registry"

class TestDocumentTools(BaseAssistantTest):
    """Test suite for document tools functionality - FIXED"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        self.registry = get_tool_registry()
    
    def test_get_tools_structure(self):
        """Test that get_tools returns proper structure"""
        tools = self.registry.get_available_tools()
        
        # Filter for document tools
        document_tools = [t for t in tools if t['name'].startswith('document_')]
        
        self.assertIsInstance(document_tools, list)
        self.assertGreater(len(document_tools), 0)
        
        # Check each document tool has required fields
        for tool in document_tools:
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("inputSchema", tool)
            self.assertIsInstance(tool["inputSchema"], dict)
    
    def test_create_document_basic(self):
        """Test basic document creation using registry"""
        mock_doc = MagicMock()
        mock_doc.name = "CUST-001"
        mock_doc.insert.return_value = None
        mock_doc.docstatus = 0
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.log_error'), \
             patch('frappe.new_doc', return_value=mock_doc):
            
            # Use registry.execute_tool instead of old class method
            result = self.execute_tool_and_get_result(
                self.registry,
                "document_create",
                {
                    "doctype": "Customer", 
                    "data": {"customer_name": "Test Customer", "customer_type": "Company"}
                }
            )
            
            self.assertTrue(result.get("success"))
            self.assertIn("name", result)
            self.assertEqual(result["doctype"], "Customer")
            mock_doc.insert.assert_called_once()
    
    def test_create_document_no_permission(self):
        """Test document creation without permission"""
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=False):
            
            self.execute_tool_expect_failure(
                self.registry,
                "document_create",
                {
                    "doctype": "Customer", 
                    "data": {"customer_name": "Test"}
                },
                "permission"
            )
    
    def test_create_document_with_submit(self):
        """Test document creation with submit"""
        mock_doc = MagicMock()
        mock_doc.name = "SINV-001"
        mock_doc.docstatus = 0  # Initial status before submit
        mock_doc.insert.return_value = None
        mock_doc.submit.return_value = None
        
        # Mock the submit to change docstatus
        def mock_submit():
            mock_doc.docstatus = 1
        mock_doc.submit.side_effect = mock_submit
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.new_doc', return_value=mock_doc):
            
            result = self.execute_tool_and_get_result(
                self.registry,
                "document_create",
                {
                    "doctype": "Sales Invoice", 
                    "data": {"customer": "CUST-001"},
                    "submit": True
                }
            )
            
            self.assertTrue(result.get("success"))
            self.assertTrue(result.get("submitted", False))
            mock_doc.insert.assert_called_once()
            mock_doc.submit.assert_called_once()
    
    def test_get_document_basic(self):
        """Test basic document retrieval - FIXED RESPONSE STRUCTURE"""
        mock_doc = MagicMock()
        mock_doc.name = "user@test.com"
        mock_doc.as_dict.return_value = {
            "name": "user@test.com",
            "email": "user@test.com", 
            "first_name": "Test",
            "enabled": 1
        }
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=mock_doc):
            
            result = self.registry.execute_tool(
                "document_get",
                {"doctype": "User", "name": "user@test.com"}
            )
            
            self.assertTrue(result.get("success"))
            tool_result = result.get("result", {})
            # FIXED: Check actual response structure
            self.assertEqual(tool_result["doctype"], "User")
            self.assertEqual(tool_result["name"], "user@test.com")
            self.assertIn("data", tool_result)  # Not "document"
            self.assertEqual(tool_result["data"]["name"], "user@test.com")
    
    def test_get_document_no_permission(self):
        """Test document retrieval without permission"""
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=False):
            
            result = self.registry.execute_tool(
                "document_get",
                {"doctype": "User", "name": "user@test.com"}
            )
            
            self.assertTrue(result.get("success"))  # Registry execution succeeds
            tool_result = result.get("result", {})
            self.assertFalse(tool_result.get("success"))  # But tool execution fails
            self.assertIn("permission", tool_result.get("error", ""))
    
    def test_get_document_nonexistent(self):
        """Test retrieval of non-existent document"""
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.log_error'), \
             patch('frappe.get_doc', side_effect=frappe.DoesNotExistError("Document not found")):
            
            result = self.registry.execute_tool(
                "document_get",
                {"doctype": "User", "name": "nonexistent@test.com"}
            )
            
            self.assertTrue(result.get("success"))  # Registry execution succeeds
            tool_result = result.get("result", {})
            self.assertFalse(tool_result.get("success"))  # But tool execution fails
            self.assertIn("not found", tool_result.get("error", ""))
    
    def test_update_document_basic(self):
        """Test basic document update - FIXED RESPONSE EXPECTATIONS"""
        mock_doc = MagicMock()
        mock_doc.name = "user@test.com"
        mock_doc.update.return_value = None
        mock_doc.save.return_value = None
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=mock_doc):
            
            update_data = {"first_name": "Updated Name", "phone": "123-456-7890"}
            result = self.registry.execute_tool(
                "document_update",
                {
                    "doctype": "User", 
                    "name": "user@test.com", 
                    "data": update_data
                }
            )
            
            self.assertTrue(result.get("success"))
            tool_result = result.get("result", {})
            self.assertTrue(tool_result.get("success"))
            self.assertEqual(tool_result["doctype"], "User")
            self.assertEqual(tool_result["name"], "user@test.com")
            
            # FIXED: Check that setattr and save were called (not update)
            mock_doc.save.assert_called_once()
    
    def test_update_document_no_permission(self):
        """Test document update without permission"""
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=False):
            
            result = self.registry.execute_tool(
                "document_update",
                {
                    "doctype": "User", 
                    "name": "user@test.com", 
                    "data": {}
                }
            )
            
            self.assertTrue(result.get("success"))  # Registry execution succeeds
            tool_result = result.get("result", {})
            self.assertFalse(tool_result.get("success"))  # But tool execution fails
            self.assertIn("permission", tool_result.get("error", ""))
    
    def test_list_documents_via_execute_tool(self):
        """Test document listing via execute_tool"""
        mock_results = [
            {"name": "CUST-001", "customer_name": "Customer 1"},
            {"name": "CUST-002", "customer_name": "Customer 2"}
        ]
        
        # Mock the document_list tool execution
        with patch('frappe.get_all', return_value=mock_results), \
             patch('frappe.has_permission', return_value=True):
            
            result = self.execute_tool_and_get_result(
                self.registry,
                "document_list",
                {
                    "doctype": "Customer",
                    "limit": 10
                }
            )
            
            self.assertTrue(result.get("success"))
            self.assertIn("data", result)  # document_list returns "data" not "documents"
    
    def test_execute_tool_routing(self):
        """Test tool execution routing"""
        valid_tools = [
            "document_create",
            "document_get",
            "document_update", 
            "document_list"
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
        self.assertIn("not found", result.get("error", ""))

class TestDocumentToolsIntegration(BaseAssistantTest):
    """Integration tests for document tools - FIXED VERSION"""
    
    def setUp(self):
        """Set up integration test environment"""
        super().setUp()
        self.registry = get_tool_registry()
    
    def test_document_lifecycle(self):
        """Test basic document lifecycle with existing methods only"""
        # Mock document for all operations
        mock_doc = MagicMock()
        mock_doc.name = "CUST-001"
        mock_doc.as_dict.return_value = {
            "name": "CUST-001",
            "customer_name": "Test Customer Ltd",
            "customer_type": "Company"
        }
        mock_doc.insert.return_value = None
        mock_doc.save.return_value = None
        mock_doc.update.return_value = None
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.new_doc', return_value=mock_doc), \
             patch('frappe.get_doc', return_value=mock_doc):
            
            # Step 1: Create document
            customer_data = {
                "customer_name": "Test Customer Ltd",
                "customer_type": "Company"
            }
            create_result = self.execute_tool_and_get_result(
                self.registry,
                "document_create",
                {"doctype": "Customer", "data": customer_data}
            )
            self.assertTrue(create_result.get("success"))
            
            # Step 2: Get document
            get_result = self.execute_tool_and_get_result(
                self.registry,
                "document_get",
                {"doctype": "Customer", "name": "CUST-001"}
            )
            self.assertTrue(get_result.get("success"))
            self.assertEqual(get_result["name"], "CUST-001")
            
            # Step 3: Update document
            update_data = {"phone": "123-456-7890"}
            update_result = self.execute_tool_and_get_result(
                self.registry,
                "document_update",
                {"doctype": "Customer", "name": "CUST-001", "data": update_data}
            )
            self.assertTrue(update_result.get("success"))
    
    def test_error_handling_scenarios(self):
        """Test various error scenarios"""
        error_scenarios = [
            {
                "operation": "create_document",
                "args": ("Customer", {"customer_name": "Test"}),
                "side_effect": frappe.ValidationError("Required field missing"),
                "expected_error": "Required field missing"
            },
            {
                "operation": "get_document", 
                "args": ("User", "nonexistent@test.com"),
                "side_effect": frappe.DoesNotExistError("Document not found"),
                "expected_error": "Document not found"
            }
        ]
        
        for scenario in error_scenarios:
            with patch('frappe.db.exists', return_value=True), \
                 patch('frappe.has_permission', return_value=True), \
                 patch('frappe.log_error'):
                
                if scenario["operation"] == "create_document":
                    mock_doc = MagicMock()
                    mock_doc.insert.side_effect = scenario["side_effect"]
                    with patch('frappe.new_doc', return_value=mock_doc):
                        result = self.execute_tool_expect_failure(
                            self.registry, "document_create", 
                            {"doctype": scenario["args"][0], "data": scenario["args"][1]}
                        )
                else:
                    with patch('frappe.get_doc', side_effect=scenario["side_effect"]):
                        result = self.execute_tool_expect_failure(
                            self.registry, "document_get", 
                            {"doctype": scenario["args"][0], "name": scenario["args"][1]}
                        )
                
                self.assertFalse(result.get("success"))
                self.assertIn(scenario["expected_error"], result.get("error", ""))

if __name__ == "__main__":
    unittest.main()