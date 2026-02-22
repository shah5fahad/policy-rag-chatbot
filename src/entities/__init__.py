from fastapi import APIRouter

from .audit_log import *
from .base import *
from .document import *

api_router = APIRouter(prefix="/v1")
api_router.include_router(
    AuditLogController().router, prefix="/audit-logs", tags=["audit-logs"]
)
api_router.include_router(
    DocumentController().router, prefix="/documents", tags=["documents"]
)
