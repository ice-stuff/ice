from unittest import TestCase
from iCE import APIClient
from iCE.entities import Instance


class APIClientTest(TestCase):

    def setUp(self):
        self.api = APIClient('localhost', 5000)

    def tearDown(self):
        del self.api

    def test(self):
        self._testGetMyIp()
        self._testGetInstancesList()
        inst = self._testSubmitInstance()
        self._testDeleteInstance(inst)

    def _testGetMyIp(self):
        self.assertEquals(self.api.getMyIP(), '127.0.0.1')

    def _testGetInstancesList(self):
        self.api.getInstancesList()  # no exceptions

    def _testSubmitInstance(self):
        instances = self.api.getInstancesList()

        inst = Instance(
            cloud_id='AWS',
            ssh_authorized_fingerprint='corrupted',
            public_ip_addr='56.78.33.55',
            public_reverse_dns='jaky.cern.ch'
        )
        inst.add_network(
            '192.168.1.112/24', bcast_addr='192.168.1.255'
        )
        self.assertNotEqual(self.api.submitInstance(inst), None)

        new_instances = self.api.getInstancesList()
        self.assertEquals(len(new_instances) - len(instances), 1)

        return inst

    def _testDeleteInstance(self, inst):
        self.assertTrue(self.api.deleteInstance(inst.id))
