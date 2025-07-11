from fastapi import Body

from src.entities.base import BaseController

from ._model import Example
from ._service import ExampleService


class ExampleController(BaseController):
    def __init__(self):
        super().__init__(ExampleService)
        self.service: ExampleService = self.service

    async def get(self, example_id: str):
        result = await self.service.get_example_with_examples2(example_id)
        return result

    async def create(self, object: Example = Body(...)):
        return await super().create(object)

    async def upsert(self, object: Example = Body(...)):
        return await super().upsert(object)
