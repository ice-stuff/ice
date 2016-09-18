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

__version__ = '2.1.0'

#
# Configuration directories list
#

CONFIG_DIRS = [
    os.path.join(sys.prefix, 'etc', 'ice'),
    os.path.join(sys.prefix, 'local', 'etc', 'ice'),
    os.path.join('/etc/ice'),
    os.path.expanduser('~/.ice')
]
env_paths_str = os.environ.get('ICE_CONFIG_PATHS')
if env_paths_str is not None:
    env_paths = env_paths_str.split(':')
    for path in env_paths:
        CONFIG_DIRS.append(os.path.abspath(path))

