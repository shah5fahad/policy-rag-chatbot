# database/entities/document/_repository.py
from typing import Optional, List
from unittest import result
from sqlalchemy import select
from datetime import datetime

from ..base import BaseRepository
from ._model import Document, ProcessingStatus


class DocumentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Document)
    
    async def get_by_filename(self, filename: str) -> Optional[Document]:
        """Get document by filename."""
        async with self.get_session() as session:
            query = select(self.model).where(self.model.filename == filename)
            result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_status(self, status: ProcessingStatus, limit: int = 100) -> List[Document]:
        """Get documents by status."""
        async with self.get_session() as session:
            query = select(self.model).where(
                self.model.status == status
            ).order_by(self.model.created_at).limit(limit)
            result = await session.execute(query)
        return result.scalars().all()
    
    async def update_status(self, id: int, status: ProcessingStatus, error: str = None) -> Optional[Document]:
        """Update document status."""
        async with self.get_session() as session:
            document = await session.get(self.model, id)
            if document:
                document.status = status
                if status == ProcessingStatus.COMPLETED:
                    document.processed_at = datetime.now()
                if error:
                    document.error_message = error
                await session.commit()
                await session.refresh(document)
        return document