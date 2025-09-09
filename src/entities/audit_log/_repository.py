from ..base import BaseRepository
from ._model import AuditLog


class AuditLogRepository(BaseRepository):
    def __init__(self):
        super().__init__(AuditLog)
