from sqlalchemy import Column, String

from ..base._model import BaseModel_


class Test(BaseModel_):
    __tablename__ = "tests"

    key = Column(String(255), nullable=False, index=True)
    value = Column(String(255), nullable=False)
