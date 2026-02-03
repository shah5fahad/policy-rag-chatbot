from ..base import BaseService
from ._repository import TestRepository


class TestService(BaseService):
    def __init__(self):
        super().__init__(TestRepository)
