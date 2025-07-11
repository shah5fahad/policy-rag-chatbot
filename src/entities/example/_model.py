from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from src.entities.base import BaseModel

if TYPE_CHECKING:
    from src.entities.example2 import Example2


class Example(BaseModel, table=True):
    __tablename__ = "examples"

    name: str = Field(index=True, nullable=False)
    email: str = Field(index=True, nullable=False, unique=True)

    examples2: list["Example2"] = Relationship(
        back_populates="example",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
