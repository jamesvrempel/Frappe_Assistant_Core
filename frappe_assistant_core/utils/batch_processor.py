"""
Batch Processing Engine for Frappe Assistant Core
Enables parallel execution of multiple operations with progress tracking
"""

import frappe
import asyncio
import concurrent.futures
import threading
import time
import uuid
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from frappe_assistant_core.utils.logger import api_logger

class BatchStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class BatchOperation:
    """Represents a single operation in a batch"""
    operation_id: str
    operation_type: str
    parameters: Dict[str, Any]
    status: BatchStatus = BatchStatus.PENDING
    result: Any = None
    error: str = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type,
            "parameters": self.parameters,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "progress": self.progress,
            "duration_seconds": (
                (self.end_time - self.start_time).total_seconds() 
                if self.start_time and self.end_time else None
            )
        }

@dataclass
class BatchJob:
    """Represents a batch job containing multiple operations"""
    batch_id: str
    user: str
    operations: List[BatchOperation]
    status: BatchStatus = BatchStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    max_parallel: int = 3
    progress_callback: Optional[Callable] = None
    
    def get_progress(self) -> Dict[str, Any]:
        """Get overall batch progress"""
        total_ops = len(self.operations)
        completed_ops = sum(1 for op in self.operations if op.status in [BatchStatus.COMPLETED, BatchStatus.FAILED])
        successful_ops = sum(1 for op in self.operations if op.status == BatchStatus.COMPLETED)
        failed_ops = sum(1 for op in self.operations if op.status == BatchStatus.FAILED)
        
        return {
            "batch_id": self.batch_id,
            "status": self.status.value,
            "total_operations": total_ops,
            "completed_operations": completed_ops,
            "successful_operations": successful_ops,
            "failed_operations": failed_ops,
            "progress_percent": (completed_ops / total_ops * 100) if total_ops > 0 else 0,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "operations": [op.to_dict() for op in self.operations]
        }

