"""Entry point for the iCE application."""
from . import api
from .tasks import Callable, Runner, Task, ParallelTask

__VERSION__ = '0.3.0'
