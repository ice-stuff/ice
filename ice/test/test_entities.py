import unittest2
from ice import entities


class TestEntity(unittest2.TestCase):
    def test_to_json(self):
        e = entities.Entity()
        e.id = 'test-123'
        e.name = 'banana'
        e.age = 12

        self.assertDictEqual(
            e.to_dict(),
            {
                'name': 'banana',
                'age': 12
            }
        )

    def test_to_json_with_underscore(self):
        e = entities.Entity()
        e._test = 123
        e.name = 'banana'

        self.assertEqual(e.to_dict(), {'name': 'banana'})


class TestSession(unittest2.TestCase):
    def test_missing_property(self):
        with self.assertRaises(KeyError):
            entities.Session()

    def test_to_json(self):
        e = entities.Session(client_ip_addr='127.0.0.1')

        self.assertDictEqual(
            e.to_dict(),
            {'client_ip_addr': '127.0.0.1'}
        )


class TestInstance(unittest2.TestCase):
    def test_with_missing_session_id(self):
        with self.assertRaises(KeyError):
            entities.Instance(
                public_ip_addr='127.0.0.1',
                public_reverse_dns='localhost'
            )

    def test_with_missing_ip_addr(self):
        with self.assertRaises(KeyError):
            entities.Instance(
                session_id='banana',
                public_reverse_dns='localhost'
            )

    def test_with_missing_ip_reverse_dns(self):
        with self.assertRaises(KeyError):
            entities.Instance(
                session_id='banana',
                public_ip_addr='127.0.0.1'
            )

    def test_mantadory_fields(self):
        entities.Instance(
            session_id='banana',
            public_ip_addr='127.0.0.1',
            public_reverse_dns='localhost'
        )

    def test_add_network(self):
        entityA = entities.Instance(
            session_id='banana',
            public_ip_addr='127.0.0.1',
            public_reverse_dns='localhost'
        )
        entityA.add_network('192.168.1.12', iface='eth0',
                            bcast_addr='192.168.1.255')
        entityA.add_network('127.0.0.1', iface='lo')
        entityA.add_network('56.58.59.60')

        entityB = entities.Instance(
            session_id='banana',
            public_ip_addr='127.0.0.1',
            public_reverse_dns='localhost',
            networks=[
                {
                    'addr': '192.168.1.12',
                    'iface': 'eth0',
                    'bcast_addr': '192.168.1.255'
                },
                {
                    'addr': '127.0.0.1',
                    'iface': 'lo'
                },
                {
                    'addr': '56.58.59.60'
                }
            ]
        )

        self.assertEqual(entityA.networks, entityB.networks)
