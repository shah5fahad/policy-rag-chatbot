from fastapi import Body, HTTPException

from ..base import BaseController
from ._schema import AuditLogSchema
from ._service import AuditLogService


class AuditLogController(BaseController):
    def __init__(self):
        super().__init__(AuditLogService)

    async def create(self, data: AuditLogSchema = Body(...)):
        raise HTTPException(status_code=405, detail="Method not allowed")

    async def patch(self, id: int, data: AuditLogSchema = Body(...)):
        raise HTTPException(status_code=405, detail="Method not allowed")

    async def delete(self, id: int):
        raise HTTPException(status_code=405, detail="Method not allowed")
