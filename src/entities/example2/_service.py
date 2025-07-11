from src.entities.base import BaseService

from ._repository import Example2Repository


class Example2Service(BaseService):
    def __init__(self):
        super().__init__(repository=Example2Repository)
        self.repository: Example2Repository = self.repository
