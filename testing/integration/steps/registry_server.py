import os
import random
import threading
from behave import given
from ice.registry.client import CfgRegistryClient, RegistryClient
from ice.registry.server import RegistryServer
from ice.registry.server.domain.instances import InstancesDomain
from ice.registry.server.domain.sessions import SessionsDomain
from ice.registry.server.config import CfgRegistryServer
from ice.test.logger import get_dummy_logger


class ServerThread(threading.Thread):
    def __init__(self, server):
        super(ServerThread, self).__init__()
        self.server = server

    def run(self):
        self.server.run()


@given('we start iCE registry server')
def step_impl(context):
    registry_port = random.randint(50000, 60000)

    mongo_port = int(os.environ.get('TEST_ICE_MONGO_PORT', 27017))
    mongo_db = 'ice' + str(random.randint(10, 1000))
    cfg = CfgRegistryServer(
        host='0.0.0.0',
        port=registry_port,
        mongo_host='localhost',
        mongo_port=mongo_port,
        mongo_db=mongo_db
    )

    logger = get_dummy_logger('ice-registry-server')

    registry_server = RegistryServer(
        cfg, [InstancesDomain(), SessionsDomain()], logger
    )

    registry_thread = ServerThread(registry_server)
    context.registry_thread = registry_thread
    registry_thread.daemon = True
    registry_thread.start()

    context.registry_client = RegistryClient(CfgRegistryClient(
        host='localhost',
        port=registry_port
    ))
    context.registry_client.ping_with_retries(10)
