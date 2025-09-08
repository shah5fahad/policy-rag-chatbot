from ..base import BaseRepository
from ._model import Test


class TestRepository(BaseRepository):
    def __init__(self):
        super().__init__(Test)
