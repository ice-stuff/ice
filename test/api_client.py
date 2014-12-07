from unittest import TestCase

from ice import entities
from ice import api_client


class APIClientTest(TestCase):
    def setUp(self):
        self.api = api_client.APIClient('localhost', 5000)

    def tearDown(self):
        del self.api

    def test(self):
        self._test_get_my_ip()

        # Sessions
        session = self._test_submit_session()
        self._test_get_sessions_list(session)

        instances = self._test_submit_instances(session)
        self._test_get_instances_list(session, instances)
        for i in range(0, len(instances) - 2):
            self._test_delete_instance(instances[i])
        self._test_delete_session(session)

    def _test_get_my_ip(self):
        self.assertEquals(self.api.get_my_ip(), '127.0.0.1')

    #
    # Session
    #

    def _test_get_sessions_list(self, current_session):
        sessions = self.api.get_sessions_list()
        found = False
        for sess in sessions:
            if sess.id == current_session.id:
                found = True
                break
        self.assertTrue(found)

    def _test_submit_session(self):
        sess = entities.Session(
            client_ip_addr='127.0.0.1'
        )
        old_amt = len(self.api.get_sessions_list())
        self.assertTrue(
            self.api.submit_session(sess) is not None
        )
        new_amt = len(self.api.get_sessions_list())
        self.assertEqual(new_amt, old_amt + 1)
        return sess

    def _test_delete_session(self, session):
        old_amt = len(self.api.get_sessions_list())
        self.assertTrue(self.api.delete_session(session.id))
        new_amt = len(self.api.get_sessions_list())
        self.assertEqual(new_amt, old_amt - 1)

    #
    # Instance
    #

    def _test_get_instances_list(self, session, current_instances):
        instances = self.api.get_instances_list()
        found_amt = 0
        for inst in instances:
            for our_inst in current_instances:
                if inst.id == our_inst.id:
                    found_amt += 1
                    break
        self.assertEqual(found_amt, len(current_instances))
        self.assertEqual(
            len(self.api.get_instances_list(session.id)),
            len(current_instances)
        )

    def _test_submit_instances(self, session):
        old_amt = len(self.api.get_instances_list())

        instances = []
        for i in range(0, 10):
            inst = entities.Instance(
                session_id=session.id,
                cloud_id='AWS',
                ssh_authorized_fingerprint='corrupted',
                public_ip_addr='56.78.33.%d' % (i + 1),
                public_reverse_dns='jaky.cern.ch'
            )
            inst.add_network(
                '192.168.1.112/24', bcast_addr='192.168.1.255'
            )
            self.assertNotEqual(self.api.submit_instance(inst), None)
            instances.append(inst)

        new_amt = len(self.api.get_instances_list())
        self.assertEquals(new_amt, old_amt + len(instances))

        return instances

    def _test_delete_instance(self, inst):
        old_amt = len(self.api.get_instances_list())
        self.assertTrue(self.api.delete_instance(inst.id))
        new_amt = len(self.api.get_instances_list())
        self.assertEquals(new_amt, old_amt - 1)
