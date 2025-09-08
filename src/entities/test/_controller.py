from ..base import BaseController
from ._schema import TestSchema
from ._service import TestService


class TestController(BaseController[TestSchema]):
    def __init__(self):
        super().__init__(TestService, TestSchema)
