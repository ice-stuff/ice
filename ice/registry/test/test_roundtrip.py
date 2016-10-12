import os
import unittest2
import random
import threading
from ice import entities
from ice.registry.client import RegistryClient, CfgRegistryClient
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


class ServerTestCase(unittest2.TestCase):
    def setUp(self):
        self.port = random.randint(50000, 60000)

        mongo_port = int(os.environ.get('TEST_ICE_MONGO_PORT', 27017))
        mongo_db = 'ice' + str(random.randint(10, 1000))
        cfg = CfgRegistryServer(
            host='localhost',
            port=self.port,
            mongo_host='localhost',
            mongo_port=mongo_port,
            mongo_db=mongo_db
        )

        logger = get_dummy_logger('ice-registry-server')

        self.server = RegistryServer(
            cfg,
            [InstancesDomain(), SessionsDomain()],
            logger
        )

        self.thread = ServerThread(self.server)
        self.thread.daemon = True
        self.thread.start()

        self.client = RegistryClient(CfgRegistryClient('localhost', self.port))


class TestMyIP(ServerTestCase):
    def test(self):
        self.assertEqual(self.client.get_my_ip(), '127.0.0.1')


class TestSessionLifecycle(ServerTestCase):
    def setUp(self):
        ServerTestCase.setUp(self)

        self.sess = entities.Session(client_ip_addr='127.128.129.130')

    def test_submit_session(self):
        sess_id = self.client.submit_session(self.sess)
        self.assertIsNotNone(sess_id)

    def test_get_session(self):
        sess_id = self.client.submit_session(self.sess)

        recv_sess = self.client.get_session(sess_id)
        self.assertEquals(self.sess.to_dict(), recv_sess.to_dict())

    def test_delete_session(self):
        sess_id = self.client.submit_session(self.sess)

        self.client.delete_session(self.sess)

        self.assertIsNone(self.client.get_session(sess_id))


class TestInstanceLifecycle(ServerTestCase):
    def setUp(self):
        ServerTestCase.setUp(self)

        self.sess = entities.Session(
            client_ip_addr='127.128.129.130'
        )

        self.client.submit_session(self.sess)

        self.inst = entities.Instance(
            session_id=self.sess.id,
            public_ip_addr='127.0.0.1',
            public_reverse_dns='localhost'
        )

    def test_submit_instance(self):
        inst_id = self.client.submit_instance(self.inst)
        self.assertIsNotNone(inst_id)

    def test_get_instance(self):
        inst_id = self.client.submit_instance(self.inst)

        recv_inst = self.client.get_instance(inst_id)
        self.assertEquals(self.inst.to_dict(), recv_inst.to_dict())

    def test_delete_instance(self):
        inst_id = self.client.submit_instance(self.inst)

        self.client.delete_instance(self.inst)

        recv_inst = self.client.get_instance(inst_id)
        self.assertIsNone(recv_inst)

    def test_delete_session_delets_instances(self):
        inst_id = self.client.submit_instance(self.inst)

        self.client.delete_session(self.sess)

        recv_inst = self.client.get_instance(inst_id)
        self.assertIsNone(recv_inst)


class TestSubmitInstance(ServerTestCase):
    def setUp(self):
        ServerTestCase.setUp(self)
        self.sess = entities.Session(
            client_ip_addr='127.128.129.130'
        )
        self.client.submit_session(self.sess)

    def test_it_validates_ips(self):
        inst = entities.Instance(
            session_id=self.sess.id,
            public_ip_addr='127.x.0.1',
            public_reverse_dns='localhost',
            tags=['a_tag', 'b_tag']
        )
        with self.assertRaisesRegex(
            RegistryClient.APIException, 'must be of Ip type'
        ):
            self.client.submit_instance(inst)

        inst.public_ip_addr = '127.900.0.1'
        with self.assertRaisesRegex(
            RegistryClient.APIException, 'must be of Ip type'
        ):
            self.client.submit_instance(inst)
