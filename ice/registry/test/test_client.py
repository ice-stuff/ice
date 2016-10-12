import unittest2
from ice import entities
from ice.registry import client


class TestCompileUserData(unittest2.TestCase):
    def test(self):
        # client will not try to connect to the endpoint
        c = client.RegistryClient(client.CfgRegistryClient('localhost', 8080))

        user_data = c.compile_user_data(
            entities.Session(
                _id='1234abcd',
                client_ip_addr='80.10.100.200'
            ),
            client.CfgRegistryClient('public.ice.registry', 1234)
        )
        expected_user_data = """#!/bin/sh -ex
wget {:s} -O ./ice-agent
chmod +x ./ice-agent
""".format(client.ICE_AGENT_URL)
        expected_user_data += './ice-agent register-self' + \
            ' --api-endpoint http://public.ice.registry:1234' + \
            ' --session-id 1234abcd'
        expected_user_data += '\n'
        self.assertEquals(user_data, expected_user_data)
