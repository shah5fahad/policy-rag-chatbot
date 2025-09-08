from typing import Any, Dict, Optional

from ..base import BaseSchema


class TestSchema(BaseSchema):
    name: str
    data: Optional[Dict[str, Any]]
