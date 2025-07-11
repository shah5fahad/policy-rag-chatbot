import uuid
from typing import Optional

from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    __abstract__ = True  # This model should not be instantiated directly
    __table_args__ = {"extend_existing": True}  # Allow table extension

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
        nullable=False,
        unique=True,
    )
