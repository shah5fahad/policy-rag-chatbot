from datetime import datetime
from typing import Any, Dict, Optional

from ..base import BaseSchema


class AuditLogSchema(BaseSchema):
    table_name: str
    record_id: int
    action: str
    old_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    performed_at: datetime
    performed_by: str
