from fastapi import APIRouter

from ._file_controller import FileController

api_router = APIRouter()
api_router.include_router(FileController().router, prefix="/v1/files", tags=["File"])

__all__ = ["api_router"]
__version__ = "0.1.0"
__author__ = "Kanha Upadhyay"
