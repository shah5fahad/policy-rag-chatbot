from typing import Any, Dict, Optional

from ..base import BaseSchema


class TestSchema(BaseSchema):
    key: str
    value: str
