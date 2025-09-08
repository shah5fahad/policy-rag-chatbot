from sqlalchemy import JSON, Column, String

from ..base import BaseModel


class Test(BaseModel):
    __tablename__ = "tests"

    name = Column(String(255), nullable=False, unique=True)
    data = Column(JSON, nullable=True)
