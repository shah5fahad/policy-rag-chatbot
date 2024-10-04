from ._file_controller import FileController

file_router = FileController().router
api_router = file_router

__all__ = ["api_router"]
__version__ = "0.1.0"
__author__ = "Kanha Upadhyay"
