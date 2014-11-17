#
# A test experiment
#
import os
import random
from fabric.api import run, parallel, env, task, settings, put

KEY_ADDED = {}


@parallel
def get_system_info(instances):
    """Gets system information."""
    run('uname -a')
    return env.host_string


@task
def ping(instances):
    inst = instances[random.randint(0, len(instances) - 1)]
    net = inst.networks[0]
    addr = net['addr'].replace('/20', '')
    with settings(warn_only=True):
        run(
            'sudo dd if=/dev/xvda1 bs=1024 count=102400'
            + ' | ssh -o "StrictHostKeyChecking no" {}'.format(addr)
            + ' "dd of=~/test"'
        )
        run('rm ~/test')


@parallel
def copy_key(instances):
    if env.host_string in KEY_ADDED:
        return

    put(os.path.expanduser('~/.ssh/id_rsa'), '/home/ec2-user/.ssh')
    put(os.path.expanduser('~/.ssh/id_rsa.pub'), '/home/ec2-user/.ssh')
    run('chmod 600 ~/.ssh/id_rsa*')
    KEY_ADDED[env.host_string] = True
