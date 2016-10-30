"""Entry point for the iCE application."""
import os
import sys

#
# iCE experiment API
#

from .tasks import Callable, Runner, ParallelRunner, Task, ParallelTask

#
# iCE Version
#

__version__ = '2.1.0-dev'
