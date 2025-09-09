from ..base._service import BaseService
from ._repository import AuditLogRepository


class AuditLogService(BaseService):
    def __init__(self):
        super().__init__(AuditLogRepository)
