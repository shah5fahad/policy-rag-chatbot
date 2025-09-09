from sqlalchemy import JSON, Column, String

from ..base import BaseModel_


class Test(BaseModel_):
    __tablename__ = "tests"

    name = Column(String(255), nullable=False, unique=True)
    data = Column(JSON, nullable=True)
