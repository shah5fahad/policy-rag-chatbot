from ..base._controller import BaseController
from ._service import AuditLogService


class AuditLogController(BaseController):
    def __init__(self):
        super().__init__(AuditLogService)
