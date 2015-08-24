import time
import unittest2
import logging
import random
import threading
from ice.registry.client import RegistryClient
from ice.registry.server import RegistryServer
from ice.registry.server.config import CfgRegistryServer
from .fake_data_layer import FakeDataLayer


class ServerThread(threading.Thread):
    def __init__(self, server):
        super(ServerThread, self).__init__()
        self.server = server

    def run(self):
        self.server.run()


class ServerTestCase(unittest2.TestCase):
    def setUp(self):
        self.port = random.randint(50000, 60000)

        cfg = CfgRegistryServer(
            host='localhost',
            port=self.port,
            mongo_host='localhost',
            mongo_port=12345,
            mongo_db='ice'
        )
        logger = logging.getLogger('testing')
        self.server = RegistryServer(cfg, logger, data=FakeDataLayer)

        self.thread = ServerThread(self.server)
        self.thread.daemon = True
        self.thread.start()

        self.client = RegistryClient('localhost', self.port)


class TestMyIP(ServerTestCase):
    def test(self):
        self.assertEqual(self.client.get_my_ip(), '127.0.0.1')
