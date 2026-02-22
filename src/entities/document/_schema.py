# database/entities/document/_schema.py
from typing import Optional, Dict, Any
from datetime import datetime

from ..base import BaseSchema


class DocumentSchema(BaseSchema):
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    document_type: str
    status: Optional[str] = "pending"
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = {}


class DocumentCreateSchema(BaseSchema):
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    document_type: str
    doc_metadata: Optional[Dict[str, Any]] = {}


class DocumentUpdateSchema(BaseSchema):
    status: Optional[str] = None
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = None


class DocumentStatusSchema(BaseSchema):
    id: int  # or str depending on your base ID type
    filename: str
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None