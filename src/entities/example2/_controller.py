from fastapi import Body

from src.entities.base import BaseController

from ._model import Example2
from ._service import Example2Service


class Example2Controller(BaseController):
    def __init__(self):
        super().__init__(Example2Service)
        self.service: Example2Service = self.service

    async def create(self, object: Example2 = Body(...)):
        return await super().create(object)

    async def upsert(self, object: Example2 = Body(...)):
        return await super().upsert(object)
