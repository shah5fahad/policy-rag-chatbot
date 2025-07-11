from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.entities.base import BaseRepository

from ._model import Example


class ExampleRepository(BaseRepository):
    def __init__(self):
        super().__init__(model=Example)
        self.model: Example = self.model

    async def get_example_with_examples2(self, example_id: str):
        query = (
            select(self.model)
            .options(selectinload(self.model.examples2))
            .where(self.model.id == example_id)
        )
        result = await self.execute(query)
        result: Example | None = result.scalar_one_or_none()
        if not result:
            raise NoResultFound(f"Example with id {example_id} not found")
        examples_2 = result.examples2
        result = result.model_dump()
        result["examples2"] = examples_2
        return result
