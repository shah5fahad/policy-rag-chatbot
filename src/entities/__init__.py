from fastapi import APIRouter

from .audit_log import *
from .base import *
from .test import *

api_router = APIRouter(prefix="/v1")
api_router.include_router(
    AuditLogController().router, prefix="/audit-logs", tags=["audit-logs"]
)
api_router.include_router(TestController().router, prefix="/tests", tags=["tests"])
