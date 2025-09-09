from fastapi import Body

from ..base import BaseController
from ._schema import AuditLogSchema
from ._service import AuditLogService


class AuditLogController(BaseController):
    def __init__(self):
        super().__init__(AuditLogService)

    async def create(self, data: AuditLogSchema = Body(...)):
        return await super().create(data.model_dump())

    async def patch(self, id: int, data: AuditLogSchema = Body(...)):
        return await super().patch(id, data.model_dump())
