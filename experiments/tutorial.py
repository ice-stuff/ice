#
# A test experiment
#
from fabric.api import task, run


@task
def get_system_info():
    run('uname -a')
