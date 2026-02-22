# database/entities/document/_model.py
import enum
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Enum
from ..base._model import BaseModel_


class ProcessingStatus(str, enum.Enum):
    """Document processing status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(BaseModel_):
    __tablename__ = "documents"

    filename = Column(String(500), nullable=False, index=True)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    document_type = Column(String(50), nullable=False, index=True)  # pdf, txt, docx
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    doc_metadata = Column(JSON, default={})