class BatchProcessor:
    """Enhanced batch processor with parallel execution and progress tracking"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.active_batches: Dict[str, BatchJob] = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.Lock()
    
    def create_batch_job(self, user: str, operations: List[Dict[str, Any]], max_parallel: int = 3) -> str:
        """Create a new batch job"""
        batch_id = str(uuid.uuid4())
        
        # Convert operation dicts to BatchOperation objects
        batch_operations = []
        for op_data in operations:
            operation_id = str(uuid.uuid4())
            operation = BatchOperation(
                operation_id=operation_id,
                operation_type=op_data.get("type"),
                parameters=op_data.get("parameters", {})
            )
            batch_operations.append(operation)
        
        # Create batch job
        batch_job = BatchJob(
            batch_id=batch_id,
            user=user,
            operations=batch_operations,
            max_parallel=min(max_parallel, self.max_workers)
        )
        
        with self._lock:
            self.active_batches[batch_id] = batch_job
        
        api_logger.info(f"Created batch job {batch_id} with {len(operations)} operations")
        return batch_id
    
    def execute_batch(self, batch_id: str, progress_callback: Optional[Callable] = None) -> BatchJob:
        """Execute a batch job with parallel processing"""
        with self._lock:
            if batch_id not in self.active_batches:
                raise ValueError(f"Batch job {batch_id} not found")
            
            batch_job = self.active_batches[batch_id]
        
        if batch_job.status != BatchStatus.PENDING:
            raise ValueError(f"Batch job {batch_id} is not in pending state")
        
        batch_job.status = BatchStatus.RUNNING
        batch_job.start_time = datetime.now()
        batch_job.progress_callback = progress_callback
        
        try:
            # Execute operations in parallel with limited concurrency
            self._execute_operations_parallel(batch_job)
            
            # Determine final status
            failed_count = sum(1 for op in batch_job.operations if op.status == BatchStatus.FAILED)
            if failed_count > 0:
                batch_job.status = BatchStatus.FAILED
            else:
                batch_job.status = BatchStatus.COMPLETED
                
        except Exception as e:
            api_logger.error(f"Batch execution error: {str(e)}")
            batch_job.status = BatchStatus.FAILED
            for op in batch_job.operations:
                if op.status == BatchStatus.RUNNING:
                    op.status = BatchStatus.FAILED
                    op.error = "Batch execution failed"
        finally:
            batch_job.end_time = datetime.now()
            self._notify_progress(batch_job)
        
        return batch_job
    
    def _execute_operations_parallel(self, batch_job: BatchJob):
        """Execute operations with parallel processing"""
        # Create semaphore to limit concurrent operations
        semaphore = threading.Semaphore(batch_job.max_parallel)
        
        # Submit all operations to thread pool
        futures = []
        for operation in batch_job.operations:
            future = self.executor.submit(self._execute_single_operation, operation, semaphore, batch_job)
            futures.append(future)
        
        # Wait for all operations to complete
        concurrent.futures.wait(futures)
    
    def _execute_single_operation(self, operation: BatchOperation, semaphore: threading.Semaphore, batch_job: BatchJob):
        """Execute a single operation with proper resource management"""
        with semaphore:
            try:
                operation.status = BatchStatus.RUNNING
                operation.start_time = datetime.now()
                self._notify_progress(batch_job)
                
                # Set Frappe user context
                frappe.set_user(batch_job.user)
                
                # Execute based on operation type
                if operation.operation_type == "tool_call":
                    operation.result = self._execute_tool_call(operation)
                elif operation.operation_type == "query":
                    operation.result = self._execute_query(operation)
                elif operation.operation_type == "analysis":
                    operation.result = self._execute_analysis(operation)
                elif operation.operation_type == "report":
                    operation.result = self._execute_report(operation)
                else:
                    raise ValueError(f"Unknown operation type: {operation.operation_type}")
                
                operation.status = BatchStatus.COMPLETED
                operation.progress = 100
                
            except Exception as e:
                operation.status = BatchStatus.FAILED
                operation.error = str(e)
                api_logger.error(f"Operation {operation.operation_id} failed: {str(e)}")
            finally:
                operation.end_time = datetime.now()
                self._notify_progress(batch_job)
    
    def _execute_tool_call(self, operation: BatchOperation) -> Any:
        """Execute a tool call operation"""
        from frappe_assistant_core.tools.tool_registry import AutoToolRegistry
        
        tool_name = operation.parameters.get("tool_name")
        arguments = operation.parameters.get("arguments", {})
        
        if not tool_name:
            raise ValueError("Missing tool_name parameter")
        
        return AutoToolRegistry.execute_tool(tool_name, arguments)
    
    def _execute_query(self, operation: BatchOperation) -> Any:
        """Execute a database query operation"""
        query = operation.parameters.get("query")
        values = operation.parameters.get("values", [])
        
        if not query:
            raise ValueError("Missing query parameter")
        
        # Security check - only allow SELECT queries
        if not query.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed")
        
        return frappe.db.sql(query, values, as_dict=True)
    
    def _execute_analysis(self, operation: BatchOperation) -> Any:
        """Execute a data analysis operation"""
        from frappe_assistant_core.tools.analysis_tools import AnalysisTools
        
        analysis_type = operation.parameters.get("analysis_type")
        data_source = operation.parameters.get("data_source")
        parameters = operation.parameters.get("parameters", {})
        
        if analysis_type == "frappe_data":
            return AnalysisTools.execute_tool("analyze_frappe_data", {
                "doctype": data_source,
                **parameters
            })
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    def _execute_report(self, operation: BatchOperation) -> Any:
        """Execute a report generation operation"""
        from frappe_assistant_core.tools.report_tools import ReportTools
        
        report_name = operation.parameters.get("report_name")
        filters = operation.parameters.get("filters", {})
        
        if not report_name:
            raise ValueError("Missing report_name parameter")
        
        return ReportTools.execute_tool("report_execute", {
            "report_name": report_name,
            "filters": filters
        })
    
    def _notify_progress(self, batch_job: BatchJob):
        """Notify progress callback if available"""
        if batch_job.progress_callback:
            try:
                progress_data = batch_job.get_progress()
                batch_job.progress_callback(progress_data)
            except Exception as e:
                api_logger.error(f"Progress callback error: {str(e)}")
    
    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get status of a batch job"""
        with self._lock:
            if batch_id not in self.active_batches:
                raise ValueError(f"Batch job {batch_id} not found")
            
            batch_job = self.active_batches[batch_id]
            return batch_job.get_progress()
    
    def cancel_batch(self, batch_id: str) -> bool:
        """Cancel a running batch job"""
        with self._lock:
            if batch_id not in self.active_batches:
                return False
            
            batch_job = self.active_batches[batch_id]
            
            if batch_job.status == BatchStatus.RUNNING:
                batch_job.status = BatchStatus.CANCELLED
                
                # Mark pending operations as cancelled
                for operation in batch_job.operations:
                    if operation.status == BatchStatus.PENDING:
                        operation.status = BatchStatus.CANCELLED
                
                return True
            
            return False
    
    def cleanup_completed_batches(self, max_age_hours: int = 24):
        """Remove old completed batch jobs"""
        current_time = datetime.now()
        expired_batches = []
        
        with self._lock:
            for batch_id, batch_job in self.active_batches.items():
                if batch_job.end_time:
                    age_hours = (current_time - batch_job.end_time).total_seconds() / 3600
                    if age_hours > max_age_hours:
                        expired_batches.append(batch_id)
            
            for batch_id in expired_batches:
                del self.active_batches[batch_id]
        
        api_logger.info(f"Cleaned up {len(expired_batches)} expired batch jobs")
        return len(expired_batches)
    
    def get_all_batches(self, user: str = None) -> List[Dict[str, Any]]:
        """Get all batch jobs (optionally filtered by user)"""
        with self._lock:
            batches = []
            for batch_job in self.active_batches.values():
                if user is None or batch_job.user == user:
                    batches.append(batch_job.get_progress())
            return batches

