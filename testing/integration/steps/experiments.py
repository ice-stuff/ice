from os import path
from behave import then
from ice import experiment
from ice.test import logger as test_logger

ASSETS_PATH = path.abspath(
    path.join(path.dirname(__file__), '..', '..', 'assets')
)


@then(
    'we can run \'{exp_path}\' experiment' +
    ' with task \'{task_name}\'' +
    ' under session \'{session_key}\''
)
def step_impl(context, exp_path, task_name, session_key):
    if session_key not in context.sessions:
        raise AssertionError(
            'No session named `{:s}` was found'.format(session_key)
        )
    session = context.sessions[session_key]

    logger = test_logger.get_dummy_logger('expriment')
    try:
        exp = experiment.Experiment(logger, exp_path)
    except experiment.Experiment.LoadError as err:
        raise AssertionError(
            'Failed to load `{:s}`: {:s}'.format(exp_path, str(err))
        )

    instances = context.registry_client.get_instances_list(session)
    _fix_inst_for_ssh(instances, context.spawned_containers)

    ssh_cfg = experiment.CfgSSH('root', path.join(ASSETS_PATH, 'id_rsa'))
    res = exp.run(instances, ssh_cfg, task_name)
    for key, val in res.items():
        if val.failed:
            raise AssertionError(
                'Failed to get hostname of `{:s}`: {:s}'.format(key, val)
            )


def _fix_inst_for_ssh(instances, containers):
    port_per_ip = {}
    for c in containers:
        port = c.spec.port_bindings[22]
        ip = c.get_ip()
        port_per_ip[ip] = port

    # set the address to connect to
    for i in instances:
        net = None
        for n in i.networks:
            if n['iface'] != 'eth0':
                continue
            net = n
            break
        if net is None:
            continue

        if net['addr'] in port_per_ip:
            i.ssh_port = port_per_ip[net['addr']]
        i.public_ip_addr = '127.0.0.1'
        i.public_reverse_dns = 'localhost'
