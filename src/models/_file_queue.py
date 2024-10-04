from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, Integer, String, func

from ._base import Base


class FileQueueStatus(PyEnum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


class FileQueue(Base):
    __tablename__ = "file_queues"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    s3_folder_name = Column(String, nullable=False)
    status = Column(
        Enum(FileQueueStatus), nullable=False, default=FileQueueStatus.UPLOADED
    )
    details = Column(String, nullable=True)
    email_id = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
