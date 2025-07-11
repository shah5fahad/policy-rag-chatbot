import sys

from ._controller import BaseController
from ._model import BaseModel
from ._repository import BaseRepository
from ._service import BaseService

__all__ = ["BaseModel", "BaseController", "BaseService", "BaseRepository"]
__author__ = "Kanha Upadhyay"
__doc__ = "Base module providing foundational classes for models, controllers, services, and repositories in the application."
__import__ = "src.modules.base"
sys.modules[__import__] = sys.modules[__name__]
