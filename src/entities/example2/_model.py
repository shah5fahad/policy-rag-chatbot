from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from src.entities.base import BaseModel

if TYPE_CHECKING:
    from src.entities.example import Example


class Example2(BaseModel, table=True):
    __tablename__ = "examples2"

    name: str = Field(index=True, nullable=False)
    email: str = Field(index=True, nullable=False, unique=True)
    example_id: str = Field(foreign_key="examples.id", nullable=False)

    example: "Example" = Relationship(back_populates="examples2")
