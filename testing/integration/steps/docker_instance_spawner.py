import os
import copy
import tarfile
import StringIO
from os import path
from behave import when
import docker
from ice.registry.client import CfgRegistryClient

ASSETS_PATH = path.abspath(
    path.join(path.dirname(__file__), '..', '..', 'assets')
)


class ContainerSpec():
    # image
    image = 'alpine:latest'
    # added files
    files = []
    # command to run
    command = 'tail -f /dev/null'
    # port mappings
    port_bindings = {}

    def with_image(self, image):
        ns = copy.deepcopy(self)
        ns.image = image
        return ns

    def with_file(self, dest_path, mode, contents):
        ns = copy.deepcopy(self)
        ns.files = ns.files + [{
            'dest_path': dest_path,
            'mode': mode,
            'contents': contents,
        }]
        return ns

    def with_port_binding(self, container_port, host_port):
        ns = copy.deepcopy(self)
        ns.port_bindings = copy.deepcopy(self.port_bindings)
        ns.port_bindings[container_port] = host_port
        return ns

    def with_command(self, command):
        ns = copy.deepcopy(self)
        ns.command = command
        return ns


class Container():
    STATE_CREATED = 0
    STATE_STARTED = 1
    STATE_DELETED = 2

    def __init__(self, id, spec, docker_client):
        self.id = id
        self.spec = spec
        self.docker_client = docker_client
        self.state = self.STATE_CREATED

    def start(self):
        self.docker_client.start(container=self.id)
        self.state = self.STATE_STARTED

    def get_ip(self):
        d = self.docker_client.inspect_container(container=self.id)
        return d['NetworkSettings']['IPAddress']

    def delete(self):
        self.docker_client.remove_container(container=self.id, force=True)
        self.state = self.STATE_DELETED


class ContainerCreator():
    def __init__(self):
        self.docker_client = docker.Client()

    def create(self, spec):
        c = self.docker_client.create_container(
            image=spec.image,
            command=spec.command,
            ports=spec.port_bindings.keys(),
            host_config=self.docker_client.create_host_config(
                port_bindings=spec.port_bindings
            ),
            detach=True
        )
        container_id = c.get('Id')

        for f in spec.files:
            archive_contents = self._make_archive(f)
            self.docker_client.put_archive(
                container=container_id,
                path=path.dirname(f['dest_path']),
                data=archive_contents
            )

        return Container(container_id, spec, self.docker_client)

    def _make_archive(self, file):
        buffer = StringIO.StringIO()
        tf = tarfile.TarFile(fileobj=buffer, mode='w')
        tfi = tarfile.TarInfo()
        tfi.name = './' + path.basename(file['dest_path'])
        tfi.type = tarfile.REGTYPE
        tfi.size = len(file['contents'])
        tfi.mode = file['mode']
        contents_buffer = StringIO.StringIO(file['contents'])
        tf.addfile(tfi, contents_buffer)
        tf.close()

        return buffer.getvalue()


def _make_script(session_key, context):
    if session_key not in context.sessions:
        raise AssertionError(
            'No session named `{:s}` was found'.format(session_key)
        )

    session = context.sessions[session_key]
    reg_cfg = context.registry_client.cfg
    host_ip_from_container = os.environ.get('TEST_HOST_IP_FC', '127.0.0.1')
    container_reg_cfg = CfgRegistryClient(
        host=host_ip_from_container, port=reg_cfg.port
    )
    return context.registry_client.compile_user_data(
        session, container_reg_cfg
    )


@when('we spawn {amt} containers with sshd in session \'{session_key}\'')
def step_impl_w_sshd(context, amt, session_key):
    script = _make_script(session_key, context)
    pub_key = open(path.join(ASSETS_PATH, 'id_rsa.pub'), 'r').read()
    spec = ContainerSpec().with_image('quay.io/macropin/sshd:latest'). \
        with_command(
            '/bin/sh -c \"/tmp/register-self.sh && ' +
            '/usr/sbin/sshd -D -f /etc/ssh/ssh_config\"'
        ). \
        with_file('/root/.ssh/authorized_keys', 0700, pub_key). \
        with_file('/tmp/register-self.sh', 0755, script)

    base_port = 50200
    creator = ContainerCreator()
    for idx in range(0, int(amt)):
        container = creator.create(
            # set port mapping
            spec.with_port_binding(22, base_port + idx)
        )
        container.start()
        context.spawned_containers.append(container)


@when('we spawn {amt} containers in session \'{session_key}\'')
def step_impl(context, amt, session_key):
    script = _make_script(session_key, context)
    spec = ContainerSpec().with_image('alpine:latest'). \
        with_command('/tmp/register-self.sh'). \
        with_file('/tmp/register-self.sh', 0755, script)

    creator = ContainerCreator()
    for idx in range(0, int(amt)):
        container = creator.create(spec)
        container.start()
        context.spawned_containers.append(container)
