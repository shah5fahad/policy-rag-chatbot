import sys

from ._controller import ExampleController
from ._model import Example

__all__ = ["Example", "ExampleController"]
__author__ = "Kanha Upadhyay"
__doc__ = "This module provides the Example model and its controller for managing example data."
__import__ = "src.modules.example"
sys.modules[__import__] = sys.modules[__name__]
