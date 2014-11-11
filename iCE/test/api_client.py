from unittest import TestCase
from iCE import APIClient
from iCE.entities import Instance


class APIClientTest(TestCase):

    def setUp(self):
        self.api = APIClient('localhost', 5000)

    def tearDown(self):
        del self.api

    def test(self):
        self._test_get_my_ip()
        self._test_get_instances_list()
        inst = self._test_submit_instance()
        self._test_delete_instance(inst)

    def _test_get_my_ip(self):
        self.assertEquals(self.api.get_my_ip(), '127.0.0.1')

    def _test_get_instances_list(self):
        self.api.get_instances_list()  # no exceptions

    def _test_submit_instance(self):
        instances = self.api.get_instances_list()

        inst = Instance(
            cloud_id='AWS',
            ssh_authorized_fingerprint='corrupted',
            public_ip_addr='56.78.33.55',
            public_reverse_dns='jaky.cern.ch'
        )
        inst.add_network(
            '192.168.1.112/24', bcast_addr='192.168.1.255'
        )
        self.assertNotEqual(self.api.submit_instance(inst), None)

        new_instances = self.api.get_instances_list()
        self.assertEquals(len(new_instances) - len(instances), 1)

        return inst

    def _test_delete_instance(self, inst):
        self.assertTrue(self.api.delete_instance(inst.id))
