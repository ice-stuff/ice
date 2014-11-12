#
# A test experiment
#
from fabric.api import run, parallel, env


@parallel
def get_system_info(instances):
    """Gets system information."""
    run('uname -a')
    return env.host_string
