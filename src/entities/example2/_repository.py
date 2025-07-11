from src.entities.base import BaseRepository

from ._model import Example2


class Example2Repository(BaseRepository):
    def __init__(self):
        super().__init__(model=Example2)
        self.model: Example2 = self.model
