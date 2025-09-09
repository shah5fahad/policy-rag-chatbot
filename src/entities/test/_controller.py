from ..base import BaseController
from ._service import TestService


class TestController(BaseController):
    def __init__(self):
        super().__init__(TestService)
