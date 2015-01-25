"""Entry point for the iCE application."""
from . import api
from .tasks import Callable, Runner, Task, ParallelTask

__version__ = '1.3.0'
