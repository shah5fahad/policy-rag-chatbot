import sys

from ._controller import Example2Controller
from ._model import Example2

__all__ = ["Example2", "Example2Controller"]
__author__ = "Kanha Upadhyay"
__doc__ = "This module provides the Example2 model and its controller for managing example2 data."
__import__ = "src.modules.example2"
sys.modules[__import__] = sys.modules[__name__]
