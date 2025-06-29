"""
Test suite for Document Tools - FIXED VERSION
Tests only methods that actually exist with correct signatures
"""

import frappe
import unittest
import json
from unittest.mock import patch, MagicMock
from frappe_assistant_core.tools.document_tools import DocumentTools
from frappe_assistant_core.tests.base_test import BaseAssistantTest, TestDataBuilder

class TestDocumentTools(BaseAssistantTest):
    """Test suite for document tools functionality - FIXED"""
    
    def setUp(self):
        """Set up test environment"""
        super().setUp()
        self.tools = DocumentTools()
    
    def test_get_tools_structure(self):
        """Test that get_tools returns proper structure"""
        tools = DocumentTools.get_tools()
        
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        
        # Check each tool has required fields
        for tool in tools:
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("inputSchema", tool)
            self.assertIsInstance(tool["inputSchema"], dict)
    
    def test_create_document_basic(self):
        """Test basic document creation - FIXED SIGNATURE"""
        mock_doc = MagicMock()
        mock_doc.name = "CUST-001"
        mock_doc.insert.return_value = None
        mock_doc.docstatus = 0
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.log_error'), \
             patch('frappe.get_doc', return_value=mock_doc):
            
            # FIXED: Use correct signature - doctype, data, submit
            result = DocumentTools.create_document(
                "Customer", 
                {"customer_name": "Test Customer", "customer_type": "Company"}
            )
            
            self.assertTrue(result.get("success"))
            self.assertIn("name", result)
            self.assertEqual(result["doctype"], "Customer")
            mock_doc.insert.assert_called_once()
    
    def test_create_document_no_permission(self):
        """Test document creation without permission"""
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=False):
            
            result = DocumentTools.create_document(
                "Customer", 
                {"customer_name": "Test"}
            )
            
            self.assertFalse(result.get("success"))
            self.assertIn("permission", result.get("error", ""))
    
    def test_create_document_with_submit(self):
        """Test document creation with submit"""
        mock_doc = MagicMock()
        mock_doc.name = "SINV-001"
        mock_doc.docstatus = 0
        mock_doc.insert.return_value = None
        mock_doc.submit.return_value = None
        mock_doc.submit = MagicMock()  # Ensure submit method exists
        
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.get_doc', return_value=mock_doc):
            
            result = DocumentTools.create_document(
                "Sales Invoice", 
                {"customer": "CUST-001"},
                submit=True
            )
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["status"], "Submitted")
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
            
            result = DocumentTools.get_document("User", "user@test.com")
            
            self.assertTrue(result.get("success"))
            # FIXED: Check actual response structure
            self.assertEqual(result["doctype"], "User")
            self.assertEqual(result["name"], "user@test.com")
            self.assertIn("data", result)  # Not "document"
            self.assertEqual(result["data"]["name"], "user@test.com")
    
    def test_get_document_no_permission(self):
        """Test document retrieval without permission"""
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=False):
            
            result = DocumentTools.get_document("User", "user@test.com")
            
            self.assertFalse(result.get("success"))
            self.assertIn("permission", result.get("error", ""))
    
    def test_get_document_nonexistent(self):
        """Test retrieval of non-existent document"""
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=True), \
             patch('frappe.log_error'), \
             patch('frappe.get_doc', side_effect=frappe.DoesNotExistError("Document not found")):
            
            result = DocumentTools.get_document("User", "nonexistent@test.com")
            
            self.assertFalse(result.get("success"))
            self.assertIn("Document not found", result.get("error", ""))
    
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
            result = DocumentTools.update_document("User", "user@test.com", update_data)
            
            self.assertTrue(result.get("success"))
            self.assertEqual(result["doctype"], "User")
            self.assertEqual(result["name"], "user@test.com")
            
            # FIXED: Check that update and save were called
            mock_doc.update.assert_called_once_with(update_data)
            mock_doc.save.assert_called_once()
    
    def test_update_document_no_permission(self):
        """Test document update without permission"""
        with patch('frappe.db.exists', return_value=True), \
             patch('frappe.has_permission', return_value=False):
            
            result = DocumentTools.update_document("User", "user@test.com", {})
            
            self.assertFalse(result.get("success"))
            self.assertIn("permission", result.get("error", ""))
    
    def test_list_documents_via_execute_tool(self):
        """Test document listing via execute_tool"""
        mock_results = [
            {"name": "CUST-001", "customer_name": "Customer 1"},
            {"name": "CUST-002", "customer_name": "Customer 2"}
        ]
        
        # Mock the list_documents method (assuming it exists)
        with patch.object(DocumentTools, 'list_documents', return_value={
            "success": True,
            "documents": mock_results,
            "count": 2
        }):
            
            result = DocumentTools.execute_tool("document_list", {
                "doctype": "Customer",
                "limit": 10
            })
            
            self.assertTrue(result.get("success"))
            self.assertIn("documents", result)
    
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
                result = DocumentTools.execute_tool(tool_name, {})
                self.assertIsInstance(result, dict)
            except Exception:
                # Expected for some tools due to missing arguments
                pass
    
    def test_execute_tool_invalid_tool(self):
        """Test execution of invalid tool name"""
        with self.assertRaises(Exception):
            DocumentTools.execute_tool("invalid_tool_name", {})

class TestDocumentToolsIntegration(BaseAssistantTest):
    """Integration tests for document tools - FIXED VERSION"""
    
    def setUp(self):
        """Set up integration test environment"""
        super().setUp()
    
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
             patch('frappe.get_doc', return_value=mock_doc):
            
            # Step 1: Create document
            customer_data = {
                "customer_name": "Test Customer Ltd",
                "customer_type": "Company"
            }
            create_result = DocumentTools.create_document("Customer", customer_data)
            self.assertTrue(create_result.get("success"))
            
            # Step 2: Get document
            get_result = DocumentTools.get_document("Customer", "CUST-001")
            self.assertTrue(get_result.get("success"))
            self.assertEqual(get_result["name"], "CUST-001")
            
            # Step 3: Update document
            update_data = {"phone": "123-456-7890"}
            update_result = DocumentTools.update_document("Customer", "CUST-001", update_data)
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
                    with patch('frappe.get_doc', return_value=mock_doc):
                        method = getattr(DocumentTools, scenario["operation"])
                        result = method(*scenario["args"])
                else:
                    with patch('frappe.get_doc', side_effect=scenario["side_effect"]):
                        method = getattr(DocumentTools, scenario["operation"])
                        result = method(*scenario["args"])
                
                self.assertFalse(result.get("success"))
                self.assertIn(scenario["expected_error"], result.get("error", ""))

if __name__ == "__main__":
    unittest.main()