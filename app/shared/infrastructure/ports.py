from typing import Protocol, Any, Dict, Optional
from enum import Enum

class StoragePort(Protocol):
    """Port for storing and retrieving files (e.g. datasets, images, reports)."""
    def save(self, file_name: str, content: bytes, content_type: str) -> str:
        """Saves a file and returns its URI or path."""
        ...
        
    def get(self, file_path: str) -> bytes:
        """Retrieves a file's content by its URI or path."""
        ...
        
    def delete(self, file_path: str) -> bool:
        """Deletes a file by its URI or path."""
        ...

class EmailPort(Protocol):
    """Port for sending emails."""
    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """Sends an email."""
        ...

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class QueuePort(Protocol):
    """Port for background job execution (e.g., forecasting)."""
    def enqueue(self, task_name: str, payload: Dict[str, Any]) -> str:
        """Enqueues a job and returns its tracking ID."""
        ...
        
    def get_status(self, job_id: str) -> JobStatus:
        """Gets the status of a background job."""
        ...
        
    def get_result(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Gets the result of a completed job."""
        ...

class HttpClientPort(Protocol):
    """Port for external HTTP communications (e.g., FTGM Engine)."""
    def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Performs a GET request."""
        ...
        
    def post(self, url: str, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Performs a POST request."""
        ...
