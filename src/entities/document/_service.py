# database/entities/document/_service.py
from datetime import datetime
from typing import Optional, Dict, Any
from loguru import logger

from ..base import BaseService
from ._repository import DocumentRepository
from ._model import ProcessingStatus


class DocumentService(BaseService):
    def __init__(self):
        super().__init__(DocumentRepository)
    
    async def create_document(self, filename: str, file_path: str, file_size: int, 
                              mime_type: str, document_type: str, 
                              doc_metadata: Optional[Dict[str, Any]] = None) -> Any:
        """Create a new document record."""
        data = {
            "filename": filename,
            "file_path": file_path,
            "file_size": file_size,
            "mime_type": mime_type,
            "document_type": document_type,
            "doc_metadata": doc_metadata or {},
            "status": ProcessingStatus.PENDING
        }
        return await self.create(data)
    
    async def update_document_metadata(self, id: int, metadata: Dict[str, Any]) -> Any:
        """Update document metadata."""
        return await self.patch(id, {"doc_metadata": metadata})
    
    async def mark_as_processing(self, id: int) -> Any:
        """Mark document as processing."""
        return await self.repository.update_status(id, ProcessingStatus.PROCESSING)
    
    async def mark_as_completed(self, id: int) -> Any:
        """Mark document as completed."""
        return await self.repository.update_status(id, ProcessingStatus.COMPLETED)
    
    async def mark_as_failed(self, id: int, error: str) -> Any:
        """Mark document as failed."""
        logger.error(f"Document {id} failed: {error}")
        return await self.repository.update_status(id, ProcessingStatus.FAILED, error)
    
    async def get_document_status(self, id: int) -> Dict[str, Any]:
        """Get document processing status."""
        document = await self.get(id)
        if not document:
            return None
        
        return {
            "id": document.id,
            "filename": document.filename,
            "status": document.status.value if hasattr(document.status, 'value') else document.status,
            "created_at": document.created_at,
            "processed_at": document.processed_at,
            "error_message": document.error_message
        }
        
    async def get_by_status(self, status: ProcessingStatus):
        return await self.repository.get_by_status(status=status)
    
    async def get_by_status_count(self, process: str | None = None):
        filter_by = {"status": process} if process else {}
        return await self.count(filter_by=filter_by)
    
    async def get_pending_documents(self, limit: int = 10) -> list:
        """Get pending documents for processing."""
        return await self.repository.get_by_status(ProcessingStatus.PENDING, limit)
    
    async def get_document_stats(self) -> dict[str, Any]:
        """Get documents stats."""
        return {
            "total": await self.get_by_status_count(),
            "pending": await self.get_by_status_count(ProcessingStatus.PENDING.value),
            "processing": await self.get_by_status_count(ProcessingStatus.PROCESSING.value),
            "completed": await self.get_by_status_count(ProcessingStatus.COMPLETED.value),
            "failed": await self.get_by_status_count(ProcessingStatus.FAILED.value)
        }