# Global batch processor instance
_batch_processor: Optional[BatchProcessor] = None

def get_batch_processor() -> BatchProcessor:
    """Get or create the global batch processor instance"""
    global _batch_processor
    if _batch_processor is None:
        _batch_processor = BatchProcessor(max_workers=5)
    return _batch_processor

@frappe.whitelist()
def create_batch_job(operations: List[Dict[str, Any]], max_parallel: int = 3) -> Dict[str, Any]:
    """API endpoint to create a batch job"""
    try:
        processor = get_batch_processor()
        user = frappe.session.user
        
        batch_id = processor.create_batch_job(user, operations, max_parallel)
        
        return {
            "success": True,
            "batch_id": batch_id,
            "message": f"Batch job created with {len(operations)} operations"
        }
        
    except Exception as e:
        api_logger.error(f"Failed to create batch job: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def execute_batch_job(batch_id: str) -> Dict[str, Any]:
    """API endpoint to execute a batch job"""
    try:
        processor = get_batch_processor()
        
        # Execute in background
        def progress_callback(progress_data):
            # Could publish to WebSocket or store in cache
            frappe.cache.set_value(f"batch_progress_{batch_id}", progress_data, expires_in_sec=3600)
        
        batch_job = processor.execute_batch(batch_id, progress_callback)
        
        return {
            "success": True,
            "batch_status": batch_job.get_progress()
        }
        
    except Exception as e:
        api_logger.error(f"Failed to execute batch job: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def get_batch_job_status(batch_id: str) -> Dict[str, Any]:
    """API endpoint to get batch job status"""
    try:
        processor = get_batch_processor()
        status = processor.get_batch_status(batch_id)
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def cancel_batch_job(batch_id: str) -> Dict[str, Any]:
    """API endpoint to cancel a batch job"""
    try:
        processor = get_batch_processor()
        cancelled = processor.cancel_batch(batch_id)
        
        return {
            "success": cancelled,
            "message": "Batch job cancelled" if cancelled else "Batch job could not be cancelled"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }