from fastapi import APIRouter

from src.entities.base import *
from src.entities.example import *
from src.entities.example2 import *

api_router = APIRouter()

api_router.include_router(
    ExampleController().router, prefix="/example", tags=["example"]
)
api_router.include_router(
    Example2Controller().router, prefix="/example2", tags=["example2"]
)

__all__ = ["api_router", "Example", "Example2"]
