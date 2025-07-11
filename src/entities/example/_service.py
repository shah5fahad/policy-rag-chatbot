from src.entities.base import BaseService

from ._repository import ExampleRepository


class ExampleService(BaseService):
    def __init__(self):
        super().__init__(repository=ExampleRepository)
        self.repository: ExampleRepository = self.repository

    async def get_example_with_examples2(self, example_id: str):
        result = await self.repository.get_example_with_examples2(example_id)
        return result
