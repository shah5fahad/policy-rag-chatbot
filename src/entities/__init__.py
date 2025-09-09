from fastapi import APIRouter

from .base import *
from .test import *

api_router = APIRouter(prefix="/v1")

api_router.include_router(TestController().router, prefix="/tests", tags=["tests"])
